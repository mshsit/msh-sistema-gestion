import streamlit as st
from supabase import create_client
from datetime import datetime

st.set_page_config(
    page_title="MSH-Hub | Gastos por Proyecto",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="collapsed"
)

# ── Protección ──
if not st.session_state.get("autenticado"):
    st.switch_page("app.py")

# ══════════════════════════════════════════════
# CSS: mismo lenguaje visual del resto de MSH-Hub
# ══════════════════════════════════════════════
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
.folio-tag {
    font-family: 'DM Mono', monospace; font-size: 10px; color: #94A3B8;
    background: #F1F5F9; border-radius: 4px; padding: 1px 5px; display: inline-block;
}
.panel-card-titulo { font-size: 15px; font-weight: 700; color: #1E293B; margin-bottom: 2px; }
.panel-card-subtitulo { font-size: 12px; color: #94A3B8; margin-bottom: 16px; }
div[class*="st-key-panel_filtros"],
div[class*="st-key-panel_tabla_ent"],
div[class*="st-key-panel_tabla_sal"],
div[class*="st-key-panel_resumen"] {
    background: #ffffff; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 22px 24px; margin-bottom: 18px;
    box-shadow: 0 2px 10px rgba(30,52,71,0.06);
}
.proyecto-card {
    background: #ffffff; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 22px 26px; margin-bottom: 18px; box-shadow: 0 2px 10px rgba(30,52,71,0.06);
}
.gasto-num { font-family: 'DM Mono', monospace; font-size: 26px; font-weight: 700; color: #1E3447; }
.gasto-lbl { font-size: 12px; color: #64748B; font-weight: 500; margin-bottom: 4px; }
.presupuesto-bar-bg { background: #F1F5F9; border-radius: 99px; height: 10px; overflow: hidden; margin-top: 6px; }
.presupuesto-bar-fill { height: 100%; border-radius: 99px; }
.aviso-box {
    background: #FEF3E8; color: #C2410C; border-radius: 8px; padding: 10px 14px;
    font-size: 12px; margin-bottom: 14px;
}
[data-testid="stButton"] button {
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 12px !important;
}
</style>
""", unsafe_allow_html=True)

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://unsugrcleytqroxuuhaf.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()


def registrar_acceso(usuario, nombre, accion):
    try:
        supabase.table("usuarios_accesos").insert({
            "usuario": usuario, "nombre": nombre,
            "accion": accion, "fecha_hora": datetime.now().isoformat()
        }).execute()
    except:
        pass


def cargar_proyectos():
    try:
        res = supabase.table("almacen_proyectos").select("*").order("numero_proyecto").execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Error al cargar proyectos: {e}")
        return []


def cargar_entradas_de_proyecto(proyecto_id):
    try:
        res = supabase.table("almacen_entradas").select(
            "id, folio, fecha, almacen_entradas_detalle(cantidad, costo_unitario, almacen_productos(codigo, nombre))"
        ).eq("proyecto_id", proyecto_id).order("fecha", desc=True).execute()
        filas = []
        for entrada in (res.data or []):
            for d in entrada.get("almacen_entradas_detalle") or []:
                p = d.get("almacen_productos") or {}
                cantidad = d.get("cantidad") or 0
                costo = d.get("costo_unitario") or 0
                filas.append({
                    "folio": entrada["folio"], "fecha": entrada["fecha"],
                    "producto_codigo": p.get("codigo", "—"), "producto_nombre": p.get("nombre", "—"),
                    "cantidad": cantidad, "costo_unitario": costo, "subtotal": cantidad * costo,
                })
        return filas
    except Exception as e:
        st.error(f"Error al cargar entradas del proyecto: {e}")
        return []


def cargar_salidas_de_proyecto(proyecto_id):
    filas = []
    try:
        res = supabase.table("almacen_salidas").select(
            "id, folio, fecha, almacen_salidas_detalle(cantidad, costo_unitario, activo_id, almacen_productos(codigo, nombre), almacen_activos(codigo_activo))"
        ).eq("proyecto_id", proyecto_id).execute()
        for salida in (res.data or []):
            for d in salida.get("almacen_salidas_detalle") or []:
                if not d.get("activo_id"):
                    continue
                p = d.get("almacen_productos") or {}
                a = d.get("almacen_activos") or None
                costo = d.get("costo_unitario") or 0
                filas.append({
                    "folio": salida["folio"], "fecha": salida["fecha"],
                    "producto_codigo": p.get("codigo", "—"),
                    "producto_nombre": p.get("nombre", "—") + (f" ({a['codigo_activo']})" if a else ""),
                    "cantidad": 1, "costo_unitario": costo, "subtotal": costo,
                })
    except Exception as e:
        st.error(f"Error al cargar salidas (activos) del proyecto: {e}")

    try:
        res = supabase.table("almacen_salidas_prorrateo").select(
            "porcentaje, costo_imputado, "
            "almacen_salidas_detalle(cantidad, costo_unitario, "
            "almacen_productos(codigo, nombre), almacen_salidas(folio, fecha))"
        ).eq("proyecto_id", proyecto_id).execute()
        for pr in (res.data or []):
            d = pr.get("almacen_salidas_detalle") or {}
            s = d.get("almacen_salidas") or {}
            p = d.get("almacen_productos") or {}
            cantidad_total = d.get("cantidad") or 0
            cantidad_imputada = round(cantidad_total * (pr["porcentaje"] / 100), 4)
            sufijo = "" if pr["porcentaje"] == 100 else f" ({pr['porcentaje']:.0f}% prorrateado)"
            filas.append({
                "folio": s.get("folio", "—"), "fecha": s.get("fecha", "—"),
                "producto_codigo": p.get("codigo", "—"),
                "producto_nombre": p.get("nombre", "—") + sufijo,
                "cantidad": cantidad_imputada, "costo_unitario": d.get("costo_unitario") or 0,
                "subtotal": pr["costo_imputado"],
            })
    except Exception as e:
        st.error(f"Error al cargar salidas (insumos) del proyecto: {e}")

    filas.sort(key=lambda f: f["fecha"], reverse=True)
    return filas

def tabla_movimientos(filas, titulo, key_panel):
    panel = st.container(key=key_panel)
    with panel:
        st.markdown(f'<div class="panel-card-titulo">{titulo}</div>', unsafe_allow_html=True)
        if not filas:
            st.info("Sin movimientos registrados.")
            return
        cw, ths = [1.3, 1.1, 1.3, 2.5, 1, 1.2, 1.2], ["Folio", "Fecha", "Código", "Producto", "Cant.", "Costo unit.", "Subtotal"]
        h_cols = st.columns(cw)
        for col, txt in zip(h_cols, ths):
            col.markdown(f"<p class='th'>{txt}</p>", unsafe_allow_html=True)
        for i, f in enumerate(filas):
            cls = "td-alt" if i % 2 == 1 else "td"
            r = st.columns(cw)
            r[0].markdown(f"<div class='{cls}'><span class='folio-tag'>{f['folio']}</span></div>", unsafe_allow_html=True)
            r[1].markdown(f"<div class='{cls}'>{f['fecha']}</div>", unsafe_allow_html=True)
            r[2].markdown(f"<div class='{cls}'>{f['producto_codigo']}</div>", unsafe_allow_html=True)
            r[3].markdown(f"<div class='{cls}'>{f['producto_nombre']}</div>", unsafe_allow_html=True)
            r[4].markdown(f"<div class='{cls}'>{f['cantidad']}</div>", unsafe_allow_html=True)
            r[5].markdown(f"<div class='{cls}'>${f['costo_unitario']:,.2f}</div>", unsafe_allow_html=True)
            r[6].markdown(f"<div class='{cls}'><b>${f['subtotal']:,.2f}</b></div>", unsafe_allow_html=True)


nombre_actual  = st.session_state.get("nombre", "")
rol_actual     = st.session_state.get("rol", "")
usuario_actual = st.session_state.get("usuario", "")
iniciales      = "".join([p[0].upper() for p in nombre_actual.split()[:2]]) if nombre_actual else "AD"

st.markdown(f"""
    <div class="msh-header">
        <div class="msh-header-left">
            <div class="msh-logo-box">📊</div>
            <div>
                <div class="msh-title">MSH-Hub · Almacén · Gastos por Proyecto</div>
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

proyectos = cargar_proyectos()
if not proyectos:
    st.info("📭 No hay proyectos registrados todavía. Crea uno primero en el catálogo de Proyectos.")
    st.stop()

panel_filtros = st.container(key="panel_filtros")
with panel_filtros:
    opciones = {f"{p['numero_proyecto']} — {p['nombre']}": p for p in proyectos}
    seleccion = st.selectbox("Selecciona un proyecto", list(opciones.keys()), label_visibility="collapsed")
    proyecto = opciones[seleccion]

entradas = cargar_entradas_de_proyecto(proyecto["id"])
salidas = cargar_salidas_de_proyecto(proyecto["id"])

gasto_entradas = sum(f["subtotal"] for f in entradas)
gasto_salidas = sum(f["subtotal"] for f in salidas)
gasto_total = gasto_entradas + gasto_salidas
presupuesto = proyecto.get("presupuesto_estimado")

with st.container(key="proyecto_card"):
    st.markdown('<div class="proyecto-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 3])
    with c1:
        st.markdown(f"### {proyecto['numero_proyecto']}")
        st.caption(proyecto["nombre"])
        if proyecto.get("cliente_ubicacion"):
            st.caption(f"📍 {proyecto['cliente_ubicacion']}")
        st.caption(f"Estado: **{proyecto['estado'].capitalize()}** · Inicio: {proyecto.get('fecha_inicio') or '—'}")
    with c2:
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            st.markdown('<div class="gasto-lbl">Gasto en Entradas</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="gasto-num">${gasto_entradas:,.2f}</div>', unsafe_allow_html=True)
        with cc2:
            st.markdown('<div class="gasto-lbl">Gasto en Salidas</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="gasto-num">${gasto_salidas:,.2f}</div>', unsafe_allow_html=True)
        with cc3:
            st.markdown('<div class="gasto-lbl">Gasto total</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="gasto-num" style="color:#1D4ED8;">${gasto_total:,.2f}</div>', unsafe_allow_html=True)

        if presupuesto:
            pct = min(100, (gasto_total / presupuesto) * 100) if presupuesto > 0 else 0
            color = "#15803D" if pct < 80 else ("#C2410C" if pct < 100 else "#B91C1C")
            st.markdown(f"""
                <div style="margin-top:14px;">
                    <div class="gasto-lbl">Presupuesto: ${presupuesto:,.2f} · Usado: {pct:.1f}%</div>
                    <div class="presupuesto-bar-bg">
                        <div class="presupuesto-bar-fill" style="width:{pct}%; background:{color};"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

if gasto_entradas > 0 and gasto_salidas > 0:
    st.markdown(
        '<div class="aviso-box">⚠️ Este proyecto tiene gasto tanto en Entradas como en Salidas. '
        'Si compraste un material específicamente para este proyecto (Entrada) y luego también registraste '
        'su salida del almacén hacia el mismo proyecto (Salida), el "Gasto total" de arriba podría estar '
        'contando ese material dos veces. Revisa los detalles abajo si el número se ve más alto de lo esperado.</div>',
        unsafe_allow_html=True
    )

tabla_movimientos(entradas, "📥 Entradas asignadas a este proyecto", "panel_tabla_ent")
tabla_movimientos(salidas, "📤 Salidas asignadas a este proyecto", "panel_tabla_sal")
