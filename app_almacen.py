import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, date
from fpdf import FPDF
import math
import uuid

# ══════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════
st.set_page_config(page_title="MSH-Hub | Almacén", layout="wide", page_icon="📦")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
}

/* ── FONDO GENERAL ── */
[data-testid="stAppViewContainer"] {
    background: #F0F4F8;
}
[data-testid="stHeader"] {
    background: transparent;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #F0F4F8; }
::-webkit-scrollbar-thumb { background: #CBD5E0; border-radius: 99px; }

/* ══════════════════════════════════════════════
   HEADER
══════════════════════════════════════════════ */
.msh-header {
    background: #1E3447;
    border-radius: 12px;
    padding: 14px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    box-shadow: 0 4px 20px rgba(30,52,71,0.25);
}
.msh-header-left {
    display: flex;
    align-items: center;
    gap: 12px;
}
.msh-logo-box {
    width: 38px; height: 38px;
    background: rgba(255,255,255,0.12);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
}
.msh-title {
    font-size: 16px; font-weight: 600;
    color: #FFFFFF; line-height: 1.2;
    letter-spacing: -0.2px;
}
.msh-subtitle {
    font-size: 11px; color: rgba(255,255,255,0.5);
    font-weight: 400;
}
.msh-user-pill {
    display: flex; align-items: center; gap: 10px;
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 99px;
    padding: 6px 14px 6px 8px;
}
.msh-avatar {
    width: 28px; height: 28px; border-radius: 50%;
    background: linear-gradient(135deg, #4A90D9, #2D6FA8);
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700; color: #fff;
    flex-shrink: 0;
}
.msh-uname { font-size: 12px; font-weight: 600; color: #fff; }
.msh-urole {
    font-size: 10px; color: rgba(255,255,255,0.55);
    text-transform: uppercase; letter-spacing: 0.4px;
}

/* ══════════════════════════════════════════════
   KPI PILLS BAR
══════════════════════════════════════════════ */
.kpi-bar {
    background: #ffffff;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 10px 18px;
    display: flex;
    align-items: center;
    gap: 4px;
    margin-bottom: 14px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    flex-wrap: wrap;
}
.kpi-pill {
    display: flex; align-items: center; gap: 7px;
    padding: 5px 12px; border-radius: 99px;
}
.kpi-icon { font-size: 14px; }
.kpi-val { font-size: 15px; font-weight: 700; line-height: 1; }
.kpi-lbl { font-size: 11px; color: #64748B; font-weight: 500; }
.kpi-sep {
    width: 1px; height: 22px;
    background: #E2E8F0; margin: 0 4px; flex-shrink: 0;
}
.kpi-alert-pill {
    background: #FEF2F2;
    border: 1px solid #FECACA;
    border-radius: 99px;
    padding: 5px 12px;
    display: flex; align-items: center; gap: 7px;
}

/* ══════════════════════════════════════════════
   ALERT BANNER
══════════════════════════════════════════════ */
.alert-banner {
    display: flex; align-items: center; gap: 10px;
    background: #FEF2F2;
    border: 1px solid #FECACA;
    border-left: 4px solid #EF4444;
    border-radius: 8px;
    padding: 9px 14px;
    margin-bottom: 14px;
    font-size: 12px; color: #991B1B; font-weight: 500;
}

/* ══════════════════════════════════════════════
   PANEL DE CONTROLES
══════════════════════════════════════════════ */
.controls-panel {
    background: #ffffff;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

/* ══════════════════════════════════════════════
   TABLA
══════════════════════════════════════════════ */
.tbl-container {
    background: #ffffff;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}
.th {
    font-size: 10px !important;
    font-weight: 700 !important;
    color: #94A3B8 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 10px 6px 8px !important;
    border-bottom: 1px solid #E2E8F0;
    margin: 0 !important;
    background: #F8FAFC;
}
.td {
    font-size: 12px !important;
    color: #1E293B !important;
    padding: 9px 6px !important;
    border-bottom: 1px solid #F1F5F9;
    margin: 0 !important;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    background: transparent;
    font-family: 'DM Sans', sans-serif;
}
.td-alt {
    font-size: 12px !important;
    color: #1E293B !important;
    padding: 9px 6px !important;
    border-bottom: 1px solid #F1F5F9;
    margin: 0 !important;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    background: #FAFBFC;
}
.td-alerta {
    font-size: 12px !important;
    color: #991B1B !important;
    font-weight: 600 !important;
    padding: 9px 6px !important;
    border-bottom: 1px solid #FECACA;
    margin: 0 !important;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    background: #FEF2F2;
}
.td-hl {
    font-size: 12px !important;
    color: #166534 !important;
    font-weight: 500 !important;
    padding: 9px 6px !important;
    border-bottom: 1px solid #BBF7D0;
    margin: 0 !important;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    background: #F0FDF4;
}
.folio-tag {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #94A3B8;
    background: #F1F5F9;
    border-radius: 4px;
    padding: 1px 5px;
    display: inline-block;
}
.folio-tag-alerta {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #F87171;
    background: #FEF2F2;
    border-radius: 4px;
    padding: 1px 5px;
    display: inline-block;
}

/* ══════════════════════════════════════════════
   BADGES DE ESTADO
══════════════════════════════════════════════ */
.badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 9px;
    border-radius: 99px;
    font-size: 10px; font-weight: 600;
    white-space: nowrap;
}
.badge-prestado  { background:#FFF3E0; color:#C2410C; }
.badge-devuelto  { background:#DCFCE7; color:#15803D; }
.badge-asignado  { background:#DBEAFE; color:#1D4ED8; }
.badge-proceso   { background:#F3E8FF; color:#7E22CE; }
.badge-alerta    { background:#FEE2E2; color:#B91C1C; }

/* ══════════════════════════════════════════════
   DÍAS PENDIENTES
══════════════════════════════════════════════ */
.dias-activo {
    color: #DC2626; font-weight: 700; font-size: 11px;
    display: inline-flex; align-items: center; gap: 3px;
}
.dias-activo-warn {
    color: #D97706; font-weight: 700; font-size: 11px;
    display: inline-flex; align-items: center; gap: 3px;
}
.dias-ok {
    color: #16A34A; font-size: 11px; font-weight: 600;
    display: inline-flex; align-items: center; gap: 3px;
}
.dias-normal {
    color: #475569; font-size: 11px;
    display: inline-flex; align-items: center; gap: 3px;
}

/* ══════════════════════════════════════════════
   PAGINACIÓN
══════════════════════════════════════════════ */
.pg-info {
    text-align: center;
    font-size: 12px;
    color: #64748B;
    padding: 6px 0;
    font-weight: 500;
}

/* ══════════════════════════════════════════════
   VENTANAS EMERGENTES (DIÁLOGOS)
══════════════════════════════════════════════ */
div[data-testid="stDialog"] div[role="dialog"] {
    width: 65vw !important;
    max-width: 1000px !important;
    min-width: 380px !important;
    border-radius: 16px !important;
}
div[data-testid="stDialog"] .stVerticalBlock {
    gap: 0.35rem !important;
}
div[data-testid="stDialog"] [data-testid="stWidgetLabel"] p {
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #64748B !important;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    margin-bottom: -2px !important;
}
div[data-testid="stDialog"] input,
div[data-testid="stDialog"] select,
div[data-testid="stDialog"] div[role="combobox"] {
    height: 32px !important;
    font-size: 13px !important;
    border-radius: 8px !important;
}
div[data-testid="stDialog"] textarea {
    font-size: 12px !important;
    border-radius: 8px !important;
}
div[data-testid="stDialog"] hr {
    margin: 0.8rem 0 !important;
    border-color: #E2E8F0 !important;
}
.dialog-folio-chip {
    display: inline-flex; align-items: center; gap: 6px;
    background: #F1F5F9;
    border: 1px solid #E2E8F0;
    border-radius: 99px;
    padding: 4px 12px;
    font-size: 11px; color: #475569;
    font-family: 'DM Mono', monospace;
    margin-bottom: 10px;
}
.dialog-alerta-chip {
    display: inline-flex; align-items: center; gap: 6px;
    background: #FEF2F2;
    border: 1px solid #FECACA;
    border-radius: 99px;
    padding: 4px 12px;
    font-size: 11px; color: #991B1B;
    font-weight: 600;
    margin-bottom: 10px;
    margin-left: 8px;
}

/* ══════════════════════════════════════════════
   LOGIN
══════════════════════════════════════════════ */
.login-card {
    background: white;
    border-radius: 16px;
    padding: 32px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 8px 32px rgba(30,52,71,0.10);
}

/* ══════════════════════════════════════════════
   TABLA CONTENEDOR VISUAL
══════════════════════════════════════════════ */
.tbl-header-bar {
    background: #F8FAFC;
    border-bottom: 1px solid #E2E8F0;
    padding: 8px 12px;
    display: flex; align-items: center; justify-content: space-between;
    font-size: 11px; color: #64748B; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.4px;
}
.tbl-footer-bar {
    background: #F8FAFC;
    border-top: 1px solid #E2E8F0;
    padding: 8px 12px;
}
/* ── Botones globales ── */
[data-testid="stButton"] button {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 12px !important;
}
[data-testid="stButton"] button[kind="primary"] {
    background: #1E3447 !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(30,52,71,0.25) !important;
}
[data-testid="stButton"] button[kind="primary"]:hover {
    background: #16283A !important;
    box-shadow: 0 4px 12px rgba(30,52,71,0.35) !important;
}
/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] div[role="combobox"] {
    border-radius: 8px !important;
    border-color: #E2E8F0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #1E3447 !important;
    box-shadow: 0 0 0 3px rgba(30,52,71,0.10) !important;
}
/* ── Download buttons ── */
[data-testid="stDownloadButton"] button {
    border-radius: 8px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    border-color: #E2E8F0 !important;
    color: #475569 !important;
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

def cargar_prestamos():
    try:
        res = supabase.table("almacen_prestamos").select("*").order("created_at", desc=True).execute()
        return res.data if res.data else []
    except:
        return []

def agregar_prestamo(payload):
    try:
        supabase.table("almacen_prestamos").insert(payload).execute()
        return True
    except:
        return False

def modificar_prestamo(id_registro, payload):
    try:
        supabase.table("almacen_prestamos").update(payload).eq("id", id_registro).execute()
        return True
    except:
        return False

def eliminar_prestamo(id_registro):
    try:
        supabase.table("almacen_prestamos").delete().eq("id", id_registro).execute()
        return True
    except:
        return False

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
            except:
                continue
        if not fecha_inicio:
            return None, ""
        estados_activos = ["Prestado", "Asignado", "Proceso de asignacion"]
        if fecha_fin_str and str(fecha_fin_str).strip():
            for fmt in formatos:
                try:
                    fecha_fin = datetime.strptime(str(fecha_fin_str).strip(), fmt).date()
                    return (fecha_fin - fecha_inicio).days, "ok"
                except:
                    continue
        if estado in estados_activos:
            return (date.today() - fecha_inicio).days, "activo"
        return None, ""
    except:
        return None, ""

def generar_folio():
    """
    Genera un folio único combinando timestamp + fragmento UUID.
    Formato: ID-YYYYMMDDHHMMSS-XXXX
    Ejemplo: ID-20250601143022-A3F9
    - El timestamp garantiza orden cronológico y unicidad por segundo.
    - El fragmento UUID de 4 caracteres elimina colisiones si se crean
      múltiples registros en el mismo segundo.
    """
    ts   = datetime.now().strftime('%Y%m%d%H%M%S')
    uid  = uuid.uuid4().hex[:4].upper()
    return f"ID-{ts}-{uid}"
    """Convierte string de fecha a objeto date para comparaciones."""
    for fmt in ['%d/%m/%Y', '%Y-%m-%d']:
        try:
            return datetime.strptime(str(fecha_str).strip(), fmt).date()
        except:
            continue
    return None

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

    widths   = [22, 22, 34, 40, 10, 26, 22, 22, 41, 42]
    columnas = ["Folio", "Fecha", "Responsable", "Articulo", "Cant", "Estado", "F.Inicio", "F.Devol.", "Observaciones", "Nota"]

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

        lineas_por_celda = []
        for texto, ancho in zip(valores, widths):
            if not texto.strip():
                lineas_por_celda.append(1)
            else:
                ancho_texto = pdf.get_string_width(texto)
                ancho_disponible = ancho - 2
                lineas = math.ceil(ancho_texto / ancho_disponible) if ancho_disponible > 0 else 1
                lineas_por_celda.append(max(1, lineas))

        max_lineas = max(lineas_por_celda)
        altura_fila = max_lineas * 5

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
            pdf.multi_cell(ancho, altura_fila / lineas_por_celda[i], texto, border=1, align=align, fill=True)
            x_inicial += ancho

        pdf.set_xy(8, y_inicial + altura_fila)

    return pdf.output(dest='S').encode('latin-1', errors='ignore')

# ══════════════════════════════════════════════
# VENTANAS EMERGENTES
# ══════════════════════════════════════════════
@st.dialog("📝 Nuevo Registro de Préstamo", width="large")
def ventana_nuevo_prestamo():
    col1, col2, col3 = st.columns(3)
    with col1:
        fecha  = st.date_input("Fecha *", value=datetime.now(), format="DD/MM/YYYY")
        resp   = st.text_input("Responsable *", placeholder="Nombre completo")
    with col2:
        estado = st.selectbox("Estado *", ["Prestado", "Asignado", "Proceso de asignacion", "Devuelto"])
        art    = st.text_input("Artículo / Herramienta *", placeholder="Nombre del artículo")
    with col3:
        cant   = st.text_input("Cantidad *", value="1")
        alerta = st.selectbox("¿Activar Alerta?", ["NO", "SI"])

    c_obs, c_fdev = st.columns([2, 1])
    with c_obs:
        obs = st.text_area("Observaciones", placeholder="Descripción o notas del préstamo...", height=70)
    with c_fdev:
        fecha_dev = st.date_input("Fecha de Devolución", value=datetime.now(), format="DD/MM/YYYY")

    nota = st.text_input("Nota Interna (solo admins)", placeholder="Información confidencial...")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Crear Registro", type="primary", use_container_width=True):
            if not resp.strip() or not art.strip():
                st.error("Responsable y Artículo son obligatorios.")
            elif not cant.isdigit() or int(cant) < 1:
                st.error("La cantidad debe ser un número mayor a 0.")
            else:
                folio = generar_folio()
                payload = {
                    "id": folio,
                    "fecha": fecha.strftime('%d/%m/%Y'),
                    "responsable": resp.strip(),
                    "articulo": art.strip(),
                    "cantidad": int(cant),
                    "estado": estado,
                    "observaciones": obs.strip(),
                    "nota": nota.strip(),
                    "alerta": alerta,
                    "fecha_devolucion": fecha_dev.strftime('%d/%m/%Y') if estado in ["Devuelto", "Asignado"] else ""
                }
                if agregar_prestamo(payload):
                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"AGREGAR: {folio}")
                    st.session_state["ultimo_editado"] = folio
                    st.rerun()
                else:
                    st.error("Error al guardar. Verifica la conexión.")
    with c2:
        if st.button("❌ Cancelar", use_container_width=True):
            st.rerun()


@st.dialog("⚠️ Confirmar Eliminación")
def ventana_confirmar_eliminacion():
    """Diálogo de confirmación — lee los datos del flag en session_state."""
    id_reg      = st.session_state.get("_del_id", "")
    responsable = st.session_state.get("_del_resp", "")
    articulo    = st.session_state.get("_del_art", "")
    folio_visual = str(id_reg).replace("ID-", "#")

    st.markdown(f"""
        <div style="background:#FEF2F2; border:1px solid #FECACA; border-left:4px solid #EF4444;
                    border-radius:8px; padding:14px 16px; margin-bottom:14px;">
            <div style="font-size:14px; font-weight:700; color:#991B1B; margin-bottom:6px;">
                ¿Eliminar este registro permanentemente?
            </div>
            <div style="font-size:12px; color:#7F1D1D; line-height:1.7;">
                📋 <b>Folio:</b> {folio_visual}<br>
                👤 <b>Responsable:</b> {responsable}<br>
                🔧 <b>Artículo:</b> {articulo}
            </div>
        </div>
        <div style="font-size:11px; color:#94A3B8; margin-bottom:4px;">
            Esta acción <b>no se puede deshacer</b>. El registro será eliminado de la base de datos.
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Sí, eliminar", type="primary", use_container_width=True):
            if eliminar_prestamo(id_reg):
                registrar_acceso(
                    st.session_state["usuario"],
                    st.session_state["nombre"],
                    f"ELIMINAR: {id_reg}"
                )
                st.session_state["ultimo_editado"] = ""
                st.session_state["_del_id"] = ""
                st.rerun()
            else:
                st.error("Error al eliminar. Verifica la conexión.")
    with c2:
        if st.button("↩️ Cancelar", use_container_width=True):
            st.session_state["_del_id"] = ""
            st.rerun()


@st.dialog("✏️ Modificar Registro", width="large")
def ventana_editar_prestamo(id_reg, datos):
    folio_visual = str(id_reg).replace("ID-", "#")
    en_alerta_actual = normalizar_alerta(datos.get('alerta', 'NO')) == 'SI'

    # Info chips
    chips = f'<span class="dialog-folio-chip">📋 Folio {folio_visual}</span>'
    if en_alerta_actual:
        dias_p, tipo_p = calcular_dias(datos.get('fecha', ''), datos.get('fecha_devolucion', ''), datos.get('estado', ''))
        dias_txt = f" · {dias_p} días pendiente" if dias_p else ""
        chips += f'<span class="dialog-alerta-chip">🚨 Alerta activa{dias_txt}</span>'
    st.markdown(chips, unsafe_allow_html=True)

    try:
        fecha_def = datetime.strptime(str(datos.get('fecha', '')), '%d/%m/%Y')
    except:
        fecha_def = datetime.now()

    col1, col2, col3 = st.columns(3)
    with col1:
        nueva_fec  = st.date_input("Fecha *", value=fecha_def, format="DD/MM/YYYY")
        nuevo_resp = st.text_input("Responsable *", value=datos.get('responsable', ''))
    with col2:
        estados_op = ["Prestado", "Devuelto", "Asignado", "Proceso de asignacion"]
        est_idx    = estados_op.index(datos.get('estado', 'Prestado')) if datos.get('estado') in estados_op else 0
        nuevo_est  = st.selectbox("Estado *", estados_op, index=est_idx)
        nuevo_art  = st.text_input("Artículo *", value=datos.get('articulo', ''))
    with col3:
        nueva_cant = st.text_input("Cantidad *", value=str(datos.get('cantidad', '1')))
        ale_idx    = 1 if normalizar_alerta(datos.get('alerta', 'NO')) == "SI" else 0
        nueva_ale  = st.selectbox("Alerta", ["NO", "SI"], index=ale_idx)

    try:
        fdev_def = datetime.strptime(str(datos.get('fecha_devolucion', '')), '%d/%m/%Y') if datos.get('fecha_devolucion') else datetime.now()
    except:
        fdev_def = datetime.now()

    c_obs, c_fdev = st.columns([2, 1])
    with c_obs:
        nueva_obs = st.text_area("Observaciones", value=datos.get('observaciones', ''), height=70)
    with c_fdev:
        nueva_fdev = st.date_input("Fecha de Devolución", value=fdev_def, format="DD/MM/YYYY")

    nueva_not = st.text_input("Nota Interna", value=datos.get('nota', ''))

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💾 Guardar Cambios", type="primary", use_container_width=True):
            if not nuevo_resp.strip() or not nuevo_art.strip():
                st.error("Responsable y Artículo son obligatorios.")
            else:
                payload = {
                    "fecha": nueva_fec.strftime('%d/%m/%Y'),
                    "responsable": nuevo_resp.strip(),
                    "articulo": nuevo_art.strip(),
                    "cantidad": int(nueva_cant) if nueva_cant.isdigit() else 1,
                    "estado": nuevo_est,
                    "observaciones": nueva_obs.strip(),
                    "nota": nueva_not.strip(),
                    "alerta": nueva_ale,
                    "fecha_devolucion": nueva_fdev.strftime('%d/%m/%Y')
                }
                if modificar_prestamo(id_reg, payload):
                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"MODIFICAR: {id_reg}")
                    st.session_state["ultimo_editado"] = id_reg
                    st.rerun()
    with c2:
        if st.button("🗑️ Eliminar Registro", use_container_width=True):
            # Guardamos los datos en session_state y cerramos este diálogo.
            # En el siguiente rerun se abre el diálogo de confirmación (no anidado).
            st.session_state["_del_id"]   = id_reg
            st.session_state["_del_resp"] = datos.get('responsable', '')
            st.session_state["_del_art"]  = datos.get('articulo', '')
            st.rerun()
    with c3:
        if st.button("❌ Cerrar", use_container_width=True):
            st.rerun()

# ══════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════
for key, val in [("autenticado", False), ("ultimo_editado", ""), ("pagina_actual", 1),
                  ("_limpiar_fechas", False), ("_del_id", ""), ("_del_resp", ""), ("_del_art", "")]:
    if key not in st.session_state:
        st.session_state[key] = val

# ══════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════
if not st.session_state["autenticado"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_c, _ = st.columns([1, 1.1, 1])
    with col_c:
        st.markdown("""
            <div style='text-align:center; margin-bottom:28px;'>
                <div style='font-size:44px; margin-bottom:8px;'>📦</div>
                <div style='font-size:26px; font-weight:700; color:#1E3447; letter-spacing:-0.5px;'>MSH-Hub</div>
                <div style='font-size:13px; color:#94A3B8; margin-top:4px;'>Mendoza Servicios y Herramientas</div>
            </div>
        """, unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("##### 🔒 Acceso al Sistema")
            u_input = st.text_input("Usuario", placeholder="tu.usuario", label_visibility="collapsed")
            st.caption("Usuario")
            p_input = st.text_input("Contraseña", type="password", placeholder="••••••••", label_visibility="collapsed")
            st.caption("Contraseña")
            st.write("")
            if st.button("Ingresar al Sistema →", type="primary", use_container_width=True):
                user = verificar_usuario(u_input.strip(), p_input.strip())
                if user:
                    st.session_state.update({
                        "autenticado": True,
                        "usuario": user["usuario"],
                        "nombre": user["nombre"],
                        "rol": user["rol"]
                    })
                    registrar_acceso(user["usuario"], user["nombre"], "LOGIN")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

# ══════════════════════════════════════════════
# DASHBOARD PRINCIPAL
# ══════════════════════════════════════════════
else:
    usuario_actual = st.session_state["usuario"]
    nombre_actual  = st.session_state["nombre"]
    rol_actual     = st.session_state["rol"]
    es_admin       = rol_actual == "admin"
    iniciales      = "".join([p[0].upper() for p in nombre_actual.split()[:2]])

    # ── HEADER ──
    st.markdown(f"""
        <div class="msh-header">
            <div class="msh-header-left">
                <div class="msh-logo-box">📦</div>
                <div>
                    <div class="msh-title">MSH-Hub · Control de Almacén</div>
                    <div class="msh-subtitle">Mendoza Servicios y Herramientas</div>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:10px;">
                <div class="msh-user-pill">
                    <div class="msh-avatar">{iniciales}</div>
                    <div>
                        <div class="msh-uname">{nombre_actual}</div>
                        <div class="msh-urole">{rol_actual}</div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Botón salir aparte (Streamlit no permite botones dentro de markdown)
    _, col_salir = st.columns([11, 1])
    with col_salir:
        if st.button("🚪 Salir", use_container_width=True):
            registrar_acceso(usuario_actual, nombre_actual, "LOGOUT")
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    # ── DISPARADOR CONFIRMACIÓN ELIMINACIÓN ──
    # Se activa cuando el usuario presionó "Eliminar" en el modal de edición.
    # Al estar fuera de cualquier diálogo, Streamlit lo permite sin error.
    if st.session_state.get("_del_id"):
        ventana_confirmar_eliminacion()

    # ── CARGA DE DATOS ──
    df_master = pd.DataFrame(cargar_prestamos())
    if not df_master.empty and 'alerta' in df_master.columns:
        df_master['alerta'] = df_master['alerta'].apply(normalizar_alerta)

    # ── KPIs ──
    total   = len(df_master) if not df_master.empty else 0
    prest   = len(df_master[df_master['estado'] == 'Prestado'])               if not df_master.empty else 0
    devuel  = len(df_master[df_master['estado'] == 'Devuelto'])               if not df_master.empty else 0
    asign   = len(df_master[df_master['estado'] == 'Asignado'])               if not df_master.empty else 0
    proceso = len(df_master[df_master['estado'] == 'Proceso de asignacion'])  if not df_master.empty else 0
    alertas = len(df_master[df_master['alerta'] == 'SI'])                     if not df_master.empty else 0

    st.markdown(f"""
        <div class="kpi-bar">
            <div class="kpi-pill">
                <span class="kpi-icon">📦</span>
                <span class="kpi-val" style="color:#1E293B;">{total}</span>
                <span class="kpi-lbl">Total</span>
            </div>
            <div class="kpi-sep"></div>
            <div class="kpi-pill">
                <span class="kpi-icon">📤</span>
                <span class="kpi-val" style="color:#C2410C;">{prest}</span>
                <span class="kpi-lbl">Prestados</span>
            </div>
            <div class="kpi-sep"></div>
            <div class="kpi-pill">
                <span class="kpi-icon">✅</span>
                <span class="kpi-val" style="color:#15803D;">{devuel}</span>
                <span class="kpi-lbl">Devueltos</span>
            </div>
            <div class="kpi-sep"></div>
            <div class="kpi-pill">
                <span class="kpi-icon">👤</span>
                <span class="kpi-val" style="color:#1D4ED8;">{asign}</span>
                <span class="kpi-lbl">Asignados</span>
            </div>
            <div class="kpi-sep"></div>
            <div class="kpi-pill">
                <span class="kpi-icon">⏳</span>
                <span class="kpi-val" style="color:#7E22CE;">{proceso}</span>
                <span class="kpi-lbl">En Proceso</span>
            </div>
            <div class="kpi-sep"></div>
            <div class="kpi-alert-pill">
                <span class="kpi-icon">🚨</span>
                <span class="kpi-val" style="color:#B91C1C;">{alertas}</span>
                <span class="kpi-lbl" style="color:#B91C1C;">Alertas</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── BANNER ALERTAS ──
    if alertas > 0:
        st.markdown(f"""
            <div class="alert-banner">
                🚨 <strong>{alertas} registro{'s' if alertas > 1 else ''}</strong> con alerta activa 
                — revisa las filas marcadas en rojo antes de continuar.
            </div>
        """, unsafe_allow_html=True)

    # ── PANEL DE CONTROLES ──
    with st.container():
        # Fila 1: búsqueda + estado + nuevo
        c_busq, c_est, c_nuevo = st.columns([4, 2.5, 1.5])
        with c_busq:
            busqueda = st.text_input(
                "buscar", placeholder="🔍  Buscar por responsable, artículo o folio...",
                label_visibility="collapsed"
            )
        with c_est:
            filtro_est = st.selectbox(
                "estado", ["Todos", "Prestado", "Devuelto", "Asignado", "Proceso de asignacion", "🚨 En Alerta"],
                label_visibility="collapsed"
            )
        with c_nuevo:
            if es_admin:
                if st.button("➕ Nuevo Registro", type="primary", use_container_width=True):
                    ventana_nuevo_prestamo()

        # Fila 2: filtro de fechas + exportar
        # Patrón correcto: usar flag para limpiar, recrear widget con key nueva
        if st.session_state.get("_limpiar_fechas"):
            st.session_state["_limpiar_fechas"] = False
            st.session_state["_fecha_key_ver"] = st.session_state.get("_fecha_key_ver", 0) + 1

        _fver = st.session_state.get("_fecha_key_ver", 0)

        c_f1, c_f2, c_f3, c_csv, c_pdf = st.columns([1.5, 1.5, 1.5, 1.2, 1.2])
        with c_f1:
            st.caption("📅 Desde")
            fecha_desde = st.date_input(
                "desde", value=None, format="DD/MM/YYYY",
                label_visibility="collapsed", key=f"fecha_desde_{_fver}"
            )
        with c_f2:
            st.caption("📅 Hasta")
            fecha_hasta = st.date_input(
                "hasta", value=None, format="DD/MM/YYYY",
                label_visibility="collapsed", key=f"fecha_hasta_{_fver}"
            )
        with c_f3:
            st.caption("🔁 Limpiar fechas")
            if st.button("🔄 Limpiar fechas", use_container_width=True):
                st.session_state["_limpiar_fechas"] = True
                st.rerun()
        with c_csv:
            if not df_master.empty:
                st.caption("⬇️ Exportar")
                st.download_button(
                    "📥 CSV", data=df_master.to_csv(index=False).encode('utf-8'),
                    file_name=f"almacen_{datetime.now().strftime('%d%m%Y')}.csv",
                    mime="text/csv", use_container_width=True
                )
        with c_pdf:
            if not df_master.empty:
                st.caption("⬇️ Reporte")
                st.download_button(
                    "📕 PDF", data=generar_pdf(df_master, nombre_actual),
                    file_name=f"reporte_{datetime.now().strftime('%d%m%Y')}.pdf",
                    mime="application/pdf", use_container_width=True
                )

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── FILTRADO ──
    df_f = df_master.copy() if not df_master.empty else pd.DataFrame()

    if not df_f.empty:
        # Filtro texto
        if busqueda.strip():
            df_f = df_f[
                df_f['responsable'].str.contains(busqueda, case=False, na=False) |
                df_f['articulo'].str.contains(busqueda, case=False, na=False) |
                df_f['id'].str.contains(busqueda, case=False, na=False)
            ]
        # Filtro estado
        if filtro_est == "🚨 En Alerta":
            df_f = df_f[df_f['alerta'] == 'SI']
        elif filtro_est != "Todos":
            df_f = df_f[df_f['estado'] == filtro_est]

        # Filtro por fechas
        if fecha_desde or fecha_hasta:
            def en_rango(fecha_str):
                f = parsear_fecha(fecha_str)
                if not f:
                    return False
                if fecha_desde and f < fecha_desde:
                    return False
                if fecha_hasta and f > fecha_hasta:
                    return False
                return True
            df_f = df_f[df_f['fecha'].apply(en_rango)]

        # Reset página si cambian filtros
        filtro_key = f"{busqueda}|{filtro_est}|{fecha_desde}|{fecha_hasta}"
        if filtro_key != st.session_state.get("_fkey", ""):
            st.session_state["pagina_actual"] = 1
            st.session_state["_fkey"] = filtro_key

    # ── TABLA ──
    if not df_f.empty:
        IPP = 15
        total_filas = len(df_f)
        total_pags  = max(1, -(-total_filas // IPP))
        pag         = st.session_state["pagina_actual"]
        df_pag      = df_f.iloc[(pag - 1) * IPP : pag * IPP]

        cw   = [1.0, 0.85, 2.3, 2.6, 0.55, 1.8, 1.1, 0.5] if es_admin else [1.0, 0.85, 2.3, 2.6, 0.55, 1.8, 1.1]
        ths  = ["Fecha", "Folio", "Responsable", "Artículo", "Cant.", "Estado", "Días pend.", ""] if es_admin else ["Fecha", "Folio", "Responsable", "Artículo", "Cant.", "Estado", "Días pend."]

        # Cabecera de tabla
        with st.container():
            h_cols = st.columns(cw)
            for col, txt in zip(h_cols, ths):
                col.markdown(f"<p class='th'>{txt}</p>", unsafe_allow_html=True)

            # Filas
            for i, (_, row) in enumerate(df_pag.iterrows()):
                id_f       = row['id']
                folio_corto = "#" + str(id_f).replace("ID-", "")[-9:]  # últimos 9 chars: HHMMSS-XXXX
                en_alerta  = str(row.get('alerta', 'NO')).upper() == 'SI'
                es_ult     = id_f == st.session_state.get("ultimo_editado", "")

                if es_ult:
                    cls = "td-hl"
                elif en_alerta:
                    cls = "td-alerta"
                elif i % 2 == 1:
                    cls = "td-alt"
                else:
                    cls = "td"

                r = st.columns(cw)

                r[0].markdown(f"<div class='{cls}'>{row.get('fecha', '')}</div>", unsafe_allow_html=True)

                folio_html = f"<span class='folio-tag-alerta'>{folio_corto}</span>" if en_alerta else f"<span class='folio-tag'>{folio_corto}</span>"
                r[1].markdown(f"<div class='{cls}'>{folio_html}</div>", unsafe_allow_html=True)

                r[2].markdown(f"<div class='{cls}'><b>{row.get('responsable', '')}</b></div>", unsafe_allow_html=True)
                r[3].markdown(f"<div class='{cls}'>{row.get('articulo', '')}</div>", unsafe_allow_html=True)
                r[4].markdown(f"<div class='{cls}' style='text-align:center;'>{row.get('cantidad', 1)}</div>", unsafe_allow_html=True)

                est = row.get('estado', 'Prestado')
                badge_map = {
                    "Prestado": "badge-prestado",
                    "Devuelto": "badge-devuelto",
                    "Asignado": "badge-asignado"
                }
                badge_cls = "badge-alerta" if en_alerta and est == "Prestado" else badge_map.get(est, "badge-proceso")
                r[5].markdown(f"<div class='{cls}'><span class='badge {badge_cls}'>{est}</span></div>", unsafe_allow_html=True)

                d, tipo = calcular_dias(row.get('fecha', ''), row.get('fecha_devolucion', ''), est)
                if tipo == "activo" and d is not None:
                    if d >= 7:
                        dias_html = f"<span class='dias-activo'>⏱ {d}d</span>"
                    elif d >= 3:
                        dias_html = f"<span class='dias-activo-warn'>⚠ {d}d</span>"
                    else:
                        dias_html = f"<span class='dias-normal'>{d}d</span>"
                elif tipo == "ok" and d is not None:
                    dias_html = f"<span class='dias-ok'>✓ {d}d</span>"
                else:
                    dias_html = "<span style='color:#CBD5E0;font-size:11px;'>—</span>"
                r[6].markdown(f"<div class='{cls}'>{dias_html}</div>", unsafe_allow_html=True)

                if es_admin:
                    with r[7]:
                        if st.button("✏️", key=f"ed_{id_f}", help=f"Editar {folio_corto}", use_container_width=True):
                            ventana_editar_prestamo(id_f, row.to_dict())

        # ── PAGINACIÓN ──
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        p1, p2, p3, p4, p5 = st.columns([1, 1, 3, 1, 1])
        with p1:
            if st.button("⏮", disabled=(pag == 1), use_container_width=True, help="Primera página"):
                st.session_state["pagina_actual"] = 1
                st.rerun()
        with p2:
            if st.button("◀", disabled=(pag == 1), use_container_width=True, help="Página anterior"):
                st.session_state["pagina_actual"] -= 1
                st.rerun()
        p3.markdown(
            f"<p class='pg-info'>Página <b>{pag}</b> de <b>{total_pags}</b> &nbsp;·&nbsp; <b>{total_filas}</b> registros</p>",
            unsafe_allow_html=True
        )
        with p4:
            if st.button("▶", disabled=(pag == total_pags), use_container_width=True, help="Página siguiente"):
                st.session_state["pagina_actual"] += 1
                st.rerun()
        with p5:
            if st.button("⏭", disabled=(pag == total_pags), use_container_width=True, help="Última página"):
                st.session_state["pagina_actual"] = total_pags
                st.rerun()

    elif not df_master.empty:
        st.info("🔍 No se encontraron registros con los filtros aplicados.")
    else:
        st.info("📭 No hay registros en el sistema. ¡Crea el primero!")
