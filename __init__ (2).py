"""Emparejado de productos entre tiendas.

Regla de oro: el style code (SKU del fabricante) es la llave canónica.
Si dos tiendas nombran distinto al mismo par pero comparten SKU, se agrupan.
Sin SKU, matching difuso por tokens de nombre (marca + modelo + colorway).
"""
import re
import unicodedata
from rapidfuzz import fuzz

FUZZY_THRESHOLD = 87  # 0-100; subir si agrupa de más, bajar si agrupa de menos

STOPWORDS = {
    "mens", "men", "womens", "women", "hombre", "mujer", "para", "de",
    "shoes", "shoe", "sneaker", "sneakers", "tenis", "zapatillas", "casual",
    "running", "road", "the", "and", "unisex", "adult", "kids", "sandal", "sandals",
}


def norm_sku(s: str | None) -> str:
    if not s:
        return ""
    return re.sub(r"[^A-Z0-9]", "", s.upper())


def norm_name(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z0-9\s]", " ", s.lower())
    tokens = [t for t in s.split() if t not in STOPWORDS]
    return " ".join(tokens)


def name_similarity(a: str, b: str) -> float:
    return fuzz.token_set_ratio(norm_name(a), norm_name(b))


def group_listings(listings: list[dict]) -> list[dict]:
    """Agrupa listados de distintas tiendas en productos canónicos.

    Devuelve: [{key, title, sku, image, listings: [...]}]
    """
    groups: list[dict] = []
    sku_index: dict[str, dict] = {}

    # 1) Agrupar por SKU exacto
    no_sku = []
    for l in listings:
        k = norm_sku(l.get("sku"))
        if k:
            if k not in sku_index:
                g = {"key": k, "title": l["title"], "sku": l.get("sku"),
                     "image": l.get("image"), "listings": []}
                sku_index[k] = g
                groups.append(g)
            g = sku_index[k]
            g["listings"].append(l)
            if not g.get("image") and l.get("image"):
                g["image"] = l["image"]
        else:
            no_sku.append(l)

    # 2) Sin SKU: pegar por similitud de nombre al mejor grupo existente
    for l in no_sku:
        best, best_score = None, 0.0
        for g in groups:
            score = max(name_similarity(l["title"], x["title"]) for x in g["listings"])
            if score > best_score:
                best, best_score = g, score
        if best is not None and best_score >= FUZZY_THRESHOLD:
            best["listings"].append(l)
        else:
            groups.append({"key": f"name:{norm_name(l['title'])[:40]}",
                           "title": l["title"], "sku": l.get("sku"),
                           "image": l.get("image"), "listings": [l]})

    # Título del grupo: el más corto suele ser el más limpio
    for g in groups:
        g["title"] = min((x["title"] for x in g["listings"]), key=len)
    return groups
