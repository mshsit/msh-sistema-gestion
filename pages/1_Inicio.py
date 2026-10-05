import streamlit as st
import base64
from pathlib import Path

st.set_page_config(
    page_title="MSH-Hub | Inicio",
    layout="wide",
    page_icon="📦",
    initial_sidebar_state="expanded"
)

# ── Protección: redirige al login si no hay sesión ──
if not st.session_state.get("autenticado"):
    st.switch_page("app.py")

# ══════════════════════════════════════════════
# VARIABLES DE SESIÓN
# ══════════════════════════════════════════════
nombre_actual  = st.session_state.get("nombre", "")
rol_actual     = st.session_state.get("rol", "")
usuario_actual = st.session_state.get("usuario", "")
iniciales      = "".join([p[0].upper() for p in nombre_actual.split()[:2]])

if "categoria_activa" not in st.session_state:
    st.session_state["categoria_activa"] = "almacen"

# ─────────────────────────────────────────────────────
# LOGO (base64)
# ─────────────────────────────────────────────────────
@st.cache_data
def cargar_logo_base64(ruta: str) -> str:
    archivo = Path(ruta)
    if not archivo.exists():
        return ""
    return base64.b64encode(archivo.read_bytes()).decode()

LOGO_B64 = cargar_logo_base64("assets/logo_m.png")

# ─────────────────────────────────────────────────────
# DEFINICIÓN DE CATEGORÍAS Y SUS OPCIONES
# Cada opción: (etiqueta, descripción, icono, página destino, disponible)
# ─────────────────────────────────────────────────────
CATEGORIAS = {
    "almacen": {
        "label": "Almacén",
        "icono": "📦",
        "opciones": [
            ("Dashboard", "Resumen general del almacén", "📈", "pages/26_Dashboard.py", True),
            ("Control de Préstamos", "Registra préstamos y devoluciones", "📋", "pages/2_Prestamos.py", True),
            ("Productos", "Catálogo de productos y activos", "📦", "pages/13_Productos.py", True),
            ("Movimientos", "Entradas, Salidas, Préstamos y Custodias", "🔄", "pages/15_Movimientos.py", True),
            ("Activos", "Consulta y gestión de unidades individuales", "🔧", "pages/16_Activos.py", True),
            ("Proyectos", "Control de gasto por número de proyecto", "📁", "pages/17_Proyectos.py", True),
            ("Seguimiento Proyectos", "Seguimiento de proyecto", "🏢", "pages/19_SeguimientoProyectos.py", True),
            ("Mantenimientos", "Historial y alertas de mantenimiento", "🛠️", "pages/23_Mantenimientos.py", True),
            ("Inventarios Físicos", "Conteo periódico y diferencias", "📊", "pages/25_InventariosFisicos.py", True),            
        ],
    },
    "compras": {
        "label": "Compras",
        "icono": "🛒",
        "opciones": [
            ("Requerimientos", "Solicita y da seguimiento a requerimientos", "🧾", "pages/3_Requerimientos.py", True),
        ],
    },
    "reportes": {
       "label": "Reportes",
       "icono": "📊",
       "opciones": [
           ("Gastos por Proyecto", "Control de gasto por número de proyecto", "📊", "pages/18_GastosProyecto.py", True),
           ("Kardex", "Historial cruzado de movimientos por producto", "📇", "pages/24_Kardex.py", True),

       ],
    },
    "configuracion": {
        "label": "Configuración",
        "icono": "⚙️",
        "opciones": [
            ("Clasificaciones", "Tipos generales de producto", "🧭", "pages/6_Clasificaciones.py", True),
            ("Categorías", "Subdivisión por clasificación", "🗂️", "pages/7_Categorias.py", True),
            ("Marcas", "Fabricantes de los productos", "🏷️", "pages/8_Marcas.py", True),
            ("Modelos", "Modelos específicos por marca", "🔧", "pages/9_Modelos.py", True),
            ("Unidades de Medida", "Pieza, caja, metro, litro...", "📏", "pages/10_UnidadesMedida.py", True),
            ("Ubicaciones", "Estructura física del almacén", "📍", "pages/11_Ubicaciones.py", True),
            ("Correlativo de Activos", "Ajuste de numeración para migración", "🔢", "pages/12_CorrelativoActivos.py", True),
            ("Correlativo de Numero de Proyecto y OT", "Ajuste de numeración para migración", "🔢", "pages/20_Configuracion.py", True),
            ("Usuarios y roles",   "Administra accesos del sistema", "👤", "pages/7_Usuarios.py", False),
            ("Historial de acceso", "Consulta los inicios de sesión", "🕓", "pages/8_Historial.py", False),
            ("Departamentos", "Áreas internas de la empresa", "🏢", "pages/20_Departamentos.py", True),
            ("Personas", "Responsables y empleados", "👤", "pages/21_Personas.py", True),
            ("Proveedores", "Origen de compras y entidades", "🏭", "pages/22_Proveedores.py", True),

        ],
     },
}

# ══════════════════════════════════════════════
# CSS SIDEBAR + GLOBAL
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }
[data-testid="stAppViewContainer"] { background: #F0F4F8; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainMenu"] { display: none !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
button[kind="header"] { display: none !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #1E3447 !important;
    border-right: none !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }
[data-testid="stSidebar"] [data-testid="stButton"] button {
    background: transparent !important; border: none !important;
    color: rgba(255,255,255,0.65) !important; text-align: left !important;
    font-size: 13px !important; font-weight: 500 !important;
    padding: 10px 12px !important; border-radius: 8px !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
    background: rgba(255,255,255,0.08) !important; color: #fff !important;
}
/* Categoría activa en sidebar */
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {
    background: rgba(255,255,255,0.12) !important; color: #fff !important;
    border-left: 3px solid #4A90D9 !important;
    border-radius: 0 8px 8px 0 !important; box-shadow: none !important;
}

/* Botón de cerrar sesión: estilo propio, visible y diferenciado */
.btn-salir div[data-testid="stButton"] button {
    background: rgba(239,68,68,0.12) !important;
    color: #FCA5A5 !important;
    border: 1px solid rgba(239,68,68,0.25) !important;
    text-align: center !important;
    justify-content: center !important;
}
.btn-salir div[data-testid="stButton"] button:hover {
    background: rgba(239,68,68,0.22) !important;
    color: #fff !important;
    border-color: rgba(239,68,68,0.4) !important;
}

/* ── BOTONES GLOBALES ── */
[data-testid="stButton"] button {
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 12px !important;
}
[data-testid="stButton"] button[kind="primary"] {
    background: #1E3447 !important; border: none !important;
    box-shadow: 0 2px 8px rgba(30,52,71,0.25) !important;
}

/* ── PANEL DERECHO: tarjetas de opción ── */
.panel-title {
    font-size: 11px; font-weight: 700; letter-spacing: 0.06em;
    color: #94A3B8; text-transform: uppercase; margin: 0 4px 14px 4px;
}
.opt-card {
    background: #FAFAFA; border: 1px solid #F1F5F9; border-radius: 10px;
    padding: 10px 16px; display: flex; align-items: center; gap: 10px;
    margin-bottom: 8px; box-sizing: border-box; opacity: 0.55; min-height: 56px;
}
.oi { font-size: 18px; flex-shrink: 0; }
.on-wrap { flex: 1; min-width: 0; }
.on   { font-size: 13px; font-weight: 600; color: #1E293B; }
.ondesc { font-size: 11px; color: #94A3B8; margin-top: 2px; }
.olock  { font-size: 13px; color: #CBD5E0; flex-shrink: 0; }
.opt-desc {
    font-size: 11px; color: #94A3B8; margin: -4px 0 8px 4px;
}

/* Botón real que reemplaza la tarjeta de opción disponible */
.opt-btn,
.opt-btn div[data-testid="stButton"] {
    width: 100% !important;
    display: block !important;
}
.opt-btn div[data-testid="stButton"] button {
    background: #fff !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    padding: 10px 16px !important;
    height: 42px !important;
    width: 100% !important;
    box-sizing: border-box !important;
    color: #1E293B !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    box-shadow: none !important;
    margin-bottom: 2px !important;
}
.opt-btn div[data-testid="stButton"] button [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    text-align: left !important;
    margin-right: auto !important;
    justify-content: flex-start !important;
}
.opt-btn div[data-testid="stButton"] button [data-testid="stMarkdownContainer"] p {
    text-align: left !important;
    margin: 0 !important;
}
.opt-btn div[data-testid="stButton"] button:hover {
    border-color: #93C5FD !important;
    box-shadow: 0 2px 8px rgba(30,52,71,0.06) !important;
}

/* ── HEADER DE BIENVENIDA (estilo Préstamos) ── */
.header-bienvenida {
    background: #1E3447; border-radius: 14px;
    padding: 20px 26px; margin: 16px 0 28px 0;
    display: flex; align-items: center; justify-content: space-between;
}
.header-saludo-wrap {
    display: flex; align-items: center; gap: 14px;
}
.header-logo {
    width: 46px; height: 46px; border-radius: 12px;
    background: #fff;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; overflow: hidden;
}
.header-logo img { width: 100%; height: 100%; object-fit: contain; padding: 6px; box-sizing: border-box; }
.header-titulo { font-size: 17px; font-weight: 700; color: #fff; letter-spacing: -0.2px; line-height: 1.2; }
.header-subtitulo { font-size: 12px; color: rgba(255,255,255,0.55); margin-top: 2px; }
.header-derecha {
    display: flex; align-items: center; gap: 16px;
}
.header-usuario {
    background: rgba(255,255,255,0.08); border-radius: 10px;
    padding: 6px 14px 6px 8px; display: flex; align-items: center; gap: 10px;
}
.header-avatar {
    width: 32px; height: 32px; border-radius: 50%;
    background: linear-gradient(135deg,#4A90D9,#2D6FA8);
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; color: #fff; flex-shrink: 0;
}
.header-nombre { font-size: 13px; font-weight: 600; color: #fff; }
.header-rol { font-size: 10px; color: rgba(255,255,255,0.55); text-transform: uppercase; letter-spacing: 0.4px; }

/* ── PANEL: título de categoría con línea de acento ── */
.panel-title-wrap { margin: 0 0 20px 4px; }
.panel-title-nuevo {
    font-size: 12px; font-weight: 700; letter-spacing: 0.06em;
    color: #1E3447; text-transform: uppercase;
}
.panel-title-linea {
    width: 32px; height: 3px; background: #4A90D9; border-radius: 2px; margin-top: 6px;
}

/* ── TARJETAS GRANDES (grid) ── */
.tarjeta-grande {
    background: #fff; border: 1px solid #E8EDF2; border-radius: 14px;
    padding: 28px 24px 24px 24px; box-sizing: border-box; position: relative;
}
.tarjeta-grande.bloqueada { opacity: 0.55; }
.tg-icono-wrap {
    width: 64px; height: 64px; border-radius: 50%;
    background: #EFF6FF; display: flex; align-items: center; justify-content: center;
    font-size: 28px; margin-bottom: 18px;
}
.tarjeta-grande.bloqueada .tg-icono-wrap { background: #F1F5F9; }
.tg-titulo { font-size: 16px; font-weight: 700; color: #1E293B; margin-bottom: 6px; }
.tg-desc { font-size: 12px; color: #94A3B8; }
.tg-candado {
    position: absolute; bottom: 24px; right: 24px;
    font-size: 15px; color: #CBD5E0;
}

/* Tarjeta disponible: el botón real de Streamlit se superpone sobre toda la tarjeta y queda invisible.
   El stElementContainer que envuelve el stButton es quien debe llevar position:absolute,
   ya que es hijo directo del stVerticalBlock con la key (mismo nivel que el stElementContainer
   que contiene el HTML decorativo de la tarjeta). */
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .tarjeta-grande) {
    position: relative !important;
}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .tarjeta-grande)
    > div[data-testid="stElementContainer"]:has(div[data-testid="stButton"]) {
    position: absolute !important; inset: 0 !important; z-index: 5 !important;
    height: 100% !important; width: 100% !important;
}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .tarjeta-grande)
    div[data-testid="stButton"] {
    height: 100% !important; width: 100% !important;
}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .tarjeta-grande)
    div[data-testid="stButton"] button {
    width: 100% !important; height: 100% !important;
    background: transparent !important; border: none !important;
    box-shadow: none !important; color: transparent !important;
    font-size: 0 !important; padding: 0 !important; cursor: pointer !important;
}
.tg-flecha-fija {
    position: absolute; bottom: 24px; right: 24px;
    font-size: 18px; color: #4A90D9; font-weight: 700; line-height: 1; z-index: 0;
}

/* ── PANEL: marco exterior real ── */
div[class*="st-key-panel_opciones"] {
    background: #fff; border: 1px solid #E8EDF2; border-radius: 16px;
    padding: 28px 32px 24px 32px; margin-top: 4px;
}

/* ── PIE DE PÁGINA INFORMATIVO ── */
.pie-info {
    display: flex; align-items: center; gap: 10px;
    margin-top: 12px; padding-top: 20px;
    border-top: 1px solid #F1F5F9;
    font-size: 12px; color: #94A3B8;
}

/* ── SIDEBAR: tarjeta de cerrar sesión (botón real superpuesto, invisible) ── */
.tarjeta-salir-card {
    background: rgba(239,68,68,0.10); border: 1px solid rgba(239,68,68,0.3);
    border-radius: 12px; padding: 14px 16px; display: flex; align-items: center; gap: 12px;
}
.tarjeta-salir-icono { font-size: 18px; color: #F87171; }
.tarjeta-salir-titulo { font-size: 13px; font-weight: 700; color: #FCA5A5; }
.tarjeta-salir-sub { font-size: 10px; color: rgba(252,165,165,0.7); margin-top: 1px; }
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .tarjeta-salir-card) {
    position: relative !important; margin-top: 8px;
}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .tarjeta-salir-card)
    > div[data-testid="stElementContainer"]:has(div[data-testid="stButton"]) {
    position: absolute !important; inset: 0 !important; z-index: 5 !important;
    height: 100% !important; width: 100% !important;
}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .tarjeta-salir-card)
    div[data-testid="stButton"] {
    height: 100% !important; width: 100% !important;
}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .tarjeta-salir-card)
    div[data-testid="stButton"] button {
    width: 100% !important; height: 100% !important;
    background: transparent !important; border: none !important;
    box-shadow: none !important; color: transparent !important;
    font-size: 0 !important; padding: 0 !important; cursor: pointer !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
        <div style="padding:24px 16px 16px 16px;
                    border-bottom:1px solid rgba(255,255,255,0.08); margin-bottom:4px;">
            <div style="font-size:22px; margin-bottom:6px;">📦</div>
            <div style="font-size:17px; font-weight:700; color:#fff;
                        letter-spacing:-0.3px; line-height:1.2;">MSH-Hub</div>
            <div style="font-size:10px; color:rgba(255,255,255,0.45); margin-top:2px;">
                Mendoza Servicios y Herramientas</div>
        </div>
        <div style="font-size:9px; font-weight:700; color:rgba(255,255,255,0.3);
                    text-transform:uppercase; letter-spacing:1px;
                    padding:12px 4px 4px 4px;">Áreas</div>
    """, unsafe_allow_html=True)

    for clave, datos in CATEGORIAS.items():
        es_activa = st.session_state["categoria_activa"] == clave
        if st.button(
            f"{datos['icono']}  {datos['label']}",
            width="stretch",
            key=f"nav_{clave}",
            type="primary" if es_activa else "secondary",
        ):
            st.session_state["categoria_activa"] = clave
            st.rerun()

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    cont_salir = st.container(key="cont_salir")
    with cont_salir:
        st.markdown("""
            <div class="tarjeta-salir-card">
                <div class="tarjeta-salir-icono">↪️</div>
                <div>
                    <div class="tarjeta-salir-titulo">Cerrar sesión</div>
                    <div class="tarjeta-salir-sub">Finaliza tu sesión de forma segura</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Cerrar sesión", key="btn_salir", width="stretch"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.switch_page("app.py")

# ══════════════════════════════════════════════
# CONTENIDO PRINCIPAL: PANEL DE OPCIONES SEGÚN CATEGORÍA ACTIVA
# ══════════════════════════════════════════════
logo_img_html = f'<img src="data:image/png;base64,{LOGO_B64}" />' if LOGO_B64 else "📦"

st.markdown(f"""
    <div class="header-bienvenida">
        <div class="header-saludo-wrap">
            <div class="header-logo">{logo_img_html}</div>
            <div>
                <div class="header-titulo">Bienvenido 👋</div>
                <div class="header-subtitulo">Por favor seleccione una opción para continuar.</div>
            </div>
        </div>
        <div class="header-derecha">
            <div class="header-usuario">
                <div class="header-avatar">{iniciales}</div>
                <div>
                    <div class="header-nombre">{nombre_actual}</div>
                    <div class="header-rol">{rol_actual}</div>
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

activa = CATEGORIAS[st.session_state["categoria_activa"]]

panel = st.container(key="panel_opciones")
with panel:
    st.markdown(f"""
        <div class="panel-title-wrap">
            <div class="panel-title-nuevo">{activa["label"]}</div>
            <div class="panel-title-linea"></div>
        </div>
    """, unsafe_allow_html=True)

    opciones = activa["opciones"]
    NUM_COLUMNAS = 3
    filas = [opciones[i:i + NUM_COLUMNAS] for i in range(0, len(opciones), NUM_COLUMNAS)]

    for fila in filas:
        cols = st.columns(NUM_COLUMNAS)
        for col, (titulo, desc, icono, destino, disponible) in zip(cols, fila):
            with col:
                if disponible:
                    clave_tarjeta = f"tarjeta_{st.session_state['categoria_activa']}_{titulo}"
                    cont_tarjeta = st.container(key=clave_tarjeta)
                    with cont_tarjeta:
                        st.markdown(f"""
                            <div class="tarjeta-grande">
                                <div class="tg-icono-wrap">{icono}</div>
                                <div class="tg-titulo">{titulo}</div>
                                <div class="tg-desc">{desc}</div>
                                <div class="tg-flecha-fija">›</div>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button(titulo, key=f"opt_{clave_tarjeta}", width="stretch"):
                            st.switch_page(destino)
                else:
                    st.markdown(f"""
                        <div class="tarjeta-grande bloqueada">
                            <div class="tg-icono-wrap">{icono}</div>
                            <div class="tg-titulo">{titulo}</div>
                            <div class="tg-desc">{desc}</div>
                            <div class="tg-candado">🔒</div>
                        </div>
                    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="pie-info">
            <span>ℹ️</span>
            <span>Selecciona una opción para gestionar los procesos de {activa["label"].lower()}.</span>
        </div>
    """, unsafe_allow_html=True)
