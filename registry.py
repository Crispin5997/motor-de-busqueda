"""Tienda demo: datos de ejemplo para ver la app funcionando de inmediato.

Nota cómo cada 'tienda' nombra distinto al mismo modelo pero el SKU los
agrupa — exactamente el comportamiento esperado con tiendas reales.
Se apaga con demo_mode: false en stores.yaml.
"""
from .base import StoreAdapter

# key de tienda demo -> catálogo
CATALOG = {
    "demo_fl": [
        dict(title="On Cloudmonster Men's Road Running Shoes", sku="61.98288",
             price=153.99, list_price=169.99, q="on cloudmonster"),
        dict(title="New Balance 9060 - Men's", sku="U9060ECA",
             price=149.99, list_price=None, q="new balance 9060 nb"),
        dict(title="Birkenstock Boston Soft Footbed Suede", sku="0660461",
             price=170.00, list_price=None, q="birkenstock boston"),
    ],
    "demo_dicks": [
        dict(title="On Men's Cloudmonster Running Shoes", sku="61.98288",
             price=169.99, list_price=None, q="on cloudmonster"),
        dict(title="New Balance Men's 9060 Shoes", sku="U9060ECA",
             price=144.99, list_price=149.99, q="new balance 9060 nb"),
    ],
    "demo_jd": [
        dict(title="Cloudmonster 'Undyed White'", sku="61.98288",
             price=170.00, list_price=None, q="on cloudmonster"),
        dict(title="NB 9060 Sea Salt", sku="U9060ECA",
             price=129.99, list_price=149.99, q="new balance 9060 nb"),
        dict(title="Veja Campo Chromefree Leather", sku="CP0502429",
             price=150.00, list_price=None, q="veja campo"),
    ],
    "demo_on": [
        dict(title="Cloudmonster", sku="61.98288",
             price=170.00, list_price=None, q="on cloudmonster"),
    ],
    "demo_mx": [
        dict(title="Tenis On Cloudmonster para hombre", sku="61.98288",
             price=3599.00, list_price=3999.00, q="on cloudmonster"),
        dict(title="Veja Campo blanco natural", sku="CP0502429",
             price=3199.00, list_price=None, q="veja campo"),
        dict(title="Sandalias Birkenstock Boston gamuza", sku="0660461",
             price=3499.00, list_price=None, q="birkenstock boston"),
    ],
}


class DemoAdapter(StoreAdapter):
    async def search(self, query: str) -> list[dict]:
        ql = set(query.lower().split())
        out = []
        for item in CATALOG.get(self.cfg.key, []):
            hay = set(item["q"].split()) | set(item["title"].lower().split()) | {item["sku"].lower()}
            if ql & hay:
                out.append({
                    "title": item["title"],
                    "url": f"https://demo/{item['sku']}",
                    "price": item["price"],
                    "list_price": item["list_price"],
                    "sku": item["sku"],
                    "image": None,
                    "in_stock": True,
                })
        return out
