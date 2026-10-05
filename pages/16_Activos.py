import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw
import io

st.set_page_config(
    page_title="MSH-Hub | Activos",
    layout="wide",
    page_icon="🔧",
    initial_sidebar_state="collapsed"
)

# ── Protección ──
if not st.session_state.get("autenticado"):
    st.switch_page("app.py")

# ══════════════════════════════════════════════
# CSS: mismo lenguaje visual del resto de MSH-Hub
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
.badge-disponible   { background:#DCFCE7; color:#15803D; }
.badge-prestado     { background:#EFF6FF; color:#1D4ED8; }
.badge-custodia     { background:#F3E8FF; color:#7E22CE; }
.badge-mantenimiento{ background:#FEF3E8; color:#C2410C; }
.badge-entregado    { background:#E0F2FE; color:#0369A1; }
.badge-inactivo     { background:#F1F5F9; color:#64748B; }
.badge-reservado    { background:#FEF9C3; color:#854D0E; }
.badge-activo-si    { background:#DCFCE7; color:#15803D; }
.badge-activo-no    { background:#FEE2E2; color:#B91C1C; }
.folio-tag {
    font-family: 'DM Mono', monospace; font-size: 10px; color: #94A3B8;
    background: #F1F5F9; border-radius: 4px; padding: 1px 5px; display: inline-block;
}
.panel-card-titulo { font-size: 15px; font-weight: 700; color: #1E293B; margin-bottom: 2px; }
.panel-card-subtitulo { font-size: 12px; color: #94A3B8; margin-bottom: 16px; }
div[class*="st-key-panel_filtros"],
div[class*="st-key-panel_tabla"] {
    background: #ffffff; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 22px 24px; margin-bottom: 18px;
    box-shadow: 0 2px 10px rgba(30,52,71,0.06);
}
div[data-testid="stDialog"] div[role="dialog"] {
    width: 55vw !important; max-width: 720px !important;
    min-width: 420px !important; border-radius: 16px !important;
    max-height: 85vh !important; overflow-y: auto !important;
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

# ══════════════════════════════════════════════
# CONEXIÓN SUPABASE
# ══════════════════════════════════════════════
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://unsugrcleytqroxuuhaf.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

ESTADOS = ["disponible", "prestado", "mantenimiento", "inactivo", "reservado", "custodia", "entregado"]
ESTADO_LABELS = {
    "disponible": "🟢 Disponible", "prestado": "🔵 Prestado", "mantenimiento": "🟠 Mantenimiento",
    "inactivo": "⚪ Inactivo", "reservado": "🟡 Reservado", "custodia": "🟣 Custodia", "entregado": "🔷 Entregado",
}


# ══════════════════════════════════════════════
# FUNCIONES DE ACCESO A DATOS
# ══════════════════════════════════════════════
def registrar_acceso(usuario, nombre, accion):
    try:
        supabase.table("usuarios_accesos").insert({
            "usuario": usuario, "nombre": nombre,
            "accion": accion, "fecha_hora": datetime.now().isoformat()
        }).execute()
    except:
        pass


def generar_etiqueta_codigo(codigo, texto_secundario=None):
    rv = io.BytesIO()
    clase_barcode = barcode.get_barcode_class("code128")
    codigo_gen = clase_barcode(codigo, writer=ImageWriter())
    codigo_gen.write(rv, options={"write_text": False, "module_height": 9, "quiet_zone": 2})
    rv.seek(0)
    img_barcode = Image.open(rv).convert("RGB")

    alto_texto = 42 if texto_secundario else 22
    lienzo = Image.new("RGB", (img_barcode.width, img_barcode.height + alto_texto + 14), "white")
    lienzo.paste(img_barcode, (0, 6))

    draw = ImageDraw.Draw(lienzo)
    draw.text((10, img_barcode.height + 10), codigo, fill="black")
    if texto_secundario:
        draw.text((10, img_barcode.height + 26), texto_secundario[:42], fill="black")

    out = io.BytesIO()
    lienzo.save(out, format="PNG")
    return out.getvalue()


def cargar_productos_tipo_activo():
    try:
        res = supabase.table("almacen_productos").select("id, codigo, nombre").eq("tipo_producto", "activo").eq("activo", True).order("nombre").execute()
        return res.data if res.data else []
    except:
        return []


def cargar_ubicaciones_activas():
    try:
        res = supabase.table("almacen_ubicaciones").select("*").eq("activo", True).order("nivel").order("nombre").execute()
        registros = res.data if res.data else []
        lookup = {r["id"]: r for r in registros}

        def breadcrumb(id_reg):
            partes, actual, vistos = [], lookup.get(id_reg), set()
            while actual and actual["id"] not in vistos:
                vistos.add(actual["id"])
                partes.append(actual["nombre"])
                actual = lookup.get(actual.get("ubicacion_padre"))
            return " > ".join(reversed(partes))

        return [{"id": r["id"], "breadcrumb": breadcrumb(r["id"])} for r in registros]
    except:
        return []


def cargar_activos(pagina=0, tam_pagina=50, busqueda="", filtro_producto_id=None, filtro_estado="Todos", incluir_baja=False):
    try:
        q = supabase.table("almacen_activos").select(
            "*, almacen_productos(codigo, nombre), almacen_ubicaciones(nombre), almacen_personas(nombres, apellidos)",
            count="exact"
        )
        if not incluir_baja:
            q = q.eq("activo", True)
        if busqueda.strip():
            q = q.or_(f"codigo_activo.ilike.%{busqueda}%,serial.ilike.%{busqueda}%")
        if filtro_producto_id:
            q = q.eq("producto_id", filtro_producto_id)
        if filtro_estado != "Todos":
            q = q.eq("estado", filtro_estado)
        inicio = pagina * tam_pagina
        fin = inicio + tam_pagina - 1
        res = q.order("codigo_activo").range(inicio, fin).execute()
        data = res.data if res.data else []
        for row in data:
            p = row.pop("almacen_productos", None)
            u = row.pop("almacen_ubicaciones", None)
            resp = row.pop("almacen_personas", None)
            row["producto_codigo"] = p["codigo"] if p else "—"
            row["producto_nombre"] = p["nombre"] if p else "—"
            row["ubicacion_nombre"] = u["nombre"] if u else "—"
            row["responsable_nombre"] = f"{resp['nombres']} {resp.get('apellidos') or ''}".strip() if resp else "—"
        return data, (res.count or 0)
    except Exception as e:
        st.error(f"Error al cargar activos: {e}")
        return [], 0


def contar_activos(filtro_estado=None, incluir_baja=False):
    try:
        q = supabase.table("almacen_activos").select("id", count="exact")
        if not incluir_baja:
            q = q.eq("activo", True)
        if filtro_estado:
            q = q.eq("estado", filtro_estado)
        res = q.range(0, 0).execute()
        return res.count or 0
    except:
        return 0


def actualizar_activo(id_registro, payload):
    try:
        supabase.table("almacen_activos").update(payload).eq("id", id_registro).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar el activo: {e}")
        return False


def dar_de_baja_activo(id_registro):
    try:
        supabase.table("almacen_activos").update({"activo": False, "estado": "inactivo"}).eq("id", id_registro).execute()
        return True
    except Exception as e:
        st.error(f"Error al dar de baja el activo: {e}")
        return False


def reactivar_activo(id_registro):
    try:
        supabase.table("almacen_activos").update({"activo": True, "estado": "disponible"}).eq("id", id_registro).execute()
        return True
    except Exception as e:
        st.error(f"Error al reactivar el activo: {e}")
        return False


def cargar_prestamo_activo_de(activo_id):
    try:
        res = supabase.table("almacen_prestamos_inventario_detalle").select(
            "*, almacen_prestamos_inventario(folio, fecha_prestamo, fecha_estimada, estado)"
        ).eq("activo_id", activo_id).eq("devuelto", False).execute().data
        return res[0]["almacen_prestamos_inventario"] if res else None
    except:
        return None


def cargar_custodia_activa_de(activo_id):
    try:
        res = supabase.table("almacen_custodias").select("folio, fecha_inicio").eq("activo_id", activo_id).eq("estado", "activa").execute().data
        return res[0] if res else None
    except:
        return None


# ══════════════════════════════════════════════
# DIÁLOGOS
# ══════════════════════════════════════════════
@st.dialog("🏷️ Etiqueta de Activo")
def ventana_etiqueta_activo(activo):
    st.markdown(f"**{activo['producto_nombre']}**")
    st.caption(f"Código: {activo['codigo_activo']}")
    imagen_bytes = generar_etiqueta_codigo(activo["codigo_activo"], activo["producto_nombre"])
    st.image(imagen_bytes)
    st.download_button(
        "⬇️ Descargar etiqueta (PNG)", data=imagen_bytes,
        file_name=f"etiqueta_{activo['codigo_activo']}.png", mime="image/png",
        type="primary", width="stretch"
    )
    st.caption("Imprime esta imagen y pégala en la unidad física correspondiente.")
    if st.button("Cerrar", width="stretch"):
        st.rerun()


@st.dialog("✏️ Editar Activo")
def ventana_editar_activo(activo):
    ubicaciones = cargar_ubicaciones_activas()

    st.markdown(f"**{activo['producto_codigo']} — {activo['producto_nombre']}**")
    st.caption(f"Código de activo: `{activo['codigo_activo']}`")

    # Contexto: préstamo o custodia activa relacionada
    if activo["estado"] == "prestado":
        prestamo = cargar_prestamo_activo_de(activo["id"])
        if prestamo:
            st.info(f"📌 En préstamo activo: `{prestamo['folio']}` · Devolución estimada: {prestamo.get('fecha_estimada') or '—'}")
    elif activo["estado"] == "custodia":
        custodia = cargar_custodia_activa_de(activo["id"])
        if custodia:
            st.info(f"📌 En custodia activa: `{custodia['folio']}` desde {custodia['fecha_inicio']}")

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        serial = st.text_input("Serial", value=activo.get("serial") or "")
        condicion = st.selectbox("Condición", ["nuevo", "usado", "reacondicionado"],
                                   index=["nuevo", "usado", "reacondicionado"].index(activo.get("condicion", "nuevo")),
                                   format_func=lambda v: v.capitalize())
    with c2:
        opciones_ubi = {"— Sin especificar —": None, **{u["breadcrumb"]: u["id"] for u in ubicaciones}}
        label_actual = next((l for l, i in opciones_ubi.items() if i == activo.get("ubicacion_actual")), "— Sin especificar —")
        sel_ubi = st.selectbox("Ubicación actual", list(opciones_ubi.keys()), index=list(opciones_ubi.keys()).index(label_actual))
        ubicacion_id = opciones_ubi[sel_ubi]

        estado_actual_idx = ESTADOS.index(activo["estado"]) if activo["estado"] in ESTADOS else 0
        nuevo_estado = st.selectbox("Estado", ESTADOS, index=estado_actual_idx, format_func=lambda v: ESTADO_LABELS[v])
        if nuevo_estado != activo["estado"]:
            st.caption("⚠️ Cambiar el estado aquí NO actualiza préstamos/custodias asociados automáticamente. Úsalo solo para correcciones manuales.")

    observaciones = st.text_area("Observaciones", value=activo.get("observaciones") or "", height=70)

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💾 Guardar Cambios", type="primary", width="stretch"):
            payload = {
                "serial": serial.strip() or None, "condicion": condicion,
                "ubicacion_actual": ubicacion_id, "estado": nuevo_estado,
                "observaciones": observaciones.strip() or None,
            }
            if actualizar_activo(activo["id"], payload):
                registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"EDITAR ACTIVO: {activo['codigo_activo']}")
                st.session_state["_msg"] = f"Activo {activo['codigo_activo']} actualizado."
                st.rerun()
    with c2:
        if activo.get("activo", True):
            if st.button("🚫 Dar de Baja", width="stretch"):
                if dar_de_baja_activo(activo["id"]):
                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"DAR DE BAJA ACTIVO: {activo['codigo_activo']}")
                    st.session_state["_msg"] = f"Activo {activo['codigo_activo']} dado de baja."
                    st.rerun()
        else:
            if st.button("✅ Reactivar", width="stretch"):
                if reactivar_activo(activo["id"]):
                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"REACTIVAR ACTIVO: {activo['codigo_activo']}")
                    st.session_state["_msg"] = f"Activo {activo['codigo_activo']} reactivado."
                    st.rerun()
    with c3:
        if st.button("❌ Cerrar", width="stretch"):
            st.rerun()


# ══════════════════════════════════════════════
# SESIÓN / HEADER
# ══════════════════════════════════════════════
nombre_actual  = st.session_state.get("nombre", "")
rol_actual     = st.session_state.get("rol", "")
usuario_actual = st.session_state.get("usuario", "")
es_admin       = rol_actual == "admin"
iniciales      = "".join([p[0].upper() for p in nombre_actual.split()[:2]]) if nombre_actual else "AD"

st.markdown(f"""
    <div class="msh-header">
        <div class="msh-header-left">
            <div class="msh-logo-box">🔧</div>
            <div>
                <div class="msh-title">MSH-Hub · Almacén · Activos</div>
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

# ══════════════════════════════════════════════
# PANEL DE FILTROS
# ══════════════════════════════════════════════
productos_activos = cargar_productos_tipo_activo()

panel_filtros = st.container(key="panel_filtros")
with panel_filtros:
    st.markdown('<div class="panel-card-titulo">🔍 Filtros y búsqueda</div>', unsafe_allow_html=True)
    c_busq, c_prod, c_est, c_incl = st.columns([3, 2.5, 2, 1.8])
    with c_busq:
        busqueda = st.text_input("buscar", placeholder="🔍  Buscar por código o serial...", label_visibility="collapsed")
    with c_prod:
        opciones_prod = {"Todos los productos": None, **{f"{p['codigo']} — {p['nombre']}": p["id"] for p in productos_activos}}
        filtro_prod_label = st.selectbox("producto", list(opciones_prod.keys()), label_visibility="collapsed")
        filtro_prod_id = opciones_prod[filtro_prod_label]
    with c_est:
        filtro_est = st.selectbox("estado", ["Todos"] + ESTADOS, format_func=lambda v: "Todos" if v == "Todos" else ESTADO_LABELS[v], label_visibility="collapsed")
    with c_incl:
        incluir_baja = st.checkbox("Incluir dados de baja", value=False)

# ══════════════════════════════════════════════
# KPIs (consultas ligeras, no dependen de la página actual)
# ══════════════════════════════════════════════
total        = contar_activos(incluir_baja=incluir_baja)
disponibles  = contar_activos(filtro_estado="disponible", incluir_baja=incluir_baja)
prestados    = contar_activos(filtro_estado="prestado", incluir_baja=incluir_baja)
custodia     = contar_activos(filtro_estado="custodia", incluir_baja=incluir_baja)
mantenim     = contar_activos(filtro_estado="mantenimiento", incluir_baja=incluir_baja)
entregados   = contar_activos(filtro_estado="entregado", incluir_baja=incluir_baja)

st.markdown(f"""
    <div class="kpi-bar">
        <div class="kpi-pill"><span class="kpi-icon">🔧</span><span class="kpi-val" style="color:#1E293B;">{total}</span><span class="kpi-lbl">Total</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">🟢</span><span class="kpi-val" style="color:#15803D;">{disponibles}</span><span class="kpi-lbl">Disponibles</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">🔵</span><span class="kpi-val" style="color:#1D4ED8;">{prestados}</span><span class="kpi-lbl">Prestados</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">🟣</span><span class="kpi-val" style="color:#7E22CE;">{custodia}</span><span class="kpi-lbl">Custodia</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">🟠</span><span class="kpi-val" style="color:#C2410C;">{mantenim}</span><span class="kpi-lbl">Mantenimiento</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">🔷</span><span class="kpi-val" style="color:#0369A1;">{entregados}</span><span class="kpi-lbl">Entregados</span></div>
    </div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# CARGA PAGINADA Y TABLA
# ══════════════════════════════════════════════
if "activos_pagina" not in st.session_state:
    st.session_state["activos_pagina"] = 0
TAM_PAGINA = 50

filtro_actual = (busqueda, filtro_prod_id, filtro_est, incluir_baja)
if st.session_state.get("activos_filtro_anterior") != filtro_actual:
    st.session_state["activos_pagina"] = 0
    st.session_state["activos_filtro_anterior"] = filtro_actual

datos, total_filtrado = cargar_activos(
    pagina=st.session_state["activos_pagina"], tam_pagina=TAM_PAGINA,
    busqueda=busqueda, filtro_producto_id=filtro_prod_id, filtro_estado=filtro_est, incluir_baja=incluir_baja
)
df_f = pd.DataFrame(datos)

if not df_f.empty:
    cw  = [1.6, 2.8, 1.5, 2, 1.7, 1.5, 1.2]
    ths = ["Código", "Producto", "Serial", "Ubicación", "Responsable", "Estado", "⚙️"]

    panel_tabla = st.container(key="panel_tabla")
    with panel_tabla:
        st.markdown('<div class="panel-card-titulo">📋 Activos registrados</div>', unsafe_allow_html=True)

        h_cols = st.columns(cw)
        for idx, (col, txt) in enumerate(zip(h_cols, ths)):
            estilo = " style='text-align:center;'" if idx == len(ths) - 1 else ""
            col.markdown(f"<p class='th'{estilo}>{txt}</p>", unsafe_allow_html=True)

        for i, (_, row) in enumerate(df_f.iterrows()):
            cls = "td-alt" if i % 2 == 1 else "td"
            r = st.columns(cw)
            r[0].markdown(f"<div class='{cls}'><span class='folio-tag'>{row['codigo_activo']}</span></div>", unsafe_allow_html=True)
            r[1].markdown(f"<div class='{cls}'>{row['producto_codigo']} — {row['producto_nombre']}</div>", unsafe_allow_html=True)
            r[2].markdown(f"<div class='{cls}'>{row.get('serial') or '—'}</div>", unsafe_allow_html=True)
            r[3].markdown(f"<div class='{cls}'>{row['ubicacion_nombre']}</div>", unsafe_allow_html=True)
            r[4].markdown(f"<div class='{cls}'>{row['responsable_nombre']}</div>", unsafe_allow_html=True)
            r[5].markdown(f"<div class='{cls}'><span class='badge badge-{row['estado']}'>{ESTADO_LABELS[row['estado']].split(' ',1)[1]}</span></div>", unsafe_allow_html=True)

            with r[6]:
                b1, b2 = st.columns(2)
                if b1.button("✏️", key=f"ed_act_{row['id']}", help="Editar", width="stretch"):
                    ventana_editar_activo(row.to_dict())
                if b2.button("🏷️", key=f"lbl_act_{row['id']}", help="Imprimir etiqueta", width="stretch"):
                    ventana_etiqueta_activo(row.to_dict())

        total_paginas = max(1, -(-total_filtrado // TAM_PAGINA))
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if st.button("← Anterior", disabled=st.session_state["activos_pagina"] <= 0, key="act_pag_ant"):
                st.session_state["activos_pagina"] -= 1
                st.rerun()
        with c2:
            st.markdown(f"<p style='text-align:center; font-size:12px; color:#64748B; margin-top:8px;'>Página {st.session_state['activos_pagina'] + 1} de {total_paginas} · {total_filtrado} resultados</p>", unsafe_allow_html=True)
        with c3:
            if st.button("Siguiente →", disabled=st.session_state["activos_pagina"] >= total_paginas - 1, key="act_pag_sig"):
                st.session_state["activos_pagina"] += 1
                st.rerun()

elif total == 0:
    st.info("📭 No hay activos registrados todavía — se crean automáticamente al dar de alta un Producto tipo 'Activo individual' o registrar una Entrada.")
else:
    st.info("🔍 No se encontraron activos con los filtros aplicados.")
