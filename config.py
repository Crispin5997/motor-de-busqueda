"""Importador masivo de tiendas desde marcadores de Chrome.

Uso:
    python importar_tiendas.py bookmarks.html
    (o arrastra el archivo encima de importar_tiendas.bat)

Cómo exportar los marcadores:
    Chrome -> chrome://bookmarks -> menú ⋮ (arriba derecha) -> Exportar marcadores

Qué hace:
1. Saca todos los dominios de tus marcadores (ignora YouTube, Google, redes, etc.)
2. Prueba cada uno: si es tienda Shopify (/products.json responde), la agrega
   a config/stores.yaml lista para usar, con país/moneda según el dominio.
3. Las que no son Shopify quedan en config/tiendas_pendientes.yaml —
   pásale esa lista a Claude y se les hace adaptador dedicado.

No toca las tiendas que ya tienes: solo agrega las nuevas al final.
"""
import asyncio
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import httpx
import yaml

ROOT = Path(__file__).resolve().parent
STORES_YAML = ROOT / "config" / "stores.yaml"
PENDING_YAML = ROOT / "config" / "tiendas_pendientes.yaml"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

IGNORAR = {
    "google", "youtube", "gmail", "facebook", "instagram", "tiktok", "twitter",
    "x", "whatsapp", "reddit", "pinterest", "linkedin", "netflix", "spotify",
    "wikipedia", "amazon", "mercadolibre", "ebay", "aliexpress", "paypal",
    "stockx", "goat", "claude", "anthropic", "openai", "chatgpt", "gemini",
    "github", "localhost", "discord", "twitch", "canva", "shopify",
}


def extraer_dominios(html: str) -> list[str]:
    urls = re.findall(r'HREF="(https?://[^"]+)"', html, flags=re.I)
    vistos, out = set(), []
    for u in urls:
        p = urlparse(u)
        host = p.netloc.lower()
        raiz = host.split(":")[0].removeprefix("www.")
        marca = raiz.split(".")[0]
        if not raiz or raiz in vistos or marca in IGNORAR:
            continue
        vistos.add(raiz)
        out.append(f"{p.scheme}://{host}")
    return out


def slug(base_url: str) -> str:
    host = urlparse(base_url).netloc.removeprefix("www.")
    return re.sub(r"[^a-z0-9]+", "_", host.rsplit(".", 2)[0].lower()).strip("_") or host


def es_mx(base_url: str) -> bool:
    host = urlparse(base_url).netloc.lower()
    return host.endswith(".mx")


async def probar_shopify(client: httpx.AsyncClient, base: str, sem: asyncio.Semaphore):
    async with sem:
        try:
            r = await client.get(f"{base}/products.json", params={"limit": 1})
            if r.status_code == 200 and "products" in r.json():
                return base, True
        except Exception:
            pass
        return base, False


def claves_existentes() -> tuple[set, set]:
    data = yaml.safe_load(STORES_YAML.read_text(encoding="utf-8")) or {}
    keys, hosts = set(), set()
    for s in data.get("stores", []):
        keys.add(str(s.get("key")))
        h = urlparse(str(s.get("base_url", ""))).netloc.removeprefix("www.")
        if h:
            hosts.add(h)
    return keys, hosts


def bloque_yaml(base: str) -> str:
    mx = es_mx(base)
    ship = "{ free_over: 1500, flat: 150 }" if mx else "{ free_over: 75, flat: 8 }"
    return (
        f"\n  - key: {slug(base)}\n"
        f"    name: \"{urlparse(base).netloc.removeprefix('www.')}\"\n"
        f"    type: shopify\n"
        f"    country: {'mx' if mx else 'us'}\n"
        f"    currency: {'MXN' if mx else 'USD'}\n"
        f"    base_url: \"{base}\"\n"
        f"    shipping: {ship}   # AJUSTAR: umbral/costo real de esta tienda\n"
        f"    active: true\n"
    )


async def main():
    if len(sys.argv) < 2 or not Path(sys.argv[1]).exists():
        print("Uso: python importar_tiendas.py bookmarks.html")
        print("(Chrome -> chrome://bookmarks -> menu \u22ee -> Exportar marcadores)")
        return

    html = Path(sys.argv[1]).read_text(encoding="utf-8", errors="ignore")
    dominios = extraer_dominios(html)
    print(f"Dominios candidatos en tus marcadores: {len(dominios)}")
    if not dominios:
        return

    keys, hosts = claves_existentes()
    dominios = [d for d in dominios
                if urlparse(d).netloc.removeprefix("www.") not in hosts]

    print("Probando cu\u00e1les son Shopify (tienda por tienda, como usuario)...")
    sem = asyncio.Semaphore(8)
    async with httpx.AsyncClient(headers={"User-Agent": UA}, timeout=8,
                                 follow_redirects=True) as client:
        res = await asyncio.gather(*[probar_shopify(client, d, sem) for d in dominios])

    shopify = [b for b, ok in res if ok]
    otras = [b for b, ok in res if not ok]

    if shopify:
        with open(STORES_YAML, "a", encoding="utf-8") as f:
            f.write("\n  # ---------- importadas de marcadores ----------\n")
            for b in shopify:
                if slug(b) in keys:
                    continue
                f.write(bloque_yaml(b))
                print(f"  [OK Shopify] {b}  -> agregada")

    if otras:
        data = {"pendientes": otras,
                "nota": "No son Shopify: p\u00e1sale esta lista a Claude para hacerles adaptador"}
        PENDING_YAML.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
                                encoding="utf-8")
        for b in otras:
            print(f"  [pendiente]  {b}")

    print(f"\nResumen: {len(shopify)} tiendas agregadas y listas, "
          f"{len(otras)} en tiendas_pendientes.yaml")
    print("Reinicia el buscador para que aparezcan. Revisa el envio de cada una en stores.yaml.")


if __name__ == "__main__":
    asyncio.run(main())
