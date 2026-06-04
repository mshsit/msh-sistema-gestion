import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, date
from fpdf import FPDF

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
.kpi-label { font-size: 10px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: .5px; }
.kpi-num   { font-size: 22px; font-weight: 800; line-height: 1; }

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
.td-selected { background:#EFF6FF; border-left:3px solid #3B82F6; }

/* ── USER INFO ── */
.user-chip { background:#F0FDF4; border:1px solid #BBF7D0; border-radius:20px; padding:4px 12px; font-size:12px; color:#166534; display:inline-block; }

/* ── DIAS ── */
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
# GENERADOR PDF
# ══════════════════════════════════════════════
def generar_pdf(df, nombre_usuario=""):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_margins(8, 8, 8)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 13)
    pdf.set_text_color(30, 52, 71)
    pdf.cell(0, 7, "MSH-HUB | CONTROL DE ALMACEN - MENDOZA SERVICIOS Y HERRAMIENTAS", ln=True, align='L')
    pdf.set_font("Arial", '', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Usuario: {nombre_usuario}", ln=True, align='L')
    pdf.ln(3)
    widths   = [28, 22, 36, 42, 10, 28, 22, 22, 50, 12]
    columnas = ["Folio", "Fecha", "Responsable", "Articulo", "Cant", "Estado", "F.Inicio", "F.Devol.", "Observaciones", "Alerta"]
    pdf.set_font("Arial", 'B', 8)
    pdf.set_fill_color(30, 52, 71)
    pdf.set_text_color(255, 255, 255)
    for i, col in enumerate(columnas):
        pdf.cell(widths[i], 7, col, border=1, ln=0, align='C' if i in [4, 9] else 'L', fill=True)
    pdf.ln()
    for _, row in df.iterrows():
        en_alerta = str(row.get('alerta', 'NO')).upper() == 'SI'
        if en_alerta:
            pdf.set_fill_color(254, 226, 226); pdf.set_text_color(153, 27, 27); fondo = True
        else:
            pdf.set_text_color(0, 0, 0); fondo = False
        def celda(texto, ancho, align='L'):
            t = str(texto) if texto else ""
            pdf.set_font("Arial", '', 5.5 if len(t) * 4.5 / 2.834 > (ancho - 1) else 7.5)
            pdf.cell(ancho, 6, t, 1, 0, align, fondo)
        celda(row.get('id', ''),              widths[0])
        celda(row.get('fecha', ''),            widths[1], 'C')
        celda(row.get('responsable', ''),      widths[2])
        celda(row.get('articulo', ''),         widths[3])
        celda(str(row.get('cantidad', 1)),     widths[4], 'C')
        celda(row.get('estado', ''),           widths[5])
        celda(row.get('fecha', ''),            widths[6], 'C')
        celda(row.get('fecha_devolucion', ''), widths[7], 'C')
        celda(row.get('observaciones', ''),    widths[8])
        pdf.set_font("Arial", '', 7.5)
        pdf.cell(widths[9], 6, "SI" if en_alerta else "NO", 1, 0, 'C', fondo)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1', errors='ignore')

# ══════════════════════════════════════════════
# VENTANAS EMERGENTES (DIALOGS)
# ══════════════════════════════════════════════
@st.dialog("📝 Nuevo Registro de Préstamo")
def ventana_nuevo_prestamo():
    col1, col2 = st.columns(2)
    with col1:
        fecha  = st.date_input("Fecha *", value=datetime.now(), format="DD/MM/YYYY")
        estado = st.selectbox("Estado *", ["Prestado", "Asignado", "Proceso de asignacion", "Devuelto"])
        cant   = st.text_input("Cantidad *", value="1")
    with col2:
        resp = st.text_input("Responsable *", placeholder="Nombre del trabajador")
        art  = st.text_input("Artículo / Herramienta *", placeholder="Nombre del artículo")
        alerta = st.selectbox("¿Activar Alerta?", ["NO", "SI"])

    if estado in ["Devuelto", "Asignado"]:
        fecha_dev = st.date_input("Fecha de Devolución / Asignación", value=datetime.now(), format="DD/MM/YYYY")
        fecha_dev_str = fecha_dev.strftime('%d/%m/%Y')
    else:
        fecha_dev_str = ""

    obs  = st.text_area("Observaciones", placeholder="Descripción opcional", height=80)
    nota = st.text_input("Nota Interna", placeholder="Solo visible para administradores")

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Crear Registro", type="primary", use_container_width=True):
            errores = []
            if not resp.strip() or len(resp.strip()) < 3:
                errores.append("Responsable debe tener al menos 3 caracteres.")
            if not art.strip() or len(art.strip()) < 2:
                errores.append("Artículo debe tener al menos 2 caracteres.")
            if not cant.isdigit() or int(cant) <= 0:
                errores.append("Cantidad debe ser un número mayor a 0.")
            if fecha > datetime.now().date():
                errores.append("La fecha no puede ser futura.")
            if errores:
                for e in errores: st.error(e)
            else:
                payload = {
                    "id": f"ID-{int(datetime.now().timestamp())}",
                    "fecha": fecha.strftime('%d/%m/%Y'),
                    "responsable": resp.strip(), "articulo": art.strip(),
                    "cantidad": int(cant), "estado": estado,
                    "observaciones": obs.strip(), "nota": nota.strip(),
                    "alerta": alerta, "fecha_devolucion": fecha_dev_str
                }
                if agregar_prestamo(payload):
                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"AGREGAR: {payload['id']}")
                    st.session_state["ultimo_editado"] = payload["id"]
                    st.success("¡Registro creado!")
                    st.rerun()
                else:
                    st.error("Error al guardar. Intenta de nuevo.")
    with c2:
        if st.button("❌ Cancelar", use_container_width=True):
            st.rerun()

@st.dialog("✏️ Modificar Registro")
def ventana_editar_prestamo(id_reg, datos):
    st.markdown(f"**Folio:** `{id_reg}`")
    st.divider()
    try: fecha_def = datetime.strptime(str(datos.get('fecha', '')), '%d/%m/%Y')
    except: fecha_def = datetime.now()

    col1, col2 = st.columns(2)
    with col1:
        nueva_fec  = st.date_input("Fecha *", value=fecha_def, format="DD/MM/YYYY")
        estados_op = ["Prestado", "Devuelto", "Asignado", "Proceso de asignacion"]
        est_idx    = estados_op.index(datos.get('estado', 'Prestado')) if datos.get('estado') in estados_op else 0
        nuevo_est  = st.selectbox("Estado *", estados_op, index=est_idx)
        nueva_cant = st.text_input("Cantidad *", value=str(datos.get('cantidad', '1')))
    with col2:
        nuevo_resp = st.text_input("Responsable *", value=datos.get('responsable', ''))
        nuevo_art  = st.text_input("Artículo *",    value=datos.get('articulo', ''))
        ale_idx    = 1 if normalizar_alerta(datos.get('alerta', 'NO')) == "SI" else 0
        nueva_ale  = st.selectbox("Alerta", ["NO", "SI"], index=ale_idx)

    # Fecha devolución
    fdev_val = str(datos.get('fecha_devolucion', ''))
    try: fdev_def = datetime.strptime(fdev_val, '%d/%m/%Y') if fdev_val else datetime.now()
    except: fdev_def = datetime.now()
    nueva_fdev = st.date_input("Fecha Devolución / Asignación (si aplica)", value=fdev_def, format="DD/MM/YYYY")

    nueva_obs = st.text_area("Observaciones", value=datos.get('observaciones', ''), height=80)
    nueva_not = st.text_input("Nota Interna",  value=datos.get('nota', ''))

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💾 Guardar Cambios", type="primary", use_container_width=True):
            errores = []
            if not nuevo_resp.strip() or len(nuevo_resp.strip()) < 3:
                errores.append("Responsable debe tener al menos 3 caracteres.")
            if not nuevo_art.strip() or len(nuevo_art.strip()) < 2:
                errores.append("Artículo debe tener al menos 2 caracteres.")
            if not nueva_cant.isdigit() or int(nueva_cant) <= 0:
                errores.append("Cantidad debe ser número mayor a 0.")
            if errores:
                for e in errores: st.error(e)
            else:
                payload = {
                    "fecha": nueva_fec.strftime('%d/%m/%Y'),
                    "responsable": nuevo_resp.strip(), "articulo": nuevo_art.strip(),
                    "cantidad": int(nueva_cant), "estado": nuevo_est,
                    "observaciones": nueva_obs.strip(), "nota": nueva_not.strip(),
                    "alerta": nueva_ale,
                    "fecha_devolucion": nueva_fdev.strftime('%d/%m/%Y')
                }
                if modificar_prestamo(id_reg, payload):
                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"MODIFICAR: {id_reg}")
                    st.session_state["ultimo_editado"] = id_reg
                    st.success("¡Cambios guardados!")
                    st.rerun()
                else:
                    st.error("Error al guardar.")
    with c2:
        if st.button("🗑️ Eliminar Registro", type="secondary", use_container_width=True):
            if eliminar_prestamo(id_reg):
                registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"ELIMINAR: {id_reg}")
                st.session_state["ultimo_editado"] = ""
                st.success("Registro eliminado.")
                st.rerun()
    with c3:
        if st.button("❌ Cerrar", use_container_width=True):
            st.rerun()

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
            st.write("")
            if st.button("Ingresar al Sistema", type="primary", use_container_width=True):
                if u_input.strip() and p_input.strip():
                    user = verificar_usuario(u_input.strip(), p_input.strip())
                    if user:
                        st.session_state.update({
                            "autenticado": True,
                            "usuario": user["usuario"],
                            "nombre":  user["nombre"],
                            "rol":     user["rol"]
                        })
                        registrar_acceso(user["usuario"], user["nombre"], "LOGIN")
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos.")
                else:
                    st.warning("Completa los campos de acceso.")

# ══════════════════════════════════════════════
# DASHBOARD PRINCIPAL
# ══════════════════════════════════════════════
else:
    usuario_actual = st.session_state["usuario"]
    nombre_actual  = st.session_state["nombre"]
    rol_actual     = st.session_state["rol"]
    es_admin       = rol_actual == "admin"

    # ── HEADER ──────────────────────────────────────────────────────────────
    c_tit, c_user, c_logout = st.columns([5, 2, 1])
    with c_tit:
        st.markdown("<h4 style='color:#1E3447; margin:8px 0 0 0;'>📦 MSH-Hub | Control de Almacén</h4>", unsafe_allow_html=True)
    with c_user:
        st.markdown(f"<div style='margin-top:10px;'><span class='user-chip'>👤 <b>{nombre_actual}</b> · {rol_actual.upper()}</span></div>", unsafe_allow_html=True)
    with c_logout:
        st.write("")
        if st.button("🚪 Salir", use_container_width=True, key="btn_logout"):
            registrar_acceso(usuario_actual, nombre_actual, "LOGOUT")
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

    # ── CARGA DE DATOS ───────────────────────────────────────────────────────
    with st.spinner("Cargando datos..."):
        datos     = cargar_prestamos()
        df_master = pd.DataFrame(datos)

    if not df_master.empty and 'alerta' in df_master.columns:
        df_master['alerta'] = df_master['alerta'].apply(normalizar_alerta)

    # ── KPIs ─────────────────────────────────────────────────────────────────
    total    = len(df_master)
    prest    = len(df_master[df_master['estado'] == 'Prestado'])              if not df_master.empty else 0
    devuel   = len(df_master[df_master['estado'] == 'Devuelto'])              if not df_master.empty else 0
    asign    = len(df_master[df_master['estado'] == 'Asignado'])              if not df_master.empty else 0
    proceso  = len(df_master[df_master['estado'] == 'Proceso de asignacion']) if not df_master.empty else 0
    alertas  = len(df_master[df_master['alerta'] == 'SI'])                    if not df_master.empty else 0

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    s = "display:flex;align-items:center;justify-content:space-between;background:white;padding:8px 14px;border-radius:8px;border:1px solid #E2E8F0;box-shadow:0 1px 3px rgba(0,0,0,0.07);"
    with k1: st.markdown(f'<div style="{s}"><span style="font-size:10px;font-weight:700;color:#94A3B8;text-transform:uppercase;">Total</span><span style="font-size:22px;font-weight:800;color:#1E293B;">{total}</span></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div style="{s}"><span style="font-size:10px;font-weight:700;color:#94A3B8;text-transform:uppercase;">Prestados</span><span style="font-size:22px;font-weight:800;color:#EA580C;">{prest}</span></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div style="{s}"><span style="font-size:10px;font-weight:700;color:#94A3B8;text-transform:uppercase;">Devueltos</span><span style="font-size:22px;font-weight:800;color:#16A34A;">{devuel}</span></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div style="{s}"><span style="font-size:10px;font-weight:700;color:#94A3B8;text-transform:uppercase;">Asignados</span><span style="font-size:22px;font-weight:800;color:#2563EB;">{asign}</span></div>', unsafe_allow_html=True)
    with k5: st.markdown(f'<div style="{s}"><span style="font-size:10px;font-weight:700;color:#94A3B8;text-transform:uppercase;">En Proceso</span><span style="font-size:22px;font-weight:800;color:#7C3AED;">{proceso}</span></div>', unsafe_allow_html=True)
    with k6: st.markdown(f'<div style="{s}"><span style="font-size:10px;font-weight:700;color:#94A3B8;text-transform:uppercase;">En Alerta</span><span style="font-size:22px;font-weight:800;color:#DC2626;">{alertas}</span></div>', unsafe_allow_html=True)

    st.write("")

    # ── CONTROLES: BÚSQUEDA + FILTROS + BOTONES ──────────────────────────────
    c_busq, c_filt, c_acc1, c_acc2, c_acc3 = st.columns([3.5, 2.5, 1.2, 1.2, 1.2])
    with c_busq:
        busqueda = st.text_input("Buscar", placeholder="🔍  Responsable, artículo o folio...", label_visibility="collapsed")
    with c_filt:
        opciones_filtro = ["Todos", "Prestado", "Devuelto", "Asignado", "Proceso de asignacion", "🚨 En Alerta"]
        filtro_est = st.selectbox("Filtro", opciones_filtro, label_visibility="collapsed")
    with c_acc1:
        if not df_master.empty:
            st.download_button("📥 CSV", data=df_master.to_csv(index=False).encode('utf-8'),
                               file_name="almacen_prestamos.csv", mime="text/csv", use_container_width=True)
    with c_acc2:
        if not df_master.empty:
            st.download_button("📕 PDF", data=generar_pdf(df_master, nombre_actual),
                               file_name="reporte_almacen.pdf", mime="application/pdf", use_container_width=True)
    with c_acc3:
        if es_admin:
            if st.button("➕ Nuevo", type="primary", use_container_width=True):
                ventana_nuevo_prestamo()

    # ── FILTRADO ─────────────────────────────────────────────────────────────
    df_f = df_master.copy() if not df_master.empty else pd.DataFrame()

    if not df_f.empty:
        if busqueda.strip():
            df_f = df_f[
                df_f['responsable'].str.contains(busqueda, case=False, na=False) |
                df_f['articulo'].str.contains(busqueda, case=False, na=False)    |
                df_f['id'].str.contains(busqueda, case=False, na=False)
            ]
        if filtro_est == "🚨 En Alerta":
            df_f = df_f[df_f['alerta'] == 'SI']
        elif filtro_est != "Todos":
            df_f = df_f[df_f['estado'] == filtro_est]

    # ── TABLA ────────────────────────────────────────────────────────────────
    if not df_f.empty:

        # Paginación
        IPP         = 15
        total_filas = len(df_f)
        total_pags  = max(1, -(-total_filas // IPP))

        if busqueda != st.session_state.get("ub", "") or filtro_est != st.session_state.get("uf", ""):
            st.session_state["pagina_actual"] = 1
            st.session_state["ub"] = busqueda
            st.session_state["uf"] = filtro_est

        pag      = st.session_state["pagina_actual"]
        df_pag   = df_f.iloc[(pag - 1) * IPP : pag * IPP]

        # Encabezados
        if es_admin:
            cw = [1.3, 1.5, 2.2, 2.5, 0.7, 1.8, 1.4, 0.55]
            ths = ["Fecha", "Folio", "Responsable", "Artículo", "Cant.", "Estado", "Días", ""]
        else:
            cw = [1.3, 1.5, 2.2, 2.5, 0.7, 1.8, 1.4]
            ths = ["Fecha", "Folio", "Responsable", "Artículo", "Cant.", "Estado", "Días"]

        h_cols = st.columns(cw)
        for col, txt in zip(h_cols, ths):
            col.markdown(f"<p class='th'>{txt}</p>", unsafe_allow_html=True)

        # Filas
        for _, row in df_pag.iterrows():
            id_f      = row['id']
            en_alerta = str(row.get('alerta', 'NO')).upper() == 'SI'
            es_ult    = id_f == st.session_state.get("ultimo_editado", "")

            bg    = "#FEF2F2" if en_alerta else ("#F0FDF4" if es_ult else "transparent")
            cls   = "td-alerta" if en_alerta else "td"

            # Badge estado
            est = row.get('estado', '')
            if est == "Prestado":
                est_html = f"<span class='badge badge-prestado'>{est}</span>"
            elif est == "Devuelto":
                est_html = f"<span class='badge badge-devuelto'>{est}</span>"
            elif est == "Asignado":
                est_html = f"<span class='badge badge-asignado'>{est}</span>"
            else:
                est_html = f"<span class='badge badge-proceso'>{est}</span>"

            # Días
            dias, tipo = calcular_dias(row.get('fecha',''), row.get('fecha_devolucion',''), est)
            if dias is not None:
                if tipo == "activo":
                    dias_html = f"<span class='dias-activo'>⏱ {dias}d</span>"
                else:
                    dias_html = f"<span class='dias-ok'>✓ {dias}d</span>"
            else:
                dias_html = "<span style='color:#CBD5E0;'>—</span>"

            s = f"background:{bg};"
            r = st.columns(cw)
            r[0].markdown(f"<div class='{cls}' style='{s}'>{row.get('fecha','')}</div>", unsafe_allow_html=True)
            r[1].markdown(f"<div class='{cls}' style='{s}'>{str(id_f)[:14]}</div>", unsafe_allow_html=True)
            r[2].markdown(f"<div class='{cls}' style='{s}'><b>{row.get('responsable','')}</b></div>", unsafe_allow_html=True)
            r[3].markdown(f"<div class='{cls}' style='{s}'>{row.get('articulo','')}</div>", unsafe_allow_html=True)
            r[4].markdown(f"<div class='{cls}' style='{s}; text-align:center;'>{row.get('cantidad',1)}</div>", unsafe_allow_html=True)
            r[5].markdown(f"<div class='{cls}' style='{s}'>{est_html}</div>", unsafe_allow_html=True)
            r[6].markdown(f"<div class='{cls}' style='{s}'>{dias_html}</div>", unsafe_allow_html=True)

            if es_admin:
                with r[7]:
                    if st.button("✏️", key=f"ed_{id_f}", help="Editar registro", use_container_width=True):
                        ventana_editar_prestamo(id_f, row.to_dict())

        # ── CONTROLES PAGINACIÓN ─────────────────────────────────────────────
        st.write("")
        p1, p2, p3, p4, p5 = st.columns([1, 1, 3, 1, 1])
        with p1:
            if st.button("⏮ Primera", disabled=(pag == 1), use_container_width=True):
                st.session_state["pagina_actual"] = 1; st.rerun()
        with p2:
            if st.button("◀ Anterior", disabled=(pag == 1), use_container_width=True):
                st.session_state["pagina_actual"] -= 1; st.rerun()
        with p3:
            st.markdown(f"<p style='text-align:center;margin-top:6px;color:#94A3B8;font-size:12px;'>Página <b>{pag}</b> de <b>{total_pags}</b> &nbsp;·&nbsp; <b>{total_filas}</b> registros</p>", unsafe_allow_html=True)
        with p4:
            if st.button("Siguiente ▶", disabled=(pag == total_pags), use_container_width=True):
                st.session_state["pagina_actual"] += 1; st.rerun()
        with p5:
            if st.button("Última ⏭", disabled=(pag == total_pags), use_container_width=True):
                st.session_state["pagina_actual"] = total_pags; st.rerun()

    else:
        if busqueda.strip() or filtro_est != "Todos":
            st.markdown("""
                <div style='text-align:center;padding:50px 0;color:#94A3B8;'>
                    <div style='font-size:36px;'>🔍</div>
                    <p style='font-size:15px;font-weight:600;margin:8px 0 4px;'>Sin resultados</p>
                    <p style='font-size:12px;'>No hay registros que coincidan con tu búsqueda.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style='text-align:center;padding:50px 0;color:#94A3B8;'>
                    <div style='font-size:36px;'>📦</div>
                    <p style='font-size:15px;font-weight:600;margin:8px 0 4px;'>Sin registros</p>
                    <p style='font-size:12px;'>Agrega el primer préstamo usando el botón ➕ Nuevo.</p>
                </div>
            """, unsafe_allow_html=True)
