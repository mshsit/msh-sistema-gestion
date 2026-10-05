import streamlit as st
from supabase import create_client
from datetime import datetime

st.set_page_config(
    page_title="MSH-Hub | Correlativos del Sistema",
    layout="wide",
    page_icon="🔢",
    initial_sidebar_state="collapsed"
)

# ── Protección ──
if not st.session_state.get("autenticado"):
    st.switch_page("app.py")

if st.session_state.get("rol") != "admin":
    st.error("⛔ Esta sección es exclusiva para administradores.")
    if st.button("← Regresar al menú"):
        st.switch_page("pages/1_Inicio.py")
    st.stop()

# ══════════════════════════════════════════════
# CSS: mismo lenguaje visual del resto de páginas
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
.correlativo-card {
    background: #ffffff; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 28px 32px; margin-bottom: 18px;
    box-shadow: 0 2px 10px rgba(30,52,71,0.06);
}
.correlativo-actual {
    font-family: 'DM Mono', monospace; font-size: 42px; font-weight: 700;
    color: #1E3447; line-height: 1;
}
.correlativo-lbl { font-size: 12px; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.4px; }
.ejemplo-tag {
    font-family: 'DM Mono', monospace; font-size: 13px; color: #1D4ED8;
    background: #EFF6FF; border-radius: 6px; padding: 4px 10px; display: inline-block;
}
[data-testid="stButton"] button[kind="primary"] {
    background: #1E3447 !important; border: none !important;
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


def obtener_correlativo_actual():
    try:
        res = supabase.rpc("consultar_correlativo_actual", {}).execute()
        return res.data
    except Exception as e:
        st.error(f"No se pudo consultar el correlativo: {e}")
        return None


def ajustar_correlativo(nuevo_valor):
    try:
        supabase.rpc("ajustar_correlativo_activos", {"p_nuevo_valor": nuevo_valor}).execute()
        return True
    except Exception as e:
        st.error(f"Error al ajustar el correlativo: {e}")
        return False


nombre_actual = st.session_state.get("nombre", "")
usuario_actual = st.session_state.get("usuario", "")

# ══════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════
st.markdown("""
    <div class="msh-header">
        <div class="msh-header-left">
            <div class="msh-logo-box">🔢</div>
            <div>
                <div class="msh-title">MSH-Hub · Configuración · Correlativos del Sistema</div>
                <div class="msh-subtitle">Mendoza Servicios y Herramientas</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

if st.button("← Regresar al menú"):
    st.switch_page("pages/1_Inicio.py")

st.divider()

# ══════════════════════════════════════════════
# ESTADO ACTUAL
# ══════════════════════════════════════════════
valor_actual = obtener_correlativo_actual()

with st.container(key="correlativo_card"):
    st.markdown('<div class="correlativo-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown('<div class="correlativo-lbl">Último correlativo emitido</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="correlativo-actual">{valor_actual if valor_actual is not None else "—"}</div>', unsafe_allow_html=True)
    with c2:
        st.markdown("**Formato de código de activo:**")
        st.markdown(
            "`A1` (almacén principal) + 2 letras de categoría + 3 letras de producto + correlativo global"
        )
        st.markdown('<span class="ejemplo-tag">Ejemplo: A1HITAL1501</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.info(
    "💡 El correlativo crece automáticamente cada vez que se crea un nuevo activo en el sistema. "
    "Solo necesitas tocar esta pantalla **una vez**, el día que migres tus productos existentes de Excel, "
    "para que MSH-Hub continúe la numeración exactamente donde la dejaste."
)

st.divider()

# ══════════════════════════════════════════════
# AJUSTE MANUAL (MIGRACIÓN)
# ══════════════════════════════════════════════
st.subheader("⚠️ Ajustar correlativo (solo para migración)")
st.caption(
    "Usa esto ÚNICAMENTE cuando estés migrando tus ~5,000 productos existentes de Excel. "
    "Escribe el ÚLTIMO correlativo que ya usaste físicamente — el sistema continuará desde el siguiente número."
)

nuevo_valor = st.number_input(
    "Último correlativo usado en tus etiquetas actuales",
    min_value=0, step=1, value=0,
    help="Ej. si tu última herramienta etiquetada fue A1HITAL5000, escribe 5000. El siguiente código generado usará 5001."
)

confirmacion = st.text_input(
    'Para confirmar, escribe "CONFIRMAR" en mayúsculas',
    placeholder="CONFIRMAR"
)

if st.button("🔒 Ajustar correlativo", type="primary", disabled=(confirmacion != "CONFIRMAR")):
    if ajustar_correlativo(int(nuevo_valor)):
        registrar_acceso(usuario_actual, nombre_actual, f"AJUSTAR CORRELATIVO ACTIVOS: {nuevo_valor}")
        st.success(f"✅ Correlativo ajustado. El próximo código de activo usará el número {int(nuevo_valor) + 1}.")
        st.rerun()

st.caption(
    "🔒 Esta acción queda registrada en el historial de auditoría del sistema."
)

st.divider()
st.divider()

# ══════════════════════════════════════════════
# CORRELATIVO DE PRODUCTOS (catálogo)
# ══════════════════════════════════════════════
def obtener_correlativo_productos_actual():
    try:
        res = supabase.rpc("consultar_correlativo_productos_actual", {}).execute()
        return res.data
    except Exception as e:
        st.error(f"No se pudo consultar el correlativo de productos: {e}")
        return None


def ajustar_correlativo_productos(nuevo_valor):
    try:
        supabase.rpc("ajustar_correlativo_productos", {"p_nuevo_valor": nuevo_valor}).execute()
        return True
    except Exception as e:
        st.error(f"Error al ajustar el correlativo de productos: {e}")
        return False


valor_actual_prod = obtener_correlativo_productos_actual()

with st.container(key="correlativo_prod_card"):
    st.markdown('<div class="correlativo-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown('<div class="correlativo-lbl">Último código de producto emitido</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="correlativo-actual">{valor_actual_prod if valor_actual_prod is not None else "—"}</div>', unsafe_allow_html=True)
    with c2:
        st.markdown("**Formato de código de producto:**")
        st.markdown("`PRO-` + correlativo global de 4 dígitos (crece sin límite)")
        st.markdown('<span class="ejemplo-tag">Ejemplo: PRO-0001</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.info(
    "💡 A diferencia del correlativo de Activos, este **no requiere ajuste por migración** — "
    "tus productos en Excel no tenían un código de catálogo separado, así que este contador "
    "puede empezar limpio desde 1. Esta sección es solo para casos excepcionales "
    "(ej. importaste productos por otro medio y quieres realinear el contador)."
)

st.subheader("⚠️ Ajustar correlativo de productos (caso excepcional)")
nuevo_valor_prod = st.number_input(
    "Último correlativo de producto ya usado",
    min_value=0, step=1, value=0, key="ajuste_prod_valor"
)
confirmacion_prod = st.text_input(
    'Para confirmar, escribe "CONFIRMAR" en mayúsculas',
    placeholder="CONFIRMAR", key="ajuste_prod_confirm"
)
if st.button("🔒 Ajustar correlativo de productos", type="primary", disabled=(confirmacion_prod != "CONFIRMAR")):
    if ajustar_correlativo_productos(int(nuevo_valor_prod)):
        registrar_acceso(usuario_actual, nombre_actual, f"AJUSTAR CORRELATIVO PRODUCTOS: {nuevo_valor_prod}")
        st.success(f"✅ Correlativo ajustado. El próximo código de producto usará PRO-{int(nuevo_valor_prod) + 1:04d}.")
        st.rerun()
