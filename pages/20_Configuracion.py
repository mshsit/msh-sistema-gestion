import streamlit as st
from supabase import create_client
from datetime import datetime

st.set_page_config(
    page_title="MSH-Hub | Configuración",
    layout="wide",
    page_icon="⚙️",
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
div[class*="st-key-panel_consecutivo"] {
    background: #ffffff; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 22px 24px; margin-bottom: 18px;
    box-shadow: 0 2px 10px rgba(30,52,71,0.06);
}
.panel-card-titulo { font-size: 15px; font-weight: 700; color: #1E293B; margin-bottom: 2px; }
.panel-card-subtitulo { font-size: 12px; color: #94A3B8; margin-bottom: 16px; }
.consecutivo-actual {
    font-family: 'DM Mono', monospace; font-size: 22px; font-weight: 700; color: #1E3447;
    background: #F4F8FC; border: 1px solid #DCE7F3; border-radius: 10px;
    padding: 10px 16px; display: inline-block; margin-bottom: 14px;
}
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
    except Exception:
        pass


def siguiente_numero_proyecto():
    try:
        return supabase.rpc("siguiente_numero_proyecto_preview", {}).execute().data
    except Exception:
        return "????"


def siguiente_numero_ot():
    try:
        return supabase.rpc("siguiente_numero_ot_preview", {}).execute().data
    except Exception:
        return "OT-????-???"


def reiniciar_numero_proyecto(nuevo_inicio):
    try:
        supabase.rpc("reiniciar_numero_proyecto", {"nuevo_inicio": nuevo_inicio}).execute()
        return True
    except Exception as e:
        st.error(f"Error al reiniciar el consecutivo: {e}")
        return False


def reiniciar_numero_ot(nuevo_inicio):
    try:
        supabase.rpc("reiniciar_numero_ot", {"nuevo_inicio": nuevo_inicio}).execute()
        return True
    except Exception as e:
        st.error(f"Error al reiniciar el consecutivo: {e}")
        return False


nombre_actual  = st.session_state.get("nombre", "")
rol_actual     = st.session_state.get("rol", "")
usuario_actual = st.session_state.get("usuario", "")
es_admin       = rol_actual == "admin"
iniciales      = "".join([p[0].upper() for p in nombre_actual.split()[:2]]) if nombre_actual else "AD"

st.markdown(f"""
    <div class="msh-header">
        <div class="msh-header-left">
            <div class="msh-logo-box">⚙️</div>
            <div>
                <div class="msh-title">MSH-Hub · Configuración</div>
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

if not es_admin:
    st.error("🔒 Esta pantalla es exclusiva para administradores.")
    st.stop()

if "_msg_config" in st.session_state:
    st.success(st.session_state.pop("_msg_config"))

# ── Consecutivo de número de proyecto ──
panel_proy = st.container(key="panel_consecutivo_proyecto")
with panel_proy:
    st.markdown('<div class="panel-card-titulo">📁 Consecutivo de Número de Proyecto</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-card-subtitulo">Usado por la pantalla de Proyectos al crear uno nuevo.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="consecutivo-actual">Próximo: {siguiente_numero_proyecto()}</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="aviso-box">⚠️ Cambiar este valor afecta a todo el sistema. Úsalo solo para alinear el '
        'consecutivo con proyectos ya existentes (por ejemplo, al migrar desde Excel) — no lo cambies con '
        'proyectos activos sin confirmar antes el número correcto.</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns([2, 1])
    with c1:
        nuevo_inicio_proy = st.number_input("Nuevo punto de partida", min_value=1, step=1, key="config_inicio_proyecto")
    with c2:
        st.write("")
        st.write("")
        if st.button("Aplicar", key="btn_reiniciar_proyecto", width="stretch"):
            if reiniciar_numero_proyecto(int(nuevo_inicio_proy)):
                registrar_acceso(usuario_actual, nombre_actual, f"REINICIAR CONSECUTIVO PROYECTO: {nuevo_inicio_proy}")
                st.session_state["_msg_config"] = f"Consecutivo de proyecto reiniciado — el próximo será {str(int(nuevo_inicio_proy)).zfill(4)}."
                st.rerun()

# ── Consecutivo de número de OT ──
panel_ot = st.container(key="panel_consecutivo_ot")
with panel_ot:
    st.markdown('<div class="panel-card-titulo">🛠️ Consecutivo de Número de OT</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-card-subtitulo">Usado por la pantalla de Seguimiento de Proyectos al crear una OT nueva.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="consecutivo-actual">Próximo: {siguiente_numero_ot()}</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="aviso-box">⚠️ Mismo criterio que el de proyecto — solo para alinear con OTs ya '
        'existentes al migrar datos.</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns([2, 1])
    with c1:
        nuevo_inicio_ot = st.number_input("Nuevo punto de partida", min_value=1, step=1, key="config_inicio_ot")
    with c2:
        st.write("")
        st.write("")
        if st.button("Aplicar", key="btn_reiniciar_ot", width="stretch"):
            if reiniciar_numero_ot(int(nuevo_inicio_ot)):
                registrar_acceso(usuario_actual, nombre_actual, f"REINICIAR CONSECUTIVO OT: {nuevo_inicio_ot}")
                st.session_state["_msg_config"] = f"Consecutivo de OT reiniciado — el próximo será OT-{datetime.now().year}-{str(int(nuevo_inicio_ot)).zfill(3)}."
                st.rerun()
