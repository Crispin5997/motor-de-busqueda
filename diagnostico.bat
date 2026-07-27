"""Carga de configuración (tiendas, cupones, settings)."""
from dataclasses import dataclass, field
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
STORES_YAML = ROOT / "config" / "stores.yaml"
COUPONS_YAML = ROOT / "config" / "coupons.yaml"


@dataclass
class StoreCfg:
    key: str
    name: str
    type: str
    country: str            # "us" | "mx"
    currency: str           # "USD" | "MXN"
    base_url: str
    shipping: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)
    active: bool = True


@dataclass
class Coupon:
    store: str
    code: str
    kind: str               # "percent" | "fixed"
    value: float
    min_purchase: float = 0
    note: str = ""
    active: bool = True


def load_settings() -> dict:
    data = yaml.safe_load(STORES_YAML.read_text(encoding="utf-8"))
    return data.get("settings", {})


def load_stores() -> list[StoreCfg]:
    data = yaml.safe_load(STORES_YAML.read_text(encoding="utf-8"))
    settings = data.get("settings", {})
    demo = bool(settings.get("demo_mode", False))
    out = []
    for s in data.get("stores", []):
        cfg = StoreCfg(
            key=s["key"], name=s["name"], type=s["type"],
            country=s.get("country", "us"), currency=s.get("currency", "USD"),
            base_url=s.get("base_url", ""),
            shipping=s.get("shipping") or {},
            headers=s.get("headers") or {},
            active=bool(s.get("active", True)),
        )
        if not cfg.active:
            continue
        if cfg.type == "demo" and not demo:
            continue
        out.append(cfg)
    return out


def load_coupons() -> list[Coupon]:
    if not COUPONS_YAML.exists():
        return []
    data = yaml.safe_load(COUPONS_YAML.read_text(encoding="utf-8")) or {}
    out = []
    for c in data.get("coupons", []):
        if not c.get("active", True):
            continue
        out.append(Coupon(
            store=c["store"], code=c["code"], kind=c.get("kind", "percent"),
            value=float(c.get("value", 0)), min_purchase=float(c.get("min_purchase", 0)),
            note=c.get("note", ""), active=True,
        ))
    return out


def add_coupon(c: dict):
    data = yaml.safe_load(COUPONS_YAML.read_text(encoding="utf-8")) or {"coupons": []}
    data.setdefault("coupons", []).append(c)
    COUPONS_YAML.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
