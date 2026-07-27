"""Adaptadores para tiendas grandes con protección anti-bot.

Foot Locker, Dick's y JD usan Akamai/DataDome: una petición limpia desde
datacenter casi siempre da 403. Desde tu IP residencial las probabilidades
mejoran mucho, y si una tienda sigue bloqueando, se le pegan cookies de tu
navegador en stores.yaml (headers: {Cookie: "..."}), igual que hicimos con
el monitor de mipase.

Si la tienda bloquea, el adaptador NO truena: reporta estado "bloqueada"
y la interfaz lo muestra, el resto de tiendas sigue funcionando.
"""
import re
from .base import StoreAdapter


class BlockedError(Exception):
    pass


def _check_blocked(r):
    if r.status_code in (403, 406, 429) or "captcha" in r.text[:2000].lower():
        raise BlockedError(f"HTTP {r.status_code}")


class FootLockerAdapter(StoreAdapter):
    async def search(self, query: str) -> list[dict]:
        base = self.cfg.base_url.rstrip("/")
        async with self.stealth() as c:
            r = await c.get(f"{base}/api/products/search",
                            params={"query": query, "currentPage": 0, "pageSize": 12},
                            headers={"x-api-lang": "en-US", "Referer": base + "/"})
            _check_blocked(r)
            r.raise_for_status()
            data = r.json()
            out = []
            for p in (data.get("products") or [])[:12]:
                sku = p.get("sku") or p.get("styleSku") or None
                price_obj = p.get("price") or {}
                price = price_obj.get("value") or price_obj.get("salePrice")
                list_price = price_obj.get("originalPrice")
                url = base + (p.get("url") or "")
                img = None
                images = p.get("images") or []
                if images:
                    img = (images[0].get("url") if isinstance(images[0], dict) else images[0])
                if price:
                    out.append({"title": p.get("name", ""), "url": url,
                                "price": float(price),
                                "list_price": float(list_price) if list_price else None,
                                "sku": sku, "image": img, "in_stock": True})
            return out


class DicksAdapter(StoreAdapter):
    async def search(self, query: str) -> list[dict]:
        base = self.cfg.base_url.rstrip("/")
        async with self.stealth() as c:
            # API de catálogo de Dick's (puede cambiar; ajustar si regresa vacío)
            r = await c.get(
                "https://prod-catalog-product-api.dickssportinggoods.com/v2/search",
                params={"searchTypes": "PINNING", "searchTerm": query,
                        "pageNumber": 0, "pageSize": 12, "selectedStore": "0"},
                headers={"Referer": base + "/", "Origin": base})
            _check_blocked(r)
            r.raise_for_status()
            data = r.json()
            out = []
            for p in (data.get("productVOs") or data.get("products") or [])[:12]:
                title = p.get("name") or p.get("title") or ""
                sku = p.get("style") or p.get("parentSku") or None
                price = None; list_price = None
                pr = p.get("priceVO") or p.get("price") or {}
                if isinstance(pr, dict):
                    price = pr.get("minSalePrice") or pr.get("salePrice") or pr.get("minListPrice")
                    list_price = pr.get("minListPrice") or pr.get("listPrice")
                seo = p.get("seoURL") or p.get("url") or ""
                url = seo if seo.startswith("http") else base + "/p/" + seo.lstrip("/")
                if price:
                    out.append({"title": title, "url": url, "price": float(price),
                                "list_price": float(list_price) if list_price else None,
                                "sku": sku, "image": p.get("imageURL"), "in_stock": True})
            return out


class JDSportsAdapter(StoreAdapter):
    async def search(self, query: str) -> list[dict]:
        base = self.cfg.base_url.rstrip("/")
        async with self.stealth() as c:
            r = await c.get(f"{base}/api/search/{query}",
                            params={"from": 0, "max": 12},
                            headers={"Referer": base + "/"})
            _check_blocked(r)
            r.raise_for_status()
            data = r.json()
            out = []
            items = data.get("products") or data.get("items") or []
            for p in items[:12]:
                price = p.get("salePrice") or p.get("price")
                if isinstance(price, str):
                    price = float(re.sub(r"[^\d.]", "", price) or 0)
                url = p.get("url") or ""
                if url and not url.startswith("http"):
                    url = base + url
                if price:
                    out.append({"title": p.get("name", ""), "url": url,
                                "price": float(price),
                                "list_price": _f(p.get("listPrice") or p.get("originalPrice")),
                                "sku": p.get("sku") or p.get("styleId"),
                                "image": p.get("image") or p.get("imageUrl"),
                                "in_stock": True})
            return out


class OnRunningAdapter(StoreAdapter):
    """on.com corre en stack propio; este endpoint puede requerir ajuste.
    Si regresa bloqueada/vacía: abrir on.com con DevTools (pestaña Network),
    buscar un modelo y pegar aquí el endpoint real de búsqueda que aparezca."""
    async def search(self, query: str) -> list[dict]:
        base = self.cfg.base_url.rstrip("/")
        async with self.stealth() as c:
            r = await c.get(f"{base}/api/search", params={"q": query},
                            headers={"Referer": base + "/"})
            _check_blocked(r)
            r.raise_for_status()
            data = r.json()
            out = []
            items = data.get("products") or data.get("results") or []
            for p in items[:12]:
                price = p.get("price")
                if isinstance(price, dict):
                    price = price.get("value")
                if price:
                    url = p.get("url") or ""
                    if url and not url.startswith("http"):
                        url = base + url
                    out.append({"title": p.get("name", ""), "url": url,
                                "price": float(price), "list_price": None,
                                "sku": p.get("sku") or p.get("id"),
                                "image": p.get("image"), "in_stock": True})
            return out


def _f(v):
    try:
        return float(v) if v else None
    except (TypeError, ValueError):
        return None
