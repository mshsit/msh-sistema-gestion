import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# ══════════════════════════════════════════════
# CONFIGURACIÓN Y ESTILOS
# ══════════════════════════════════════════════
st.set_page_config(page_title="MSH-Hub | Almacén", layout="wide", page_icon="📦")

st.markdown("""
    <style>
    .kpi-title { font-size: 11px !important; font-weight: bold !important; color: #7A8B99 !important; text-align: center; margin-bottom: 5px; text-transform: uppercase; }
    .kpi-value { font-size: 32px !important; font-weight: bold !important; text-align: center; margin-top: -10px; }
    .card { background-color: white; padding: 12px; border-radius: 6px; box-shadow: 0px 1px 3px rgba(0,0,0,0.1); border: 1px solid #E2E8F0; }
    .user-info { background-color: #F0FFF4; border-left: 4px solid #38A169; padding: 8px 12px; border-radius: 4px; font-size: 13px; color: #276749; margin-bottom: 8px; }
    
    /* 💡 ESTILO GLOBAL PARA HACER RESPONSIVAS LAS VENTANAS EMERGENTES */
    div[data-testid="stDialog"] div[role="dialog"] {
        width: 85vw !important;       
        max-width: 1400px !important; 
        min-width: 320px !important;  
    }

    /* 📐 REDUCCIÓN DE ALTO Y ESPACIADOS EN VENTANAS EMERGENTES */
    div[data-testid="stDialog"] div[role="dialog"] .stVerticalBlock {
        gap: 0.4rem !important; /* Reduce el espacio vertical entre filas de componentes */
    }
    
    div[data-testid="stDialog"] div[role="dialog"] [data-testid="stWidgetLabel"] p {
        font-size: 12px !important; /* Etiquetas más pequeñas */
        margin-bottom: -2px !important; /* Acerca la etiqueta al campo de texto */
    }

    div[data-testid="stDialog"] div[role="dialog"] input, 
    div[data-testid="stDialog"] div[role="dialog"] select,
    div[data-testid="stDialog"] div[role="dialog"] div[role="combobox"] {
        height: 32px !important; /* Reduce la altura de los inputs y selectores */
        line-height: 32px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    
    div[data-testid="stDialog"] div[role="dialog"] textarea {
        padding-top: 6px !important; /* Compacta el área de texto */
    }

    div[data-testid="stDialog"] div[role="dialog"] hr {
        margin-top: 8px !important; /* Reduce la separación de las líneas divisorias */
        margin-bottom: 8px !important;
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

# ══════════════════════════════════════════════
# FUNCIONES DE BASE DE DATOS
# ══════════════════════════════════════════════
def verificar_usuario(usuario, contrasena):
    try:
        res = supabase.table("usuarios").select("*").eq("usuario", usuario).eq("contrasena", contrasena).eq("activo", True).execute()
        return res.data[0] if res.data else None
    except: return None

def registrar_acceso(usuario, nombre, accion):
    try: supabase.table("usuarios_accesos").insert({"usuario": usuario, "nombre": nombre, "accion": accion, "fecha_hora": datetime.now().isoformat()}).execute()
    except: pass

def cargar_prestamos():
    try:
        res = supabase.table("almacen_prestamos").select("*").order("created_at", desc=True).execute()
        return res.data if res.data else []
    except: return []

def agregar_prestamo(payload):
    try:
        supabase.table("almacen_prestamos").insert(payload).execute()
        return True
    except: return False

def modificar_prestamo(id_registro, payload):
    try:
        supabase.table("almacen_prestamos").update(payload).eq("id", id_registro).execute()
        return True
    except: return False

def eliminar_prestamo(id_registro):
    try:
        supabase.table("almacen_prestamos").delete().eq("id", id_registro).execute()
        return True
    except: return False

def normalizar_alerta(val):
    return 'SI' if str(val).upper().strip() in ['SI', 'TRUE', '1'] else 'NO'

# ══════════════════════════════════════════════
# DIÁLOGOS (MODALES COMPACTOS)
# ══════════════════════════════════════════════

@st.dialog("📝 Nuevo Registro de Almacén", width="large")
def ventana_nuevo_prestamo():
    col1, col2 = st.columns(2)
    with col1:
        estado = st.selectbox("Estado inicial", ["Prestado", "Asignado", "Proceso de asignacion", "Devuelto"])
        fecha = st.date_input("Fecha", value=datetime.now(), format="DD/MM/YYYY")
    with col2:
        resp = st.text_input("Responsable *")
        art = st.text_input("Artículo / Herramienta *")
    
    c3, c4 = st.columns([1, 1])
    with c3: cant = st.text_input("Cantidad", value="1")
    with c4: alerta = st.selectbox("¿Activar Alerta?", ["NO", "SI"])
    
    obs = st.text_area("Observaciones Públicas", height=65) # Alto reducido
    nota = st.text_input("Nota Interna (Opcional)")

    st.write("")
    if st.button("➕ Crear Registro", type="primary", use_container_width=True):
        if resp.strip() and art.strip() and cant.isdigit():
            payload = {
                "id": f"ID-{int(datetime.now().timestamp())}", "fecha": fecha.strftime('%d/%m/%Y'),
                "responsable": resp.strip(), "articulo": art.strip(), "cantidad": int(cant),
                "estado": estado, "observaciones": obs.strip(), "nota": nota.strip(), "alerta": alerta
            }
            if agregar_prestamo(payload):
                st.session_state["ultimo_editado"] = payload["id"]
                st.rerun()
        else: st.error("Completa los campos obligatorios (*)")

@st.dialog("✏️ Modificar Registro", width="large")
def ventana_editar_prestamo(id_reg, datos):
    try: fecha_def = datetime.strptime(str(datos.get('fecha', '')), '%d/%m/%Y')
    except: fecha_def = datetime.now()

    col1, col2 = st.columns(2)
    with col1:
        nuevo_est = st.selectbox("Estado", ["Prestado", "Devuelto", "Asignado", "Proceso de asignacion"], 
                                 index=["Prestado", "Devuelto", "Asignado", "Proceso de asignacion"].index(datos.get('estado', 'Prestado')))
        nueva_fec = st.date_input("Fecha", value=fecha_def, format="DD/MM/YYYY")
    with col2:
        nuevo_resp = st.text_input("Responsable *", value=datos.get('responsable', ''))
        nuevo_art = st.text_input("Artículo *", value=datos.get('articulo', ''))

    c3, c4 = st.columns([1, 1])
    with c3: nueva_cant = st.text_input("Cantidad", value=str(datos.get('cantidad', '1')))
    with c4: nueva_ale = st.selectbox("Alerta", ["NO", "SI"], index=(1 if datos.get('alerta') == "SI" else 0))

    nueva_obs = st.text_area("Observaciones", value=datos.get('observaciones', ''), height=65) # Alto reducido
    nueva_not = st.text_input("Nota Interna", value=datos.get('nota', ''))

    st.divider()
    c_btn1, c_btn2, c_btn3 = st.columns([1, 1, 1])
    with c_btn1:
        if st.button("💾 Guardar", type="primary", use_container_width=True):
            if nuevo_resp.strip() and nuevo_art.strip():
                payload = {
                    "fecha": nueva_fec.strftime('%d/%m/%Y'), "responsable": nuevo_resp.strip(),
                    "articulo": nuevo_art.strip(), "cantidad": int(nueva_cant), "estado": nuevo_est,
                    "observaciones": nueva_obs.strip(), "nota": nueva_not.strip(), "alerta": nueva_ale
                }
                if modificar_prestamo(id_reg, payload):
                    st.session_state["ultimo_editado"] = id_reg
                    st.rerun()
    with c_btn2:
        if st.button("🗑️ Eliminar", type="secondary", use_container_width=True):
            if eliminar_prestamo(id_reg): st.rerun()
    with c_btn3:
        if st.button("❌ Cerrar", use_container_width=True): st.rerun()

# ══════════════════════════════════════════════
# GESTIÓN DE SESIÓN Y LOGIN
# ══════════════════════════════════════════════
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if "ultimo_editado" not in st.session_state: st.session_state["ultimo_editado"] = ""
if "pagina_actual" not in st.session_state: st.session_state["pagina_actual"] = 1

if not st.session_state["autenticado"]:
    st.markdown("<div style='text-align:center; margin-top:60px;'><h1>MSH-Hub</h1><p>Mendoza Servicios y Herramientas</p></div>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 1.2, 1])
    with col_center:
        with st.container(border=True):
            st.markdown("### Acceso al Almacén")
            u_input = st.text_input("Usuario:")
            p_input = st.text_input("Contraseña:", type="password")
            if st.button("Ingresar", type="primary", use_container_width=True):
                user = verificar_usuario(u_input.strip(), p_input.strip())
                if user:
                    st.session_state.update({
                        "autenticado": True, 
                        "usuario": user["usuario"], 
                        "nombre": user["nombre"], 
                        "rol": user["rol"]
                    })
                    registrar_acceso(user["usuario"], user["nombre"], "LOGIN_SUCCESS")
                    st.rerun()
                else:
                    st.error("Credenciales inválidas o usuario inactivo")
else:
    # HEADER
    c_tit, c_user = st.columns([6, 2])
    c_tit.markdown(f"<h3 style='color:#1E3447;'>📦 MSH-Hub | Almacén</h3>", unsafe_allow_html=True)
    with c_user:
        st.markdown(f'<div class="user-info">👤 <b>{st.session_state["nombre"]}</b></div>', unsafe_allow_html=True)
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state["autenticado"] = False
            st.rerun()

    # CARGA DE DATOS
    datos = cargar_prestamos()
    df_master = pd.DataFrame(datos)
    if not df_master.empty: 
        df_master['alerta'] = df_master['alerta'].apply(normalizar_alerta)

    # INDICADORES (KPIs)
    if not df_master.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="card"><p class="kpi-title">TOTAL</p><p class="kpi-value">{len(df_master)}</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="card"><p class="kpi-title">PRESTADOS</p><p class="kpi-value" style="color:#DD6B20;">{len(df_master[df_master["estado"]=="Prestado"])}</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="card"><p class="kpi-title">DEVUELTOS</p><p class="kpi-value" style="color:#38A169;">{len(df_master[df_master["estado"]=="Devuelto"])}</p></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="card"><p class="kpi-title">ALERTAS</p><p class="kpi-value" style="color:#E53E3E;">{len(df_master[df_master["alerta"]=="SI"])}</p></div>', unsafe_allow_html=True)

    st.divider()

    # CONTROLES SUPERIORES
    col_busq, col_filtro, col_nuevo = st.columns([4, 2, 2])
    with col_busq:
        busqueda = st.text_input("🔍 Buscar...", placeholder="Responsable o Herramienta")
    with col_filtro:
        filtro_est = st.selectbox("Estado", ["Todos", "Prestado", "Devuelto", "Asignado", "Proceso de asignacion"])
    with col_nuevo:
        if st.button("➕ Nuevo Registro", type="primary", use_container_width=True):
            ventana_nuevo_prestamo()

    # FILTRADO DE DATOS
    df_f = df_master.copy()
    if filtro_est != "Todos": 
        df_f = df_f[df_f['estado'] == filtro_est]
    if busqueda:
        df_f = df_f[df_f['responsable'].str.contains(busqueda, case=False, na=False) | 
                    df_f['articulo'].str.contains(busqueda, case=False, na=False)]

    # RENDERIZADO DE TABLA
    if not df_f.empty:
        h = st.columns([1.2, 1.5, 2.5, 3.0, 0.8, 1.8, 0.5])
        titulos = ["Fecha", "Folio", "Responsable", "Artículo", "Cant.", "Estado", ""]
        for col, t in zip(h, titulos): col.markdown(f"**{t}**")

        items_per_page = 15
        total_pages = max(1, -(-len(df_f) // items_per_page))
        curr_page = st.session_state["pagina_actual"]
        df_p = df_f.iloc[(curr_page-1)*items_per_page : curr_page*items_per_page]

        for _, row in df_p.iterrows():
            id_f = row['id']
            bg = "#F0FFF4" if id_f == st.session_state["ultimo_editado"] else "transparent"
            estilo = f"background-color:{bg}; padding:5px; border-radius:4px;"
            
            c = st.columns([1.2, 1.5, 2.5, 3.0, 0.8, 1.8, 0.5])
            c[0].markdown(f"<div style='{estilo}'>{row['fecha']}</div>", unsafe_allow_html=True)
            c[1].markdown(f"<div style='{estilo}'>{id_f}</div>", unsafe_allow_html=True)
            c[2].markdown(f"<div style='{estilo}'><b>{row['responsable']}</b></div>", unsafe_allow_html=True)
            c[3].markdown(f"<div style='{estilo}'>{row['articulo']}</div>", unsafe_allow_html=True)
            c[4].markdown(f"<div style='{estilo}; text-align:center;'>{row['cantidad']}</div>", unsafe_allow_html=True)
            c[5].markdown(f"<div style='{estilo}'>{row['estado']}</div>", unsafe_allow_html=True)
            with c[6]:
                if st.button("✏️", key=f"ed_{id_f}"):
                    ventana_editar_prestamo(id_f, row)

        # PAGINACIÓN
        st.write("")
        cp1, cp2, cp3 = st.columns([1, 2, 1])
        if cp1.button("Anterior") and curr_page > 1:
            st.session_state["pagina_actual"] -= 1
            st.rerun()
        cp2.markdown(f"<p style='text-align:center;'>Página {curr_page} de {total_pages}</p>", unsafe_allow_html=True)
        if cp3.button("Siguiente") and curr_page < total_pages:
            st.session_state["pagina_actual"] += 1
            st.rerun()
    else:
        st.info("No hay registros que coincidan con la búsqueda.")