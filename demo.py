"""Interfaz de adaptador de tienda.

Cada tienda implementa search(query) -> lista de listados crudos:
{title, url, price, list_price?, sku?, image?, in_stock}

El resto del sistema (matching, cupones, envío, historial) es agnóstico
a la tienda: agregar tiendas nunca toca el núcleo.
"""
from abc import ABC, abstractmethod
import httpx
from core.config import StoreCfg

# curl_cffi imita la huella TLS de Chrome real. Es la lección del monitor de
# mipase v4: Akamai/Cloudflare no solo miran headers, miran la huella TLS de
# la conexión. Con curl_cffi la petición ES indistinguible de un Chrome a
# nivel de red, pero sigue siendo una petición directa: milisegundos, sin
# navegador. Si no está instalado, se cae a httpx normal.
try:
    from curl_cffi.requests import AsyncSession
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

BASE_HEADERS = {
    "User-Agent": UA,
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
}


def stealth_client(extra_headers: dict | None = None, timeout: float = 12):
    """Cliente que se ve como un usuario real de Chrome (huella TLS incluida)."""
    if HAS_CURL_CFFI:
        # impersonate ajusta TLS + headers coherentes de Chrome; solo se
        # agregan extras del usuario (ej. Cookie pegada desde DevTools).
        return AsyncSession(impersonate="chrome", timeout=timeout,
                            headers=extra_headers or {})
    h = dict(BASE_HEADERS)
    h.update(extra_headers or {})
    return httpx.AsyncClient(headers=h, timeout=timeout, follow_redirects=True)


class StoreAdapter(ABC):
    def __init__(self, cfg: StoreCfg, timeout: float = 12):
        self.cfg = cfg
        self.timeout = timeout

    @property
    def headers(self) -> dict:
        h = dict(BASE_HEADERS)
        h.update(self.cfg.headers or {})
        return h

    def client(self) -> httpx.AsyncClient:
        """Cliente simple (tiendas sin protección, ej. Shopify)."""
        return httpx.AsyncClient(headers=self.headers, timeout=self.timeout,
                                 follow_redirects=True)

    def stealth(self):
        """Cliente con huella TLS de Chrome (tiendas con Akamai/DataDome)."""
        return stealth_client(self.cfg.headers or {}, self.timeout)

    @abstractmethod
    async def search(self, query: str) -> list[dict]:
        ...
