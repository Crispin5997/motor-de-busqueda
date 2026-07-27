# ============================================================
# CONFIGURACIÓN DE TIENDAS
# Agregar una tienda nueva = agregar un bloque aquí. Nada más.
#
# type:
#   shopify   -> funciona de inmediato con cualquier tienda Shopify
#   demo      -> datos de ejemplo para probar la interfaz
#   footlocker / dicks / jdsports / on -> adaptadores dedicados
#                (tienen anti-bot; ver README para afinarlos)
#
# shipping: reglas de envío al CP destino (90021 USA / 44240 MX)
#   free_over: envío gratis a partir de este subtotal (null = nunca)
#   flat: costo de envío si no se llega al umbral
# headers: headers/cookies extra para tiendas protegidas (opcional)
# ============================================================

settings:
  demo_mode: true          # true = incluye tiendas demo para ver la app funcionando
  fx_usd_mxn: 18.70        # tipo de cambio manual para comparar US vs MX
  destino_us: "90021"      # Los Ángeles
  destino_mx: "44240"      # Guadalajara
  discord_webhook: ""      # pega aquí tu webhook para alertas de bajadas de precio
  timeout_seconds: 12
  anthropic_api_key: ""    # pega tu key (sk-ant-...) para búsqueda por imagen
  stockx_cookie: ""        # opcional: Cookie de stockx.com desde DevTools si sigue bloqueada

stores:

  # ---------- USA (reales, requieren afinación anti-bot) ----------
  - key: "on"
    name: "On Running"
    type: "on"
    country: us
    currency: USD
    base_url: "https://www.on.com/en-us"
    shipping: { free_over: 0, flat: 0 }     # On: envío estándar gratis en USA
    active: true

  - key: footlocker
    name: "Foot Locker"
    type: footlocker
    country: us
    currency: USD
    base_url: "https://www.footlocker.com"
    shipping: { free_over: 50, flat: 7.99 }  # verificar, cambia con promos
    headers: {}
    active: true

  - key: dicks
    name: "Dick's Sporting Goods"
    type: dicks
    country: us
    currency: USD
    base_url: "https://www.dickssportinggoods.com"
    shipping: { free_over: 49, flat: 7.99 }
    headers: {}
    active: true

  - key: jdsports
    name: "JD Sports US"
    type: jdsports
    country: us
    currency: USD
    base_url: "https://www.jdsports.com"
    shipping: { free_over: 75, flat: 7.99 }
    headers: {}
    active: true

  # ---------- Ejemplo de tienda Shopify (así se agregan) ----------
  # - key: kith
  #   name: "Kith"
  #   type: shopify
  #   country: us
  #   currency: USD
  #   base_url: "https://kith.com"
  #   shipping: { free_over: 250, flat: 15 }
  #   active: true

  # ---------- DEMO (para ver la interfaz; apagar con demo_mode) ----------
  - key: demo_fl
    name: "[DEMO] Foot Locker"
    type: demo
    country: us
    currency: USD
    base_url: "https://demo"
    shipping: { free_over: 50, flat: 7.99 }
    active: true

  - key: demo_dicks
    name: "[DEMO] Dick's"
    type: demo
    country: us
    currency: USD
    base_url: "https://demo"
    shipping: { free_over: 49, flat: 7.99 }
    active: true

  - key: demo_jd
    name: "[DEMO] JD Sports"
    type: demo
    country: us
    currency: USD
    base_url: "https://demo"
    shipping: { free_over: 75, flat: 7.99 }
    active: true

  - key: demo_on
    name: "[DEMO] On.com"
    type: demo
    country: us
    currency: USD
    base_url: "https://demo"
    shipping: { free_over: 0, flat: 0 }
    active: true

  - key: demo_mx
    name: "[DEMO] Tienda MX"
    type: demo
    country: mx
    currency: MXN
    base_url: "https://demo"
    shipping: { free_over: 1500, flat: 149 }
    active: true

