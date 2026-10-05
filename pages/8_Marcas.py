import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="MSH-Hub | Marcas",
    layout="wide",
    page_icon="🏷️",
    initial_sidebar_state="collapsed"
)

# ── Protección ──
if not st.session_state.get("autenticado"):
    st.switch_page("app.py")

# ══════════════════════════════════════════════
# CSS: mismo lenguaje visual que 2_Prestamos.py / 6_Clasificaciones.py / 7_Categorias.py
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
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #F0F4F8; }
::-webkit-scrollbar-thumb { background: #CBD5E0; border-radius: 99px; }
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
.badge-inactivo { background:#F1F5F9; color:#64748B; }
.panel-card-titulo { font-size: 15px; font-weight: 700; color: #1E293B; margin-bottom: 2px; }
.panel-card-subtitulo { font-size: 12px; color: #94A3B8; margin-bottom: 16px; }
div[class*="st-key-panel_filtros"],
div[class*="st-key-panel_tabla"] {
    background: #ffffff; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 22px 24px; margin-bottom: 18px;
    box-shadow: 0 2px 10px rgba(30,52,71,0.06);
}
div[data-testid="stDialog"] div[role="dialog"] {
    width: 55vw !important; max-width: 700px !important;
    min-width: 380px !important; border-radius: 16px !important;
}
div[data-testid="stDialog"] .stVerticalBlock { gap: 0.35rem !important; }
div[data-testid="stDialog"] [data-testid="stWidgetLabel"] p {
    font-size: 11px !important; font-weight: 600 !important; color: #64748B !important;
    text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: -2px !important;
}
div[data-testid="stDialog"] input,
div[data-testid="stDialog"] select,
div[data-testid="stDialog"] div[role="combobox"] {
    height: 32px !important; font-size: 13px !important; border-radius: 8px !important;
}
div[data-testid="stDialog"] textarea { font-size: 12px !important; border-radius: 8px !important; }
[data-testid="stButton"] button {
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 12px !important;
}
[data-testid="stButton"] button[kind="primary"] {
    background: #1E3447 !important; border: none !important;
    box-shadow: 0 2px 8px rgba(30,52,71,0.25) !important;
}
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] div[role="combobox"] {
    border-radius: 8px !important; border-color: #E2E8F0 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 13px !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# CONEXIÓN SUPABASE
# ══════════════════════════════════════════════
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://unsugrcleytqroxuuhaf.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

TABLE = "almacen_marcas"

# ══════════════════════════════════════════════
# FUNCIONES
# ══════════════════════════════════════════════
def registrar_acceso(usuario, nombre, accion):
    try:
        supabase.table("usuarios_accesos").insert({
            "usuario": usuario, "nombre": nombre,
            "accion": accion, "fecha_hora": datetime.now().isoformat()
        }).execute()
    except:
        pass

def cargar_marcas():
    try:
        res = supabase.table(TABLE).select("*").order("nombre").execute()
        return res.data if res.data else []
    except:
        return []

def agregar_marca(payload):
    try:
        supabase.table(TABLE).insert(payload).execute()
        return True
    except:
        return False

def modificar_marca(id_registro, payload):
    try:
        supabase.table(TABLE).update(payload).eq("id", id_registro).execute()
        return True
    except:
        return False

def set_activo(id_registro, activo):
    try:
        supabase.table(TABLE).update({"activo": activo}).eq("id", id_registro).execute()
        return True
    except:
        return False

def nombre_existe(nombre, excluir_id=None):
    try:
        q = supabase.table(TABLE).select("id").ilike("nombre", nombre).execute().data
        if excluir_id:
            q = [r for r in q if r["id"] != excluir_id]
        return len(q) > 0
    except:
        return False

# ══════════════════════════════════════════════
# DIÁLOGOS
# ══════════════════════════════════════════════
@st.dialog("🏷️ Nueva Marca")
def ventana_nueva_marca():
    nombre = st.text_input("Nombre *", placeholder="Ej. Bosch")
    descripcion = st.text_area("Descripción", placeholder="Opcional", height=70)
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Crear Marca", type="primary", width="stretch"):
            if not nombre.strip():
                st.error("El nombre es obligatorio.")
            elif nombre_existe(nombre.strip()):
                st.error(f"La marca '{nombre.strip()}' ya existe.")
            else:
                payload = {"nombre": nombre.strip(), "descripcion": descripcion.strip() or None, "activo": True}
                if agregar_marca(payload):
                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"AGREGAR MARCA: {nombre.strip()}")
                    st.session_state["ultimo_editado"] = nombre.strip()
                    st.rerun()
                else:
                    st.error("Error al guardar. Verifica la conexión.")
    with c2:
        if st.button("❌ Cancelar", width="stretch"):
            st.rerun()


@st.dialog("✏️ Editar Marca")
def ventana_editar_marca(id_reg, datos):
    nombre = st.text_input("Nombre *", value=datos.get("nombre", ""))
    descripcion = st.text_area("Descripción", value=datos.get("descripcion", "") or "", height=70)
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💾 Guardar Cambios", type="primary", width="stretch"):
            if not nombre.strip():
                st.error("El nombre es obligatorio.")
            elif nombre_existe(nombre.strip(), excluir_id=id_reg):
                st.error(f"La marca '{nombre.strip()}' ya existe.")
            else:
                payload = {"nombre": nombre.strip(), "descripcion": descripcion.strip() or None}
                if modificar_marca(id_reg, payload):
                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"EDITAR MARCA: {nombre.strip()}")
                    st.session_state["ultimo_editado"] = nombre.strip()
                    st.rerun()
                else:
                    st.error("Error al guardar.")
    with c2:
        etiqueta = "🚫 Desactivar" if datos.get("activo", True) else "✅ Reactivar"
        if st.button(etiqueta, width="stretch"):
            set_activo(id_reg, not datos.get("activo", True))
            registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"{'DESACTIVAR' if datos.get('activo', True) else 'REACTIVAR'} MARCA: {nombre.strip()}")
            st.rerun()
    with c3:
        if st.button("❌ Cerrar", width="stretch"):
            st.rerun()

# ══════════════════════════════════════════════
# SESSION STATE LOCAL
# ══════════════════════════════════════════════
for key, val in [("ultimo_editado", "")]:
    if key not in st.session_state:
        st.session_state[key] = val

nombre_actual  = st.session_state.get("nombre", "")
rol_actual     = st.session_state.get("rol", "")
usuario_actual = st.session_state.get("usuario", "")
es_admin       = rol_actual == "admin"
iniciales      = "".join([p[0].upper() for p in nombre_actual.split()[:2]]) if nombre_actual else "AD"

# ══════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════
st.markdown(f"""
    <div class="msh-header">
        <div class="msh-header-left">
            <div class="msh-logo-box">🏷️</div>
            <div>
                <div class="msh-title">MSH-Hub · Catálogos · Marcas</div>
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

# ══════════════════════════════════════════════
# CARGA DE DATOS
# ══════════════════════════════════════════════
df_master = pd.DataFrame(cargar_marcas())

# ══════════════════════════════════════════════
# KPIs
# ══════════════════════════════════════════════
total     = len(df_master) if not df_master.empty else 0
activas   = len(df_master[df_master["activo"] == True])  if not df_master.empty else 0
inactivas = len(df_master[df_master["activo"] == False]) if not df_master.empty else 0

st.markdown(f"""
    <div class="kpi-bar">
        <div class="kpi-pill">
            <span class="kpi-icon">🏷️</span>
            <span class="kpi-val" style="color:#1E293B;">{total}</span>
            <span class="kpi-lbl">Total</span>
        </div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill">
            <span class="kpi-icon">✅</span>
            <span class="kpi-val" style="color:#15803D;">{activas}</span>
            <span class="kpi-lbl">Activas</span>
        </div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill">
            <span class="kpi-icon">⚪</span>
            <span class="kpi-val" style="color:#64748B;">{inactivas}</span>
            <span class="kpi-lbl">Inactivas</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# PANEL DE CONTROLES (Filtros y búsqueda)
# ══════════════════════════════════════════════
panel_filtros = st.container(key="panel_filtros")
with panel_filtros:
    st.markdown('<div class="panel-card-titulo">🔍 Filtros y búsqueda</div>', unsafe_allow_html=True)

    c_busq, c_est, c_nuevo = st.columns([4, 2.5, 1.5])
    with c_busq:
        busqueda = st.text_input(
            "buscar", placeholder="🔍  Buscar por nombre...",
            label_visibility="collapsed"
        )
    with c_est:
        filtro_est = st.selectbox("estado", ["Todos", "Activos", "Inactivos"], label_visibility="collapsed")
    with c_nuevo:
        if es_admin:
            if st.button("➕ Nueva Marca", type="primary", width="stretch"):
                ventana_nueva_marca()

# ══════════════════════════════════════════════
# FILTRADO
# ══════════════════════════════════════════════
df_f = df_master.copy() if not df_master.empty else pd.DataFrame()
if not df_f.empty:
    if busqueda.strip():
        df_f = df_f[df_f["nombre"].str.contains(busqueda, case=False, na=False)]
    if filtro_est == "Activos":
        df_f = df_f[df_f["activo"] == True]
    elif filtro_est == "Inactivos":
        df_f = df_f[df_f["activo"] == False]

# ══════════════════════════════════════════════
# TABLA
# ══════════════════════════════════════════════
if not df_f.empty:
    cw  = [3, 5, 1.5, 1] if es_admin else [3, 5, 1.5]
    ths = ["Nombre", "Descripción", "Estado", "⚙️"] if es_admin else ["Nombre", "Descripción", "Estado"]

    panel_tabla = st.container(key="panel_tabla")
    with panel_tabla:
        st.markdown("""
            <div class="panel-card-titulo">📋 Marcas registradas</div>
            <div class="panel-card-subtitulo">Fabricantes de los productos del almacén</div>
        """, unsafe_allow_html=True)

        h_cols = st.columns(cw)
        for idx, (col, txt) in enumerate(zip(h_cols, ths)):
            estilo = " style='text-align:center;'" if (es_admin and idx == len(ths) - 1) else ""
            col.markdown(f"<p class='th'{estilo}>{txt}</p>", unsafe_allow_html=True)

        for i, (_, row) in enumerate(df_f.iterrows()):
            id_reg = row["id"]
            cls = "td-alt" if i % 2 == 1 else "td"

            r = st.columns(cw)
            r[0].markdown(f"<div class='{cls}'><b>{row['nombre']}</b></div>", unsafe_allow_html=True)
            desc = row.get("descripcion") or "—"
            r[1].markdown(f"<div class='{cls}'>{desc}</div>", unsafe_allow_html=True)
            badge_cls = "badge-activo" if row["activo"] else "badge-inactivo"
            badge_txt = "Activo" if row["activo"] else "Inactivo"
            r[2].markdown(f"<div class='{cls}'><span class='badge {badge_cls}'>{badge_txt}</span></div>", unsafe_allow_html=True)

            if es_admin:
                with r[3]:
                    if st.button("✏️", key=f"ed_{id_reg}", help=f"Editar {row['nombre']}", width="stretch"):
                        ventana_editar_marca(id_reg, row.to_dict())

elif not df_master.empty:
    st.info("🔍 No se encontraron registros con los filtros aplicados.")
else:
    st.info("📭 No hay marcas registradas. ¡Crea la primera!")
