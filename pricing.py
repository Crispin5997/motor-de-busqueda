"""Buscador privado de pares — servidor local.

Correr:  python -m uvicorn app:app --port 8712
Abrir:   http://localhost:8712
"""
import asyncio
import base64
import json
import os
from pathlib import Path

import httpx
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse

from core import db
from core.config import load_settings, load_coupons, load_stores, add_coupon
from core.matching import group_listings
from core.pricing import compute_landed
from core.notify import discord
from market import reference
from stores.registry import build_adapters
from stores.bigbox import BlockedError

app = FastAPI(title="Buscador de Pares")
db.init()

STATIC = Path(__file__).resolve().parent / "static"


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


# ---------------------------------------------------------------- búsqueda

async def _search_store(adapter, query: str):
    try:
        listings = await adapter.search(query)
        return adapter.cfg, {"status": "ok", "count": len(listings)}, listings
    except BlockedError as e:
        return adapter.cfg, {"status": "bloqueada", "detail": str(e)}, []
    except Exception as e:
        return adapter.cfg, {"status": "error", "detail": f"{type(e).__name__}: {e}"[:120]}, []


async def run_search(query: str, country: str = "all") -> dict:
    settings = load_settings()
    coupons = load_coupons()
    fx = float(settings.get("fx_usd_mxn", 18.7))

    adapters = [a for a in build_adapters()
                if country == "all" or a.cfg.country == country]

    results = await asyncio.gather(*[_search_store(a, query) for a in adapters])

    statuses, all_listings = {}, []
    for cfg, status, listings in results:
        statuses[cfg.key] = {"name": cfg.name, "country": cfg.country, **status}
        for l in listings:
            all_listings.append(compute_landed(l, cfg, coupons, fx))

    groups = group_listings(all_listings)
    for g in groups:
        g["listings"].sort(key=lambda l: l["total_mxn"])
        g["best"] = g["listings"][0] if g["listings"] else None
    groups.sort(key=lambda g: g["best"]["total_mxn"] if g["best"] else 1e18)

    # Referencia de mercado (StockX / GOAT) en paralelo
    sx, gt = await asyncio.gather(
        reference.stockx(query, cookie=settings.get("stockx_cookie", "")),
        reference.goat(query))

    return {"query": query, "groups": groups, "stores": statuses,
            "market": {"stockx": sx, "goat": gt},
            "fx_usd_mxn": fx}


@app.get("/api/search")
async def api_search(q: str, country: str = "all"):
    if not q.strip():
        return JSONResponse({"error": "query vacío"}, status_code=400)
    return await run_search(q.strip(), country)


# ---------------------------------------------------------------- imagen -> modelo

IDENTIFY_PROMPT = (
    "Identifica el calzado de la imagen (sneaker, sandalia, etc). "
    "Responde SOLO un JSON, sin markdown, con esta forma exacta: "
    '{"brand": "...", "model": "...", "colorway": "...", '
    '"style_code_guess": "... o null", "query": "texto corto para buscarlo en tiendas"}'
)


@app.post("/api/identify")
async def api_identify(image: UploadFile = File(...)):
    api_key = (load_settings().get("anthropic_api_key") or "").strip() \
        or os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return JSONResponse(
            {"error": "Falta tu API key. Pégala en config/stores.yaml → "
                      "anthropic_api_key y reinicia el buscador."}, status_code=400)
    raw = await image.read()
    media = image.content_type or "image/jpeg"
    b64 = base64.b64encode(raw).decode()
    try:
        async with httpx.AsyncClient(timeout=60) as c:
            r = await c.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": api_key,
                         "anthropic-version": "2023-06-01",
                         "content-type": "application/json"},
                json={"model": "claude-sonnet-4-6", "max_tokens": 400,
                      "messages": [{"role": "user", "content": [
                          {"type": "image",
                           "source": {"type": "base64", "media_type": media, "data": b64}},
                          {"type": "text", "text": IDENTIFY_PROMPT}]}]})
        r.raise_for_status()
        text = "".join(b.get("text", "") for b in r.json().get("content", []))
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        return JSONResponse({"error": f"No se pudo identificar: {type(e).__name__}"},
                            status_code=500)


# ---------------------------------------------------------------- watchlist

@app.get("/api/watchlist")
def api_watchlist():
    return db.get_watchlist()


@app.post("/api/watchlist")
async def api_watchlist_add(payload: dict):
    q = (payload.get("query") or "").strip()
    if q:
        db.add_watch(q, payload.get("note", ""))
    return db.get_watchlist()


@app.delete("/api/watchlist/{wid}")
def api_watchlist_del(wid: int):
    db.remove_watch(wid)
    return db.get_watchlist()


@app.post("/api/refresh")
async def api_refresh():
    """Corre todas las búsquedas de la watchlist, guarda historial y avisa
    a Discord si el mejor precio bajó vs el snapshot anterior."""
    settings = load_settings()
    webhook = settings.get("discord_webhook", "")
    report = []
    for w in db.get_watchlist():
        res = await run_search(w["query"])
        flat = [l for g in res["groups"] for l in g["listings"]]
        prev_best = db.last_best_total_mxn(w["query"])
        if flat:
            db.save_snapshot(w["query"], flat)
            best = min(flat, key=lambda l: l["total_mxn"])
            dropped = prev_best is not None and best["total_mxn"] < prev_best - 1
            if dropped and webhook:
                discord(webhook,
                        f"🔻 **Bajó de precio:** {best['title']}\n"
                        f"{best['store_name']}: {best['currency']} {best['total']:,.2f} "
                        f"(antes mejor: MXN {prev_best:,.2f})\n{best['url']}")
            report.append({"query": w["query"], "best": best,
                           "prev_best_mxn": prev_best, "dropped": dropped})
        else:
            report.append({"query": w["query"], "best": None,
                           "prev_best_mxn": prev_best, "dropped": False})
    return report


@app.get("/api/history")
def api_history(q: str):
    return db.history(q)


# ---------------------------------------------------------------- cupones / tiendas

@app.get("/api/coupons")
def api_coupons():
    return [c.__dict__ for c in load_coupons()]


@app.post("/api/coupons")
def api_coupons_add(payload: dict):
    add_coupon({
        "store": payload["store"], "code": payload["code"],
        "kind": payload.get("kind", "percent"),
        "value": float(payload.get("value", 0)),
        "min_purchase": float(payload.get("min_purchase", 0)),
        "note": payload.get("note", ""), "active": True,
    })
    return [c.__dict__ for c in load_coupons()]


@app.get("/api/stores")
def api_stores():
    return [{"key": s.key, "name": s.name, "type": s.type,
             "country": s.country, "currency": s.currency,
             "shipping": s.shipping} for s in load_stores()]
