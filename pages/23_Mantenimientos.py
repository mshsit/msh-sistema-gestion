import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import date, datetime

st.set_page_config(
    page_title="MSH-Hub | Mantenimientos",
    layout="wide",
    page_icon="🛠️",
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
.badge-tipo        { background:#EFF6FF; color:#1D4ED8; }
.badge-vencido     { background:#FEE2E2; color:#B91C1C; }
.badge-critico     { background:#FEF3E8; color:#C2410C; }
.badge-proximo     { background:#FEF9C3; color:#854D0E; }
.badge-normal       { background:#DCFCE7; color:#15803D; }
.folio-tag {
    font-family: 'DM Mono', monospace; font-size: 10px; color: #94A3B8;
    background: #F1F5F9; border-radius: 4px; padding: 1px 5px; display: inline-block;
}
.panel-card-titulo { font-size: 15px; font-weight: 700; color: #1E293B; margin-bottom: 2px; }
.panel-card-subtitulo { font-size: 12px; color: #94A3B8; margin-bottom: 16px; }
div[class*="st-key-panel_filtros"],
div[class*="st-key-panel_tabla"],
div[class*="st-key-panel_alertas"] {
    background: #ffffff; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 22px 24px; margin-bottom: 18px;
    box-shadow: 0 2px 10px rgba(30,52,71,0.06);
}
div[data-testid="stDialog"] div[role="dialog"] {
    width: 55vw !important; max-width: 700px !important;
    min-width: 400px !important; border-radius: 16px !important;
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

TIPOS = ["preventivo", "correctivo", "calibracion", "otro"]
TIPO_LABELS = {"preventivo": "🛡️ Preventivo", "correctivo": "🔧 Correctivo", "calibracion": "📐 Calibración", "otro": "📋 Otro"}


def registrar_acceso(usuario, nombre, accion):
    try:
        supabase.table("usuarios_accesos").insert({
            "usuario": usuario, "nombre": nombre,
            "accion": accion, "fecha_hora": datetime.now().isoformat()
        }).execute()
    except:
        pass


def buscar_activos(query):
    try:
        q = supabase.table("almacen_activos").select("id, codigo_activo, estado, almacen_productos(codigo, nombre)").eq("activo", True)
        if query.strip():
            q = q.ilike("codigo_activo", f"%{query}%")
        res = q.limit(10).execute()
        data = res.data or []
        for r in data:
            p = r.pop("almacen_productos", None)
            r["producto_nombre"] = p["nombre"] if p else "—"
        return data
    except Exception as e:
        st.error(f"Error al buscar activos: {e}")
        return []


def crear_mantenimiento(payload):
    try:
        supabase.table("almacen_mantenimientos").insert(payload).execute()
        return True
    except Exception as e:
        st.error(f"Error al guardar el mantenimiento: {e}")
        return False


def actualizar_estado_activo(activo_id, nuevo_estado):
    try:
        supabase.table("almacen_activos").update({"estado": nuevo_estado}).eq("id", activo_id).execute()
        return True
    except:
        return False


def cargar_mantenimientos(pagina=0, tam_pagina=50, busqueda="", filtro_tipo="Todos", desde=None, hasta=None):
    try:
        q = supabase.table("almacen_mantenimientos_resumen").select("*", count="exact")
        if busqueda.strip():
            q = q.or_(f"codigo_activo.ilike.%{busqueda}%,producto_nombre.ilike.%{busqueda}%,producto_codigo.ilike.%{busqueda}%")
        if filtro_tipo != "Todos":
            q = q.eq("tipo", filtro_tipo.lower())
        if desde:
            q = q.gte("fecha", desde)
        if hasta:
            q = q.lte("fecha", hasta)
        inicio = pagina * tam_pagina
        fin = inicio + tam_pagina - 1
        res = q.order("fecha", desc=True).range(inicio, fin).execute()
        return res.data or [], (res.count or 0)
    except Exception as e:
        st.error(f"Error al cargar mantenimientos: {e}")
        return [], 0


def contar_mantenimientos(desde=None):
    try:
        q = supabase.table("almacen_mantenimientos_resumen").select("id", count="exact")
        if desde:
            q = q.gte("fecha", desde)
        res = q.range(0, 0).execute()
        return res.count or 0
    except:
        return 0


def sumar_costo_mantenimientos(desde=None):
    try:
        q = supabase.table("almacen_mantenimientos_resumen").select("costo")
        if desde:
            q = q.gte("fecha", desde)
        res = q.execute()
        return sum((r.get("costo") or 0) for r in (res.data or []))
    except:
        return 0


def cargar_alertas_proximos(dias_umbral=30):
    try:
        res = supabase.table("almacen_mantenimientos_proximos").select("*").lte("dias_restantes", dias_umbral).order("proximo_mantenimiento").execute()
        return res.data or []
    except Exception as e:
        st.error(f"Error al cargar alertas: {e}")
        return []


if "mant_pagina" not in st.session_state:
    st.session_state["mant_pagina"] = 0


@st.dialog("🛠️ Nuevo Mantenimiento", width="large")
def ventana_nuevo_mantenimiento():
    st.caption("Registra un mantenimiento ya REALIZADO. El activo regresará automáticamente a estado 'Disponible' al guardar.")

    query = st.text_input("Buscar activo por código", placeholder="Ej. A1HITAL1501...", key="mant_busqueda")
    activo_sel = None

    if query.strip():
        resultados = buscar_activos(query)
        if not resultados:
            st.caption("Sin resultados.")
        for a in resultados:
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"🛠️ **{a['codigo_activo']}** — {a['producto_nombre']} · estado actual: {a['estado']}")
            with c2:
                if st.button("Seleccionar", key=f"mant_sel_{a['id']}", width="stretch"):
                    st.session_state["mant_activo_elegido"] = a
                    st.rerun()

    activo_sel = st.session_state.get("mant_activo_elegido")
    if activo_sel:
        st.success(f"Activo seleccionado: **{activo_sel['codigo_activo']}** — {activo_sel['producto_nombre']}")

    c1, c2 = st.columns(2)
    with c1:
        tipo = st.selectbox("Tipo *", TIPOS, format_func=lambda v: TIPO_LABELS[v])
    with c2:
        fecha = st.date_input("Fecha *", value=date.today())

    c1, c2 = st.columns(2)
    with c1:
        costo = st.number_input("Costo", min_value=0.0, step=0.01, value=0.0)
    with c2:
        proximo = st.date_input("Próximo mantenimiento (opcional)", value=None)

    observaciones = st.text_area("Observaciones", placeholder="Qué se le hizo al activo...", height=70)

    st.divider()
    if st.button("✅ Guardar Mantenimiento", type="primary", width="stretch", disabled=not activo_sel):
        payload = {
            "activo_id": activo_sel["id"], "tipo": tipo, "fecha": str(fecha),
            "costo": costo or None, "observaciones": observaciones.strip() or None,
            "proximo_mantenimiento": str(proximo) if proximo else None,
            "usuario_registro": st.session_state["usuario"], "nombre_registro": st.session_state["nombre"],
        }
        if crear_mantenimiento(payload):
            actualizar_estado_activo(activo_sel["id"], "disponible")
            registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"REGISTRAR MANTENIMIENTO: {activo_sel['codigo_activo']}")
            del st.session_state["mant_activo_elegido"]
            st.session_state["_msg"] = f"Mantenimiento de {activo_sel['codigo_activo']} registrado. El activo vuelve a estar disponible."
            st.rerun()


@st.dialog("📄 Detalle de Mantenimiento")
def ventana_ver_mantenimiento(m):
    st.markdown(f"**Activo:** `{m['codigo_activo']}` — {m['producto_nombre']}")
    st.markdown(f"**Tipo:** {TIPO_LABELS.get(m['tipo'], m['tipo'])}  ·  **Fecha:** {m['fecha']}")
    if m.get("costo"):
        st.markdown(f"**Costo:** ${m['costo']:,.2f}")
    if m.get("proximo_mantenimiento"):
        st.markdown(f"**Próximo mantenimiento:** {m['proximo_mantenimiento']}")
    if m.get("observaciones"):
        st.caption(m["observaciones"])
    if st.button("Cerrar", width="stretch"):
        st.rerun()


nombre_actual  = st.session_state.get("nombre", "")
rol_actual     = st.session_state.get("rol", "")
usuario_actual = st.session_state.get("usuario", "")
iniciales      = "".join([p[0].upper() for p in nombre_actual.split()[:2]]) if nombre_actual else "AD"

st.markdown(f"""
    <div class="msh-header">
        <div class="msh-header-left">
            <div class="msh-logo-box">🛠️</div>
            <div>
                <div class="msh-title">MSH-Hub · Almacén · Mantenimientos</div>
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
        registrar_acceso(usuario_actual, nombre_actual, "LOGOUT")
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.switch_page("app.py")

if "_msg" in st.session_state:
    st.success(st.session_state.pop("_msg"))

# ══════════════════════════════════════════════
# KPIs
# ══════════════════════════════════════════════
total_mant   = contar_mantenimientos()
este_mes     = contar_mantenimientos(desde=str(date.today().replace(day=1)))
costo_total  = sumar_costo_mantenimientos()
alertas      = cargar_alertas_proximos(30)

st.markdown(f"""
    <div class="kpi-bar">
        <div class="kpi-pill"><span class="kpi-icon">🛠️</span><span class="kpi-val" style="color:#1E293B;">{total_mant}</span><span class="kpi-lbl">Total registrados</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">📅</span><span class="kpi-val" style="color:#1D4ED8;">{este_mes}</span><span class="kpi-lbl">Este mes</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">💰</span><span class="kpi-val" style="color:#15803D;">${costo_total:,.2f}</span><span class="kpi-lbl">Costo acumulado</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">⚠️</span><span class="kpi-val" style="color:#C2410C;">{len(alertas)}</span><span class="kpi-lbl">Próximos a vencer (30 días)</span></div>
    </div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# ALERTAS DE PRÓXIMOS MANTENIMIENTOS
# ══════════════════════════════════════════════
if alertas:
    panel_alertas = st.container(key="panel_alertas")
    with panel_alertas:
        st.markdown('<div class="panel-card-titulo">⚠️ Próximos mantenimientos (30 días o vencidos)</div>', unsafe_allow_html=True)
        cw, ths = [1.6, 3, 1.5, 1.3], ["Código", "Producto", "Próximo", "Estado"]
        h_cols = st.columns(cw)
        for col, txt in zip(h_cols, ths):
            col.markdown(f"<p class='th'>{txt}</p>", unsafe_allow_html=True)
        for i, a in enumerate(alertas):
            cls = "td-alt" if i % 2 == 1 else "td"
            r = st.columns(cw)
            r[0].markdown(f"<div class='{cls}'><span class='folio-tag'>{a['codigo_activo']}</span></div>", unsafe_allow_html=True)
            r[1].markdown(f"<div class='{cls}'>{a['producto_codigo']} — {a['producto_nombre']}</div>", unsafe_allow_html=True)
            r[2].markdown(f"<div class='{cls}'>{a['proximo_mantenimiento']}</div>", unsafe_allow_html=True)
            nivel = a["nivel_alerta"]
            label_map = {"vencido": "Vencido", "critico": "Crítico (≤7 días)", "proximo": "Próximo (≤30 días)", "normal": "Normal"}
            r[3].markdown(f"<div class='{cls}'><span class='badge badge-{nivel}'>{label_map.get(nivel, nivel)}</span></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# PANEL DE FILTROS
# ══════════════════════════════════════════════
panel_filtros = st.container(key="panel_filtros")
with panel_filtros:
    c1, c2, c3, c4 = st.columns([3, 2, 2, 1.6])
    with c1:
        busqueda = st.text_input("buscar", placeholder="🔍  Buscar por código o producto...", label_visibility="collapsed")
    with c2:
        filtro_tipo = st.selectbox("tipo", ["Todos"] + [TIPO_LABELS[t] for t in TIPOS], label_visibility="collapsed")
    with c3:
        filtro_periodo = st.selectbox("periodo", ["Todo", "Este mes", "Este año"], label_visibility="collapsed")
    with c4:
        if st.button("➕ Nuevo Mantenimiento", type="primary", width="stretch"):
            ventana_nuevo_mantenimiento()

filtro_tipo_valor = "Todos"
if filtro_tipo != "Todos":
    filtro_tipo_valor = [k for k, v in TIPO_LABELS.items() if v == filtro_tipo][0]

desde = None
if filtro_periodo == "Este mes":
    desde = str(date.today().replace(day=1))
elif filtro_periodo == "Este año":
    desde = str(date.today().replace(month=1, day=1))

TAM_PAGINA = 50
filtro_actual = (busqueda, filtro_tipo_valor, desde)
if st.session_state.get("mant_filtro_anterior") != filtro_actual:
    st.session_state["mant_pagina"] = 0
    st.session_state["mant_filtro_anterior"] = filtro_actual

datos, total_filtrado = cargar_mantenimientos(
    pagina=st.session_state["mant_pagina"], tam_pagina=TAM_PAGINA,
    busqueda=busqueda, filtro_tipo=filtro_tipo_valor, desde=desde
)
df_f = pd.DataFrame(datos)

if not df_f.empty:
    cw, ths = [1.5, 2.5, 1.3, 1, 1, 1.3, 0.7], ["Código", "Producto", "Tipo", "Fecha", "Costo", "Próximo", "👁️"]
    panel_tabla = st.container(key="panel_tabla")
    with panel_tabla:
        st.markdown('<div class="panel-card-titulo">📋 Mantenimientos registrados</div>', unsafe_allow_html=True)
        h_cols = st.columns(cw)
        for idx, (col, txt) in enumerate(zip(h_cols, ths)):
            col.markdown(f"<p class='th'{' style=text-align:center;' if idx==len(ths)-1 else ''}>{txt}</p>", unsafe_allow_html=True)
        for i, (_, row) in enumerate(df_f.iterrows()):
            cls = "td-alt" if i % 2 == 1 else "td"
            r = st.columns(cw)
            r[0].markdown(f"<div class='{cls}'><span class='folio-tag'>{row['codigo_activo']}</span></div>", unsafe_allow_html=True)
            r[1].markdown(f"<div class='{cls}'>{row['producto_codigo']} — {row['producto_nombre']}</div>", unsafe_allow_html=True)
            r[2].markdown(f"<div class='{cls}'><span class='badge badge-tipo'>{TIPO_LABELS.get(row['tipo'], row['tipo'])}</span></div>", unsafe_allow_html=True)
            r[3].markdown(f"<div class='{cls}'>{row['fecha']}</div>", unsafe_allow_html=True)
            r[4].markdown(f"<div class='{cls}'>{'$'+format(row['costo'], ',.2f') if row.get('costo') else '—'}</div>", unsafe_allow_html=True)
            r[5].markdown(f"<div class='{cls}'>{row.get('proximo_mantenimiento') or '—'}</div>", unsafe_allow_html=True)
            with r[6]:
                if st.button("👁️", key=f"ver_mant_{row['id']}", width="stretch"):
                    ventana_ver_mantenimiento(row.to_dict())

        total_paginas = max(1, -(-total_filtrado // TAM_PAGINA))
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if st.button("← Anterior", disabled=st.session_state["mant_pagina"] <= 0, key="mant_pag_ant"):
                st.session_state["mant_pagina"] -= 1
                st.rerun()
        with c2:
            st.markdown(f"<p style='text-align:center; font-size:12px; color:#64748B; margin-top:8px;'>Página {st.session_state['mant_pagina'] + 1} de {total_paginas} · {total_filtrado} resultados</p>", unsafe_allow_html=True)
        with c3:
            if st.button("Siguiente →", disabled=st.session_state["mant_pagina"] >= total_paginas - 1, key="mant_pag_sig"):
                st.session_state["mant_pagina"] += 1
                st.rerun()

elif total_mant == 0:
    st.info("📭 No hay mantenimientos registrados todavía. ¡Crea el primero!")
else:
    st.info("🔍 No se encontraron mantenimientos con los filtros aplicados.")
