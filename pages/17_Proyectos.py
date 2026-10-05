import streamlit as st
from supabase import create_client
from datetime import datetime, date

st.set_page_config(
    page_title="MSH-Hub | Proyectos",
    layout="wide",
    page_icon="📁",
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
.badge {
    display: inline-flex; align-items: center; gap: 4px; padding: 3px 9px;
    border-radius: 99px; font-size: 10px; font-weight: 600; white-space: nowrap;
}
.badge-activo   { background:#DCFCE7; color:#15803D; }
.badge-pausado  { background:#FEF3E8; color:#C2410C; }
.badge-cerrado  { background:#F1F5F9; color:#64748B; }
.folio-tag {
    font-family: 'DM Mono', monospace; font-size: 10px; color: #94A3B8;
    background: #F1F5F9; border-radius: 4px; padding: 1px 5px; display: inline-block;
}
.panel-card-titulo { font-size: 15px; font-weight: 700; color: #1E293B; margin-bottom: 2px; }
div[class*="st-key-panel_filtros"],
div[class*="st-key-panel_tabla"] {
    background: #ffffff; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 22px 24px; margin-bottom: 18px;
    box-shadow: 0 2px 10px rgba(30,52,71,0.06);
}
div[data-testid="stDialog"] div[role="dialog"] {
    width: 55vw !important; max-width: 700px !important;
    min-width: 420px !important; border-radius: 16px !important;
    max-height: 85vh !important; overflow-y: auto !important;
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
TABLE = "almacen_proyectos"


def registrar_acceso(usuario, nombre, accion):
    try:
        supabase.table("usuarios_accesos").insert({
            "usuario": usuario, "nombre": nombre, "accion": accion, "fecha_hora": datetime.now().isoformat()
        }).execute()
    except:
        pass


def cargar_proyectos():
    try:
        res = supabase.table(TABLE).select("*").order("fecha_inicio", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Error al cargar proyectos: {e}")
        return []


def numero_proyecto_existe(numero, excluir_id=None):
    try:
        q = supabase.table(TABLE).select("id").eq("numero_proyecto", numero).execute().data
        if excluir_id:
            q = [r for r in q if r["id"] != excluir_id]
        return len(q) > 0
    except:
        return False


def crear_proyecto(payload):
    try:
        supabase.table(TABLE).insert(payload).execute()
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False


def actualizar_proyecto(id_registro, payload):
    try:
        supabase.table(TABLE).update(payload).eq("id", id_registro).execute()
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False


@st.dialog("📁 Nuevo Proyecto")
def ventana_nuevo_proyecto():
    numero = st.text_input("Número de proyecto *", placeholder="Ej. PROY-2026-014")
    nombre = st.text_input("Nombre *", placeholder="Ej. Mantenimiento Planta Norte")
    descripcion = st.text_area("Descripción", height=60)
    cliente = st.text_input("Cliente / Ubicación", placeholder="Opcional")
    c1, c2 = st.columns(2)
    with c1:
        fecha_inicio = st.date_input("Fecha de inicio", value=date.today())
    with c2:
        presupuesto = st.number_input("Presupuesto estimado", min_value=0.0, step=100.0)
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Crear Proyecto", type="primary", width="stretch"):
            if not numero.strip() or not nombre.strip():
                st.error("Número de proyecto y nombre son obligatorios.")
            elif numero_proyecto_existe(numero.strip()):
                st.error(f"El número de proyecto '{numero}' ya existe.")
            else:
                payload = {
                    "numero_proyecto": numero.strip(), "nombre": nombre.strip(),
                    "descripcion": descripcion.strip() or None, "cliente_ubicacion": cliente.strip() or None,
                    "fecha_inicio": str(fecha_inicio), "presupuesto_estimado": presupuesto or None,
                    "estado": "activo", "activo": True,
                }
                if crear_proyecto(payload):
                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"AGREGAR PROYECTO: {numero}")
                    st.session_state["_msg"] = f"Proyecto '{numero}' creado correctamente."
                    st.rerun()
    with c2:
        if st.button("❌ Cancelar", width="stretch"):
            st.rerun()


@st.dialog("✏️ Editar Proyecto")
def ventana_editar_proyecto(proyecto):
    numero = st.text_input("Número de proyecto *", value=proyecto["numero_proyecto"])
    nombre = st.text_input("Nombre *", value=proyecto["nombre"])
    descripcion = st.text_area("Descripción", value=proyecto.get("descripcion") or "", height=60)
    cliente = st.text_input("Cliente / Ubicación", value=proyecto.get("cliente_ubicacion") or "")
    c1, c2, c3 = st.columns(3)
    with c1:
        estado = st.selectbox("Estado", ["activo", "pausado", "cerrado"],
                               index=["activo", "pausado", "cerrado"].index(proyecto.get("estado", "activo")),
                               format_func=lambda v: v.capitalize())
    with c2:
        fecha_inicio = st.date_input("Fecha de inicio", value=date.fromisoformat(proyecto["fecha_inicio"]) if proyecto.get("fecha_inicio") else date.today())
    with c3:
        presupuesto = st.number_input("Presupuesto estimado", min_value=0.0, step=100.0, value=float(proyecto.get("presupuesto_estimado") or 0))
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Guardar Cambios", type="primary", width="stretch"):
            if not numero.strip() or not nombre.strip():
                st.error("Número de proyecto y nombre son obligatorios.")
            elif numero_proyecto_existe(numero.strip(), excluir_id=proyecto["id"]):
                st.error(f"El número de proyecto '{numero}' ya existe.")
            else:
                payload = {
                    "numero_proyecto": numero.strip(), "nombre": nombre.strip(),
                    "descripcion": descripcion.strip() or None, "cliente_ubicacion": cliente.strip() or None,
                    "estado": estado, "fecha_inicio": str(fecha_inicio), "presupuesto_estimado": presupuesto or None,
                }
                if actualizar_proyecto(proyecto["id"], payload):
                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"EDITAR PROYECTO: {numero}")
                    st.session_state["_msg"] = f"Proyecto '{numero}' actualizado."
                    st.rerun()
    with c2:
        if st.button("❌ Cerrar", width="stretch"):
            st.rerun()


nombre_actual  = st.session_state.get("nombre", "")
rol_actual     = st.session_state.get("rol", "")
usuario_actual = st.session_state.get("usuario", "")
es_admin       = rol_actual == "admin"
iniciales      = "".join([p[0].upper() for p in nombre_actual.split()[:2]]) if nombre_actual else "AD"

st.markdown(f"""
    <div class="msh-header">
        <div class="msh-header-left">
            <div class="msh-logo-box">📁</div>
            <div>
                <div class="msh-title">MSH-Hub · Almacén · Proyectos</div>
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

import pandas as pd
df_master = pd.DataFrame(cargar_proyectos())
total    = len(df_master) if not df_master.empty else 0
activos  = len(df_master[df_master["estado"] == "activo"]) if not df_master.empty else 0
pausados = len(df_master[df_master["estado"] == "pausado"]) if not df_master.empty else 0
cerrados = len(df_master[df_master["estado"] == "cerrado"]) if not df_master.empty else 0

st.markdown(f"""
    <div class="kpi-bar">
        <div class="kpi-pill"><span class="kpi-icon">📁</span><span class="kpi-val" style="color:#1E293B;">{total}</span><span class="kpi-lbl">Total</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">🟢</span><span class="kpi-val" style="color:#15803D;">{activos}</span><span class="kpi-lbl">Activos</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">🟠</span><span class="kpi-val" style="color:#C2410C;">{pausados}</span><span class="kpi-lbl">Pausados</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">⚪</span><span class="kpi-val" style="color:#64748B;">{cerrados}</span><span class="kpi-lbl">Cerrados</span></div>
    </div>
""", unsafe_allow_html=True)

panel_filtros = st.container(key="panel_filtros")
with panel_filtros:
    st.markdown('<div class="panel-card-titulo">🔍 Filtros y búsqueda</div>', unsafe_allow_html=True)
    c_busq, c_est, c_nuevo = st.columns([4, 2.5, 1.6])
    with c_busq:
        busqueda = st.text_input("buscar", placeholder="🔍  Buscar por número o nombre...", label_visibility="collapsed")
    with c_est:
        filtro_est = st.selectbox("estado", ["Todos", "Activo", "Pausado", "Cerrado"], label_visibility="collapsed")
    with c_nuevo:
        if st.button("➕ Nuevo Proyecto", type="primary", width="stretch"):
            ventana_nuevo_proyecto()

df_f = df_master.copy() if not df_master.empty else pd.DataFrame()
if not df_f.empty:
    if busqueda.strip():
        df_f = df_f[df_f["numero_proyecto"].str.contains(busqueda, case=False, na=False) | df_f["nombre"].str.contains(busqueda, case=False, na=False)]
    if filtro_est != "Todos":
        df_f = df_f[df_f["estado"] == filtro_est.lower()]

if not df_f.empty:
    cw, ths = [1.6, 2.5, 2, 1.3, 1.5, 1], ["N° Proyecto", "Nombre", "Cliente/Ubicación", "Estado", "Presupuesto", "⚙️"]
    panel_tabla = st.container(key="panel_tabla")
    with panel_tabla:
        st.markdown('<div class="panel-card-titulo">📋 Proyectos registrados</div>', unsafe_allow_html=True)
        h_cols = st.columns(cw)
        for idx, (col, txt) in enumerate(zip(h_cols, ths)):
            col.markdown(f"<p class='th'{' style=text-align:center;' if idx==len(ths)-1 else ''}>{txt}</p>", unsafe_allow_html=True)
        for i, (_, row) in enumerate(df_f.iterrows()):
            cls = "td-alt" if i % 2 == 1 else "td"
            r = st.columns(cw)
            r[0].markdown(f"<div class='{cls}'><span class='folio-tag'>{row['numero_proyecto']}</span></div>", unsafe_allow_html=True)
            r[1].markdown(f"<div class='{cls}'><b>{row['nombre']}</b></div>", unsafe_allow_html=True)
            r[2].markdown(f"<div class='{cls}'>{row.get('cliente_ubicacion') or '—'}</div>", unsafe_allow_html=True)
            r[3].markdown(f"<div class='{cls}'><span class='badge badge-{row['estado']}'>{row['estado'].capitalize()}</span></div>", unsafe_allow_html=True)
            presup = row.get("presupuesto_estimado")
            r[4].markdown(f"<div class='{cls}'>{'$' + format(presup, ',.2f') if presup else '—'}</div>", unsafe_allow_html=True)
            with r[5]:
                if st.button("✏️", key=f"ed_proy_{row['id']}", width="stretch"):
                    ventana_editar_proyecto(row.to_dict())
else:
    st.info("📭 No hay proyectos registrados. ¡Crea el primero!")
