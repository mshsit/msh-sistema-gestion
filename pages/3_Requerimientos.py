import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, date
from fpdf import FPDF
import uuid

st.set_page_config(
    page_title="MSH-Hub | Requisiciones",
    layout="wide",
    page_icon="📋",
    initial_sidebar_state="collapsed"
)

# ── Protección ──
if not st.session_state.get("autenticado"):
    st.switch_page("app.py")

# ══════════════════════════════════════════════
# CSS: sidebar oculto + estilos del módulo
# (idéntico a 2_Prestamos.py, + clases propias de Requisiciones)
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
.kpi-alert-pill {
    background: #FEF2F2; border: 1px solid #FECACA; border-radius: 99px;
    padding: 5px 12px; display: flex; align-items: center; gap: 7px;
}
.alert-banner {
    display: flex; align-items: center; gap: 10px; background: #FEF2F2;
    border: 1px solid #FECACA; border-left: 4px solid #EF4444; border-radius: 8px;
    padding: 9px 14px; margin-bottom: 14px; font-size: 12px; color: #991B1B; font-weight: 500;
}
.th {
    font-size: 10px !important; font-weight: 700 !important; color: #FFFFFF !important;
    text-transform: uppercase; letter-spacing: 0.5px; padding: 13px 6px !important;
    margin: 0 !important; background: #1E3447;
    line-height: 1 !important; box-sizing: border-box !important;
    white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important;
}
.th:first-child { border-radius: 10px 0 0 0; }
.th:last-child { border-radius: 0 10px 0 0; }
div[data-testid="stHorizontalBlock"]:has(.th) {
    gap: 0 !important;
}
div[data-testid="stHorizontalBlock"]:has(.th) > div[data-testid="stColumn"] {
    padding: 0 !important;
}
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
.td-urgente {
    font-size: 12px !important; color: #991B1B !important; font-weight: 600 !important;
    padding: 9px 6px !important; border-bottom: 1px solid #FECACA; margin: 0 !important;
    overflow: hidden; white-space: nowrap; text-overflow: ellipsis; background: #FEF2F2;
}
.td-hl {
    font-size: 12px !important; color: #166534 !important; font-weight: 500 !important;
    padding: 9px 6px !important; border-bottom: 1px solid #BBF7D0; margin: 0 !important;
    overflow: hidden; white-space: nowrap; text-overflow: ellipsis; background: #F0FDF4;
}
.folio-tag {
    font-family: 'DM Mono', monospace; font-size: 10px; color: #94A3B8;
    background: #F1F5F9; border-radius: 4px; padding: 1px 5px; display: inline-block;
}
.folio-tag-urgente {
    font-family: 'DM Mono', monospace; font-size: 10px; color: #F87171;
    background: #FEF2F2; border-radius: 4px; padding: 1px 5px; display: inline-block;
}
.badge {
    display: inline-flex; align-items: center; gap: 4px; padding: 3px 9px;
    border-radius: 99px; font-size: 10px; font-weight: 600; white-space: nowrap;
}
.badge-pendiente { background:#FFF3E0; color:#C2410C; }
.badge-aprobada  { background:#DCFCE7; color:#15803D; }
.badge-rechazada { background:#FEE2E2; color:#B91C1C; }
.badge-proceso   { background:#DBEAFE; color:#1D4ED8; }
.badge-entregada { background:#F3E8FF; color:#7E22CE; }
.badge-urgente   { background:#FEE2E2; color:#B91C1C; }
.frac-pendiente { color:#94A3B8; font-weight:600; font-size:12px; }
.frac-parcial   { color:#C2410C; font-weight:700; font-size:12px; }
.frac-completo  { color:#15803D; font-weight:700; font-size:12px; }
.entrega-row {
    display:flex; align-items:center; justify-content:space-between;
    background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px;
    padding:7px 12px; margin-bottom:5px; font-size:12px; color:#1E293B;
}
.pg-info { text-align:center; font-size:12px; color:#64748B; padding:6px 0; font-weight:500; }

/* ── TARJETAS DE PANEL (Filtros / Tabla) ── */
div[class*="st-key-panel_filtros"],
div[class*="st-key-panel_tabla"] {
    background: #ffffff; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 22px 24px; margin-bottom: 18px;
    box-shadow: 0 2px 10px rgba(30,52,71,0.06);
}
.panel-card-titulo {
    font-size: 15px; font-weight: 700; color: #1E293B; margin-bottom: 2px;
}
.panel-card-subtitulo {
    font-size: 12px; color: #94A3B8; margin-bottom: 16px;
}
div[data-testid="stDialog"] div[role="dialog"] {
    width: 70vw !important; max-width: 1100px !important;
    min-width: 400px !important; border-radius: 16px !important;
    max-height: 85vh !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
}
div[data-testid="stDialog"] div[role="dialog"]::-webkit-scrollbar {
    width: 6px;
}
div[data-testid="stDialog"] div[role="dialog"]::-webkit-scrollbar-thumb {
    background: #CBD5E0; border-radius: 99px;
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
div[data-testid="stDialog"] hr { margin: 0.8rem 0 !important; border-color: #E2E8F0 !important; }
.dialog-folio-chip {
    display: inline-flex; align-items: center; gap: 6px; background: #F1F5F9;
    border: 1px solid #E2E8F0; border-radius: 99px; padding: 4px 12px;
    font-size: 11px; color: #475569; font-family: 'DM Mono', monospace; margin-bottom: 10px;
}
.dialog-urgente-chip {
    display: inline-flex; align-items: center; gap: 6px; background: #FEF2F2;
    border: 1px solid #FECACA; border-radius: 99px; padding: 4px 12px;
    font-size: 11px; color: #991B1B; font-weight: 600; margin-bottom: 10px; margin-left: 8px;
}
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
[data-testid="stDownloadButton"] button {
    border-radius: 8px !important; font-size: 12px !important; font-weight: 600 !important;
    border-color: #E2E8F0 !important; color: #475569 !important;
}
/* ── Partidas dentro de los diálogos ── */
.partida-row {
    background: #F8FAFC; border: 1px solid #E2E8F0;
    border-radius: 8px; padding: 8px 12px; margin-bottom: 6px;
    font-size: 12px; color: #1E293B;
}
.partida-num-chip {
    display: inline-flex; align-items: center; justify-content: center;
    width: 20px; height: 20px; border-radius: 50%;
    background: #1E3447; color: #fff; font-size: 10px; font-weight: 700;
    margin-right: 6px;
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

def cargar_requisiciones():
    try:
        res = supabase.table("requisiciones").select("*").order("created_at", desc=True).execute()
        return res.data if res.data else []
    except:
        return []

def folios_con_entrega_pendiente():
    """Calcula, para TODAS las requisiciones de una sola pasada, qué folios
    tienen al menos una partida sin entregar por completo. Hace solo 2
    consultas (todas las partidas + todas las entregas) en vez de una por
    requisición, para que la tabla principal no se vuelva lenta."""
    try:
        res_p = supabase.table("requisicion_partidas").select("id, folio_req, cantidad").execute()
        partidas = res_p.data if res_p.data else []
        res_e = supabase.table("requisicion_entregas").select("partida_id, cantidad").execute()
        entregas = res_e.data if res_e.data else []
    except:
        return set()

    entregado_por_partida = {}
    for e in entregas:
        pid = e.get("partida_id")
        entregado_por_partida[pid] = entregado_por_partida.get(pid, 0) + float(e.get("cantidad", 0) or 0)

    folios_pendientes = set()
    for p in partidas:
        pid = p.get("id")
        cant_pedida = float(p.get("cantidad", 0) or 0)
        cant_entregada = entregado_por_partida.get(pid, 0)
        if cant_entregada < cant_pedida - 0.0001:
            folios_pendientes.add(p.get("folio_req"))
    return folios_pendientes

def cargar_partidas(folio_req):
    try:
        res = supabase.table("requisicion_partidas").select("*").eq("folio_req", folio_req).order("numero").execute()
        return res.data if res.data else []
    except:
        return []

def buscar_folios_por_producto(texto):
    """Devuelve el conjunto de folios cuyas partidas tienen una descripción
    que contiene `texto` (búsqueda por producto, ej. 'thinner')."""
    if not texto or not texto.strip():
        return None
    try:
        res = (supabase.table("requisicion_partidas")
               .select("folio_req, descripcion")
               .ilike("descripcion", f"%{texto.strip()}%")
               .execute())
        datos = res.data if res.data else []
        return {row["folio_req"] for row in datos}
    except:
        return set()

# ── ENTREGAS PARCIALES ──
def cargar_entregas(folio_req):
    """Carga todas las entregas registradas para una requisición completa."""
    try:
        res = (supabase.table("requisicion_entregas")
               .select("*").eq("folio_req", folio_req)
               .order("fecha_entrega").execute())
        return res.data if res.data else []
    except:
        return []

def agregar_entrega(payload):
    try:
        supabase.table("requisicion_entregas").insert(payload).execute()
        return True
    except:
        return False

def eliminar_entrega(entrega_id):
    try:
        supabase.table("requisicion_entregas").delete().eq("id", entrega_id).execute()
        return True
    except:
        return False

def calcular_estado_partidas(partidas, entregas):
    """Combina cada partida con su total entregado y estado derivado.
    Devuelve la misma lista de partidas, agregando:
      - 'entregado_total': suma de cantidades entregadas
      - 'estado_entrega': 'Pendiente' | 'Parcial' | 'Completo'
      - 'entregas': lista de entregas de esa partida (ordenadas por fecha)
    """
    entregas_por_partida = {}
    for e in entregas:
        entregas_por_partida.setdefault(e["partida_id"], []).append(e)

    resultado = []
    for p in partidas:
        pid = p.get("id")
        ents = entregas_por_partida.get(pid, [])
        total_entregado = sum(float(e.get("cantidad", 0) or 0) for e in ents)
        cantidad_pedida = float(p.get("cantidad", 0) or 0)

        if total_entregado <= 0:
            estado = "Pendiente"
        elif total_entregado >= cantidad_pedida:
            estado = "Completo"
        else:
            estado = "Parcial"

        p_actualizada = dict(p)
        p_actualizada["entregado_total"] = total_entregado
        p_actualizada["estado_entrega"] = estado
        p_actualizada["entregas"] = ents
        resultado.append(p_actualizada)
    return resultado

def agregar_requisicion(payload):
    try:
        supabase.table("requisiciones").insert(payload).execute()
        return True
    except:
        return False

def agregar_partidas(partidas):
    try:
        # Quitar 'id' (None) de partidas nuevas: es columna identity en BD.
        limpias = [{k: v for k, v in p.items() if k != "id"} for p in partidas]
        supabase.table("requisicion_partidas").insert(limpias).execute()
        return True
    except:
        return False

def modificar_requisicion(folio, payload):
    try:
        supabase.table("requisiciones").update(payload).eq("folio", folio).execute()
        return True
    except:
        return False

def sincronizar_partidas(folio, partidas_nuevas):
    """Actualiza/inserta/borra partidas de una requisición SIN perder los
    `id` de las partidas que ya existían (y por tanto sin perder las
    entregas parciales ya registradas contra esos ids).

    `partidas_nuevas` es una lista de dicts; si un dict trae 'id' se
    actualiza esa fila existente, si no trae 'id' se inserta como nueva.
    Cualquier partida existente en BD que ya no aparezca en `partidas_nuevas`
    se elimina (junto con sus entregas, por on delete cascade).
    """
    try:
        existentes = supabase.table("requisicion_partidas").select("id").eq("folio_req", folio).execute()
        ids_existentes = {row["id"] for row in (existentes.data or [])}
        ids_conservados = set()

        for p in partidas_nuevas:
            pid = p.get("id")
            datos_partida = {k: v for k, v in p.items() if k != "id"}
            if pid and pid in ids_existentes:
                supabase.table("requisicion_partidas").update(datos_partida).eq("id", pid).execute()
                ids_conservados.add(pid)
            else:
                supabase.table("requisicion_partidas").insert(datos_partida).execute()

        ids_a_borrar = ids_existentes - ids_conservados
        for pid in ids_a_borrar:
            supabase.table("requisicion_partidas").delete().eq("id", pid).execute()
        return True
    except:
        return False

def eliminar_requisicion(folio):
    try:
        supabase.table("requisicion_partidas").delete().eq("folio_req", folio).execute()
        supabase.table("requisiciones").delete().eq("folio", folio).execute()
        return True
    except:
        return False

def generar_folio():
    ts  = datetime.now().strftime('%Y%m%d%H%M%S')
    uid = uuid.uuid4().hex[:4].upper()
    return f"REQ-{ts}-{uid}"

def parsear_fecha(fecha_str):
    for fmt in ['%d/%m/%Y', '%Y-%m-%d']:
        try:
            return datetime.strptime(str(fecha_str).strip(), fmt).date()
        except:
            continue
    return None

def calcular_dias_pendiente(fecha_str, estado):
    f = parsear_fecha(fecha_str)
    if not f:
        return None
    if estado in ["Pendiente", "En Proceso"]:
        return (date.today() - f).days
    return None

def truncar_palabra(texto, limite=30):
    texto = str(texto or "").strip()
    if not texto:
        return ""
    if len(texto) <= limite:
        return texto
    cortado = texto[:limite].rsplit(" ", 1)[0]
    if not cortado:
        cortado = texto[:limite]
    return cortado + "…"

# ══════════════════════════════════════════════
# SANITIZADO DE TEXTO PARA FPDF (fuente Arial = latin-1)
# ══════════════════════════════════════════════
_PDF_REPLACEMENTS = {
    "\u2014": "-",   # — em dash
    "\u2013": "-",   # – en dash
    "\u2018": "'",   # '
    "\u2019": "'",   # '
    "\u201c": '"',   # "
    "\u201d": '"',   # "
    "\u2026": "...", # …
    "\u2022": "-",   # •
    "\u00a0": " ",   # espacio no separable
}

def pdf_safe(texto):
    """Convierte cualquier texto a algo seguro para FPDF clásico (latin-1).
    Reemplaza caracteres tipográficos comunes y elimina cualquier otro
    carácter (emojis, etc.) que no exista en latin-1, en vez de tronar."""
    if texto is None:
        return ""
    s = str(texto)
    for orig, rep in _PDF_REPLACEMENTS.items():
        s = s.replace(orig, rep)
    return s.encode('latin-1', errors='ignore').decode('latin-1')

def pdf_output_bytes(pdf):
    """Devuelve los bytes del PDF sin importar si está instalado fpdf2
    (pdf.output() sin argumentos ya devuelve bytearray) o el fpdf clásico
    (donde se necesita dest='S' explícito; sin él, output() escribe a
    stdout y devuelve '' en vez del PDF)."""
    import inspect
    try:
        acepta_dest = 'dest' in inspect.signature(pdf.output).parameters
    except (TypeError, ValueError):
        acepta_dest = False

    if acepta_dest:
        salida = pdf.output(dest='S')  # fpdf clásico
    else:
        salida = pdf.output()  # fpdf2

    if isinstance(salida, str):
        return salida.encode('latin-1', errors='ignore')
    return bytes(salida)


# ══════════════════════════════════════════════
# GENERADOR PDF — REQUISICIÓN INDIVIDUAL
# ══════════════════════════════════════════════
def generar_pdf_requisicion(req, partidas):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_margins(15, 15, 15)
    pdf.add_page()

    pdf.set_fill_color(30, 52, 71)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", 'B', 14)
    pdf.cell(0, 10, "REQUISICION DE COMPRA", align='C', fill=True)
    pdf.ln(10)

    pdf.set_font("helvetica", '', 9)
    pdf.set_text_color(0, 0, 0)

    def label_val(label, val, w_label=35, w_val=55):
        pdf.set_font("helvetica", 'B', 8)
        pdf.set_fill_color(240, 244, 248)
        pdf.cell(w_label, 6, pdf_safe(label), border=1, fill=True)
        pdf.set_font("helvetica", '', 8)
        pdf.set_fill_color(255, 255, 255)
        pdf.cell(w_val, 6, pdf_safe(val), border=1, fill=True)

    label_val("Folio:", req.get('folio', ''), 25, 50)
    pdf.cell(5, 6, "", border=0)
    label_val("Fecha Solicitud:", req.get('fecha_solicitud', ''), 35, 50)
    pdf.ln()

    label_val("Solicitante:", req.get('solicitante', ''), 25, 50)
    pdf.cell(5, 6, "", border=0)
    label_val("Dpto. Solicitante:", req.get('departamento', ''), 35, 50)
    pdf.ln()

    label_val("Compañía:", req.get('compania', 'Mendoza Servicios y Herramientas'), 25, 50)
    pdf.cell(5, 6, "", border=0)
    label_val("Estado:", req.get('estado', ''), 35, 50)
    pdf.ln()

    label_val("Prioridad:", req.get('prioridad', 'Normal'), 25, 50)
    pdf.cell(5, 6, "", border=0)
    label_val("Referencia:", req.get('referencia', ''), 35, 50)
    pdf.ln(8)

    cols    = ["No.", "Partida de Catalogo", "Cantidad", "Unidad", "Descripcion", "Costo", "Entregado"]
    widths  = [10, 30, 18, 18, 65, 22, 17]
    aligns  = ['C', 'L', 'C', 'C', 'L', 'C', 'C']

    pdf.set_font("helvetica", 'B', 8)
    pdf.set_fill_color(30, 52, 71)
    pdf.set_text_color(255, 255, 255)
    for c, w, a in zip(cols, widths, aligns):
        pdf.cell(w, 7, c, border=1, align=a, fill=True)
    pdf.ln()

    pdf.set_font("helvetica", '', 8)
    pdf.set_text_color(0, 0, 0)
    max_filas = max(12, len(partidas))
    for i in range(max_filas):
        if i < len(partidas):
            p = partidas[i]
            entregado_t = p.get('entregado_total')
            cant_p = p.get('cantidad', 0)
            if entregado_t is not None:
                ent_txt = f"{entregado_t:g}/{cant_p:g}"
            else:
                ent_txt = 'X' if p.get('entregado') else ''
            vals = [
                pdf_safe(p.get('numero', i + 1)),
                pdf_safe(p.get('partida_catalogo', '')),
                pdf_safe(p.get('cantidad', '')),
                pdf_safe(p.get('unidad', '')),
                pdf_safe(p.get('descripcion', '')),
                pdf_safe(f"${p.get('costo', '')}") if p.get('costo') else '',
                ent_txt,
            ]
        else:
            vals = ['', '', '', '', '', '', '']

        fill = i % 2 == 0
        if fill:
            pdf.set_fill_color(248, 250, 252)
        else:
            pdf.set_fill_color(255, 255, 255)
        for v, w, a in zip(vals, widths, aligns):
            pdf.cell(w, 6, v, border=1, align=a, fill=True)
        pdf.ln()

    pdf.ln(4)
    obs = pdf_safe(req.get('observaciones', ''))
    pdf.set_font("helvetica", 'B', 8)
    pdf.set_fill_color(240, 244, 248)
    pdf.cell(0, 6, "Referencia, Especificaciones Adicionales u Observaciones:", border=1, fill=True)
    pdf.ln()
    pdf.set_font("helvetica", '', 8)
    pdf.set_fill_color(255, 255, 255)
    pdf.multi_cell(0, 5, obs if obs else " ", border=1, fill=True)

    pdf.ln(8)
    pdf.set_font("helvetica", '', 9)
    fw = (pdf.w - 30) / 2
    pdf.cell(fw, 5, "Solicitante: _______________________________")
    pdf.cell(fw, 5, "Autorizado por: _______________________________")
    pdf.ln()

    return pdf_output_bytes(pdf)


# ══════════════════════════════════════════════
# GENERADOR PDF — LISTADO (todas las requisiciones)
# ══════════════════════════════════════════════
def generar_pdf_listado(df, nombre_usuario=""):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_margins(8, 8, 8)
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 13)
    pdf.set_text_color(30, 52, 71)
    pdf.cell(0, 7, "MSH-HUB | CONTROL DE REQUISICIONES DE COMPRA - MENDOZA SERVICIOS Y HERRAMIENTAS", align='L')
    pdf.ln()
    pdf.set_font("helvetica", '', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Usuario: {nombre_usuario}", align='L')
    pdf.ln()
    pdf.ln(3)

    widths   = [26, 20, 30, 28, 24, 20, 22, 18, 23, 50]
    columnas = ["Folio", "Fecha", "Solicitante", "Departamento", "Referencia", "Estado", "Prioridad", "# Part.", "Costo Total", "Observaciones"]
    pdf.set_font("helvetica", 'B', 8)
    pdf.set_fill_color(30, 52, 71)
    pdf.set_text_color(255, 255, 255)
    for i, col in enumerate(columnas):
        pdf.cell(widths[i], 7, col, border=1, align='C', fill=True)
    pdf.ln()

    pdf.set_font("helvetica", '', 7.5)
    for idx, (_, row) in enumerate(df.iterrows()):
        es_urgente = str(row.get('prioridad', '')).upper() == 'URGENTE'
        if es_urgente:
            pdf.set_fill_color(254, 226, 226); pdf.set_text_color(153, 27, 27)
        elif idx % 2 == 0:
            pdf.set_fill_color(248, 250, 252); pdf.set_text_color(0, 0, 0)
        else:
            pdf.set_fill_color(255, 255, 255); pdf.set_text_color(0, 0, 0)

        ct = row.get('costo_total', 0)
        costo_fmt = f"${float(ct):,.2f}" if ct else "-"
        valores = [
            pdf_safe(str(row.get('folio', '')).replace("REQ-", "")),
            pdf_safe(row.get('fecha_solicitud', '')),
            pdf_safe(row.get('solicitante', '')),
            pdf_safe(row.get('departamento', '')),
            pdf_safe(row.get('referencia', '')),
            pdf_safe(row.get('estado', '')),
            pdf_safe(row.get('prioridad', '')),
            pdf_safe(row.get('num_partidas', 0)),
            costo_fmt,
            pdf_safe(str(row.get('observaciones', ''))[:60]),
        ]

        if pdf.get_y() + 6 > 200:
            pdf.add_page()
            pdf.set_font("helvetica", 'B', 8)
            pdf.set_fill_color(30, 52, 71); pdf.set_text_color(255, 255, 255)
            for c, w in zip(columnas, widths):
                pdf.cell(w, 7, c, border=1, align='C', fill=True)
            pdf.ln()
            pdf.set_font("helvetica", '', 7.5)
            if es_urgente:
                pdf.set_fill_color(254, 226, 226); pdf.set_text_color(153, 27, 27)
            else:
                pdf.set_fill_color(255, 255, 255); pdf.set_text_color(0, 0, 0)

        for v, w in zip(valores, widths):
            pdf.cell(w, 6, v[:35] if len(v) > 35 else v, border=1, fill=True)
        pdf.ln()

    return pdf_output_bytes(pdf)

# ══════════════════════════════════════════════
# DIÁLOGOS
# ══════════════════════════════════════════════
def _editor_partidas(key_prefix, partidas_iniciales=None):
    """Renderiza un editor dinámico de partidas (agregar/quitar filas) usando
    st.session_state para mantener el número de filas entre reruns."""
    state_key = f"_{key_prefix}_n"
    if state_key not in st.session_state:
        st.session_state[state_key] = max(1, len(partidas_iniciales or [])) or 1

    st.caption("Agrega las partidas necesarias. Descripción y Cantidad son obligatorios por partida.")

    c_add, c_rem, _ = st.columns([1.3, 1.3, 5])
    with c_add:
        if st.button("➕ Agregar partida", key=f"{key_prefix}_add", width="stretch"):
            st.session_state[state_key] += 1
    with c_rem:
        if st.button("➖ Quitar última", key=f"{key_prefix}_rem", width="stretch",
                      disabled=st.session_state[state_key] <= 1):
            st.session_state[state_key] -= 1

    n = st.session_state[state_key]
    iniciales = partidas_iniciales or []

    partidas_data = []
    for i in range(n):
        ini = iniciales[i] if i < len(iniciales) else {}
        st.markdown(f"<div class='partida-row'><span class='partida-num-chip'>{i+1}</span> Partida {i+1}</div>",
                    unsafe_allow_html=True)
        p1, p2, p3, p4, p5 = st.columns([2.3, 1.1, 1.1, 3.3, 1.4])
        with p1:
            cat = st.text_input("Partida de Catálogo", key=f"{key_prefix}_cat_{i}",
                                 value=str(ini.get('partida_catalogo', '')), placeholder="Código o nombre")
        with p2:
            cant = st.text_input("Cantidad *", key=f"{key_prefix}_cant_{i}",
                                  value=str(ini.get('cantidad', '1') or '1'))
        with p3:
            unidad = st.text_input("Unidad", key=f"{key_prefix}_unid_{i}",
                                    value=str(ini.get('unidad', '')), placeholder="PZA, KG, LT…")
        with p4:
            desc = st.text_input("Descripción *", key=f"{key_prefix}_desc_{i}",
                                  value=str(ini.get('descripcion', '')), placeholder="Descripción del artículo")
        with p5:
            costo = st.text_input("Costo", key=f"{key_prefix}_costo_{i}",
                                   value=str(ini.get('costo', '') or ''), placeholder="0.00")
        partidas_data.append({"num": i + 1, "id": ini.get('id'), "cat": cat, "cant": cant, "unidad": unidad,
                               "desc": desc, "costo": costo})
    return partidas_data


def _construir_payloads(folio, partidas_data):
    """Valida y construye (payload_partidas, costo_total). Cada item de
    payload_partidas conserva 'id' (None si es nueva) para que
    sincronizar_partidas() sepa si debe actualizar o insertar."""
    partidas_validas = [p for p in partidas_data if p['desc'].strip()]
    costo_total = 0.0
    payload_partidas = []
    for p in partidas_validas:
        try:
            costo_p = float(str(p['costo']).replace(',', '')) if str(p['costo']).strip() else None
        except:
            costo_p = None
        try:
            cant_p = float(str(p['cant']).replace(',', ''))
        except:
            cant_p = 1
        if costo_p:
            costo_total += costo_p * cant_p
        payload_partidas.append({
            "id":               p.get('id'),
            "folio_req":        folio,
            "numero":           p['num'],
            "partida_catalogo": p['cat'].strip(),
            "cantidad":         cant_p,
            "unidad":           p['unidad'].strip(),
            "descripcion":      p['desc'].strip(),
            "costo":            costo_p,
        })
    return payload_partidas, round(costo_total, 2)


@st.dialog("📝 Nueva Requisición de Compra", width="large")
def ventana_nueva_requisicion():
    col1, col2, col3 = st.columns(3)
    with col1:
        fecha_sol   = st.date_input("Fecha de Solicitud *", value=datetime.now(), format="DD/MM/YYYY")
        solicitante = st.text_input("Solicitante *", placeholder="Nombre completo")
    with col2:
        departamento = st.text_input("Depto. Solicitante", placeholder="Almacén, Compras…")
        estado       = st.selectbox("Estado *", ["Pendiente", "En Proceso", "Aprobada", "Rechazada", "Entregada"])
    with col3:
        prioridad  = st.selectbox("Prioridad", ["Normal", "Urgente"])
        referencia = st.text_input("Referencia (opcional)", placeholder="N° interno")

    compania = st.text_input("Compañía", value="Mendoza Servicios y Herramientas")
    obs = st.text_area("Observaciones / Especificaciones Adicionales",
                        placeholder="Referencia, especificaciones técnicas u observaciones generales…", height=70)

    st.divider()
    st.markdown("##### Partidas de la Requisición")
    partidas_data = _editor_partidas("nueva")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Crear Requisición", type="primary", width="stretch"):
            if not solicitante.strip():
                st.error("El campo Solicitante es obligatorio.")
            else:
                payload_partidas, costo_total = _construir_payloads("", partidas_data)
                if not payload_partidas:
                    st.error("Agrega al menos una partida con Descripción.")
                else:
                    folio = generar_folio()
                    for p in payload_partidas:
                        p["folio_req"] = folio

                    payload_req = {
                        "folio":            folio,
                        "fecha_solicitud":  fecha_sol.strftime('%d/%m/%Y'),
                        "solicitante":      solicitante.strip(),
                        "departamento":     departamento.strip(),
                        "compania":         compania.strip(),
                        "estado":           estado,
                        "prioridad":        prioridad,
                        "referencia":       referencia.strip(),
                        "observaciones":    obs.strip(),
                        "num_partidas":     len(payload_partidas),
                        "costo_total":      costo_total,
                    }

                    if agregar_requisicion(payload_req):
                        agregar_partidas(payload_partidas)
                        registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"NUEVA REQ: {folio}")
                        st.session_state["ultimo_editado"] = folio
                        st.session_state.pop("_nueva_n", None)
                        st.rerun()
                    else:
                        st.error("Error al guardar. Verifica la conexión.")
    with c2:
        if st.button("❌ Cancelar", width="stretch"):
            st.session_state.pop("_nueva_n", None)
            st.rerun()


@st.dialog("⚠️ Confirmar Eliminación")
def ventana_confirmar_eliminacion():
    folio = st.session_state.get("_del_folio", "")
    sol   = st.session_state.get("_del_sol", "")
    folio_visual = str(folio).replace("REQ-", "#")
    st.markdown(f"""
        <div style="background:#FEF2F2; border:1px solid #FECACA; border-left:4px solid #EF4444;
                    border-radius:8px; padding:14px 16px; margin-bottom:14px;">
            <div style="font-size:14px; font-weight:700; color:#991B1B; margin-bottom:6px;">
                ¿Eliminar esta requisición permanentemente?</div>
            <div style="font-size:12px; color:#7F1D1D; line-height:1.7;">
                📋 <b>Folio:</b> {folio_visual}<br>
                👤 <b>Solicitante:</b> {sol}
            </div>
        </div>
        <div style="font-size:11px; color:#94A3B8; margin-bottom:4px;">
            Esta acción <b>no se puede deshacer</b>. Se eliminarán también todas las partidas.</div>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Sí, eliminar", type="primary", width="stretch"):
            if eliminar_requisicion(folio):
                registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"ELIMINAR REQ: {folio}")
                st.session_state["ultimo_editado"] = ""
                st.session_state["_del_folio"] = ""
                st.rerun()
            else:
                st.error("Error al eliminar.")
    with c2:
        if st.button("↩️ Cancelar", width="stretch"):
            st.session_state["_del_folio"] = ""
            st.rerun()


@st.dialog("👁️ Ver Requisición", width="large")
def ventana_ver_requisicion(folio, datos):
    folio_vis  = str(folio).replace("REQ-", "#")
    partidas   = cargar_partidas(folio)
    entregas   = cargar_entregas(folio)
    partidas   = calcular_estado_partidas(partidas, entregas)
    en_urgente = str(datos.get('prioridad', '')).upper() == 'URGENTE'

    chips = f'<span class="dialog-folio-chip">📋 Folio {folio_vis}</span>'
    if en_urgente:
        chips += '<span class="dialog-urgente-chip">🚨 Urgente</span>'
    st.markdown(chips, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Solicitante:** {datos.get('solicitante', '—')}")
        st.markdown(f"**Departamento:** {datos.get('departamento', '—')}")
        st.markdown(f"**Compañía:** {datos.get('compania', '—')}")
    with c2:
        st.markdown(f"**Fecha:** {datos.get('fecha_solicitud', '—')}")
        st.markdown(f"**Estado:** `{datos.get('estado', '—')}`")
        st.markdown(f"**Prioridad:** `{datos.get('prioridad', '—')}`")

    if datos.get('referencia'):
        st.markdown(f"**Referencia:** {datos.get('referencia')}")
    if datos.get('observaciones'):
        st.markdown(f"**Observaciones:** {datos.get('observaciones')}")

    st.divider()
    st.markdown("##### Partidas")
    if partidas:
        h_cols = st.columns([0.5, 1.8, 1, 1, 3, 1.1, 1.1])
        for hdr, col in zip(["No.", "Catálogo", "Cant.", "Unidad", "Descripción", "Costo", "Entregado"], h_cols):
            col.markdown(f"<p class='th'>{hdr}</p>", unsafe_allow_html=True)
        for i, p in enumerate(partidas):
            cls = "td-alt" if i % 2 == 1 else "td"
            r = st.columns([0.5, 1.8, 1, 1, 3, 1.1, 1.1])
            r[0].markdown(f"<div class='{cls}' style='text-align:center;'>{p.get('numero','')}</div>", unsafe_allow_html=True)
            r[1].markdown(f"<div class='{cls}'>{p.get('partida_catalogo','') or '—'}</div>", unsafe_allow_html=True)
            r[2].markdown(f"<div class='{cls}' style='text-align:center;'>{p.get('cantidad','')}</div>", unsafe_allow_html=True)
            r[3].markdown(f"<div class='{cls}' style='text-align:center;'>{p.get('unidad','') or '—'}</div>", unsafe_allow_html=True)
            r[4].markdown(f"<div class='{cls}'>{p.get('descripcion','')}</div>", unsafe_allow_html=True)
            costo_fmt = f"${p.get('costo'):,.2f}" if p.get('costo') else '—'
            r[5].markdown(f"<div class='{cls}' style='text-align:center;'>{costo_fmt}</div>", unsafe_allow_html=True)

            entregado_t = p.get('entregado_total', 0)
            cant_pedida = p.get('cantidad', 0)
            estado_ent  = p.get('estado_entrega', 'Pendiente')
            frac_cls = {"Pendiente": "frac-pendiente", "Parcial": "frac-parcial", "Completo": "frac-completo"}.get(estado_ent, "frac-pendiente")
            unidad_p = p.get('unidad', '') or ''
            frac_txt = f"{entregado_t:g}/{cant_pedida:g} {unidad_p}".strip()
            r[6].markdown(f"<div class='{cls}' style='text-align:center;'><span class='{frac_cls}'>{frac_txt}</span></div>", unsafe_allow_html=True)
    else:
        st.info("No hay partidas registradas para esta requisición.")

    # ── Historial de entregas registradas ──
    if entregas:
        st.divider()
        st.markdown("##### Historial de entregas")
        partidas_by_id = {p.get('id'): p for p in partidas}
        for e in entregas:
            p_ref = partidas_by_id.get(e.get('partida_id'), {})
            desc_p = p_ref.get('descripcion', '—')
            nota_html = f" · {e.get('nota','')}" if e.get('nota') else ""
            if es_admin:
                ce_row, ce_btn = st.columns([9, 1])
                with ce_row:
                    st.markdown(f"""
                        <div class="entrega-row">
                            <span>📅 <b>{e.get('fecha_entrega','—')}</b> · {desc_p} · cantidad: <b>{e.get('cantidad','')}</b>{nota_html}</span>
                        </div>
                    """, unsafe_allow_html=True)
                with ce_btn:
                    if st.button("🗑️", key=f"del_entrega_{e.get('id')}", help="Eliminar esta entrega", width="stretch"):
                        if eliminar_entrega(e.get('id')):
                            registrar_acceso(st.session_state["usuario"], st.session_state["nombre"],
                                              f"ELIMINAR ENTREGA REQ: {folio}")
                            st.rerun()
            else:
                st.markdown(f"""
                    <div class="entrega-row">
                        <span>📅 <b>{e.get('fecha_entrega','—')}</b> · {desc_p} · cantidad: <b>{e.get('cantidad','')}</b>{nota_html}</span>
                    </div>
                """, unsafe_allow_html=True)

    # ── Registrar nueva entrega (solo admin, solo si hay partidas pendientes/parciales) ──
    if es_admin and partidas:
        pendientes_o_parciales = [p for p in partidas if p.get('estado_entrega') != 'Completo']
        if pendientes_o_parciales:
            st.divider()
            st.markdown("##### Registrar entrega")
            opciones = {
                f"{p['numero']} · {p.get('descripcion','')} (faltan {p.get('cantidad',0) - p.get('entregado_total',0):g} {p.get('unidad','') or ''})": p
                for p in pendientes_o_parciales
            }
            sel_label = st.selectbox("Partida a entregar", list(opciones.keys()), key=f"sel_partida_{folio}")
            p_sel = opciones[sel_label]
            ce1, ce2, ce3 = st.columns([1, 1, 2])
            with ce1:
                cant_entrega = st.text_input("Cantidad entregada *", key=f"cant_entrega_{folio}",
                                              value=str(p_sel.get('cantidad', 0) - p_sel.get('entregado_total', 0)))
            with ce2:
                fecha_entrega = st.date_input("Fecha de entrega *", value=datetime.now(), format="DD/MM/YYYY",
                                               key=f"fecha_entrega_{folio}")
            with ce3:
                nota_entrega = st.text_input("Nota (opcional)", key=f"nota_entrega_{folio}",
                                              placeholder="Proveedor, factura, observación...")
            if st.button("✅ Registrar entrega", type="primary", key=f"btn_entrega_{folio}"):
                try:
                    cant_val = float(str(cant_entrega).replace(',', ''))
                except:
                    cant_val = 0
                restante = p_sel.get('cantidad', 0) - p_sel.get('entregado_total', 0)
                if cant_val <= 0:
                    st.error("La cantidad entregada debe ser mayor a 0.")
                elif cant_val > restante + 0.0001:
                    st.error(f"No puedes entregar más de lo pendiente ({restante:g}).")
                else:
                    ok = agregar_entrega({
                        "partida_id":     p_sel.get('id'),
                        "folio_req":      folio,
                        "cantidad":       cant_val,
                        "fecha_entrega":  fecha_entrega.strftime('%d/%m/%Y'),
                        "nota":           nota_entrega.strip(),
                        "registrado_por": st.session_state.get("nombre", ""),
                    })
                    if ok:
                        registrar_acceso(st.session_state["usuario"], st.session_state["nombre"],
                                          f"ENTREGA REQ: {folio} / partida {p_sel.get('numero')}")
                        st.rerun()
                    else:
                        st.error("Error al registrar la entrega. Verifica la conexión.")

    st.divider()
    col_pdf, col_cerrar = st.columns(2)
    with col_pdf:
        pdf_bytes = generar_pdf_requisicion(datos, partidas)
        st.download_button(
            "📄 Descargar PDF", data=pdf_bytes,
            file_name=f"requisicion_{folio_vis.replace('#','')}.pdf",
            mime="application/pdf", width="stretch",
        )
    with col_cerrar:
        if st.button("❌ Cerrar", width="stretch"):
            st.rerun()


@st.dialog("✏️ Modificar Requisición", width="large")
def ventana_editar_requisicion(folio, datos):
    folio_vis  = str(folio).replace("REQ-", "#")
    en_urgente = str(datos.get('prioridad', '')).upper() == 'URGENTE'
    chips = f'<span class="dialog-folio-chip">📋 Folio {folio_vis}</span>'
    if en_urgente:
        chips += '<span class="dialog-urgente-chip">🚨 Urgente</span>'
    st.markdown(chips, unsafe_allow_html=True)

    try:
        fecha_def = datetime.strptime(str(datos.get('fecha_solicitud', '')), '%d/%m/%Y')
    except:
        fecha_def = datetime.now()

    col1, col2, col3 = st.columns(3)
    with col1:
        nueva_fecha = st.date_input("Fecha de Solicitud *", value=fecha_def, format="DD/MM/YYYY")
        nuevo_sol   = st.text_input("Solicitante *", value=datos.get('solicitante', ''))
    with col2:
        nuevo_dep  = st.text_input("Departamento", value=datos.get('departamento', ''))
        estados_op = ["Pendiente", "En Proceso", "Aprobada", "Rechazada", "Entregada"]
        est_idx    = estados_op.index(datos.get('estado', 'Pendiente')) if datos.get('estado') in estados_op else 0
        nuevo_est  = st.selectbox("Estado *", estados_op, index=est_idx)
    with col3:
        priors_op   = ["Normal", "Urgente"]
        prior_idx   = priors_op.index(datos.get('prioridad', 'Normal')) if datos.get('prioridad') in priors_op else 0
        nueva_prior = st.selectbox("Prioridad", priors_op, index=prior_idx)
        nueva_ref   = st.text_input("Referencia", value=datos.get('referencia', ''))

    nueva_comp = st.text_input("Compañía", value=datos.get('compania', 'Mendoza Servicios y Herramientas'))
    nueva_obs  = st.text_area("Observaciones", value=datos.get('observaciones', ''), height=70)

    st.divider()
    st.markdown("##### Partidas de la Requisición")
    partidas_existentes = cargar_partidas(folio)
    entregas_existentes = cargar_entregas(folio)
    partidas_con_entregas = {e["partida_id"] for e in entregas_existentes}
    if partidas_con_entregas:
        st.caption("⚠️ Algunas partidas ya tienen entregas registradas. Si quitas una partida con entregas, ese historial se perderá.")
    partidas_iniciales = [{
        "id": p.get("id"),
        "partida_catalogo": p.get("partida_catalogo", ""),
        "cantidad": p.get("cantidad", 1),
        "unidad": p.get("unidad", ""),
        "descripcion": p.get("descripcion", ""),
        "costo": p.get("costo", ""),
    } for p in partidas_existentes]
    partidas_data = _editor_partidas(f"editar_{folio}", partidas_iniciales)

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💾 Guardar Cambios", type="primary", width="stretch"):
            if not nuevo_sol.strip():
                st.error("Solicitante es obligatorio.")
            else:
                payload_partidas, costo_total = _construir_payloads(folio, partidas_data)
                payload = {
                    "fecha_solicitud": nueva_fecha.strftime('%d/%m/%Y'),
                    "solicitante":     nuevo_sol.strip(),
                    "departamento":    nuevo_dep.strip(),
                    "compania":        nueva_comp.strip(),
                    "estado":          nuevo_est,
                    "prioridad":       nueva_prior,
                    "referencia":      nueva_ref.strip(),
                    "observaciones":   nueva_obs.strip(),
                    "num_partidas":    len(payload_partidas),
                    "costo_total":     costo_total,
                }
                if modificar_requisicion(folio, payload):
                    sincronizar_partidas(folio, payload_partidas)
                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"MODIFICAR REQ: {folio}")
                    st.session_state["ultimo_editado"] = folio
                    st.session_state.pop(f"_editar_{folio}_n", None)
                    st.rerun()
    with c2:
        if st.button("🗑️ Eliminar Registro", width="stretch"):
            st.session_state["_del_folio"] = folio
            st.session_state["_del_sol"]   = datos.get('solicitante', '')
            st.rerun()
    with c3:
        if st.button("❌ Cerrar", width="stretch"):
            st.session_state.pop(f"_editar_{folio}_n", None)
            st.rerun()

# ══════════════════════════════════════════════
# SESSION STATE LOCAL
# ══════════════════════════════════════════════
for key, val in [
    ("ultimo_editado", ""), ("pagina_actual", 1),
    ("_limpiar_fechas", False), ("_del_folio", ""), ("_del_sol", ""),
    ("_fecha_key_ver", 0),
]:
    if key not in st.session_state:
        st.session_state[key] = val

# ══════════════════════════════════════════════
# VARIABLES DE SESIÓN
# ══════════════════════════════════════════════
nombre_actual  = st.session_state.get("nombre", "")
rol_actual     = st.session_state.get("rol", "")
usuario_actual = st.session_state.get("usuario", "")
es_admin       = rol_actual == "admin"
iniciales      = "".join([p[0].upper() for p in nombre_actual.split()[:2]])

# ══════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════
st.markdown(f"""
    <div class="msh-header">
        <div class="msh-header-left">
            <div class="msh-logo-box">📋</div>
            <div>
                <div class="msh-title">MSH-Hub · Requisiciones de Compra</div>
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

# Botón regresar + salir
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

# ── Disparador eliminación ──
if st.session_state.get("_del_folio"):
    ventana_confirmar_eliminacion()

# ══════════════════════════════════════════════
# CARGA DE DATOS
# ══════════════════════════════════════════════
df_master = pd.DataFrame(cargar_requisiciones())
if not df_master.empty:
    if 'prioridad' not in df_master.columns:
        df_master['prioridad'] = 'Normal'
    if 'referencia' not in df_master.columns:
        df_master['referencia'] = ''
    df_master['referencia'] = df_master['referencia'].fillna('')

_folios_pendientes = folios_con_entrega_pendiente() if not df_master.empty else set()

# ══════════════════════════════════════════════
# KPIs
# ══════════════════════════════════════════════
total     = len(df_master) if not df_master.empty else 0
pend      = len(df_master[df_master['estado'] == 'Pendiente'])    if not df_master.empty else 0
proceso   = len(df_master[df_master['estado'] == 'En Proceso'])   if not df_master.empty else 0
aprobada  = len(df_master[df_master['estado'] == 'Aprobada'])     if not df_master.empty else 0
entregada = len(df_master[df_master['estado'] == 'Entregada'])    if not df_master.empty else 0
urgentes  = len(df_master[df_master['prioridad'].str.upper() == 'URGENTE']) if not df_master.empty else 0

st.markdown(f"""
    <div class="kpi-bar">
        <div class="kpi-pill">
            <span class="kpi-icon">📋</span>
            <span class="kpi-val" style="color:#1E293B;">{total}</span>
            <span class="kpi-lbl">Total</span>
        </div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill">
            <span class="kpi-icon">⏳</span>
            <span class="kpi-val" style="color:#C2410C;">{pend}</span>
            <span class="kpi-lbl">Pendientes</span>
        </div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill">
            <span class="kpi-icon">🔄</span>
            <span class="kpi-val" style="color:#1D4ED8;">{proceso}</span>
            <span class="kpi-lbl">En Proceso</span>
        </div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill">
            <span class="kpi-icon">✅</span>
            <span class="kpi-val" style="color:#15803D;">{aprobada}</span>
            <span class="kpi-lbl">Aprobadas</span>
        </div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill">
            <span class="kpi-icon">📦</span>
            <span class="kpi-val" style="color:#7E22CE;">{entregada}</span>
            <span class="kpi-lbl">Entregadas</span>
        </div>
        <div class="kpi-sep"></div>
        <div class="kpi-alert-pill">
            <span class="kpi-icon">🚨</span>
            <span class="kpi-val" style="color:#B91C1C;">{urgentes}</span>
            <span class="kpi-lbl" style="color:#B91C1C;">Urgentes</span>
        </div>
    </div>
""", unsafe_allow_html=True)

if urgentes > 0:
    st.markdown(f"""
        <div class="alert-banner">
            🚨 <strong>{urgentes} requisición{'es' if urgentes > 1 else ''} urgente{'s' if urgentes > 1 else ''}</strong>
            — revisa las filas marcadas en rojo antes de continuar.
        </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# PANEL DE CONTROLES (tarjeta: Filtros y búsqueda)
# ══════════════════════════════════════════════
panel_filtros = st.container(key="panel_filtros")
with panel_filtros:
    st.markdown('<div class="panel-card-titulo">🔍 Filtros y búsqueda</div>', unsafe_allow_html=True)

    c_busq, c_est, c_prior, c_nuevo = st.columns([3.5, 2, 1.5, 1.5])
    with c_busq:
        busqueda = st.text_input(
            "buscar", placeholder="🔍  Buscar por folio, solicitante, departamento o referencia...",
            label_visibility="collapsed"
        )
    with c_est:
        filtro_est = st.selectbox(
            "estado", ["Todos", "Pendiente", "En Proceso", "Aprobada", "Rechazada", "Entregada"],
            label_visibility="collapsed"
        )
    with c_prior:
        filtro_prior = st.selectbox(
            "prioridad", ["Todas", "Normal", "Urgente"],
            label_visibility="collapsed"
        )
    with c_nuevo:
        if es_admin:
            if st.button("➕ Nueva Requisición", type="primary", width="stretch"):
                ventana_nueva_requisicion()

    c_prod, _sp = st.columns([3.5, 5.5])
    with c_prod:
        busqueda_producto = st.text_input(
            "buscar_producto", placeholder="📦  Buscar por producto (ej. thinner, guantes, cable...)",
            label_visibility="collapsed"
        )

    if st.session_state.get("_limpiar_fechas"):
        st.session_state["_limpiar_fechas"] = False
        st.session_state["_fecha_key_ver"] = st.session_state.get("_fecha_key_ver", 0) + 1

    _fver = st.session_state.get("_fecha_key_ver", 0)
    c_f1, c_f2, c_f3, c_csv, c_pdf = st.columns([1.5, 1.5, 1.5, 1.2, 1.2])
    with c_f1:
        st.caption("📅 Desde")
        fecha_desde = st.date_input("desde", value=None, format="DD/MM/YYYY",
            label_visibility="collapsed", key=f"fecha_desde_{_fver}")
    with c_f2:
        st.caption("📅 Hasta")
        fecha_hasta = st.date_input("hasta", value=None, format="DD/MM/YYYY",
            label_visibility="collapsed", key=f"fecha_hasta_{_fver}")
    with c_f3:
        st.caption("🔁 Limpiar fechas")
        if st.button("🔄 Limpiar fechas", width="stretch"):
            st.session_state["_limpiar_fechas"] = True
            st.rerun()
    with c_csv:
        if not df_master.empty:
            st.caption("⬇️ Exportar")
            st.download_button(
                "📥 CSV", data=df_master.to_csv(index=False).encode('utf-8'),
                file_name=f"requisiciones_{datetime.now().strftime('%d%m%Y')}.csv",
                mime="text/csv", width="stretch"
            )
    with c_pdf:
        if not df_master.empty:
            st.caption("⬇️ Reporte")
            st.download_button(
                "📕 PDF", data=generar_pdf_listado(df_master, nombre_actual),
                file_name=f"reporte_req_{datetime.now().strftime('%d%m%Y')}.pdf",
                mime="application/pdf", width="stretch"
            )

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# FILTRADO
# ══════════════════════════════════════════════
df_f = df_master.copy() if not df_master.empty else pd.DataFrame()
if not df_f.empty:
    if busqueda.strip():
        df_f = df_f[
            df_f['solicitante'].str.contains(busqueda, case=False, na=False) |
            df_f['departamento'].str.contains(busqueda, case=False, na=False) |
            df_f['folio'].str.contains(busqueda, case=False, na=False) |
            df_f['referencia'].str.contains(busqueda, case=False, na=False)
        ]
    if filtro_est != "Todos":
        df_f = df_f[df_f['estado'] == filtro_est]
    if filtro_prior != "Todas":
        df_f = df_f[df_f['prioridad'].str.capitalize() == filtro_prior]
    if busqueda_producto.strip():
        folios_match = buscar_folios_por_producto(busqueda_producto)
        if folios_match is not None:
            df_f = df_f[df_f['folio'].isin(folios_match)]
    if fecha_desde or fecha_hasta:
        def en_rango(fecha_str):
            f = parsear_fecha(fecha_str)
            if not f: return False
            if fecha_desde and f < fecha_desde: return False
            if fecha_hasta and f > fecha_hasta: return False
            return True
        df_f = df_f[df_f['fecha_solicitud'].apply(en_rango)]
    filtro_key = f"{busqueda}|{filtro_est}|{filtro_prior}|{busqueda_producto}|{fecha_desde}|{fecha_hasta}"
    if filtro_key != st.session_state.get("_fkey", ""):
        st.session_state["pagina_actual"] = 1
        st.session_state["_fkey"] = filtro_key

# ══════════════════════════════════════════════
# TABLA (tarjeta: Historial de requisiciones)
# ══════════════════════════════════════════════
if not df_f.empty:
    IPP = 15
    total_filas = len(df_f)
    total_pags  = max(1, -(-total_filas // IPP))
    pag         = st.session_state["pagina_actual"]
    df_pag      = df_f.iloc[(pag - 1) * IPP : pag * IPP]

    cw  = [0.85, 0.8, 1.7, 1.5, 1.3, 0.55, 1.1, 0.95, 1.0, 0.5, 0.5] if es_admin else [0.85, 0.8, 1.7, 1.5, 1.3, 0.55, 1.1, 0.95, 1.0, 0.5]
    ths = ["Fecha", "Folio", "Solicitante", "Departamento", "Referencia", "Part.", "Estado", "Prioridad", "Costo Total", "👁️", "✏️"] if es_admin else \
          ["Fecha", "Folio", "Solicitante", "Departamento", "Referencia", "Part.", "Estado", "Prioridad", "Costo Total", "👁️"]

    panel_tabla = st.container(key="panel_tabla")
    with panel_tabla:
        st.markdown("""
            <div class="panel-card-titulo">📋 Historial de requisiciones</div>
            <div class="panel-card-subtitulo">Consulta y administración de requisiciones de compra</div>
        """, unsafe_allow_html=True)

        h_cols = st.columns(cw)
        for idx, (col, txt) in enumerate(zip(h_cols, ths)):
            estilo = " style='text-align:center;'" if idx in (9, 10) else ""
            col.markdown(f"<p class='th'{estilo}>{txt}</p>", unsafe_allow_html=True)

        for i, (_, row) in enumerate(df_pag.iterrows()):
            folio_f    = row['folio']
            folio_corto = "#" + str(folio_f).replace("REQ-", "")[-9:]
            es_urgente  = str(row.get('prioridad', '')).upper() == 'URGENTE'
            es_ult      = folio_f == st.session_state.get("ultimo_editado", "")

            if es_ult:        cls = "td-hl"
            elif es_urgente:  cls = "td-urgente"
            elif i % 2 == 1:  cls = "td-alt"
            else:             cls = "td"

            r = st.columns(cw)
            r[0].markdown(f"<div class='{cls}'>{row.get('fecha_solicitud', '')}</div>", unsafe_allow_html=True)
            folio_html = f"<span class='folio-tag-urgente'>{folio_corto}</span>" if es_urgente else f"<span class='folio-tag'>{folio_corto}</span>"
            r[1].markdown(f"<div class='{cls}'>{folio_html}</div>", unsafe_allow_html=True)
            r[2].markdown(f"<div class='{cls}'><b>{row.get('solicitante', '')}</b></div>", unsafe_allow_html=True)
            r[3].markdown(f"<div class='{cls}'>{row.get('departamento', '') or '—'}</div>", unsafe_allow_html=True)
            ref_val = truncar_palabra(row.get('referencia', ''), limite=18) or "—"
            r[4].markdown(f"<div class='{cls}'>{ref_val}</div>", unsafe_allow_html=True)
            tiene_pendiente = folio_f in _folios_pendientes
            indicador = " <span title='Tiene partidas sin entregar por completo' style='color:#C2410C;'>⚠️</span>" if tiene_pendiente else ""
            r[5].markdown(f"<div class='{cls}' style='text-align:center;'>{row.get('num_partidas', 0)}{indicador}</div>", unsafe_allow_html=True)

            est = row.get('estado', 'Pendiente')
            badge_map = {"Pendiente": "badge-pendiente", "En Proceso": "badge-proceso",
                         "Aprobada": "badge-aprobada", "Rechazada": "badge-rechazada", "Entregada": "badge-entregada"}
            r[6].markdown(f"<div class='{cls}'><span class='badge {badge_map.get(est, 'badge-pendiente')}'>{est}</span></div>", unsafe_allow_html=True)

            prior_cls = "badge-urgente" if es_urgente else "badge-proceso"
            r[7].markdown(f"<div class='{cls}'><span class='badge {prior_cls}'>{row.get('prioridad', 'Normal')}</span></div>", unsafe_allow_html=True)

            ct = row.get('costo_total', 0)
            costo_fmt = f"${float(ct):,.2f}" if ct else "—"
            r[8].markdown(f"<div class='{cls}'>{costo_fmt}</div>", unsafe_allow_html=True)

            with r[9]:
                if st.button("👁️", key=f"ver_{folio_f}", help=f"Ver {folio_corto}", width="stretch"):
                    ventana_ver_requisicion(folio_f, row.to_dict())

            if es_admin:
                with r[10]:
                    if st.button("✏️", key=f"ed_{folio_f}", help=f"Editar {folio_corto}", width="stretch"):
                        ventana_editar_requisicion(folio_f, row.to_dict())

        # ── PAGINACIÓN ──
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        p1, p2, p3, p4, p5 = st.columns([1, 1, 3, 1, 1])
        with p1:
            if st.button("⏮", disabled=(pag == 1), width="stretch", help="Primera página"):
                st.session_state["pagina_actual"] = 1; st.rerun()
        with p2:
            if st.button("◀", disabled=(pag == 1), width="stretch", help="Página anterior"):
                st.session_state["pagina_actual"] -= 1; st.rerun()
        p3.markdown(f"<p class='pg-info'>Página <b>{pag}</b> de <b>{total_pags}</b> &nbsp;·&nbsp; <b>{total_filas}</b> registros</p>", unsafe_allow_html=True)
        with p4:
            if st.button("▶", disabled=(pag == total_pags), width="stretch", help="Página siguiente"):
                st.session_state["pagina_actual"] += 1; st.rerun()
        with p5:
            if st.button("⏭", disabled=(pag == total_pags), width="stretch", help="Última página"):
                st.session_state["pagina_actual"] = total_pags; st.rerun()

elif not df_master.empty:
    st.info("🔍 No se encontraron requisiciones con los filtros aplicados.")
else:
    st.info("📭 No hay requisiciones registradas. ¡Crea la primera!")
