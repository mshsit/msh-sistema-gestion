import streamlit as st
from supabase import create_client
from datetime import datetime

# ══════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="MSH-Hub | Acceso",
    layout="wide",
    page_icon="📦",
    initial_sidebar_state="collapsed"
)

# Ocultar sidebar y nav nativa en login
st.markdown("""
<style>
[data-testid="stSidebar"]            { display: none !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="stMainMenu"]           { display: none !important; }
header[data-testid="stHeader"]       { display: none !important; }
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }

[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: #F0F4F8 !important;
    background-image:
        radial-gradient(circle at 100% 0%, rgba(150,180,235,0.85) 0%, rgba(150,180,235,0) 38%),
        radial-gradient(circle at 0% 100%, rgba(150,180,235,0.85) 0%, rgba(150,180,235,0) 36%) !important;
    background-attachment: fixed !important;
    position: relative;
}

/* Patrón de puntos decorativo, esquina superior izquierda */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 24px; left: 24px;
    width: 170px; height: 120px;
    background-image: radial-gradient(circle, #AEC0DE 2px, transparent 2px);
    background-size: 18px 18px;
    opacity: 1;
    pointer-events: none;
    z-index: 0;
}

[data-testid="stButton"] button {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 14px !important;
}
[data-testid="stButton"] button[kind="primary"] {
    background: #1E3447 !important; border: none !important;
    box-shadow: 0 2px 8px rgba(30,52,71,0.25) !important;
    height: 46px !important;
}

/* El wrapper raíz real del input es [data-testid="stTextInputRootElement"]:
   Streamlit le pinta ahí su propio borde rojo de foco/validación.
   Anulamos ese borde nativo y ponemos el nuestro en el mismo elemento,
   para que exista un único marco. */
[data-testid="stTextInputRootElement"] {
    border: 1.5px solid #D8E0EA !important;
    border-radius: 10px !important;
    background: #FFFFFF !important;
    box-shadow: none !important;
    outline: none !important;
    overflow: hidden;
}
[data-testid="stTextInputRootElement"]:focus-within {
    border-color: #94A8C4 !important;
}
/* El div intermedio (uno por debajo del root) no debe pintar borde propio */
[data-testid="stTextInputRootElement"] > div {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}
[data-testid="stTextInput"] input {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    background: transparent !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    padding-left: 4px !important;
    padding-top: 12px !important;
    padding-bottom: 12px !important;
    height: 48px !important;
}
[data-testid="stTextInput"] input::placeholder {
    color: #A8B3C2 !important;
}
[data-testid="stTextInput"] input:-webkit-autofill {
    -webkit-box-shadow: 0 0 0 1000px #FFFFFF inset !important;
    -webkit-text-fill-color: #1E293B !important;
}

/* Card de login */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px !important;
    box-shadow: 0 12px 32px rgba(30,52,71,0.12) !important;
    border-color: #E8EDF3 !important;
    background: #FFFFFF !important;
}
[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: #FFFFFF !important;
}

/* Wrapper de icono dentro del input.
   En Streamlit, st.markdown y los widgets se renderizan como hermanos
   (stElementContainer), no anidados — por eso usamos selector de
   hermano adyacente en vez de descendiente. */
.field-icon-marker { display: none; }
.field-icon-marker + div [data-testid="stTextInput"] {
    position: relative;
}
.field-icon-marker + div [data-testid="stTextInput"]::before {
    position: absolute;
    left: 12px; top: 50%;
    transform: translateY(-50%);
    font-size: 15px;
    z-index: 5;
    pointer-events: none;
}
.icon-user + div [data-testid="stTextInput"]::before { content: "👤"; }
.icon-key + div [data-testid="stTextInput"]::before { content: "🔑"; }
.field-icon-marker + div [data-testid="stTextInput"] input {
    padding-left: 30px !important;
}

.login-field-label {
    font-size: 13px; font-weight: 700; color: #1E3447;
    margin-bottom: 6px; margin-top: 14px;
}
.login-divider {
    display: flex; align-items: center; gap: 12px;
    margin: 22px 0 14px 0;
}
.login-divider::before, .login-divider::after {
    content: ""; flex: 1; height: 1px; background: #E2E8F0;
}
.login-divider span {
    font-size: 12px; color: #94A3B8; white-space: nowrap;
}
.login-secure-box {
    display: flex; align-items: center; gap: 10px;
    background: #EAF0FA; border-radius: 10px;
    padding: 12px 14px; font-size: 12.5px; color: #4B5C73;
}
.login-footer {
    text-align: center; color: #94A3B8; font-size: 12px;
    margin-top: 22px; line-height: 1.6;
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

def verificar_usuario(usuario, contrasena):
    try:
        res = supabase.table("usuarios").select("*")\
            .eq("usuario", usuario).eq("contrasena", contrasena)\
            .eq("activo", True).execute()
        return res.data[0] if res.data else None
    except:
        return None

def registrar_acceso(usuario, nombre, accion):
    try:
        supabase.table("usuarios_accesos").insert({
            "usuario": usuario, "nombre": nombre,
            "accion": accion, "fecha_hora": datetime.now().isoformat()
        }).execute()
    except:
        pass

# ══════════════════════════════════════════════
# INICIALIZAR SESSION STATE
# ══════════════════════════════════════════════
for key, val in [
    ("autenticado", False), ("usuario", ""), ("nombre", ""), ("rol", "")
]:
    if key not in st.session_state:
        st.session_state[key] = val

# Si ya está autenticado, ir directo al inicio
if st.session_state["autenticado"]:
    st.switch_page("pages/1_Inicio.py")

# ══════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════
st.markdown("<br>", unsafe_allow_html=True)
_, col_c, _ = st.columns([1, 1.1, 1])
with col_c:
    st.markdown("""
        <div style='text-align:center; margin-bottom:28px; position:relative; z-index:1;'>
            <div style='font-size:44px; margin-bottom:8px;'>📦</div>
            <div style='font-size:32px; font-weight:700; color:#1E3447; letter-spacing:-0.5px;'>MSH-Hub</div>
            <div style='font-size:14px; color:#64748B; margin-top:4px;'>Mendoza Servicios y Herramientas</div>
        </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        # Encabezado con ícono circular
        h1, h2 = st.columns([0.16, 0.84])
        with h1:
            st.markdown("""
                <div style='width:50px; height:50px; border-radius:50%; background:#EAF0FA;
                            display:flex; align-items:center; justify-content:center; font-size:22px;'>
                    🔒
                </div>
            """, unsafe_allow_html=True)
        with h2:
            st.markdown("""
                <div style='font-size:19px; font-weight:700; color:#1E3447; line-height:1.3;'>Acceso al Sistema</div>
                <div style='font-size:13px; color:#64748B; margin-top:2px;'>Ingresa tus credenciales para continuar</div>
            """, unsafe_allow_html=True)

        st.markdown("<hr style='margin:16px 0 4px 0; border-color:#EEF1F5;'>", unsafe_allow_html=True)

        st.markdown("<div class='login-field-label'>Usuario</div>", unsafe_allow_html=True)
        st.markdown("<div class='field-icon-marker icon-user'></div>", unsafe_allow_html=True)
        u_input = st.text_input("Usuario", placeholder="tu.usuario", label_visibility="collapsed")

        st.markdown("<div class='login-field-label'>Contraseña</div>", unsafe_allow_html=True)
        st.markdown("<div class='field-icon-marker icon-key'></div>", unsafe_allow_html=True)
        p_input = st.text_input("Contraseña", type="password", placeholder="••••••••", label_visibility="collapsed")

        st.write("")
        if st.button("→  Ingresar al Sistema", type="primary", width="stretch"):
            user = verificar_usuario(u_input.strip(), p_input.strip())
            if user:
                st.session_state.update({
                    "autenticado": True,
                    "usuario": user["usuario"],
                    "nombre": user["nombre"],
                    "rol": user["rol"]
                })
                registrar_acceso(user["usuario"], user["nombre"], "LOGIN")
                st.switch_page("pages/1_Inicio.py")
            else:
                st.error("Usuario o contraseña incorrectos.")

        st.markdown("""
            <div class='login-divider'><span>Acceso seguro</span></div>
            <div class='login-secure-box'>
                🛡️ Tus datos están protegidos con encriptación de nivel empresarial.
            </div>
        """, unsafe_allow_html=True)
    st.markdown(f"""
        <div class='login-footer'>
            © {datetime.now().year} MSH-Hub - Mendoza Servicios y Herramientas<br>
            Todos los derechos reservados.
        </div>
    """, unsafe_allow_html=True)
