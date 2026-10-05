import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import date, datetime, timedelta

st.set_page_config(
    page_title="MSH-Hub | Kardex",
    layout="wide",
    page_icon="📇",
    initial_sidebar_state="collapsed"
)

if not st.session_state.get("autenticado"):
    st.switch_page("app.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }
[data-testid="stAppViewContainer"] { background: #F0F4F8; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainMenu"]              { display: none !important; }
[data-testid="stSidebar"]              { display: none !important; }
[data-testid="stSidebarCollapseButton"]{ display: none !important; }
[data-testid="collapsedControl"]       { display: none !important; }
.msh-header {
    background: #1E3447; border-radius: 12px; padding: 14px 20px;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 16px; box-shadow: 0 4px 20px rgba(30,52,71,0.25);
}
.msh-header-left { display: flex; align-items: center; gap: 12px; }
.msh-logo-box {
    width: 38px; height: 38px; background: rgba(255,255,255,0.12);
    border-radius: 10px; display: flex; align-items: center; justify-content: center;
    font-size: 18px;
}
.msh-title { font-size: 16px; font-weight: 600; color: #FFFFFF; line-height: 1.2; letter-spacing: -0.2px; }
.msh-subtitle { font-size: 11px; color: rgba(255,255,255,0.5); font-weight: 400; }
.msh-user-pill {
    display: flex; align-items: center; gap: 10px;
    background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.15);
    border-radius: 99px; padding: 6px 14px 6px 8px;
}
.msh-avatar {
    width: 28px; height: 28px; border-radius: 50%;
    background: linear-gradient(135deg, #4A90D9, #2D6FA8);
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700; color: #fff; flex-shrink: 0;
}
.msh-uname { font-size: 12px; font-weight: 600; color: #fff; }
.msh-urole { font-size: 10px; color: rgba(255,255,255,0.55); text-transform: uppercase; letter-spacing: 0.4px; }
.kpi-bar {
    background: #F4F8FC; border: 1px solid #DCE7F3; border-radius: 12px;
    padding: 14px 22px; display: flex; align-items: center; gap: 10px;
    margin-bottom: 14px; box-shadow: 0 1px 4px rgba(30,52,71,0.06); flex-wrap: wrap;
}
.kpi-pill { display: flex; align-items: center; gap: 9px; padding: 5px 16px; border-radius: 99px; }
.kpi-icon { font-size: 19px; }
.kpi-val  { font-size: 16px; font-weight: 700; line-height: 1; }
.kpi-lbl  { font-size: 11px; color: #64748B; font-weight: 500; }
.kpi-sep  { width: 1px; height: 26px; background: #CBD9E8; margin: 0 6px; flex-shrink: 0; }
.th {
    font-size: 10px !important; font-weight: 700 !important; color: #FFFFFF !important;
    text-transform: uppercase; letter-spacing: 0.5px; padding: 13px 6px !important;
    margin: 0 !important; background: #1E3447;
    line-height: 1 !important; box-sizing: border-box !important;
    white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important;
}
.th:first-child { border-radius: 10px 0 0 0; }
.th:last-child { border-radius: 0 10px 0 0; }
div[data-testid="stHorizontalBlock"]:has(.th) { gap: 0 !important; }
div[data-testid="stHorizontalBlock"]:has(.th) > div[data-testid="stColumn"] { padding: 0 !important; }
.td {
    font-size: 12px !important; color: #1E293B !important; padding: 9px 6px !important;
    border-bottom: 1px solid #F1F5F9; margin: 0 !important;
    overflow: hidden; white-space: nowrap; text-overflow: ellipsis; background: transparent;
}
.td-alt {
    font-size: 12px !important; color: #1E293B !important; padding: 9px 6px !important;
    border-bottom: 1px solid #F1F5F9; margin: 0 !important;
    overflow: hidden; white-space: nowrap; text-overflow: ellipsis; background: #FAFBFC;
}
.badge {
    display: inline-flex; align-items: center; gap: 4px; padding: 3px 9px;
    border-radius: 99px; font-size: 10px; font-weight: 600; white-space: nowrap;
}
.badge-entrada    { background:#DCFCE7; color:#15803D; }
.badge-salida     { background:#FEE2E2; color:#B91C1C; }
.badge-prestamo   { background:#EFF6FF; color:#1D4ED8; }
.badge-devolucion { background:#F3E8FF; color:#7E22CE; }
.badge-custodia   { background:#FEF3E8; color:#C2410C; }
.folio-tag {
    font-family: 'DM Mono', monospace; font-size: 10px; color: #94A3B8;
    background: #F1F5F9; border-radius: 4px; padding: 1px 5px; display: inline-block;
}
.cantidad-pos { color: #15803D; font-weight: 700; }
.cantidad-neg { color: #B91C1C; font-weight: 700; }
.panel-card-titulo { font-size: 15px; font-weight: 700; color: #1E293B; margin-bottom: 2px; }
.panel-card-subtitulo { font-size: 12px; color: #94A3B8; margin-bottom: 16px; }
.producto-card {
    background: #ffffff; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 20px 24px; margin-bottom: 18px; box-shadow: 0 2px 10px rgba(30,52,71,0.06);
}
div[class*="st-key-panel_filtros"],
div[class*="st-key-panel_tabla"] {
    background: #ffffff; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 22px 24px; margin-bottom: 18px;
    box-shadow: 0 2px 10px rgba(30,52,71,0.06);
}
[data-testid="stButton"] button {
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 12px !important;
}
[data-testid="stButton"] button[kind="primary"] {
    background: #1E3447 !important; border: none !important;
    box-shadow: 0 2px 8px rgba(30,52,71,0.25) !important;
}
</style>
""", unsafe_allow_html=True)

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://unsugrcleytqroxuuhaf.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

TIPO_LABELS = {
    "entrada": "📥 Entrada", "salida": "📤 Salida", "prestamo": "🤝 Préstamo",
    "devolucion": "↩️ Devolución", "custodia": "🔒 Custodia",
}


def buscar_productos(query):
    try:
        q = supabase.table("almacen_productos").select("id, codigo, nombre, tipo_producto").eq("activo", True)
        if query.strip():
            q = q.or_(f"codigo.ilike.%{query}%,nombre.ilike.%{query}%")
        res = q.order("nombre").limit(10).execute()
        return res.data or []
    except Exception as e:
        st.error(f"Error al buscar productos: {e}")
        return []


def obtener_saldo_producto(producto):
    """Para insumo: cantidad en Existencias. Para activo: disponibles/total."""
    try:
        if producto["tipo_producto"] == "insumo":
            res = supabase.table("almacen_existencias").select("cantidad").eq("producto_id", producto["id"]).execute().data
            return {"tipo": "insumo", "cantidad": res[0]["cantidad"] if res else 0}
        else:
            total = supabase.table("almacen_activos").select("id", count="exact").eq("producto_id", producto["id"]).eq("activo", True).range(0, 0).execute().count or 0
            disponibles = supabase.table("almacen_activos").select("id", count="exact").eq("producto_id", producto["id"]).eq("estado", "disponible").eq("activo", True).range(0, 0).execute().count or 0
            return {"tipo": "activo", "total": total, "disponibles": disponibles}
    except Exception as e:
        st.error(f"Error al calcular saldo: {e}")
        return {}


def cargar_kardex(producto_id, pagina=0, tam_pagina=50, filtro_tipo="Todos", desde=None, hasta=None):
    try:
        q = supabase.table("almacen_kardex_resumen").select("*", count="exact").eq("producto_id", producto_id)
        if filtro_tipo != "Todos":
            q = q.eq("tipo_movimiento", filtro_tipo)
        if desde:
            q = q.gte("fecha", desde)
        if hasta:
            q = q.lte("fecha", hasta)
        inicio = pagina * tam_pagina
        fin = inicio + tam_pagina - 1
        res = q.order("fecha", desc=True).order("created_at", desc=True).range(inicio, fin).execute()
        return res.data or [], (res.count or 0)
    except Exception as e:
        st.error(f"Error al cargar el kardex: {e}")
        return [], 0


def filtro_rango_fechas_kardex():
    opciones = ["Todo", "Últimos 30 días", "Este mes", "Este año", "Personalizado"]
    seleccion = st.selectbox("rango", opciones, label_visibility="collapsed", key="kardex_rango")
    hoy = date.today()
    if seleccion == "Todo":
        return None, None
    elif seleccion == "Últimos 30 días":
        return str(hoy - timedelta(days=29)), str(hoy)
    elif seleccion == "Este mes":
        return str(hoy.replace(day=1)), str(hoy)
    elif seleccion == "Este año":
        return str(hoy.replace(month=1, day=1)), str(hoy)
    else:
        c1, c2 = st.columns(2)
        with c1:
            desde = st.date_input("Desde", value=hoy - timedelta(days=30), key="kardex_desde")
        with c2:
            hasta = st.date_input("Hasta", value=hoy, key="kardex_hasta")
        return str(desde), str(hasta)


nombre_actual  = st.session_state.get("nombre", "")
rol_actual     = st.session_state.get("rol", "")
usuario_actual = st.session_state.get("usuario", "")
iniciales      = "".join([p[0].upper() for p in nombre_actual.split()[:2]]) if nombre_actual else "AD"

st.markdown(f"""
    <div class="msh-header">
        <div class="msh-header-left">
            <div class="msh-logo-box">📇</div>
            <div>
                <div class="msh-title">MSH-Hub · Almacén · Kardex</div>
                <div class="msh-subtitle">Mendoza Servicios y Herramientas</div>
            </div>
        </div>
        <div class="msh-user-pill">
            <div class="msh-avatar">{iniciales}</div>
            <div>
                <div class="msh-uname">{nombre_actual}</div>
                <div class="msh-urole">{rol_actual}</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

col_reg, _, col_sal = st.columns([2, 9, 1])
with col_reg:
    if st.button("← Regresar al menú", width="stretch"):
        st.switch_page("pages/1_Inicio.py")
with col_sal:
    if st.button("🚪 Salir", width="stretch"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.switch_page("app.py")

# ══════════════════════════════════════════════
# SELECCIÓN OBLIGATORIA DE PRODUCTO
# ══════════════════════════════════════════════
st.markdown('<div class="panel-card-titulo">🔍 Selecciona un producto para ver su historial</div>', unsafe_allow_html=True)
st.caption("El Kardex requiere elegir un producto — con miles de movimientos acumulados, mostrar todo el historial sin filtrar sería demasiado pesado.")

query = st.text_input("buscar_producto", placeholder="🔍  Buscar por código o nombre de producto...", label_visibility="collapsed", key="kardex_busqueda_producto")

if "kardex_producto" not in st.session_state:
    st.session_state["kardex_producto"] = None

if query.strip():
    resultados = buscar_productos(query)
    for p in resultados:
        c1, c2 = st.columns([4, 1])
        icono = "🛠️" if p["tipo_producto"] == "activo" else "📦"
        c1.markdown(f"{icono} **{p['codigo']}** — {p['nombre']}")
        with c2:
            if st.button("Seleccionar", key=f"kar_sel_{p['id']}", width="stretch"):
                st.session_state["kardex_producto"] = p
                st.session_state["kardex_pagina"] = 0
                st.rerun()

producto = st.session_state["kardex_producto"]

if not producto:
    st.info("👆 Busca y selecciona un producto para ver su Kardex.")
    st.stop()

# ══════════════════════════════════════════════
# TARJETA DEL PRODUCTO + SALDO ACTUAL
# ══════════════════════════════════════════════
saldo = obtener_saldo_producto(producto)

with st.container(key="producto_card"):
    st.markdown('<div class="producto-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([3, 2, 1])
    with c1:
        icono = "🛠️" if producto["tipo_producto"] == "activo" else "📦"
        st.markdown(f"### {icono} {producto['codigo']} — {producto['nombre']}")
    with c2:
        if saldo.get("tipo") == "insumo":
            st.markdown(f"**Existencia actual:** {saldo.get('cantidad', 0):g} unidades")
        else:
            st.markdown(f"**Activos:** {saldo.get('disponibles', 0)} disponibles de {saldo.get('total', 0)} totales")
    with c3:
        if st.button("🔄 Cambiar producto", width="stretch"):
            st.session_state["kardex_producto"] = None
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# FILTROS DEL HISTORIAL
# ══════════════════════════════════════════════
if "kardex_pagina" not in st.session_state:
    st.session_state["kardex_pagina"] = 0
TAM_PAGINA = 50

panel_filtros = st.container(key="panel_filtros")
with panel_filtros:
    c1, c2 = st.columns([2.5, 2.5])
    with c1:
        filtro_tipo = st.selectbox("tipo_mov", ["Todos"] + list(TIPO_LABELS.keys()),
                                     format_func=lambda v: "Todos" if v == "Todos" else TIPO_LABELS[v],
                                     label_visibility="collapsed")
    with c2:
        desde, hasta = filtro_rango_fechas_kardex()

filtro_actual = (producto["id"], filtro_tipo, desde, hasta)
if st.session_state.get("kardex_filtro_anterior") != filtro_actual:
    st.session_state["kardex_pagina"] = 0
    st.session_state["kardex_filtro_anterior"] = filtro_actual

datos, total_filtrado = cargar_kardex(
    producto["id"], pagina=st.session_state["kardex_pagina"], tam_pagina=TAM_PAGINA,
    filtro_tipo=filtro_tipo, desde=desde, hasta=hasta
)
df_f = pd.DataFrame(datos)

if not df_f.empty:
    cw, ths = [1.2, 1.5, 1.4, 1.6, 1, 2], ["Fecha", "Tipo", "Referencia", "Activo", "Cantidad", "Registrado por"]
    panel_tabla = st.container(key="panel_tabla")
    with panel_tabla:
        st.markdown('<div class="panel-card-titulo">📋 Historial de movimientos</div>', unsafe_allow_html=True)
        h_cols = st.columns(cw)
        for idx, (col, txt) in enumerate(zip(h_cols, ths)):
            col.markdown(f"<p class='th'>{txt}</p>", unsafe_allow_html=True)
        for i, (_, row) in enumerate(df_f.iterrows()):
            cls = "td-alt" if i % 2 == 1 else "td"
            r = st.columns(cw)
            r[0].markdown(f"<div class='{cls}'>{row['fecha']}</div>", unsafe_allow_html=True)
            r[1].markdown(f"<div class='{cls}'><span class='badge badge-{row['tipo_movimiento']}'>{TIPO_LABELS.get(row['tipo_movimiento'], row['tipo_movimiento'])}</span></div>", unsafe_allow_html=True)
            r[2].markdown(f"<div class='{cls}'><span class='folio-tag'>{row['referencia']}</span></div>", unsafe_allow_html=True)
            r[3].markdown(f"<div class='{cls}'>{row.get('codigo_activo') or '—'}</div>", unsafe_allow_html=True)
            cant = row["cantidad"]
            cant_cls = "cantidad-pos" if cant > 0 else "cantidad-neg"
            cant_txt = f"+{cant:g}" if cant > 0 else f"{cant:g}"
            r[4].markdown(f"<div class='{cls}'><span class='{cant_cls}'>{cant_txt}</span></div>", unsafe_allow_html=True)
            r[5].markdown(f"<div class='{cls}'>{row.get('nombre_registro') or row.get('usuario_registro') or '—'}</div>", unsafe_allow_html=True)

        total_paginas = max(1, -(-total_filtrado // TAM_PAGINA))
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if st.button("← Anterior", disabled=st.session_state["kardex_pagina"] <= 0, key="kar_pag_ant"):
                st.session_state["kardex_pagina"] -= 1
                st.rerun()
        with c2:
            st.markdown(f"<p style='text-align:center; font-size:12px; color:#64748B; margin-top:8px;'>Página {st.session_state['kardex_pagina'] + 1} de {total_paginas} · {total_filtrado} movimientos</p>", unsafe_allow_html=True)
        with c3:
            if st.button("Siguiente →", disabled=st.session_state["kardex_pagina"] >= total_paginas - 1, key="kar_pag_sig"):
                st.session_state["kardex_pagina"] += 1
                st.rerun()
else:
    st.info("📭 Este producto no tiene movimientos registrados con los filtros aplicados.")
