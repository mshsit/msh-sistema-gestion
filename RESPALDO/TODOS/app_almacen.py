import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, date
from fpdf import FPDF
import random
import math

# ══════════════════════════════════════════════
# CONFIGURACIÓN Y ESTILOS
# ══════════════════════════════════════════════
st.set_page_config(page_title="MSH-Hub | Almacén", layout="wide", page_icon="📦")

st.markdown("""
<style>
/* ── KPIs ── */
.kpi-card {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 8px 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07);
}

/* ── BADGES ESTADO ── */
.badge { display:inline-block; padding:2px 10px; border-radius:12px; font-size:11px; font-weight:600; }
.badge-prestado  { background:#FFF3E0; color:#E65100; }
.badge-devuelto  { background:#E8F5E9; color:#2E7D32; }
.badge-asignado  { background:#E3F2FD; color:#1565C0; }
.badge-proceso   { background:#F3E5F5; color:#6A1B9A; }

/* ── TABLA ── */
.th { font-size:11px; font-weight:700; color:#64748B; border-bottom:2px solid #E2E8F0; padding-bottom:4px; margin:0; }
.td { font-size:12px; color:#1E293B; padding:5px 4px; border-bottom:1px solid #F1F5F9; margin:0; overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }
.td-alerta { font-size:12px; color:#991B1B; font-weight:700; background:#FEE2E2; padding:5px 4px; border-bottom:1px solid #FCA5A5; border-radius:4px; margin:0; }

/* ── VENTANAS EMERGENTES OPTIMIZADAS (DIÁLOGOS) ── */
div[data-testid="stDialog"] div[role="dialog"] {
    width: 60vw !important;       
    max-width: 950px !important;  
    min-width: 380px !important;
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
}

div[data-testid="stDialog"] .stVerticalBlock {
    gap: 0.3rem !important;      
}

div[data-testid="stDialog"] [data-testid="stWidgetLabel"] p {
    font-size: 12px !important;
    margin-bottom: -4px !important;
}

div[data-testid="stDialog"] input, 
div[data-testid="stDialog"] select,
div[data-testid="stDialog"] div[role="combobox"] {
    height: 30px !important;     
}

div[data-testid="stDialog"] hr {
    margin: 0.6rem 0 !important;
}

.user-chip { background:#F0FDF4; border:1px solid #BBF7D0; border-radius:20px; padding:4px 12px; font-size:12px; color:#166534; display:inline-block; }
.dias-activo { color:#DC2626; font-weight:700; font-size:11px; }
.dias-ok     { color:#16A34A; font-size:11px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# CONEXIÓN SUPABASE
# ══════════════════════════════════════════════
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://unsugrcleytqroxuuhaf.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVuc3VncmNsZXl0cXJveHV1aGFmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk5MjkwMDcsImV4cCI6MjA5NTUwNTAwN30.7_P1zqSGX9zffIgYauzjObBjmGnpJmsfjVNOmX_Lmvc")

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
    try:
        supabase.table("usuarios_accesos").insert({
            "usuario": usuario, "nombre": nombre,
            "accion": accion, "fecha_hora": datetime.now().isoformat()
        }).execute()
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

def calcular_dias(fecha_inicio_str, fecha_fin_str="", estado=""):
    try:
        formatos = ['%d/%m/%Y', '%Y-%m-%d']
        fecha_inicio = None
        for fmt in formatos:
            try:
                fecha_inicio = datetime.strptime(str(fecha_inicio_str).strip(), fmt).date()
                break
            except: continue
        if not fecha_inicio: return None, ""
        estados_activos = ["Prestado", "Asignado", "Proceso de asignacion"]
        if fecha_fin_str and str(fecha_fin_str).strip():
            for fmt in formatos:
                try:
                    fecha_fin = datetime.strptime(str(fecha_fin_str).strip(), fmt).date()
                    return (fecha_fin - fecha_inicio).days, "ok"
                except: continue
        if estado in estados_activos:
            return (date.today() - fecha_inicio).days, "activo"
        return None, ""
    except: return None, ""

# ══════════════════════════════════════════════
# GENERADOR PDF SOLUCIONADO (CÁLCULO NATIVO DE LÍNEAS)
# ══════════════════════════════════════════════
def generar_pdf(df, nombre_usuario=""):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_margins(8, 8, 8)
    pdf.add_page()
    
    # Encabezado
    pdf.set_font("Arial", 'B', 13)
    pdf.set_text_color(30, 52, 71)
    pdf.cell(0, 7, "MSH-HUB | CONTROL DE ALMACEN - MENDOZA SERVICIOS Y HERRAMIENTAS", ln=True, align='L')
    pdf.set_font("Arial", '', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Usuario: {nombre_usuario}", ln=True, align='L')
    pdf.ln(3)
    
    widths   = [22, 22, 34, 40, 10, 26, 22, 22, 41, 42]
    columnas = ["Folio", "Fecha", "Responsable", "Articulo", "Cant", "Estado", "F.Inicio", "F.Devol.", "Observaciones", "Nota"]
    
    # Dibujar cabeceras
    pdf.set_font("Arial", 'B', 8)
    pdf.set_fill_color(30, 52, 71)
    pdf.set_text_color(255, 255, 255)
    for i, col in enumerate(columnas):
        pdf.cell(widths[i], 7, col, border=1, ln=0, align='C' if i in [4] else 'L', fill=True)
    pdf.ln()
    
    pdf.set_font("Arial", '', 7.5)
    for _, row in df.iterrows():
        en_alerta = str(row.get('alerta', 'NO')).upper() == 'SI'
        
        if en_alerta:
            pdf.set_fill_color(254, 226, 226)
            pdf.set_text_color(153, 27, 27)
        else:
            pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(0, 0, 0)
            
        valores = [
            str(row.get('id', '')).replace("ID-", ""),
            str(row.get('fecha', '')),
            str(row.get('responsable', '')),
            str(row.get('articulo', '')),
            str(row.get('cantidad', 1)),
            str(row.get('estado', '')),
            str(row.get('fecha', '')),
            str(row.get('fecha_devolucion', '')),
            str(row.get('observaciones', '')),
            str(row.get('nota', ''))
        ]
        
        # ── CAMBIO CLAVE: Cálculo nativo reemplazando nb_lines ──
        lineas_por_celda = []
        for texto, ancho in zip(valores, widths):
            if not texto.strip():
                lineas_por_celda.append(1)
            else:
                # Calculamos el ancho del texto en mm y dejamos un margen de tolerancia (2mm) para bordes de la celda
                ancho_texto = pdf.get_string_width(texto)
                ancho_disponible = ancho - 2
                # math.ceil redondea hacia arriba el número de líneas necesarias
                lineas = math.ceil(ancho_texto / ancho_disponible) if ancho_disponible > 0 else 1
                lineas_por_celda.append(max(1, lineas))
            
        max_lineas = max(lineas_por_celda)
        base_alt_linea = 5  
        altura_fila = max_lineas * base_alt_linea
        
        if pdf.get_y() + altura_fila > 200:
            pdf.add_page()
            pdf.set_font("Arial", 'B', 8)
            pdf.set_fill_color(30, 52, 71)
            pdf.set_text_color(255, 255, 255)
            for i, col in enumerate(columnas):
                pdf.cell(widths[i], 7, col, border=1, ln=0, align='C' if i in [4] else 'L', fill=True)
            pdf.ln()
            pdf.set_font("Arial", '', 7.5)
            if en_alerta:
                pdf.set_fill_color(254, 226, 226)
                pdf.set_text_color(153, 27, 27)
            else:
                pdf.set_fill_color(255, 255, 255)
                pdf.set_text_color(0, 0, 0)

        x_inicial = pdf.get_x()
        y_inicial = pdf.get_y()
        
        for i, (texto, ancho) in enumerate(zip(valores, widths)):
            align = 'C' if i in [0, 1, 4, 6, 7] else 'L'
            pdf.set_xy(x_inicial, y_inicial)
            
            # Repartimos la altura total de forma proporcional
            pdf.multi_cell(ancho, altura_fila / lineas_por_celda[i], texto, border=1, align=align, fill=True)
            x_inicial += ancho
            
        pdf.set_xy(8, y_inicial + altura_fila)
        
    return pdf.output(dest='S').encode('latin-1', errors='ignore')

# ══════════════════════════════════════════════
# VENTANAS EMERGENTES (DIÁLOGOS COMPACTOS)
# ══════════════════════════════════════════════
@st.dialog("📝 Nuevo Registro de Préstamo", width="large")
def ventana_nuevo_prestamo():
    col1, col2, col3 = st.columns(3)
    with col1:
        fecha  = st.date_input("Fecha *", value=datetime.now(), format="DD/MM/YYYY")
        resp = st.text_input("Responsable *", placeholder="Nombre")
    with col2:
        estado = st.selectbox("Estado *", ["Prestado", "Asignado", "Proceso de asignacion", "Devuelto"])
        art  = st.text_input("Artículo *", placeholder="Herramienta")
    with col3:
        cant   = st.text_input("Cantidad *", value="1")
        alerta = st.selectbox("¿Alerta?", ["NO", "SI"])

    c_obs, c_fdev = st.columns([2, 1])
    with c_obs:
        obs  = st.text_input("Observaciones", placeholder="Descripción opcional")
    with c_fdev:
        fecha_dev = st.date_input("Fecha Devolución", value=datetime.now(), format="DD/MM/YYYY")

    nota = st.text_input("Nota Interna (Admin)", placeholder="Solo visible para administradores")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Crear Registro", type="primary", use_container_width=True):
            if not resp.strip() or not art.strip() or not cant.isdigit():
                st.error("Por favor completa los campos obligatorios (*)")
            else:
                folio_corto = f"ID-{random.randint(10000, 99999)}"
                payload = {
                    "id": folio_corto,
                    "fecha": fecha.strftime('%d/%m/%Y'),
                    "responsable": resp.strip(), "articulo": art.strip(),
                    "cantidad": int(cant), "estado": estado,
                    "observaciones": obs.strip(), "nota": nota.strip(),
                    "alerta": alerta, "fecha_devolucion": fecha_dev.strftime('%d/%m/%Y') if estado in ["Devuelto", "Asignado"] else ""
                }
                if agregar_prestamo(payload):
                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"AGREGAR: {payload['id']}")
                    st.session_state["ultimo_editado"] = payload["id"]
                    st.rerun()
    with c2:
        if st.button("❌ Cancelar", use_container_width=True): st.rerun()

@st.dialog("✏️ Modificar Registro", width="large")
def ventana_editar_prestamo(id_reg, datos):
    folio_visual = str(id_reg).replace("ID-", "")
    st.markdown(f"**Folio:** `{folio_visual}`")
    try: fecha_def = datetime.strptime(str(datos.get('fecha', '')), '%d/%m/%Y')
    except: fecha_def = datetime.now()

    col1, col2, col3 = st.columns(3)
    with col1:
        nueva_fec  = st.date_input("Fecha *", value=fecha_def, format="DD/MM/YYYY")
        nuevo_resp = st.text_input("Responsable *", value=datos.get('responsable', ''))
    with col2:
        estados_op = ["Prestado", "Devuelto", "Asignado", "Proceso de asignacion"]
        est_idx    = estados_op.index(datos.get('estado', 'Prestado')) if datos.get('estado') in estados_op else 0
        nuevo_est  = st.selectbox("Estado *", estados_op, index=est_idx)
        nuevo_art  = st.text_input("Artículo *",    value=datos.get('articulo', ''))
    with col3:
        nueva_cant = st.text_input("Cantidad *", value=str(datos.get('cantidad', '1')))
        ale_idx    = 1 if normalizar_alerta(datos.get('alerta', 'NO')) == "SI" else 0
        nueva_ale  = st.selectbox("Alerta", ["NO", "SI"], index=ale_idx)

    try: fdev_def = datetime.strptime(str(datos.get('fecha_devolucion', '')), '%d/%m/%Y') if datos.get('fecha_devolucion') else datetime.now()
    except: fdev_def = datetime.now()

    c_obs, c_fdev = st.columns([2, 1])
    with c_obs:
        nueva_obs = st.text_input("Observaciones", value=datos.get('observaciones', ''))
    with c_fdev:
        nueva_fdev = st.date_input("F. Devolución", value=fdev_def, format="DD/MM/YYYY")
        
    nueva_not = st.text_input("Nota Interna",  value=datos.get('nota', ''))

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💾 Guardar Cambios", type="primary", use_container_width=True):
            payload = {
                "fecha": nueva_fec.strftime('%d/%m/%Y'), "responsable": nuevo_resp.strip(), 
                "articulo": nuevo_art.strip(), "cantidad": int(nueva_cant) if nueva_cant.isdigit() else 1, 
                "estado": nuevo_est, "observaciones": nueva_obs.strip(), "nota": nueva_not.strip(),
                "alerta": nueva_ale, "fecha_devolucion": nueva_fdev.strftime('%d/%m/%Y')
            }
            if modificar_prestamo(id_reg, payload):
                registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"MODIFICAR: {id_reg}")
                st.session_state["ultimo_editado"] = id_reg
                st.rerun()
    with c2:
        if st.button("🗑️ Eliminar Registro", use_container_width=True):
            if eliminar_prestamo(id_reg):
                registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"ELIMINAR: {id_reg}")
                st.session_state["ultimo_editado"] = ""
                st.rerun()
    with c3:
        if st.button("❌ Cerrar", use_container_width=True): st.rerun()

# ══════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════
if "autenticado"    not in st.session_state: st.session_state["autenticado"]    = False
if "ultimo_editado" not in st.session_state: st.session_state["ultimo_editado"] = ""
if "pagina_actual"  not in st.session_state: st.session_state["pagina_actual"]  = 1

# ══════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════
if not st.session_state["autenticado"]:
    st.markdown("""
        <div style='text-align:center; margin-top:60px;'>
            <h1 style='color:#1E3447; font-size:36px;'>📦 MSH-Hub</h1>
            <p style='color:#94A3B8; font-size:15px;'>Mendoza Servicios y Herramientas</p>
        </div>
    """, unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 1.2, 1])
    with col_center:
        with st.container(border=True):
            st.markdown("#### 🔒 Acceso al Sistema")
            u_input = st.text_input("Usuario:", placeholder="tu.usuario")
            p_input = st.text_input("Contraseña:", type="password", placeholder="••••••••")
            if st.button("Ingresar al Sistema", type="primary", use_container_width=True):
                user = verificar_usuario(u_input.strip(), p_input.strip())
                if user:
                    st.session_state.update({"autenticado": True, "usuario": user["usuario"], "nombre":  user["nombre"], "rol": user["rol"]})
                    registrar_acceso(user["usuario"], user["nombre"], "LOGIN")
                    st.rerun()
                else: st.error("Usuario o contraseña incorrectos.")

# ══════════════════════════════════════════════
# DASHBOARD PRINCIPAL
# ══════════════════════════════════════════════
else:
    usuario_actual = st.session_state["usuario"]
    nombre_actual  = st.session_state["nombre"]
    rol_actual     = st.session_state["rol"]
    es_admin       = rol_actual == "admin"

    # ── HEADER ──
    c_tit, c_user, c_logout = st.columns([5, 2, 1])
    c_tit.markdown("<h4 style='color:#1E3447; margin:8px 0 0 0;'>📦 MSH-Hub | Control de Almacén</h4>", unsafe_allow_html=True)
    c_user.markdown(f"<div style='margin-top:10px;'><span class='user-chip'>👤 <b>{nombre_actual}</b> · {rol_actual.upper()}</span></div>", unsafe_allow_html=True)
    if c_logout.button("🚪 Salir", use_container_width=True):
        registrar_acceso(usuario_actual, nombre_actual, "LOGOUT")
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

    df_master = pd.DataFrame(cargar_prestamos())
    if not df_master.empty and 'alerta' in df_master.columns:
        df_master['alerta'] = df_master['alerta'].apply(normalizar_alerta)

    # ── KPIs ──
    total   = len(df_master) if not df_master.empty else 0
    prest   = len(df_master[df_master['estado'] == 'Prestado'])              if not df_master.empty else 0
    devuel  = len(df_master[df_master['estado'] == 'Devuelto'])              if not df_master.empty else 0
    asign   = len(df_master[df_master['estado'] == 'Asignado'])              if not df_master.empty else 0
    proceso = len(df_master[df_master['estado'] == 'Proceso de asignacion']) if not df_master.empty else 0
    alertas = len(df_master[df_master['alerta'] == 'SI'])                    if not df_master.empty else 0

    st.write("")
    st.write("")

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    s = "display:flex;align-items:center;justify-content:space-between;background:white;padding:8px 14px;border-radius:8px;border:1px solid #E2E8F0;box-shadow:0 1px 3px rgba(0,0,0,0.07);"
    k1.markdown(f'<div style="{s}"><span style="font-size:10px;font-weight:700;color:#94A3B8;">TOTAL</span><span style="font-size:22px;font-weight:800;">{total}</span></div>', unsafe_allow_html=True)
    k2.markdown(f'<div style="{s}"><span style="font-size:10px;font-weight:700;color:#EA580C;">PRESTADOS</span><span style="font-size:22px;font-weight:800;color:#EA580C;">{prest}</span></div>', unsafe_allow_html=True)
    k3.markdown(f'<div style="{s}"><span style="font-size:10px;font-weight:700;color:#16A34A;">DEVUELTOS</span><span style="font-size:22px;font-weight:800;color:#16A34A;">{devuel}</span></div>', unsafe_allow_html=True)
    k4.markdown(f'<div style="{s}"><span style="font-size:10px;font-weight:700;color:#2563EB;">ASIGNADOS</span><span style="font-size:22px;font-weight:800;color:#2563EB;">{asign}</span></div>', unsafe_allow_html=True)
    k5.markdown(f'<div style="{s}"><span style="font-size:10px;font-weight:700;color:#7C3AED;">PROCESO</span><span style="font-size:22px;font-weight:800;color:#7C3AED;">{proceso}</span></div>', unsafe_allow_html=True)
    k6.markdown(f'<div style="{s}"><span style="font-size:10px;font-weight:700;color:#DC2626;">ALERTAS</span><span style="font-size:22px;font-weight:800;color:#DC2626;">{alertas}</span></div>', unsafe_allow_html=True)

    st.write("")
    st.write("")

    # ── CONTROLES ORIGINALES LIMPIOS ──
    c_busq, c_filt, c_acc1, c_acc2, c_acc3 = st.columns([3.5, 2.5, 1.2, 1.2, 1.2])
    with c_busq: busqueda = st.text_input("Buscar", placeholder="🔍 Buscar responsable, artículo o folio...", label_visibility="collapsed")
    with c_filt: filtro_est = st.selectbox("Filtro", ["Todos", "Prestado", "Devuelto", "Asignado", "Proceso de asignacion", "🚨 En Alerta"], label_visibility="collapsed")
    with c_acc1: 
        if not df_master.empty: st.download_button("📥 CSV", data=df_master.to_csv(index=False).encode('utf-8'), file_name="almacen.csv", mime="text/csv", use_container_width=True)
    with c_acc2: 
        if not df_master.empty: st.download_button("📕 PDF", data=generar_pdf(df_master, nombre_actual), file_name="reporte.pdf", mime="application/pdf", use_container_width=True)
    with c_acc3: 
        if es_admin and st.button("➕ Nuevo", type="primary", use_container_width=True): ventana_nuevo_prestamo()

    # ── FILTRADO Y TABLA PAGINADA ──
    df_f = df_master.copy() if not df_master.empty else pd.DataFrame()
    if not df_f.empty:
        if busqueda.strip():
            df_f = df_f[df_f['responsable'].str.contains(busqueda, case=False, na=False) | df_f['articulo'].str.contains(busqueda, case=False, na=False) | df_f['id'].str.contains(busqueda, case=False, na=False)]
        if filtro_est == "🚨 En Alerta": df_f = df_f[df_f['alerta'] == 'SI']
        elif filtro_est != "Todos": df_f = df_f[df_f['estado'] == filtro_est]

    if not df_f.empty:
        IPP = 15
        total_filas = len(df_f)
        total_pags = max(1, -(-total_filas // IPP))
        
        if busqueda != st.session_state.get("ub", "") or filtro_est != st.session_state.get("uf", ""):
            st.session_state["pagina_actual"] = 1
            st.session_state["ub"], st.session_state["uf"] = busqueda, filtro_est

        pag = st.session_state["pagina_actual"]
        df_pag = df_f.iloc[(pag - 1) * IPP : pag * IPP]

        cw = [1.1, 1.2, 2.4, 2.6, 0.6, 1.8, 1.3, 0.55] if es_admin else [1.1, 1.2, 2.4, 2.6, 0.6, 1.8, 1.3]
        ths = ["Fecha", "Folio", "Responsable", "Artículo", "Cant.", "Estado", "Días", ""] if es_admin else ["Fecha", "Folio", "Responsable", "Artículo", "Cant.", "Estado", "Días"]

        h_cols = st.columns(cw)
        for col, txt in zip(h_cols, ths): col.markdown(f"<p class='th'>{txt}</p>", unsafe_allow_html=True)

        for _, row in df_pag.iterrows():
            id_f = row['id']
            folio_corto = str(id_f).replace("ID-", "")
            
            en_alerta = str(row.get('alerta', 'NO')).upper() == 'SI'
            es_ult = id_f == st.session_state.get("ultimo_editado", "")
            bg = "#FEF2F2" if en_alerta else ("#F0FDF4" if es_ult else "transparent")
            cls = "td-alerta" if en_alerta else "td"
            s_row = f"background:{bg};"

            r = st.columns(cw)
            r[0].markdown(f"<div class='{cls}' style='{s_row}'>{row.get('fecha','')}</div>", unsafe_allow_html=True)
            r[1].markdown(f"<div class='{cls}' style='{s_row}'>{folio_corto}</div>", unsafe_allow_html=True)
            r[2].markdown(f"<div class='{cls}' style='{s_row}'><b>{row.get('responsable','')}</b></div>", unsafe_allow_html=True)
            r[3].markdown(f"<div class='{cls}' style='{s_row}'>{row.get('articulo','')}</div>", unsafe_allow_html=True)
            r[4].markdown(f"<div class='{cls}' style='{s_row}; text-align:center;'>{row.get('cantidad',1)}</div>", unsafe_allow_html=True)
            
            est = row.get('estado', 'Prestado')
            badge_map = {"Prestado": "badge-prestado", "Devuelto": "badge-devuelto", "Asignado": "badge-asignado"}
            r[5].markdown(f"<div class='{cls}' style='{s_row}'><span class='badge {badge_map.get(est, 'badge-proceso')}'>{est}</span></div>", unsafe_allow_html=True)
            
            d, tipo = calcular_dias(row.get('fecha',''), row.get('fecha_devolucion',''), est)
            dias_html = f"<span class='dias-activo'>⏱ {d}d</span>" if tipo == "activo" else (f"<span class='dias-ok'>✓ {d}d</span>" if d else "—")
            r[6].markdown(f"<div class='{cls}' style='{s_row}'>{dias_html}</div>", unsafe_allow_html=True)

            if es_admin:
                with r[7]:
                    if st.button("✏️", key=f"ed_{id_f}", help="Editar registro", use_container_width=True): ventana_editar_prestamo(id_f, row.to_dict())

        # Paginación Controles
        st.write("")
        p1, p2, p3, p4, p5 = st.columns([1, 1, 3, 1, 1])
        with p1: 
            if st.button("⏮ Primera", disabled=(pag == 1), use_container_width=True): st.session_state["pagina_actual"] = 1; st.rerun()
        with p2: 
            if st.button("◀ Anterior", disabled=(pag == 1), use_container_width=True): st.session_state["pagina_actual"] -= 1; st.rerun()
        p3.markdown(f"<p style='text-align:center;color:#94A3B8;font-size:12px;'>Página <b>{pag}</b> de <b>{total_pags}</b> · <b>{total_filas}</b> registros</p>", unsafe_allow_html=True)
        with p4: 
            if st.button("Siguiente ▶", disabled=(pag == total_pags), use_container_width=True): st.session_state["pagina_actual"] += 1; st.rerun()
        with p5: 
            if st.button("Última ⏭", disabled=(pag == total_pags), use_container_width=True): st.session_state["pagina_actual"] = total_pags; st.rerun()
    else:
        st.info("No se encontraron registros.")