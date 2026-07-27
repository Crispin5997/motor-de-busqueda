# PARES — Buscador privado de precios

Busca un modelo (nombre, SKU o foto) en todas tus tiendas de US y MX,
aplica cupones y envío (90021 Los Ángeles / 44240 GDL), agrupa el mismo
par aunque cada tienda lo nombre distinto, y compara contra StockX/GOAT.

## Arrancar

```
pip install -r requirements.txt
python -m uvicorn app:app --port 8712
```
Abrir: http://localhost:8712

En Windows: doble clic a `instalar.bat` (una vez) y luego `iniciar_buscador.bat`.

Arranca en **modo demo** (tiendas [DEMO] con datos de ejemplo) para que veas
la interfaz funcionando. Cuando las tiendas reales estén afinadas, pon
`demo_mode: false` en `config/stores.yaml`.

## Importar tus tiendas de Chrome en masa

1. Chrome → `chrome://bookmarks` → menú ⋮ → **Exportar marcadores**
2. Arrastra ese archivo .html encima de **`importar_tiendas.bat`**

El importador prueba cada dominio: las tiendas Shopify se agregan solas a
`stores.yaml` listas para usar (país/moneda detectados por el dominio); las
que no son Shopify quedan en `config/tiendas_pendientes.yaml` — pásale esa
lista a Claude para hacerles adaptador dedicado. No toca lo que ya tienes.
Después revisa las reglas de envío de cada tienda nueva (quedan con un
default marcado con AJUSTAR).

## Cómo se agregan tiendas a mano (lo escalable)

Todo vive en `config/stores.yaml`. Una tienda **Shopify** (la mayoría de
boutiques de sneakers en MX y muchas en US) funciona de inmediato:

```yaml
- key: mitienda
  name: "Mi Tienda MX"
  type: shopify
  country: mx
  currency: MXN
  base_url: "https://mitienda.mx"
  shipping: { free_over: 1500, flat: 149 }
  active: true
```

¿Cómo saber si es Shopify? Abre `latienda.com/products.json` — si regresa
JSON, es Shopify.

## Tiendas grandes (Foot Locker, Dick's, JD, On) — cómo pasamos sin navegador

El enfoque es petición directa, tienda por tienda, **como usuario y sin
navegador**. Para eso las tiendas protegidas usan `curl_cffi`, que imita la
huella TLS de un Chrome real: a nivel de red la petición es indistinguible
de un usuario, pero tarda milisegundos. (Es la lección del monitor de
boletos v4: Akamai/Cloudflare no solo miran headers, miran la huella TLS.)

Escalera de soluciones si una tienda marca "bloqueada" en rojo:

1. **Nada que hacer primero**: córrelo desde tu casa. Tu IP residencial +
   huella de Chrome pasa la mayoría de los filtros.
2. **Cookies de tu Chrome**: abre la tienda, F12 → Network, busca un
   producto, copia el header `Cookie` de la petición y pégalo en
   `stores.yaml` → `headers: { Cookie: "..." }`. Sigue sin navegador:
   la cookie se consigue una vez y las búsquedas siguen siendo directas.
3. **Último recurso** (solo si una tienda resiste 1 y 2): un warmup con
   navegador para renovar cookies de vez en cuando. El sistema ya está
   diseñado para enchufarlo sin tocar nada más.

Una tienda bloqueada **no rompe nada**: se marca en rojo y las demás siguen.

## StockX / GOAT

Igual: anti-bot agresivo. GOAT (vía Algolia) es la ruta más estable; StockX
es más caprichoso. Si marcan "bloqueada", el resto de la app funciona normal.

## Cupones

`config/coupons.yaml` o pestaña Cupones de la app. El buscador aplica solo
el mejor cupón válido por tienda al calcular el precio final. Los dos que
vienen son EJEMPLOS — reemplázalos con reales.

## Envío

Reglas por tienda en `stores.yaml` (`free_over` / `flat`). Cotizar en vivo
por CP requiere automatizar el checkout de cada tienda (frágil y bloqueable);
las reglas cubren casi todos los casos y se editan en segundos. Verifica los
umbrales de cada tienda, cambian con promos.

## Búsqueda por imagen

Pega tu API key de Anthropic en `config/stores.yaml` → `anthropic_api_key`
y reinicia el buscador. La foto se manda a Claude (con tu key, cuesta
centavos por foto), identifica marca/modelo/SKU probable y lanza la búsqueda.

**¿Las búsquedas normales gastan tokens?** No. Buscar por nombre o SKU son
peticiones HTTP directas desde tu PC a las tiendas: cero tokens, cero costo.
Solo la identificación por FOTO usa tu API key.

## Watchlist + alertas a Discord

Los 4 modelos constantes ya vienen precargados (Cloudmonster, Birkenstock
Boston, Veja Campo, NB 9060). El botón "Actualizar precios ahora" corre todo,
guarda historial en `data.db` y si el mejor precio bajó vs la corrida
anterior, avisa a Discord (pega tu webhook en `stores.yaml` →
`discord_webhook`). Para que corra solo cada X horas, agenda esto en el
Programador de tareas de Windows:

```
curl -X POST http://localhost:8712/api/refresh
```

## Ajustes finos

- `fx_usd_mxn` en `stores.yaml`: tipo de cambio para comparar US vs MX.
- `FUZZY_THRESHOLD` en `core/matching.py`: qué tan agresivo agrupa por nombre
  cuando no hay SKU (87 por defecto).

## Estructura

```
app.py               servidor + API
static/index.html    interfaz
config/stores.yaml   tiendas, envío, settings  ← aquí se escala
config/coupons.yaml  cupones
core/                matching (SKU + difuso), precios, historial, Discord
stores/              un adaptador por tipo de tienda (shopify = genérico)
market/              referencia StockX / GOAT
data.db              watchlist + historial de precios (SQLite)
```
