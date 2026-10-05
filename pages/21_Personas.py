import streamlit as st
from supabase import create_client
from datetime import datetime

st.set_page_config(
    page_title="MSH-Hub | Personas",
    layout="wide",
    page_icon="👤",
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
.badge-activo   { background:#DCFCE7; color:#15803D; }
.badge-inactivo { background:#F1F5F9; color:#64748B; }
.badge-depto    { background:#EFF6FF; color:#1D4ED8; }
.panel-card-titulo { font-size: 15px; font-weight: 700; color: #1E293B; margin-bottom: 2px; }
.panel-card-subtitulo { font-size: 12px; color: #94A3B8; margin-bottom: 16px; }
div[class*="st-key-panel_filtros"],
div[class*="st-key-panel_tabla"] {
    background: #ffffff; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 22px 24px; margin-bottom: 18px;
    box-shadow: 0 2px 10px rgba(30,52,71,0.06);
}
div[data-testid="stDialog"] div[role="dialog"] {
    width: 55vw !important; max-width: 680px !important;
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

TABLE = "almacen_personas"


def registrar_acceso(usuario, nombre, accion):
    try:
        supabase.table("usuarios_accesos").insert({
            "usuario": usuario, "nombre": nombre,
            "accion": accion, "fecha_hora": datetime.now().isoformat()
        }).execute()
    except:
        pass


def cargar_departamentos_activos():
    try:
        res = supabase.table("almacen_departamentos").select("id, nombre").eq("activo", True).order("nombre").execute()
        return res.data or []
    except:
        return []


def cargar_personas():
    try:
        res = supabase.table(TABLE).select("*, almacen_departamentos(nombre)").order("nombres").execute()
        data = res.data or []
        for row in data:
            d = row.pop("almacen_departamentos", None)
            row["departamento_nombre"] = d["nombre"] if d else "—"
        return data
    except Exception as e:
        st.error(f"Error al cargar personas: {e}")
        return []


def agregar_persona(payload):
    try:
        supabase.table(TABLE).insert(payload).execute()
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False


def modificar_persona(id_registro, payload):
    try:
        supabase.table(TABLE).update(payload).eq("id", id_registro).execute()
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False


def set_activo(id_registro, activo):
    try:
        supabase.table(TABLE).update({"activo": activo}).eq("id", id_registro).execute()
        return True
    except:
        return False


@st.dialog("👤 Nueva Persona")
def ventana_nueva_persona():
    departamentos = cargar_departamentos_activos()

    c1, c2 = st.columns(2)
    with c1:
        nombres = st.text_input("Nombres *", placeholder="Ej. Juan")
    with c2:
        apellidos = st.text_input("Apellidos", placeholder="Ej. Pérez")

    c1, c2 = st.columns(2)
    with c1:
        ficha = st.text_input("Ficha", placeholder="Opcional")
    with c2:
        cedula = st.text_input("Cédula", placeholder="Opcional")

    opciones_depto = {"— Ninguno —": None, **{d["nombre"]: d["id"] for d in departamentos}}
    sel_depto = st.selectbox("Departamento", list(opciones_depto.keys()))
    departamento_id = opciones_depto[sel_depto]

    cargo = st.text_input("Cargo", placeholder="Opcional")
    c1, c2 = st.columns(2)
    with c1:
        telefono = st.text_input("Teléfono", placeholder="Opcional")
    with c2:
        correo = st.text_input("Correo", placeholder="Opcional")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Crear Persona", type="primary", width="stretch"):
            if not nombres.strip():
                st.error("El nombre es obligatorio.")
            else:
                payload = {
                    "nombres": nombres.strip(), "apellidos": apellidos.strip() or None,
                    "ficha": ficha.strip() or None, "cedula": cedula.strip() or None,
                    "departamento_id": departamento_id, "cargo": cargo.strip() or None,
                    "telefono": telefono.strip() or None, "correo": correo.strip() or None,
                    "activo": True,
                }
                if agregar_persona(payload):
                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"AGREGAR PERSONA: {nombres.strip()}")
                    st.session_state["_msg"] = f"Persona '{nombres.strip()}' creada."
                    st.rerun()
    with c2:
        if st.button("❌ Cancelar", width="stretch"):
            st.rerun()


@st.dialog("✏️ Editar Persona")
def ventana_editar_persona(persona):
    departamentos = cargar_departamentos_activos()

    c1, c2 = st.columns(2)
    with c1:
        nombres = st.text_input("Nombres *", value=persona["nombres"])
    with c2:
        apellidos = st.text_input("Apellidos", value=persona.get("apellidos") or "")

    c1, c2 = st.columns(2)
    with c1:
        ficha = st.text_input("Ficha", value=persona.get("ficha") or "")
    with c2:
        cedula = st.text_input("Cédula", value=persona.get("cedula") or "")

    opciones_depto = {"— Ninguno —": None, **{d["nombre"]: d["id"] for d in departamentos}}
    nombre_depto_actual = persona.get("departamento_nombre", "")
    if nombre_depto_actual and nombre_depto_actual not in opciones_depto:
        opciones_depto = {nombre_depto_actual: persona.get("departamento_id"), **opciones_depto}
    lista_deptos = list(opciones_depto.keys())
    idx_depto = lista_deptos.index(nombre_depto_actual) if nombre_depto_actual in lista_deptos else 0
    sel_depto = st.selectbox("Departamento", lista_deptos, index=idx_depto)
    departamento_id = opciones_depto[sel_depto]

    cargo = st.text_input("Cargo", value=persona.get("cargo") or "")
    c1, c2 = st.columns(2)
    with c1:
        telefono = st.text_input("Teléfono", value=persona.get("telefono") or "")
    with c2:
        correo = st.text_input("Correo", value=persona.get("correo") or "")

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💾 Guardar Cambios", type="primary", width="stretch"):
            if not nombres.strip():
                st.error("El nombre es obligatorio.")
            else:
                payload = {
                    "nombres": nombres.strip(), "apellidos": apellidos.strip() or None,
                    "ficha": ficha.strip() or None, "cedula": cedula.strip() or None,
                    "departamento_id": departamento_id, "cargo": cargo.strip() or None,
                    "telefono": telefono.strip() or None, "correo": correo.strip() or None,
                }
                if modificar_persona(persona["id"], payload):
                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"EDITAR PERSONA: {nombres.strip()}")
                    st.session_state["_msg"] = f"Persona '{nombres.strip()}' actualizada."
                    st.rerun()
    with c2:
        etiqueta = "🚫 Desactivar" if persona.get("activo", True) else "✅ Reactivar"
        if st.button(etiqueta, width="stretch"):
            set_activo(persona["id"], not persona.get("activo", True))
            registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"{'DESACTIVAR' if persona.get('activo', True) else 'REACTIVAR'} PERSONA: {nombres.strip()}")
            st.rerun()
    with c3:
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
            <div class="msh-logo-box">👤</div>
            <div>
                <div class="msh-title">MSH-Hub · Configuración · Personas</div>
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

todos = cargar_personas()
total = len(todos)
activas = len([p for p in todos if p["activo"]])
inactivas = total - activas

st.markdown(f"""
    <div class="kpi-bar">
        <div class="kpi-pill"><span class="kpi-icon">👤</span><span class="kpi-val" style="color:#1E293B;">{total}</span><span class="kpi-lbl">Total</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">✅</span><span class="kpi-val" style="color:#15803D;">{activas}</span><span class="kpi-lbl">Activas</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">⚪</span><span class="kpi-val" style="color:#64748B;">{inactivas}</span><span class="kpi-lbl">Inactivas</span></div>
    </div>
""", unsafe_allow_html=True)

panel_filtros = st.container(key="panel_filtros")
with panel_filtros:
    c1, c2, c3 = st.columns([4, 2.5, 1.5])
    with c1:
        busqueda = st.text_input("buscar", placeholder="🔍  Buscar por nombre, cédula o ficha...", label_visibility="collapsed")
    with c2:
        filtro_est = st.selectbox("estado", ["Todos", "Activas", "Inactivas"], label_visibility="collapsed")
    with c3:
        if st.button("➕ Nueva Persona", type="primary", width="stretch"):
            ventana_nueva_persona()

datos = todos
if busqueda.strip():
    b = busqueda.lower()
    datos = [
        p for p in datos
        if b in p["nombres"].lower()
        or b in (p.get("apellidos") or "").lower()
        or b in (p.get("cedula") or "").lower()
        or b in (p.get("ficha") or "").lower()
    ]
if filtro_est == "Activas":
    datos = [p for p in datos if p["activo"]]
elif filtro_est == "Inactivas":
    datos = [p for p in datos if not p["activo"]]

if datos:
    cw, ths = [2.5, 1.8, 1.3, 1.7, 1.3, 1] , ["Nombre completo", "Departamento", "Cargo", "Teléfono", "Estado", "⚙️"]
    panel_tabla = st.container(key="panel_tabla")
    with panel_tabla:
        st.markdown('<div class="panel-card-titulo">📋 Personas registradas</div>', unsafe_allow_html=True)
        h_cols = st.columns(cw)
        for idx, (col, txt) in enumerate(zip(h_cols, ths)):
            col.markdown(f"<p class='th'{' style=text-align:center;' if idx==len(ths)-1 else ''}>{txt}</p>", unsafe_allow_html=True)
        for i, p in enumerate(datos):
            cls = "td-alt" if i % 2 == 1 else "td"
            r = st.columns(cw)
            nombre_completo = f"{p['nombres']} {p.get('apellidos') or ''}".strip()
            r[0].markdown(f"<div class='{cls}'><b>{nombre_completo}</b></div>", unsafe_allow_html=True)
            r[1].markdown(f"<div class='{cls}'><span class='badge badge-depto'>{p['departamento_nombre']}</span></div>", unsafe_allow_html=True)
            r[2].markdown(f"<div class='{cls}'>{p.get('cargo') or '—'}</div>", unsafe_allow_html=True)
            r[3].markdown(f"<div class='{cls}'>{p.get('telefono') or '—'}</div>", unsafe_allow_html=True)
            badge_cls = "badge-activo" if p["activo"] else "badge-inactivo"
            badge_txt = "Activo" if p["activo"] else "Inactivo"
            r[4].markdown(f"<div class='{cls}'><span class='badge {badge_cls}'>{badge_txt}</span></div>", unsafe_allow_html=True)
            with r[5]:
                if st.button("✏️", key=f"ed_per_{p['id']}", width="stretch"):
                    ventana_editar_persona(p)
else:
    st.info("📭 No hay personas registradas. ¡Crea la primera!")
