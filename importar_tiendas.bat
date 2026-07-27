<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PARES — buscador privado</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root{
    --paper:#F6F5F1; --card:#FFFFFF; --ink:#17191E; --muted:#767D88;
    --line:#E4E2DA; --cobalt:#1F49C7; --tag:#FFD23F; --save:#157A4A;
    --danger:#B4372B;
  }
  *{box-sizing:border-box; margin:0; padding:0}
  html{font-size:15px}
  body{background:var(--paper); color:var(--ink);
       font-family:'Archivo',system-ui,sans-serif; min-height:100vh}
  .mono{font-family:'IBM Plex Mono',monospace}

  /* ---------- barra superior ---------- */
  header{position:sticky; top:0; z-index:10; background:var(--paper);
         border-bottom:2px solid var(--ink); padding:14px 22px;
         display:flex; align-items:center; gap:16px; flex-wrap:wrap}
  .wordmark{font-weight:900; font-size:1.35rem; letter-spacing:-.03em}
  .wordmark span{color:var(--cobalt)}
  .searchwrap{flex:1; display:flex; gap:8px; min-width:280px; max-width:640px}
  input[type=text], select{font:inherit; padding:10px 12px; border:1.5px solid var(--ink);
         border-radius:6px; background:var(--card); color:var(--ink); width:100%}
  input[type=text]:focus, select:focus, button:focus-visible{outline:2.5px solid var(--cobalt); outline-offset:1px}
  select{width:auto}
  button{font:inherit; font-weight:700; padding:10px 16px; border:1.5px solid var(--ink);
         border-radius:6px; background:var(--ink); color:#fff; cursor:pointer}
  button.ghost{background:var(--card); color:var(--ink)}
  button:hover{transform:translateY(-1px)}
  @media (prefers-reduced-motion: reduce){ button:hover{transform:none} }

  nav{display:flex; gap:4px; padding:10px 22px 0}
  nav button{border:none; background:none; color:var(--muted); font-weight:700;
             padding:8px 12px; border-bottom:3px solid transparent; border-radius:0}
  nav button.on{color:var(--ink); border-bottom-color:var(--cobalt)}

  main{max-width:1060px; margin:0 auto; padding:20px 22px 80px}

  /* ---------- estado de tiendas ---------- */
  .chips{display:flex; gap:8px; flex-wrap:wrap; margin:14px 0}
  .chip{font-size:.78rem; font-weight:700; padding:5px 10px; border-radius:999px;
        border:1.5px solid var(--line); background:var(--card); color:var(--muted)}
  .chip.ok{border-color:var(--save); color:var(--save)}
  .chip.blocked{border-color:var(--danger); color:var(--danger); cursor:pointer}
  #chipdetail{font-family:'IBM Plex Mono',monospace; font-size:.75rem; color:var(--danger);
              margin:-6px 0 12px; word-break:break-all; min-height:0}
  .thumb{width:54px; height:54px; object-fit:cover; border:1.5px solid var(--line);
         border-radius:8px; background:#fff; flex:none}
  .headleft{display:flex; align-items:center; gap:12px}

  /* ---------- referencia de mercado ---------- */
  .marketbar{display:flex; gap:14px; flex-wrap:wrap; margin:6px 0 18px}
  .marketcard{background:var(--card); border:1.5px solid var(--line); border-radius:8px;
              padding:10px 14px; min-width:220px; flex:1}
  .marketcard h4{font-size:.72rem; text-transform:uppercase; letter-spacing:.08em; color:var(--muted)}
  .marketcard .val{font-size:1.05rem; font-weight:600; margin-top:2px}
  .marketcard small{color:var(--muted)}

  /* ---------- grupos de producto ---------- */
  .group{background:var(--card); border:1.5px solid var(--ink); border-radius:10px;
         margin-bottom:18px; overflow:hidden}
  .group>.head{display:flex; justify-content:space-between; align-items:baseline;
               gap:12px; padding:14px 18px; border-bottom:1.5px solid var(--line); flex-wrap:wrap}
  .group h3{font-size:1.1rem; font-weight:900; letter-spacing:-.02em}
  .sku{font-size:.8rem; color:var(--muted)}
  table{width:100%; border-collapse:collapse}
  td,th{padding:11px 18px; text-align:left; font-size:.92rem}
  th{font-size:.72rem; text-transform:uppercase; letter-spacing:.08em; color:var(--muted);
     border-bottom:1px solid var(--line); font-weight:700}
  tr+tr td{border-top:1px solid var(--line)}
  td.num{text-align:right; font-family:'IBM Plex Mono',monospace}
  .total{font-weight:600}
  tr.best{background:#FFF7DC}
  .tagbest{display:inline-block; background:var(--tag); color:var(--ink); font-weight:900;
           font-size:.68rem; letter-spacing:.06em; padding:3px 9px 3px 12px; margin-left:8px;
           clip-path:polygon(8px 0,100% 0,100% 100%,8px 100%,0 50%)}
  .pill{display:inline-block; font-size:.7rem; font-weight:700; padding:2px 8px;
        border-radius:999px; margin-left:6px}
  .pill.coupon{background:#EAF0FF; color:var(--cobalt)}
  .pill.sale{background:#EAF6EF; color:var(--save)}
  a{color:var(--cobalt); font-weight:700; text-decoration:none}
  a:hover{text-decoration:underline}
  .strike{color:var(--muted); text-decoration:line-through; font-size:.8rem; margin-right:6px}

  /* ---------- listas (watchlist, cupones, tiendas) ---------- */
  .card{background:var(--card); border:1.5px solid var(--line); border-radius:10px;
        padding:16px 18px; margin-bottom:14px}
  .row{display:flex; justify-content:space-between; align-items:center; gap:10px;
       padding:9px 0; border-bottom:1px solid var(--line); flex-wrap:wrap}
  .row:last-child{border-bottom:none}
  .formline{display:flex; gap:8px; flex-wrap:wrap; margin-top:12px}
  .formline input{max-width:180px}

  .empty{color:var(--muted); padding:30px 0; text-align:center}
  .loading{color:var(--muted); padding:20px 0}
  h2.section{font-size:.8rem; text-transform:uppercase; letter-spacing:.1em;
             color:var(--muted); margin:22px 0 10px}
</style>
</head>
<body>

<header>
  <div class="wordmark">PARES<span>.</span></div>
  <div class="searchwrap">
    <input type="text" id="q" placeholder="Nombre o SKU — ej. cloudmonster, U9060ECA…" autofocus>
    <select id="country" aria-label="País">
      <option value="all">US + MX</option>
      <option value="us">Solo USA</option>
      <option value="mx">Solo México</option>
    </select>
    <button onclick="doSearch()">Buscar</button>
    <button class="ghost" onclick="document.getElementById('img').click()" title="Buscar por imagen">📷</button>
    <input type="file" id="img" accept="image/*" hidden onchange="identify(this)">
  </div>
</header>

<nav>
  <button class="on" data-tab="buscar" onclick="tab('buscar')">Buscar</button>
  <button data-tab="watchlist" onclick="tab('watchlist')">Watchlist</button>
  <button data-tab="cupones" onclick="tab('cupones')">Cupones</button>
  <button data-tab="tiendas" onclick="tab('tiendas')">Tiendas</button>
</nav>

<main>
  <section id="tab-buscar">
    <div id="results">
      <p class="empty">Busca un modelo por nombre, SKU o foto.<br>
      Se consultan todas las tiendas activas, se aplican cupones y envío
      (90021 US · 44240 MX) y se compara contra StockX y GOAT.</p>
    </div>
  </section>

  <section id="tab-watchlist" hidden>
    <div class="card">
      <div class="row" style="border:none">
        <strong>Modelos en seguimiento</strong>
        <button onclick="refreshWatch(this)">Actualizar precios ahora</button>
      </div>
      <div id="watchrows"></div>
      <div class="formline">
        <input type="text" id="wq" placeholder="Agregar modelo…" style="max-width:280px">
        <button class="ghost" onclick="addWatch()">Agregar</button>
      </div>
    </div>
    <div id="watchreport"></div>
  </section>

  <section id="tab-cupones" hidden>
    <div class="card">
      <strong>Cupones activos</strong>
      <div id="couponrows"></div>
      <div class="formline">
        <select id="cstore"></select>
        <input type="text" id="ccode" placeholder="Código">
        <select id="ckind"><option value="percent">% off</option><option value="fixed">$ off</option></select>
        <input type="text" id="cvalue" placeholder="Valor" style="max-width:90px">
        <input type="text" id="cmin" placeholder="Mínimo" style="max-width:90px">
        <button class="ghost" onclick="addCoupon()">Guardar cupón</button>
      </div>
    </div>
  </section>

  <section id="tab-tiendas" hidden>
    <div class="card"><div id="storerows"></div></div>
    <p class="empty">Para agregar tiendas edita <span class="mono">config/stores.yaml</span> —
    una tienda Shopify funciona con solo pegar su URL.</p>
  </section>
</main>

<script>
const $ = s => document.querySelector(s);
const fmt = (n, cur) => (cur==='MXN'?'MX$':'US$') + Number(n).toLocaleString('en-US',{minimumFractionDigits:2, maximumFractionDigits:2});

function tab(name){
  document.querySelectorAll('nav button').forEach(b=>b.classList.toggle('on', b.dataset.tab===name));
  ['buscar','watchlist','cupones','tiendas'].forEach(t=>$('#tab-'+t).hidden = t!==name);
  if(name==='watchlist') loadWatch();
  if(name==='cupones') loadCoupons();
  if(name==='tiendas') loadStores();
}

$('#q').addEventListener('keydown', e=>{ if(e.key==='Enter') doSearch(); });

async function doSearch(q){
  q = q || $('#q').value.trim();
  if(!q) return;
  $('#q').value = q;
  tab('buscar');
  $('#results').innerHTML = '<p class="loading">Consultando tiendas…</p>';
  try{
    const r = await fetch(`/api/search?q=${encodeURIComponent(q)}&country=${$('#country').value}`);
    render(await r.json());
  }catch(e){
    $('#results').innerHTML = '<p class="empty">El servidor no respondió. Revisa que la app siga corriendo.</p>';
  }
}

function chipDetail(name, det){
  const el = document.getElementById('chipdetail');
  if(el) el.textContent = det ? name + ' → ' + det : '';
}

function render(data){
  let h = '';

  // estado por tienda
  h += '<div class="chips">' + Object.values(data.stores).map(s=>{
    const cls = s.status==='ok' ? (s.count>0?'ok':'') : 'blocked';
    const label = s.status==='ok' ? `${s.count} resultado${s.count===1?'':'s'}` : s.status;
    const det = (s.detail||'').replace(/"/g,'&quot;');
    return `<span class="chip ${cls}" title="${det}" onclick="chipDetail('${s.name}', this.title)">${s.name} · ${label}</span>`;
  }).join('') + '</div><div id="chipdetail"></div>';

  // referencia de mercado
  const mk = (name, m) => {
    const it = (m.items||[])[0];
    const val = it && it.lowest_ask ? fmt(it.lowest_ask,'USD') : (m.status==='ok'?'—':'sin datos ('+m.status+')');
    const sub = it ? it.title : '';
    return `<div class="marketcard"><h4>${name} · referencia reventa</h4>
            <div class="val mono">${val}</div><small>${sub}</small></div>`;
  };
  h += `<div class="marketbar">${mk('StockX', data.market.stockx)}${mk('GOAT', data.market.goat)}</div>`;

  if(!data.groups.length){
    h += '<p class="empty">Ninguna tienda regresó resultados para esta búsqueda.<br>Prueba con menos palabras o revisa las tiendas bloqueadas arriba.</p>';
    $('#results').innerHTML = h; return;
  }

  for(const g of data.groups){
    const img = g.image ? `<img class="thumb" src="${g.image}" loading="lazy" alt="" onerror="this.remove()">` : '';
    h += `<div class="group"><div class="head">
            <div class="headleft">${img}<h3>${g.title}</h3></div>
            <span class="sku mono">${g.sku ? 'SKU ' + g.sku : 'agrupado por nombre'}</span>
          </div>
          <table><thead><tr>
            <th>Tienda</th><th style="text-align:right">Precio</th>
            <th style="text-align:right">Cupón</th><th style="text-align:right">Envío</th>
            <th style="text-align:right">Total</th><th style="text-align:right">≈ MXN</th><th></th>
          </tr></thead><tbody>`;
    g.listings.forEach((l,i)=>{
      h += `<tr class="${i===0?'best':''}">
        <td>${l.store_name}${i===0?'<span class="tagbest">MEJOR PRECIO</span>':''}
            ${l.on_sale?'<span class="pill sale">rebaja</span>':''}</td>
        <td class="num">${l.list_price?`<span class="strike">${fmt(l.list_price,l.currency)}</span>`:''}${fmt(l.price,l.currency)}</td>
        <td class="num">${l.coupon_code?`−${fmt(l.discount,l.currency)}<span class="pill coupon">${l.coupon_code}</span>`:'—'}</td>
        <td class="num">${l.shipping?fmt(l.shipping,l.currency):'gratis'}</td>
        <td class="num total">${fmt(l.total,l.currency)}</td>
        <td class="num">${fmt(l.total_mxn,'MXN')}</td>
        <td><a href="${l.url}" target="_blank" rel="noopener">ver →</a></td></tr>`;
    });
    h += '</tbody></table></div>';
  }
  $('#results').innerHTML = h;
}

// ---------- imagen ----------
async function identify(input){
  if(!input.files.length) return;
  $('#results').innerHTML = '<p class="loading">Identificando el par en la foto…</p>';
  tab('buscar');
  const fd = new FormData(); fd.append('image', input.files[0]);
  const r = await fetch('/api/identify', {method:'POST', body:fd});
  const d = await r.json();
  input.value = '';
  if(d.error){ $('#results').innerHTML = `<p class="empty">${d.error}</p>`; return; }
  const q = d.style_code_guess || d.query || `${d.brand} ${d.model}`;
  doSearch(q);
}

// ---------- watchlist ----------
async function loadWatch(){
  const rows = await (await fetch('/api/watchlist')).json();
  $('#watchrows').innerHTML = rows.map(w =>
    `<div class="row"><span><a href="#" onclick="doSearch('${w.query}');return false">${w.query}</a>
     <small style="color:var(--muted)"> ${w.note||''}</small></span>
     <button class="ghost" onclick="delWatch(${w.id})">Quitar</button></div>`).join('')
    || '<p class="empty">Sin modelos en seguimiento. Agrega uno abajo.</p>';
}
async function addWatch(){
  const q = $('#wq').value.trim(); if(!q) return;
  await fetch('/api/watchlist',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query:q})});
  $('#wq').value=''; loadWatch();
}
async function delWatch(id){ await fetch('/api/watchlist/'+id,{method:'DELETE'}); loadWatch(); }

async function refreshWatch(btn){
  btn.disabled = true; btn.textContent = 'Actualizando…';
  try{
    const rep = await (await fetch('/api/refresh',{method:'POST'})).json();
    $('#watchreport').innerHTML = rep.map(r=>{
      if(!r.best) return `<div class="card"><strong>${r.query}</strong><p class="empty">Sin resultados en esta corrida.</p></div>`;
      const b = r.best;
      return `<div class="card"><div class="row" style="border:none">
        <span><strong>${r.query}</strong> — mejor: ${b.store_name}
        ${r.dropped?'<span class="pill sale">bajó 🔻</span>':''}</span>
        <span class="mono total">${fmt(b.total,b.currency)} (≈ ${fmt(b.total_mxn,'MXN')})</span>
      </div></div>`;
    }).join('');
  } finally { btn.disabled=false; btn.textContent='Actualizar precios ahora'; }
}

// ---------- cupones ----------
async function loadCoupons(){
  const [coupons, stores] = await Promise.all([
    (await fetch('/api/coupons')).json(), (await fetch('/api/stores')).json()]);
  $('#couponrows').innerHTML = coupons.map(c =>
    `<div class="row"><span><span class="mono" style="font-weight:600">${c.code}</span>
      · ${c.store} · ${c.kind==='percent'?c.value+'%':'$'+c.value} off
      ${c.min_purchase?`(mín $${c.min_purchase})`:''} <small style="color:var(--muted)">${c.note||''}</small></span></div>`).join('')
    || '<p class="empty">Sin cupones. Cuando encuentres uno, guárdalo abajo y se aplicará solo.</p>';
  $('#cstore').innerHTML = stores.map(s=>`<option value="${s.key}">${s.name}</option>`).join('');
}
async function addCoupon(){
  const body = { store:$('#cstore').value, code:$('#ccode').value.trim(),
    kind:$('#ckind').value, value:parseFloat($('#cvalue').value||0),
    min_purchase:parseFloat($('#cmin').value||0) };
  if(!body.code || !body.value) return;
  await fetch('/api/coupons',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  $('#ccode').value=''; $('#cvalue').value=''; $('#cmin').value='';
  loadCoupons();
}

// ---------- tiendas ----------
async function loadStores(){
  const stores = await (await fetch('/api/stores')).json();
  $('#storerows').innerHTML = stores.map(s=>{
    const ship = s.shipping.free_over!=null
      ? `gratis desde $${s.shipping.free_over}, si no $${s.shipping.flat||0}`
      : `$${s.shipping.flat||0}`;
    return `<div class="row"><span><strong>${s.name}</strong>
      <small style="color:var(--muted)"> ${s.country.toUpperCase()} · ${s.currency} · tipo ${s.type}</small></span>
      <span class="mono" style="font-size:.8rem">envío: ${ship}</span></div>`;
  }).join('');
}
</script>
</body>
</html>
