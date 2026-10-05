import re
import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import date, datetime, timedelta
import uuid
from io import BytesIO
from fpdf import FPDF

st.set_page_config(
    page_title="MSH-Hub | Movimientos",
    layout="wide",
    page_icon="🔄",
    initial_sidebar_state="collapsed"
)


def filtro_rango_fechas(key_prefix):
    """Widget reutilizable: selector de rango rápido + fechas personalizadas.
    Retorna (desde, hasta) como str 'YYYY-MM-DD' o (None, None) si es 'Todo'."""
    opciones = ["Todo", "Hoy", "Últimos 7 días", "Este mes", "Este año", "Personalizado"]
    seleccion = st.selectbox("rango", opciones, label_visibility="collapsed", key=f"{key_prefix}_rango")

    hoy = date.today()
    if seleccion == "Todo":
        return None, None
    elif seleccion == "Hoy":
        return str(hoy), str(hoy)
    elif seleccion == "Últimos 7 días":
        return str(hoy - timedelta(days=6)), str(hoy)
    elif seleccion == "Este mes":
        return str(hoy.replace(day=1)), str(hoy)
    elif seleccion == "Este año":
        return str(hoy.replace(month=1, day=1)), str(hoy)
    else:  # Personalizado
        c1, c2 = st.columns(2)
        with c1:
            desde = st.date_input("Desde", value=hoy - timedelta(days=30), format="DD/MM/YYYY", key=f"{key_prefix}_desde")
        with c2:
            hasta = st.date_input("Hasta", value=hoy, format="DD/MM/YYYY", key=f"{key_prefix}_hasta")
        return str(desde), str(hasta)

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
.badge-completada { background:#DCFCE7; color:#15803D; }
.badge-cancelada   { background:#FEE2E2; color:#B91C1C; }
.folio-tag {
    font-family: 'DM Mono', monospace; font-size: 10px; color: #94A3B8;
    background: #F1F5F9; border-radius: 4px; padding: 1px 5px; display: inline-block;
}
.panel-card-titulo { font-size: 15px; font-weight: 700; color: #1E293B; margin-bottom: 2px; }
.panel-card-subtitulo { font-size: 12px; color: #94A3B8; margin-bottom: 16px; }
div[class*="st-key-panel_filtros"],
div[class*="st-key-panel_tabla"],
div[class*="st-key-panel_selector"] {
    background: #ffffff; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 18px 24px; margin-bottom: 18px;
    box-shadow: 0 2px 10px rgba(30,52,71,0.06);
}
div[data-testid="stDialog"] div[role="dialog"] {
    width: 68vw !important; max-width: 900px !important;
    min-width: 460px !important; border-radius: 16px !important;
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
.selector-btn-activo button {
    background: #1E3447 !important; color: white !important; border: none !important;
}

div[class*="st-key-ent_export_excel_btn"] button,
div[class*="st-key-sal_export_excel_btn"] button,
div[class*="st-key-pre_export_excel_btn"] button,
div[class*="st-key-cus_export_excel_btn"] button,
div[class*="st-key-dev_export_excel_btn"] button {
    border: 1px solid #86EFAC !important; color: #15803D !important; background: #F0FDF4 !important;
}
div[class*="st-key-ent_export_pdf_btn"] button,
div[class*="st-key-sal_export_pdf_btn"] button,
div[class*="st-key-pre_export_pdf_btn"] button,
div[class*="st-key-cus_export_pdf_btn"] button,
div[class*="st-key-dev_export_pdf_btn"] button {
    border: 1px solid #FCA5A5 !important; color: #B91C1C !important; background: #FEF2F2 !important;
}

.export-indicador {
    font-size: 11px; color: #64748B; text-align: right; padding-top: 8px;
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


def registrar_acceso(usuario, nombre, accion):
    try:
        supabase.table("usuarios_accesos").insert({
            "usuario": usuario, "nombre": nombre,
            "accion": accion, "fecha_hora": datetime.now().isoformat()
        }).execute()
    except:
        pass


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

def val_or(valor, default="—"):
    """Como 'or', pero también trata NaN de pandas como vacío."""
    if valor is None or valor == "" or (isinstance(valor, float) and pd.isna(valor)):
        return default
    return valor

def fmt_fecha(valor):
    """Convierte 'YYYY-MM-DD' (o con hora) a 'DD/MM/YYYY'. Devuelve '' si viene vacío."""
    if not valor or (isinstance(valor, float) and pd.isna(valor)):
        return ""
    try:
        return datetime.fromisoformat(str(valor)[:10]).strftime("%d/%m/%Y")
    except ValueError:
        return str(valor)

def buscar_productos(query):
    try:
        q = supabase.table("almacen_productos").select("*").eq("activo", True)
        if query.strip():
            q = q.or_(f"codigo.ilike.%{query}%,nombre.ilike.%{query}%,codigo_barra.ilike.%{query}%")
        res = q.order("nombre").limit(8).execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Error al buscar productos: {e}")
        return []

def cargar_catalogo_movimientos():
    try:
        res_prod = supabase.table("almacen_productos").select(
            "id, codigo, nombre, tipo_producto, almacen_existencias(cantidad, costo_unitario)"
        ).eq("activo", True).order("nombre").execute()

        res_activos = supabase.table("almacen_activos").select("producto_id").eq("estado", "disponible").eq("activo", True).execute()
        conteo_activos = {}
        for a in (res_activos.data or []):
            pid = a["producto_id"]
            conteo_activos[pid] = conteo_activos.get(pid, 0) + 1

        filas = []
        for p in (res_prod.data or []):
            ex = p.get("almacen_existencias")
            if isinstance(ex, list):
                ex = ex[0] if ex else {}
            elif not isinstance(ex, dict):
                ex = {}
            es_activo = p["tipo_producto"] == "activo"
            filas.append({
                "id": p["id"], "codigo": p["codigo"], "nombre": p["nombre"],
                "tipo_producto": "🛠️ Activo" if es_activo else "📦 Insumo",
                "tipo_raw": p["tipo_producto"],
                "disponible": conteo_activos.get(p["id"], 0) if es_activo else ex.get("cantidad"),
                "costo_unitario": ex.get("costo_unitario") if not es_activo else None,
            })
        return pd.DataFrame(filas)
    except Exception as e:
        st.error(f"Error al cargar catálogo: {e}")
        return pd.DataFrame(columns=["id", "codigo", "nombre", "tipo_producto", "tipo_raw", "disponible", "costo_unitario"])

def cargar_proyectos_activos():
    try:
        res = supabase.table("almacen_proyectos").select("id, numero_proyecto, nombre").eq("estado", "activo").eq("activo", True).order("numero_proyecto").execute()
        return res.data if res.data else []
    except:
        return []


def cargar_proyectos_activos():
    try:
        res = supabase.table("almacen_proyectos").select("id, numero_proyecto, nombre").eq("activo", True).in_("estado", ["activo", "pausado"]).order("numero_proyecto").execute()
        return res.data if res.data else []
    except:
        return []


def crear_proyecto_rapido(numero, nombre):
    try:
        res = supabase.table("almacen_proyectos").insert({
            "numero_proyecto": numero.strip(), "nombre": nombre.strip() or numero.strip(), "activo": True, "estado": "activo"
        }).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as e:
        st.error(f"No se pudo crear el proyecto: {e}")
        return None


nombre_actual  = st.session_state.get("nombre", "")
rol_actual     = st.session_state.get("rol", "")
usuario_actual = st.session_state.get("usuario", "")
es_admin       = rol_actual == "admin"
iniciales      = "".join([p[0].upper() for p in nombre_actual.split()[:2]]) if nombre_actual else "AD"


# ══════════════════════════════════════════════════════════════
# ══════════════════════════════ ENTRADAS ═══════════════════════
# ══════════════════════════════════════════════════════════════
def cargar_proveedores_activos():
    try:
        res = supabase.table("almacen_entidades").select("id, nombre").eq("tipo", "proveedor").eq("activo", True).order("nombre").execute()
        return res.data if res.data else []
    except:
        return []


def crear_proveedor_rapido(nombre):
    try:
        res = supabase.table("almacen_entidades").insert({"tipo": "proveedor", "nombre": nombre.strip(), "activo": True}).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as e:
        st.error(f"No se pudo crear el proveedor: {e}")
        return None


def generar_folio_entrada():
    try:
        return supabase.rpc("generar_folio_entrada", {}).execute().data
    except Exception as e:
        st.error(f"Error al generar folio: {e}")
        return None


def generar_codigo_activo(producto_id):
    try:
        return supabase.rpc("generar_codigo_activo", {"p_producto_id": producto_id}).execute().data
    except Exception as e:
        st.error(f"Error al generar código de activo: {e}")
        return None


def subir_documento_entrada(archivo, folio):
    try:
        ruta = f"{folio}/{datetime.now().strftime('%Y%m%d%H%M%S')}_{archivo.name}"
        supabase.storage.from_("entradas-documentos").upload(
            ruta, archivo.getvalue(), {"content-type": archivo.type or "application/octet-stream"}
        )
        return supabase.storage.from_("entradas-documentos").get_public_url(ruta)
    except Exception as e:
        st.warning(f"No se pudo subir el documento: {e}")
        return None


def crear_entrada(payload):
    try:
        res = supabase.table("almacen_entradas").insert(payload).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as e:
        st.error(f"Error al crear la entrada: {e}")
        return None


def crear_entrada_detalle(entrada_id, linea):
    try:
        res = supabase.table("almacen_entradas_detalle").insert({
            "entrada_id": entrada_id, "producto_id": linea["producto_id"], "cantidad": linea["cantidad"],
            "costo_unitario": linea.get("costo_unitario"), "ubicacion_id": linea.get("ubicacion_id"),
            "numero_lote": linea.get("numero_lote"), "fecha_vencimiento": linea.get("fecha_vencimiento"),
        }).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as e:
        st.error(f"Error al guardar el detalle: {e}")
        return None


def aplicar_entrada_linea(linea, detalle_id, fecha_entrada):
    producto = linea["producto"]
    if producto["tipo_producto"] == "insumo":
        try:
            existente = supabase.table("almacen_existencias").select("*").eq("producto_id", producto["id"]).execute().data
            if existente:
                nueva_cantidad = existente[0]["cantidad"] + linea["cantidad"]
                supabase.table("almacen_existencias").update({"cantidad": nueva_cantidad}).eq("producto_id", producto["id"]).execute()
            else:
                supabase.table("almacen_existencias").insert({
                    "producto_id": producto["id"], "cantidad": linea["cantidad"],
                    "costo_unitario": linea.get("costo_unitario"), "ubicacion_id": linea.get("ubicacion_id"),
                }).execute()
            if producto.get("controla_lote") and linea.get("numero_lote"):
                supabase.table("almacen_lotes").insert({
                    "producto_id": producto["id"], "numero_lote": linea["numero_lote"],
                    "fecha_vencimiento": linea.get("fecha_vencimiento"),
                    "cantidad_inicial": linea["cantidad"], "cantidad_actual": linea["cantidad"],
                    "costo_unitario": linea.get("costo_unitario"), "fecha_ingreso": str(fecha_entrada),
                    "ubicacion_id": linea.get("ubicacion_id"),
                }).execute()
            return True
        except Exception as e:
            st.error(f"Error al aplicar existencia de '{producto['nombre']}': {e}")
            return False
    else:
        creados = []
        for _ in range(int(linea["cantidad"])):
            codigo = generar_codigo_activo(producto["id"])
            if not codigo:
                continue
            try:
                supabase.table("almacen_activos").insert({
                    "producto_id": producto["id"], "codigo_activo": codigo, "condicion": "nuevo",
                    "estado": "disponible", "ubicacion_actual": linea.get("ubicacion_id"),
                    "costo_adquisicion": linea.get("costo_unitario"), "fecha_compra": str(fecha_entrada),
                    "fecha_ingreso": str(fecha_entrada), "entrada_detalle_id": detalle_id,
                }).execute()
                creados.append(codigo)
            except Exception as e:
                st.warning(f"No se pudo crear el activo {codigo}: {e}")
        return creados


def cargar_entradas(pagina=0, tam_pagina=50, busqueda="", filtro_estado="Todos", desde=None, hasta=None):
    try:
        q = supabase.table("almacen_entradas_resumen").select("*", count="exact")
        if busqueda.strip():
            q = q.or_(f"folio.ilike.%{busqueda}%,proveedor_nombre.ilike.%{busqueda}%,productos_completos.ilike.%{busqueda}%")
        if filtro_estado != "Todos":
            q = q.eq("estado", filtro_estado.lower())
        if desde:
            q = q.gte("fecha", desde)
        if hasta:
            q = q.lte("fecha", hasta)
        inicio = pagina * tam_pagina
        fin = inicio + tam_pagina - 1
        res = q.order("fecha", desc=True).order("created_at", desc=True).range(inicio, fin).execute()
        return res.data or [], (res.count or 0)
    except Exception as e:
        st.error(f"Error al cargar entradas: {e}")
        return [], 0


def cargar_detalle_entrada(entrada_id):
    try:
        res = supabase.table("almacen_entradas_detalle").select("*, almacen_productos(codigo, nombre)").eq("entrada_id", entrada_id).execute()
        data = res.data if res.data else []
        for row in data:
            p = row.pop("almacen_productos", None)
            row["producto_codigo"] = p["codigo"] if p else "—"
            row["producto_nombre"] = p["nombre"] if p else "—"
        return data
    except:
        return []


if "entrada_detalle_lineas" not in st.session_state:
    st.session_state["entrada_detalle_lineas"] = []


@st.dialog("📥 Nueva Entrada", width="large")
def ventana_nueva_entrada():
    proveedores = cargar_proveedores_activos()
    ubicaciones = cargar_ubicaciones_activas()

    if "entrada_folio_sugerido" not in st.session_state:
        st.session_state["entrada_folio_sugerido"] = generar_folio_entrada()
    st.caption(f"Folio sugerido: `{st.session_state['entrada_folio_sugerido']}`")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        opciones_prov = {"— Ninguno —": None, **{p["nombre"]: p["id"] for p in proveedores}}
        sel_prov = st.selectbox("Proveedor / Origen", list(opciones_prov.keys()), key="entrada_prov_sel")
        entidad_id = opciones_prov.get(sel_prov)
    with c2:
        fecha_entrada = st.date_input("Fecha *", value=date.today(), format="DD/MM/YYYY", key="entrada_fecha")
    with c3:
        tipo_entrada = st.selectbox("Tipo de entrada *", ["compra", "donacion", "recepcion", "devolucion", "ajuste"],
                                     format_func=lambda v: v.capitalize(), key="entrada_tipo")
    with c4:
        proyectos = cargar_proyectos_activos()
        opciones_proy = {"— Sin proyecto —": None, **{p["numero_proyecto"]: p["id"] for p in proyectos}}
        sel_proy = st.selectbox("Proyecto", list(opciones_proy.keys()), key="entrada_proy_sel")
        proyecto_id = opciones_proy.get(sel_proy)
    observaciones = st.text_area("Observaciones", key="entrada_observaciones", height=60)
    numero_documento = st.text_input("Número de documento (factura/remisión)", key="entrada_numero_doc", placeholder="Ej. FAC-A-00123")
    documento_factura = st.file_uploader("Documento adjunto (factura, remisión...)", type=["pdf", "png", "jpg", "jpeg"], key="entrada_documento")
    st.divider()
    st.markdown("**Agregar artículos**")
    if "entrada_busqueda_expandida" not in st.session_state:
        st.session_state["entrada_busqueda_expandida"] = True

    with st.expander("🔍 Buscar producto", expanded=st.session_state["entrada_busqueda_expandida"]):
        query = st.text_input("Filtrar", placeholder="Filtrar por código o nombre...", key="entrada_busqueda", label_visibility="collapsed")

        df_catalogo = cargar_catalogo_movimientos()
        if query.strip():
            texto = (df_catalogo["codigo"] + " " + df_catalogo["nombre"]).str.lower()
            mask = pd.Series(True, index=df_catalogo.index)
            for termino in query.lower().split():
                mask &= texto.str.contains(re.escape(termino), na=False)
            df_filtrado = df_catalogo[mask]
        else:
            df_filtrado = df_catalogo

        df_vista = df_filtrado.head(200).reset_index(drop=True)
        evento = st.dataframe(
            df_vista[["codigo", "nombre", "tipo_producto", "disponible", "costo_unitario"]],
            hide_index=True, width="stretch", height=240,
            on_select="rerun", selection_mode="single-row", key="entrada_tabla_productos",
            column_config={
                "codigo": "Código", "nombre": "Nombre", "tipo_producto": "Tipo",
                "disponible": st.column_config.NumberColumn("Disp. actual"),
                "costo_unitario": st.column_config.NumberColumn("Costo prom.", format="$%.2f"),
            },
        )
        st.caption(f"{len(df_filtrado)} de {len(df_catalogo)} productos coinciden" if query.strip() else f"{len(df_catalogo)} productos activos")

        filas_sel = evento.selection.rows if evento and evento.selection else []
        p = df_vista.iloc[filas_sel[0]].to_dict() if filas_sel else None
        if p:
            p["tipo_producto"] = p.pop("tipo_raw")

    if p:
        st.markdown(f"{'🛠️' if p['tipo_producto'] == 'activo' else '📦'} **{p['codigo']}** — {p['nombre']}")
        c1, c2 = st.columns([2, 1])
        with c1:
            cantidad_key = f"ent_cant_{p['id']}"
            st.number_input("Cantidad a recibir", min_value=1.0 if p["tipo_producto"] == "activo" else 0.01,
                             value=1.0, step=1.0, key=cantidad_key)
        with c2:
            st.write("")
            st.write("")
            if st.button("➕ Agregar", key=f"ent_add_{p['id']}", width="stretch"):
                st.session_state["entrada_detalle_lineas"].append({
                    "line_id": uuid.uuid4().hex,
                    "producto": p, "producto_id": p["id"], "cantidad": st.session_state[cantidad_key],
                    "costo_unitario": None, "ubicacion_id": None, "numero_lote": "", "fecha_vencimiento": None,
                })
                st.session_state["entrada_busqueda_expandida"] = False
                st.rerun(scope="fragment")
    st.divider()
    st.markdown("**Detalle de la entrada**")

    if not st.session_state["entrada_detalle_lineas"]:
        st.info("Todavía no has agregado artículos.")
    else:
        opciones_ubi = {"— Sin especificar —": None, **{u["breadcrumb"]: u["id"] for u in ubicaciones}}
        linea_a_eliminar = None
        for linea in st.session_state["entrada_detalle_lineas"]:
            lid = linea["line_id"]
            p = linea["producto"]
            fila = st.empty()
            with fila.container():
                c1, c2, c3, c4, c5 = st.columns([3, 1, 1.3, 1.6, 0.6])
                c1.markdown(f"**{p['codigo']}** — {p['nombre']}")
                c2.markdown(f"Cant: **{linea['cantidad']}**")
                linea["costo_unitario"] = c3.number_input("Costo unit.", min_value=0.0, step=0.01,
                                                            value=linea["costo_unitario"] or 0.0, key=f"ent_costo_{lid}", label_visibility="collapsed")
                sel_ubi = c4.selectbox("Ubicación", list(opciones_ubi.keys()), key=f"ent_ubi_{lid}", label_visibility="collapsed")
                linea["ubicacion_id"] = opciones_ubi.get(sel_ubi)
                eliminar_click = c5.button("🗑️", key=f"ent_del_{lid}")
                if p.get("controla_lote"):
                    cc1, cc2 = st.columns(2)
                    linea["numero_lote"] = cc1.text_input("Número de lote", value=linea.get("numero_lote", ""), key=f"ent_lote_{lid}")
                    if p.get("controla_vencimiento"):
                        linea["fecha_vencimiento"] = str(cc2.date_input("Fecha de vencimiento", format="DD/MM/YYYY", key=f"ent_venc_{lid}"))
            if eliminar_click:
                linea_a_eliminar = lid
                fila.empty()

        if linea_a_eliminar:
            st.session_state["entrada_detalle_lineas"] = [
                l for l in st.session_state["entrada_detalle_lineas"] if l["line_id"] != linea_a_eliminar
            ]

        total_articulos = len(st.session_state["entrada_detalle_lineas"])
        total_unidades = sum(l["cantidad"] for l in st.session_state["entrada_detalle_lineas"])
        st.caption(f"Total de artículos: **{total_articulos}** · Total de unidades: **{total_unidades}**")

    st.divider()
    c_cancel, c_guardar = st.columns([1, 2])
    with c_cancel:
        if st.button("Cancelar", width="stretch", key="ent_cancelar"):
            for k in ["entrada_entidad_sel", "entrada_proyecto_sel", "entrada_busqueda_expandida", "entrada_folio_sugerido"]:
                st.session_state.pop(k, None)
            st.session_state["entrada_detalle_lineas"] = []
            st.rerun()

    with c_guardar:
        if st.button("✅ Guardar entrada", type="primary", width="stretch", key="ent_guardar", disabled=not st.session_state["entrada_detalle_lineas"]):
            documento_url = None
            if documento_factura:
                documento_url = subir_documento_entrada(documento_factura, st.session_state["entrada_folio_sugerido"])

            payload = {
                "folio": st.session_state["entrada_folio_sugerido"], "fecha": str(fecha_entrada),
                "tipo_entrada": tipo_entrada, "entidad_id": entidad_id, "proyecto_id": proyecto_id,
                "usuario_registro": st.session_state["usuario"], "nombre_registro": st.session_state["nombre"],
                "estado": "completada", "observaciones": observaciones.strip() or None,
                "numero_documento": numero_documento.strip() or None,
                "documento_url": documento_url,
                "documento_nombre": documento_factura.name if documento_factura else None,
            }
            entrada_id = crear_entrada(payload)
            if entrada_id:
                codigos_generados = []
                for linea in st.session_state["entrada_detalle_lineas"]:
                    detalle_id = crear_entrada_detalle(entrada_id, linea)
                    if detalle_id:
                        resultado = aplicar_entrada_linea(linea, detalle_id, fecha_entrada)
                        if isinstance(resultado, list):
                            codigos_generados.extend(resultado)
                registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"REGISTRAR ENTRADA: {payload['folio']}")
                st.session_state["entrada_detalle_lineas"] = []
                del st.session_state["entrada_folio_sugerido"]
                st.session_state["_msg"] = f"Entrada {payload['folio']} guardada correctamente."
                if codigos_generados:
                    st.session_state["_msg_activos_creados"] = codigos_generados
                st.rerun()

def actualizar_entrada(id_registro, payload):
    try:
        supabase.table("almacen_entradas").update(payload).eq("id", id_registro).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar la entrada: {e}")
        return False


@st.dialog("✏️ Editar Entrada")
def ventana_editar_entrada(entrada):
    st.caption(f"Folio: `{entrada['folio']}`  ·  Este folio y sus artículos ya no se pueden modificar — solo los datos abajo.")

    proveedores = cargar_proveedores_activos()
    proyectos = cargar_proyectos_activos()

    opciones_prov = {"— Ninguno —": None, **{p["nombre"]: p["id"] for p in proveedores}}
    nombres_prov = list(opciones_prov.keys())
    idx_prov = nombres_prov.index(entrada["proveedor_nombre"]) if entrada.get("proveedor_nombre") in nombres_prov else 0
    sel_prov = st.selectbox("Proveedor / Origen", nombres_prov, index=idx_prov)
    entidad_id = opciones_prov.get(sel_prov)

    tipos = ["compra", "donacion", "recepcion", "devolucion", "ajuste"]
    tipo_entrada = st.selectbox("Tipo de entrada", tipos, index=tipos.index(entrada.get("tipo_entrada", "compra")),
                                 format_func=lambda v: v.capitalize())

    opciones_proy = {"— Sin proyecto —": None, **{p["numero_proyecto"]: p["id"] for p in proyectos}}
    nombres_proy = list(opciones_proy.keys())
    proyecto_actual_id = entrada.get("proyecto_id")
    label_proy_actual = next((l for l, i in opciones_proy.items() if i == proyecto_actual_id), "— Sin proyecto —")
    idx_proy = nombres_proy.index(label_proy_actual) if label_proy_actual in nombres_proy else 0
    sel_proy = st.selectbox("Proyecto", nombres_proy, index=idx_proy)
    proyecto_id = opciones_proy.get(sel_proy)

    numero_documento = st.text_input("Número de documento (factura/remisión)", value=entrada.get("numero_documento") or "")
    observaciones = st.text_area("Observaciones", value=entrada.get("observaciones") or "", height=60)

    if entrada.get("documento_url"):
        st.caption(f"📎 Documento actual: [{entrada.get('documento_nombre') or 'archivo'}]({entrada['documento_url']})")
    nuevo_documento = st.file_uploader("Reemplazar documento adjunto (opcional)", type=["pdf", "png", "jpg", "jpeg"])

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Guardar Cambios", type="primary", width="stretch"):
            payload = {
                "entidad_id": entidad_id, "tipo_entrada": tipo_entrada, "proyecto_id": proyecto_id,
                "numero_documento": numero_documento.strip() or None,
                "observaciones": observaciones.strip() or None,
            }
            if nuevo_documento:
                payload["documento_url"] = subir_documento_entrada(nuevo_documento, entrada["folio"])
                payload["documento_nombre"] = nuevo_documento.name
            if actualizar_entrada(entrada["id"], payload):
                registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"EDITAR ENTRADA: {entrada['folio']}")
                st.session_state["_msg"] = f"Entrada {entrada['folio']} actualizada."
                st.rerun()
    with c2:
        if st.button("❌ Cancelar", width="stretch"):
            st.rerun()


@st.dialog("📄 Detalle de Entrada")
def ventana_ver_detalle_entrada(entrada):
    st.markdown(f"**Folio:** `{entrada['folio']}`  ·  **Fecha:** {fmt_fecha(entrada['fecha'])}")
    st.markdown(f"**Proveedor:** {entrada['proveedor_nombre']}  ·  **Tipo:** {entrada['tipo_entrada'].capitalize()}")
    if entrada.get("numero_documento"):
        st.caption(f"📄 Documento: {entrada['numero_documento']}")
    if entrada.get("observaciones"):
        st.caption(entrada["observaciones"])
    if entrada.get("documento_url"):
        st.markdown(f"📎 [Ver documento adjunto: {entrada.get('documento_nombre') or 'archivo'}]({entrada['documento_url']})")
    st.divider()
    detalle = cargar_detalle_entrada(entrada["id"])
    if not detalle:
        st.info("Esta entrada no tiene artículos registrados.")
    else:
        for d in detalle:
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"**{d['producto_codigo']}** — {d['producto_nombre']}")
            c2.markdown(f"Cant: {d['cantidad']}")
    if st.button("Cerrar", width="stretch", key="cerrar_detalle_entrada"):
        st.rerun()


def contar_entradas(filtro_fecha=None, filtro_estado=None):
    try:
        q = supabase.table("almacen_entradas_resumen").select("id", count="exact")
        if filtro_fecha:
            q = q.eq("fecha", filtro_fecha)
        if filtro_estado:
            q = q.eq("estado", filtro_estado)
        res = q.range(0, 0).execute()
        return res.count or 0
    except:
        return 0


_PDF_REPLACEMENTS = {
    "\u2014": "-", "\u2013": "-", "\u2018": "'", "\u2019": "'",
    "\u201c": '"', "\u201d": '"', "\u2026": "...", "\u2022": "-", "\u00a0": " ",
}

def pdf_safe(texto):
    if texto is None:
        return ""
    s = str(texto)
    for orig, rep in _PDF_REPLACEMENTS.items():
        s = s.replace(orig, rep)
    return s.encode('latin-1', errors='ignore').decode('latin-1')

def pdf_output_bytes(pdf):
    import inspect
    try:
        acepta_dest = 'dest' in inspect.signature(pdf.output).parameters
    except (TypeError, ValueError):
        acepta_dest = False
    salida = pdf.output(dest='S') if acepta_dest else pdf.output()
    if isinstance(salida, str):
        return salida.encode('latin-1', errors='ignore')
    return bytes(salida)


def cargar_todas_entradas(busqueda="", desde=None, hasta=None):
    """Trae TODAS las entradas que cumplen el filtro, sin paginar — para exportar."""
    todos = []
    pagina = 0
    tam = 1000
    while True:
        datos, total = cargar_entradas(pagina=pagina, tam_pagina=tam, busqueda=busqueda, desde=desde, hasta=hasta)
        todos.extend(datos)
        if len(datos) < tam or len(todos) >= total:
            break
        pagina += 1
    return todos


def generar_excel_entradas(datos):
    filas = []
    for e in datos:
        filas.append({
            "Folio": e["folio"], "Fecha": fmt_fecha(e["fecha"]),
            "Producto": (e.get("primer_producto") or "—") + (f" (+{e['total_articulos']-1} más)" if e["total_articulos"] > 1 else ""),
            "Proveedor": e["proveedor_nombre"], "Tipo": e["tipo_entrada"].capitalize(),
            "Documento": e.get("numero_documento") or "", "Artículos": e["total_articulos"],
            "Unidades": e["total_unidades"], "Observaciones": e.get("observaciones") or "",
        })
    df = pd.DataFrame(filas)
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl", sheet_name="Entradas")
    return buffer.getvalue()


def generar_pdf_entradas(datos, filtros_texto):
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "MSH-Hub - Reporte de Entradas", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 6, f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    if filtros_texto:
        pdf.cell(0, 6, pdf_safe(f"Filtros: {filtros_texto}"), ln=True)
    pdf.cell(0, 6, f"Total de registros: {len(datos)}", ln=True)
    pdf.ln(3)

    headers = ["Folio", "Fecha", "Producto", "Proveedor", "Tipo", "Documento", "Artículos", "Unidades"]
    widths =  [28, 22, 65, 45, 22, 30, 20, 22]

    pdf.set_font("Arial", "B", 8)
    pdf.set_fill_color(30, 52, 71)
    pdf.set_text_color(255, 255, 255)
    for h, w in zip(headers, widths):
        pdf.cell(w, 7, h, border=1, fill=True)
    pdf.ln()

    pdf.set_font("Arial", "", 7.5)
    pdf.set_text_color(30, 30, 30)
    for i, e in enumerate(datos):
        if i % 2 == 1:
            pdf.set_fill_color(250, 251, 252)
        else:
            pdf.set_fill_color(255, 255, 255)
        producto_txt = (e.get("primer_producto") or "-") + (f" +{e['total_articulos']-1}" if e["total_articulos"] > 1 else "")
        fila = [
            e["folio"], fmt_fecha(e["fecha"]), producto_txt[:40], e["proveedor_nombre"][:28],
            e["tipo_entrada"].capitalize(), (e.get("numero_documento") or "-")[:20],
            str(e["total_articulos"]), f"{e['total_unidades']:g}",
        ]
        for val, w in zip(fila, widths):
            texto = pdf_safe(val)
            pdf.cell(w, 6, texto, border=1, fill=True)
        pdf.ln()

        if pdf.get_y() > 190:
            pdf.add_page()
            pdf.set_font("Arial", "B", 8)
            pdf.set_fill_color(30, 52, 71)
            pdf.set_text_color(255, 255, 255)
            for h, w in zip(headers, widths):
                pdf.cell(w, 7, h, border=1, fill=True)
            pdf.ln()
            pdf.set_font("Arial", "", 7.5)
            pdf.set_text_color(30, 30, 30)

    return pdf_output_bytes(pdf)


def render_seccion_entradas():
    total = contar_entradas()
    hoy = contar_entradas(filtro_fecha=str(date.today()))

    st.markdown(f"""
        <div class="kpi-bar">
            <div class="kpi-pill"><span class="kpi-icon">📥</span><span class="kpi-val" style="color:#1E293B;">{total}</span><span class="kpi-lbl">Total entradas</span></div>
            <div class="kpi-sep"></div>
            <div class="kpi-pill"><span class="kpi-icon">📅</span><span class="kpi-val" style="color:#1D4ED8;">{hoy}</span><span class="kpi-lbl">Hoy</span></div>
        </div>
    """, unsafe_allow_html=True)

    if "entradas_pagina" not in st.session_state:
        st.session_state["entradas_pagina"] = 0
    TAM_PAGINA = 50

    panel_filtros = st.container(key="panel_filtros")
    with panel_filtros:
        c_busq, c_fecha, c_nuevo = st.columns([4, 2.2, 1.6])
        with c_busq:
            busqueda = st.text_input("buscar", placeholder="🔍  Buscar por folio, proveedor o producto...", label_visibility="collapsed", key="busq_entradas")
        with c_fecha:
            desde, hasta = filtro_rango_fechas("entradas")
        with c_nuevo:
            if st.button("➕ Nueva Entrada", type="primary", width="stretch"):
                ventana_nueva_entrada()

    # Si cambia la búsqueda o el rango de fechas, regresa a la página 1
    filtro_actual = (busqueda, desde, hasta)
    if st.session_state.get("entradas_filtro_anterior") != filtro_actual:
        st.session_state["entradas_pagina"] = 0
        st.session_state["entradas_filtro_anterior"] = filtro_actual

    datos, total_filtrado = cargar_entradas(
        pagina=st.session_state["entradas_pagina"], tam_pagina=TAM_PAGINA,
        busqueda=busqueda, desde=desde, hasta=hasta
    )
    df_f = pd.DataFrame(datos)

    if not df_f.empty:
        cw, ths = [1.2, 1, 2.1, 1.5, 1, 1.3, 1, 0.5, 0.7, 0.7], ["Folio", "Fecha", "Producto", "Proveedor", "Tipo", "Documento", "Unidades", "📝", "✏️", "👁️"]
        panel_tabla = st.container(key="panel_tabla")
        with panel_tabla:
            c_titulo, c_indicador, c_excel, c_pdf = st.columns([2.3, 3.1, 2, 1.9])
            filtros_texto_partes = []
            if busqueda.strip():
                filtros_texto_partes.append(f"Búsqueda: '{busqueda}'")
            if desde:
                filtros_texto_partes.append(f"Desde {desde}" + (f" hasta {hasta}" if hasta else ""))
            filtros_texto = " · ".join(filtros_texto_partes) if filtros_texto_partes else "Sin filtros (todo el historial)"

            with c_titulo:
                st.markdown('<div class="panel-card-titulo">📋 Entradas registradas</div>', unsafe_allow_html=True)
            with c_indicador:
                st.markdown(f"<p class='export-indicador'>Mostrando {len(df_f)} de {total_filtrado} registros con el filtro actual</p>", unsafe_allow_html=True)
            with c_excel:
                if st.button(f"⬇️ Exportar Excel ({total_filtrado})", width="stretch", key="ent_export_excel_btn"):
                    st.session_state["ent_generar_excel"] = True
            with c_pdf:
                if st.button(f"📄 Exportar PDF ({total_filtrado})", width="stretch", key="ent_export_pdf_btn"):
                    st.session_state["ent_generar_pdf"] = True

            if st.session_state.get("ent_generar_excel"):
                with st.spinner(f"Generando Excel de {total_filtrado} entradas..."):
                    todas = cargar_todas_entradas(busqueda=busqueda, desde=desde, hasta=hasta)
                    excel_bytes = generar_excel_entradas(todas)
                st.download_button(
                    "✅ Descargar Excel", data=excel_bytes,
                    file_name=f"entradas_{date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="ent_download_excel"
                )
                st.session_state["ent_generar_excel"] = False

            if st.session_state.get("ent_generar_pdf"):
                with st.spinner(f"Generando PDF de {total_filtrado} entradas..."):
                    todas = cargar_todas_entradas(busqueda=busqueda, desde=desde, hasta=hasta)
                    pdf_bytes = generar_pdf_entradas(todas, filtros_texto)
                st.download_button(
                    "✅ Descargar PDF", data=pdf_bytes,
                    file_name=f"entradas_{date.today()}.pdf", mime="application/pdf",
                    key="ent_download_pdf"
                )
                st.session_state["ent_generar_pdf"] = False

            h_cols = st.columns(cw)
            for idx, (col, txt) in enumerate(zip(h_cols, ths)):
                col.markdown(f"<p class='th'{' style=text-align:center;' if idx >= len(ths)-4 else ''}>{txt}</p>", unsafe_allow_html=True)
            for i, (_, row) in enumerate(df_f.iterrows()):
                cls = "td-alt" if i % 2 == 1 else "td"
                r = st.columns(cw)
                r[0].markdown(f"<div class='{cls}'><span class='folio-tag'>{row['folio']}</span></div>", unsafe_allow_html=True)
                r[1].markdown(f"<div class='{cls}'>{fmt_fecha(row['fecha'])}</div>", unsafe_allow_html=True)
                primer_producto = row.get("primer_producto") or "—"
                extra = row["total_articulos"] - 1
                texto_producto = f"{primer_producto} +{extra} más" if extra > 0 else primer_producto
                tooltip = (row.get("productos_completos") or "").replace('"', "&quot;")
                r[2].markdown(f"<div class='{cls}' title=\"{tooltip}\">{texto_producto}</div>", unsafe_allow_html=True)
                r[3].markdown(f"<div class='{cls}'>{row['proveedor_nombre']}</div>", unsafe_allow_html=True)
                r[4].markdown(f"<div class='{cls}'>{row['tipo_entrada'].capitalize()}</div>", unsafe_allow_html=True)
                doc_texto = val_or(row.get("numero_documento"))
                doc_icono = " 📎" if row.get("documento_url") else ""
                r[5].markdown(f"<div class='{cls}'>{doc_texto}{doc_icono}</div>", unsafe_allow_html=True)
                r[6].markdown(f"<div class='{cls}' style='text-align:center;'>{row['total_articulos']} art. · {row['total_unidades']:g} uds</div>", unsafe_allow_html=True)
                obs_tooltip = (row.get("observaciones") or "").replace('"', "&quot;")
                obs_icono = f"<span title=\"{obs_tooltip}\">📝</span>" if row.get("observaciones") else ""
                r[7].markdown(f"<div class='{cls}' style='text-align:center;'>{obs_icono}</div>", unsafe_allow_html=True)
                with r[8]:
                    if st.button("✏️", key=f"ed_ent_{row['id']}", width="stretch"):
                        ventana_editar_entrada(row.to_dict())
                with r[9]:
                    if st.button("👁️", key=f"ver_ent_{row['id']}", width="stretch"):
                        ventana_ver_detalle_entrada(row.to_dict())

            total_paginas = max(1, -(-total_filtrado // TAM_PAGINA))
            c1, c2, c3 = st.columns([1, 2, 1])
            with c1:
                if st.button("← Anterior", disabled=st.session_state["entradas_pagina"] <= 0, key="ent_pag_ant"):
                    st.session_state["entradas_pagina"] -= 1
                    st.rerun()
            with c2:
                st.markdown(f"<p style='text-align:center; font-size:12px; color:#64748B; margin-top:8px;'>Página {st.session_state['entradas_pagina'] + 1} de {total_paginas} · {total_filtrado} resultados</p>", unsafe_allow_html=True)
            with c3:
                if st.button("Siguiente →", disabled=st.session_state["entradas_pagina"] >= total_paginas - 1, key="ent_pag_sig"):
                    st.session_state["entradas_pagina"] += 1
                    st.rerun()
    else:
        st.info("📭 No hay entradas registradas todavía. ¡Crea la primera!")

    if "_msg" in st.session_state:
        st.success(st.session_state.pop("_msg"))
    if "_msg_activos_creados" in st.session_state:
        codigos = st.session_state.pop("_msg_activos_creados")
        st.info("Activos generados: " + ", ".join(f"`{c}`" for c in codigos))


# ══════════════════════════════════════════════════════════════
# ══════════════════════════════ SALIDAS ════════════════════════
# ══════════════════════════════════════════════════════════════
def cargar_departamentos_activos():
    try:
        res = supabase.table("almacen_departamentos").select("id, nombre").eq("activo", True).order("nombre").execute()
        return res.data if res.data else []
    except:
        return []


def crear_departamento_rapido(nombre):
    try:
        res = supabase.table("almacen_departamentos").insert({"nombre": nombre.strip(), "activo": True}).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as e:
        st.error(f"No se pudo crear el departamento: {e}")
        return None


def buscar_activos_disponibles(producto_id):
    try:
        res = supabase.table("almacen_activos").select("id, codigo_activo, serial, costo_adquisicion").eq("producto_id", producto_id).eq("estado", "disponible").eq("activo", True).order("codigo_activo").execute()
        return res.data if res.data else []
    except:
        return []


def consultar_existencia(producto_id):
    try:
        res = supabase.table("almacen_existencias").select("*").eq("producto_id", producto_id).execute().data
        return res[0] if res else None
    except:
        return None


def descontar_lote_fifo(producto_id, cantidad):
    try:
        supabase.rpc("descontar_lote_fifo", {"p_producto_id": producto_id, "p_cantidad": cantidad}).execute()
        return True
    except Exception as e:
        st.warning(f"No se pudo descontar por lote FIFO: {e}")
        return False


def calcular_costo_activo(activo_id):
    try:
        res = supabase.table("almacen_activos").select("costo_adquisicion").eq("id", activo_id).execute().data
        return res[0]["costo_adquisicion"] if res else None
    except:
        return None


def calcular_costo_insumo(producto, cantidad):
    """Costo del lote consumido (ponderado, FIFO) si controla_lote; si no, promedio de Existencias."""
    if producto.get("controla_lote"):
        try:
            lotes = supabase.table("almacen_lotes").select("costo_unitario, cantidad_actual") \
                .eq("producto_id", producto["id"]).eq("activo", True).gt("cantidad_actual", 0) \
                .order("fecha_vencimiento", desc=False).order("created_at", desc=False).execute().data
            restante, costo_total = float(cantidad), 0.0
            for lote in lotes:
                if restante <= 0:
                    break
                tomar = min(lote["cantidad_actual"], restante)
                costo_total += tomar * (lote.get("costo_unitario") or 0)
                restante -= tomar
            if cantidad > 0:
                return round(costo_total / float(cantidad), 4)
        except Exception:
            pass
    existente = consultar_existencia(producto["id"])
    return existente.get("costo_unitario") if existente else None


def generar_folio_salida():
    try:
        return supabase.rpc("generar_folio_salida", {}).execute().data
    except Exception as e:
        st.error(f"Error al generar folio: {e}")
        return None


def subir_documento_salida(archivo, folio):
    try:
        ruta = f"{folio}/{datetime.now().strftime('%Y%m%d%H%M%S')}_{archivo.name}"
        supabase.storage.from_("salidas-documentos").upload(
            ruta, archivo.getvalue(), {"content-type": archivo.type or "application/octet-stream"}
        )
        return supabase.storage.from_("salidas-documentos").get_public_url(ruta)
    except Exception as e:
        st.warning(f"No se pudo subir el documento: {e}")
        return None


def crear_salida(payload):
    try:
        res = supabase.table("almacen_salidas").insert(payload).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as e:
        st.error(f"Error al crear la salida: {e}")
        return None


def aplicar_salida_linea(linea, salida_id):
    producto = linea["producto"]
    try:
        if producto["tipo_producto"] == "activo":
            costo = calcular_costo_activo(linea["activo_id"])
            supabase.table("almacen_salidas_detalle").insert({
                "salida_id": salida_id, "producto_id": producto["id"], "activo_id": linea["activo_id"],
                "costo_unitario": costo,
            }).execute()
            supabase.table("almacen_activos").update({"estado": "entregado"}).eq("id", linea["activo_id"]).execute()
        else:
            costo = calcular_costo_insumo(producto, linea["cantidad"])
            detalle = supabase.table("almacen_salidas_detalle").insert({
                "salida_id": salida_id, "producto_id": producto["id"], "cantidad": linea["cantidad"],
                "costo_unitario": costo,
            }).execute()
            detalle_id = detalle.data[0]["id"] if detalle.data else None
            costo_linea = (costo or 0) * linea["cantidad"]
            if detalle_id:
                for fila in (linea.get("prorrateo") or []):
                    if fila.get("proyecto_id"):
                        supabase.table("almacen_salidas_prorrateo").insert({
                            "salida_detalle_id": detalle_id, "proyecto_id": fila["proyecto_id"],
                            "porcentaje": fila["porcentaje"],
                            "costo_imputado": round(costo_linea * (fila["porcentaje"] / 100), 2),
                        }).execute()
            existente = consultar_existencia(producto["id"])
            if existente:
                nueva_cantidad = max(0, existente["cantidad"] - linea["cantidad"])
                supabase.table("almacen_existencias").update({"cantidad": nueva_cantidad}).eq("producto_id", producto["id"]).execute()
            if producto.get("controla_lote"):
                descontar_lote_fifo(producto["id"], linea["cantidad"])
        return True
    except Exception as e:
        st.error(f"Error al aplicar salida de '{producto['nombre']}': {e}")
        return False

def cargar_todas_salidas(busqueda="", desde=None, hasta=None):
    todos = []
    pagina = 0
    while True:
        datos, total = cargar_salidas(pagina=pagina, tam_pagina=1000, busqueda=busqueda, desde=desde, hasta=hasta)
        todos.extend(datos)
        if len(datos) < 1000 or len(todos) >= total:
            break
        pagina += 1
    return todos


def generar_excel_salidas(datos):
    filas = [{
        "Folio": s["folio"], "Fecha": fmt_fecha(s["fecha"]),
        "Producto": (s.get("primer_producto") or "—") + (f" (+{s['total_articulos']-1} más)" if s["total_articulos"] > 1 else ""),
        "Departamento": s["departamento_nombre"], "Motivo": s.get("motivo_uso") or "",
        "Documento": s.get("numero_documento") or "", "Artículos": s["total_articulos"], "Unidades": s["total_unidades"],
    } for s in datos]
    buffer = BytesIO()
    pd.DataFrame(filas).to_excel(buffer, index=False, engine="openpyxl", sheet_name="Salidas")
    return buffer.getvalue()


def generar_pdf_salidas(datos, filtros_texto):
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "MSH-Hub - Reporte de Salidas", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 6, f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    if filtros_texto:
        pdf.cell(0, 6, pdf_safe(f"Filtros: {filtros_texto}"), ln=True)
    pdf.cell(0, 6, f"Total de registros: {len(datos)}", ln=True)
    pdf.ln(3)
    headers = ["Folio", "Fecha", "Producto", "Departamento", "Motivo", "Documento", "Artículos", "Unidades"]
    widths =  [26, 20, 55, 40, 40, 28, 20, 22]
    pdf.set_font("Arial", "B", 8); pdf.set_fill_color(30, 52, 71); pdf.set_text_color(255, 255, 255)
    for h, w in zip(headers, widths):
        pdf.cell(w, 7, h, border=1, fill=True)
    pdf.ln()
    pdf.set_font("Arial", "", 7.5); pdf.set_text_color(30, 30, 30)
    for i, s in enumerate(datos):
        if i % 2 == 1:
            pdf.set_fill_color(250, 251, 252)
        else:
            pdf.set_fill_color(255, 255, 255)
        producto_txt = (s.get("primer_producto") or "-") + (f" +{s['total_articulos']-1}" if s["total_articulos"] > 1 else "")
        fila = [s["folio"], fmt_fecha(s["fecha"]), producto_txt[:38], s["departamento_nombre"][:26],
                (s.get("motivo_uso") or "-")[:26], (s.get("numero_documento") or "-")[:18],
                str(s["total_articulos"]), f"{s['total_unidades']:g}"]
        for val, w in zip(fila, widths):
            pdf.cell(w, 6, pdf_safe(val), border=1, fill=True)
        pdf.ln()
        if pdf.get_y() > 190:
            pdf.add_page()
            pdf.set_font("Arial", "B", 8); pdf.set_fill_color(30, 52, 71); pdf.set_text_color(255, 255, 255)
            for h, w in zip(headers, widths):
                pdf.cell(w, 7, h, border=1, fill=True)
            pdf.ln()
            pdf.set_font("Arial", "", 7.5); pdf.set_text_color(30, 30, 30)
    return pdf_output_bytes(pdf)


def cargar_salidas(pagina=0, tam_pagina=50, busqueda="", desde=None, hasta=None):
    try:
        q = supabase.table("almacen_salidas_resumen").select("*", count="exact")
        if busqueda.strip():
            q = q.or_(f"folio.ilike.%{busqueda}%,departamento_nombre.ilike.%{busqueda}%,productos_completos.ilike.%{busqueda}%")
        if desde:
            q = q.gte("fecha", desde)
        if hasta:
            q = q.lte("fecha", hasta)
        inicio = pagina * tam_pagina
        fin = inicio + tam_pagina - 1
        res = q.order("fecha", desc=True).order("created_at", desc=True).range(inicio, fin).execute()
        return res.data or [], (res.count or 0)
    except Exception as e:
        st.error(f"Error al cargar salidas: {e}")
        return [], 0


def contar_salidas(filtro_fecha=None):
    try:
        q = supabase.table("almacen_salidas_resumen").select("id", count="exact")
        if filtro_fecha:
            q = q.eq("fecha", filtro_fecha)
        res = q.range(0, 0).execute()
        return res.count or 0
    except:
        return 0


def cargar_detalle_salida(salida_id):
    try:
        res = supabase.table("almacen_salidas_detalle").select("*, almacen_productos(codigo, nombre), almacen_activos(codigo_activo)").eq("salida_id", salida_id).execute()
        data = res.data if res.data else []
        for row in data:
            p = row.pop("almacen_productos", None)
            a = row.pop("almacen_activos", None)
            row["producto_codigo"] = p["codigo"] if p else "—"
            row["producto_nombre"] = p["nombre"] if p else "—"
            row["activo_codigo"] = a["codigo_activo"] if a else None
        return data
    except:
        return []


if "salida_detalle_lineas" not in st.session_state:
    st.session_state["salida_detalle_lineas"] = []


@st.dialog("📤 Nueva Salida", width="large")
def ventana_nueva_salida():
    if "salida_folio_sugerido" not in st.session_state:
        st.session_state["salida_folio_sugerido"] = generar_folio_salida()
    st.caption(f"Folio sugerido: `{st.session_state['salida_folio_sugerido']}`")

    tipo_receptor_label = st.radio(
        "¿Quién recibe? *", ["Empleado", "Proveedor / Persona Externa", "Otro"],
        horizontal=True, key="salida_tipo_receptor"
    )

    persona_id = entidad_id = receptor_texto = departamento_id = None

    if tipo_receptor_label == "Empleado":
        personas = cargar_personas_con_departamento()
        opciones_persona = {p["nombre_completo"]: p for p in personas}
        if opciones_persona:
            sel_persona = st.selectbox("Recibe *", list(opciones_persona.keys()), key="salida_persona_sel")
            persona_id = opciones_persona[sel_persona]["id"]
            departamento_id = opciones_persona[sel_persona]["departamento_id"]
            st.text_input("Área", value=opciones_persona[sel_persona].get("departamento_nombre") or "— Sin área asignada —", disabled=True)
        else:
            st.warning("No hay empleados activos registrados en Personas.")

    elif tipo_receptor_label == "Proveedor / Persona Externa":
        proveedores = cargar_proveedores_activos()
        if proveedores:
            opciones_prov = {p["nombre"]: p["id"] for p in proveedores}
            sel_prov = st.selectbox("Recibe *", list(opciones_prov.keys()), key="salida_entidad_sel")
            entidad_id = opciones_prov[sel_prov]
        else:
            st.warning("No hay proveedores activos registrados.")

    else:  # Otro
        receptor_texto = st.text_input("Recibe", value=st.session_state.get("salida_receptor_texto", "NINGUNO"), key="salida_receptor_texto")
        departamentos = cargar_departamentos_activos()
        opciones_depto = {"— Ninguno —": None, **{d["nombre"]: d["id"] for d in departamentos}}
        sel_depto = st.selectbox("Área", list(opciones_depto.keys()), key="salida_depto_otro_sel")
        departamento_id = opciones_depto[sel_depto]

    c1, c2 = st.columns(2)
    with c1:
        fecha_salida = st.date_input("Fecha *", value=date.today(), format="DD/MM/YYYY", key="salida_fecha")
    with c2:
        tipo_salida = st.selectbox(
            "Tipo de salida *", ["compra", "donacion", "recepcion", "devolucion", "ajuste"],
            format_func=lambda v: v.capitalize(), key="salida_tipo_salida"
        )

    proyectos = cargar_proyectos_activos()
    opciones_proy = {"— Sin proyecto —": None, **{p["numero_proyecto"]: p["id"] for p in proyectos}}
    sel_proy = st.selectbox("Proyecto", list(opciones_proy.keys()), key="salida_proy_sel")
    proyecto_id = opciones_proy[sel_proy]

    motivo_uso = st.text_area("Observaciones", key="salida_motivo", height=60)
    numero_documento = st.text_input("Número de documento (vale/remisión)", key="salida_numero_doc", placeholder="Ej. VALE-00045")
    documento_comprobante = st.file_uploader("Documento adjunto (vale de salida, comprobante firmado...)", type=["pdf", "png", "jpg", "jpeg"], key="salida_documento")

    st.divider()
    st.markdown("**Agregar artículos**")

    if "salida_busqueda_expandida" not in st.session_state:
        st.session_state["salida_busqueda_expandida"] = True

    with st.expander("🔍 Buscar producto", expanded=st.session_state["salida_busqueda_expandida"]):
        query = st.text_input("Filtrar", placeholder="Filtrar por código o nombre...", key="salida_busqueda", label_visibility="collapsed")

        df_catalogo = cargar_catalogo_movimientos()
        if query.strip():
            texto = (df_catalogo["codigo"] + " " + df_catalogo["nombre"]).str.lower()
            mask = pd.Series(True, index=df_catalogo.index)
            for termino in query.lower().split():
                mask &= texto.str.contains(re.escape(termino), na=False)
            df_filtrado = df_catalogo[mask]
        else:
            df_filtrado = df_catalogo

        df_vista = df_filtrado.head(200).reset_index(drop=True)
        evento = st.dataframe(
            df_vista[["codigo", "nombre", "tipo_producto", "disponible", "costo_unitario"]],
            hide_index=True, width="stretch", height=240,
            on_select="rerun", selection_mode="single-row", key="salida_tabla_productos",
            column_config={
                "codigo": "Código", "nombre": "Nombre", "tipo_producto": "Tipo",
                "disponible": st.column_config.NumberColumn("Disp."),
                "costo_unitario": st.column_config.NumberColumn("Costo unit.", format="$%.2f"),
            },
        )
        st.caption(f"{len(df_filtrado)} de {len(df_catalogo)} productos coinciden" if query.strip() else f"{len(df_catalogo)} productos activos")

        filas_sel = evento.selection.rows if evento and evento.selection else []
        p = df_vista.iloc[filas_sel[0]].to_dict() if filas_sel else None
        if p:
            p["tipo_producto"] = p.pop("tipo_raw")

    if p:
        if p["tipo_producto"] == "activo":
            st.markdown(f"🛠️ **{p['codigo']}** — {p['nombre']}")
            ids_ya_en_carrito = {
                l["activo_id"] for l in st.session_state["salida_detalle_lineas"]
                if l["producto"]["id"] == p["id"] and l.get("activo_id")
            }
            disponibles = [a for a in buscar_activos_disponibles(p["id"]) if a["id"] not in ids_ya_en_carrito]
            if not disponibles:
                st.caption("⚠️ No hay unidades disponibles de este producto.")
            else:
                opciones_activo = {f"{a['codigo_activo']}" + (f" ({a['serial']})" if a.get("serial") else ""): a["id"] for a in disponibles}
                c1, c2 = st.columns([3, 1])
                with c1:
                    sel_activo = st.selectbox("Unidad específica", list(opciones_activo.keys()), key=f"sal_unidad_{p['id']}", label_visibility="collapsed")
                with c2:
                    if st.button("➕ Agregar", key=f"sal_add_{p['id']}", width="stretch"):
                        st.session_state["salida_detalle_lineas"].append({
                            "line_id": uuid.uuid4().hex,
                            "producto": p, "activo_id": opciones_activo[sel_activo],
                            "activo_label": sel_activo, "cantidad": None,
                        })
                        st.session_state["salida_busqueda_expandida"] = False
                        st.rerun(scope="fragment")
        else:
            st.markdown(f"📦 **{p['codigo']}** — {p['nombre']}")
            existente = consultar_existencia(p["id"])
            disponible_real = existente["cantidad"] if existente else 0
            ya_en_carrito = sum(
                l["cantidad"] for l in st.session_state["salida_detalle_lineas"]
                if l["producto"]["id"] == p["id"] and l.get("activo_id") is None
            )
            disponible = max(0, disponible_real - ya_en_carrito)
            if disponible <= 0:
                st.warning("⚠️ Ya agregaste todo el disponible de este producto en esta salida.")
            c1, c2 = st.columns([2, 1])
            c1.caption(f"Disponible: **{disponible}**")
            with c2:
                cant_key = f"sal_cant_{p['id']}"
                st.number_input("Cant.", min_value=0.01, max_value=float(disponible) if disponible else 0.01,
                                value=min(1.0, float(disponible)) if disponible else 0.01, step=1.0, key=cant_key, label_visibility="collapsed")

            prorratear = st.toggle("🔀 Prorratear entre proyectos", value=False, key=f"sal_prorratear_{p['id']}", disabled=disponible <= 0)
            if disponible <= 0 and prorratear:
                prorratear = False
                st.session_state.pop(f"sal_prorrateo_rows_{p['id']}", None)
            costo_ref = (existente.get("costo_unitario") if existente else 0) or 0
            cantidad_actual = st.session_state.get(cant_key, 0.0)
            costo_linea_est = cantidad_actual * costo_ref

            if not prorratear:
                ids_proy = list(opciones_proy.values())
                idx_default = ids_proy.index(proyecto_id) if proyecto_id in ids_proy else 0
                sel_proy_linea = st.selectbox("Proyecto", list(opciones_proy.keys()), index=idx_default,
                                               key=f"sal_proy_linea_{p['id']}", label_visibility="collapsed")
                prorrateo_rows = [{"proyecto_id": opciones_proy[sel_proy_linea], "proyecto_label": sel_proy_linea, "porcentaje": 100.0}]
                habilitado = bool(disponible)
            else:
                pk = f"sal_prorrateo_rows_{p['id']}"
                if pk not in st.session_state:
                    st.session_state[pk] = [{"proyecto_id": proyecto_id, "porcentaje": 100.0}]
                rows = st.session_state[pk]
                if st.button("+ Agregar proyecto", key=f"sal_prorrateo_add_{p['id']}"):
                    rows.append({"proyecto_id": None, "porcentaje": 0.0})
                total_pct, eliminar_idx = 0.0, None
                for i, fila in enumerate(rows):
                    rc1, rc2, rc3, rc4 = st.columns([2.5, 1.3, 1.3, 0.5])
                    ids_proy = list(opciones_proy.values())
                    idx = ids_proy.index(fila["proyecto_id"]) if fila["proyecto_id"] in ids_proy else 0
                    with rc1:
                        sel = st.selectbox("Proyecto", list(opciones_proy.keys()), index=idx,
                                            key=f"sal_prorrateo_proy_{p['id']}_{i}", label_visibility="collapsed")
                        fila["proyecto_id"] = opciones_proy[sel]
                        fila["proyecto_label"] = sel
                    with rc2:
                        fila["porcentaje"] = st.number_input("%", min_value=0.0, max_value=100.0, value=fila["porcentaje"],
                                                              step=1.0, key=f"sal_prorrateo_pct_{p['id']}_{i}", label_visibility="collapsed")
                    with rc3:
                        st.caption(f"$ {round(costo_linea_est * (fila['porcentaje']/100), 2):.2f}")
                    with rc4:
                        if st.button("🗑️", key=f"sal_prorrateo_del_{p['id']}_{i}"):
                            eliminar_idx = i
                    total_pct += fila["porcentaje"]
                if eliminar_idx is not None:
                    rows.pop(eliminar_idx)
                    st.rerun(scope="fragment")
                color = "🟢" if abs(total_pct - 100) < 0.01 else "🔴"
                st.caption(f"{color} Total asignado: {total_pct:.0f}% · $ {round(costo_linea_est * total_pct / 100, 2):.2f}")
                prorrateo_rows = [{"proyecto_id": r["proyecto_id"], "proyecto_label": r.get("proyecto_label", ""), "porcentaje": r["porcentaje"]} for r in rows]
                habilitado = bool(disponible) and abs(total_pct - 100) < 0.01

            if st.button("➕ Agregar", key=f"sal_add_{p['id']}", width="stretch", disabled=not habilitado):
                st.session_state["salida_detalle_lineas"].append({
                    "line_id": uuid.uuid4().hex,
                    "producto": p, "activo_id": None, "cantidad": st.session_state[cant_key],
                    "prorrateo": prorrateo_rows,
                })
                if prorratear:
                    del st.session_state[f"sal_prorrateo_rows_{p['id']}"]
                st.session_state["salida_busqueda_expandida"] = False
                st.rerun(scope="fragment")

    st.markdown("**Detalle de la salida**")
    if not st.session_state["salida_detalle_lineas"]:
        st.info("Todavía no has agregado artículos.")
    else:
        linea_a_eliminar = None
        for linea in st.session_state["salida_detalle_lineas"]:
            lid = linea["line_id"]
            p = linea["producto"]
            fila = st.empty()
            with fila.container():
                c1, c2, c3 = st.columns([4, 2, 0.6])
                c1.markdown(f"**{p['codigo']}** — {p['nombre']}")
                if linea["activo_id"]:
                    c2.markdown(f"Unidad: `{linea['activo_label']}`")
                else:
                    prorrateo = linea.get("prorrateo") or []
                    if len(prorrateo) > 1:
                        c2.markdown(f"Cant: **{linea['cantidad']}** · 🔀 {len(prorrateo)} proyectos")
                    else:
                        etiqueta = prorrateo[0]["proyecto_label"] if prorrateo else "— Sin proyecto —"
                        c2.markdown(f"Cant: **{linea['cantidad']}** · {etiqueta}")
                eliminar_click = c3.button("🗑️", key=f"sal_del_{lid}")
            if eliminar_click:
                linea_a_eliminar = lid
                fila.empty()
        if linea_a_eliminar:
            st.session_state["salida_detalle_lineas"] = [
                l for l in st.session_state["salida_detalle_lineas"] if l["line_id"] != linea_a_eliminar
            ]
        st.caption(f"Total de artículos: **{len(st.session_state['salida_detalle_lineas'])}**")

    st.divider()

    receptor_valido = (
        (tipo_receptor_label == "Empleado" and persona_id) or
        (tipo_receptor_label == "Proveedor / Persona Externa" and entidad_id) or
        (tipo_receptor_label == "Otro")
    )

    c_cancel, c_guardar = st.columns([1, 2])
    with c_cancel:
        if st.button("Cancelar", width="stretch", key="sal_cancelar"):
            for k in ["salida_persona_sel", "salida_entidad_sel", "salida_receptor_texto", "salida_depto_otro_sel",
                      "salida_busqueda_expandida", "salida_folio_sugerido"]:
                st.session_state.pop(k, None)
            st.session_state["salida_detalle_lineas"] = []
            st.rerun()

    with c_guardar:
        if st.button("✅ Guardar salida", type="primary", width="stretch",
                     disabled=not st.session_state["salida_detalle_lineas"] or not receptor_valido, key="sal_guardar"):
            documento_url = None
            if documento_comprobante:
                documento_url = subir_documento_salida(documento_comprobante, st.session_state["salida_folio_sugerido"])

            mapa_tipo = {"Empleado": "empleado", "Proveedor / Persona Externa": "proveedor", "Otro": "otro"}
            payload = {
                "folio": st.session_state["salida_folio_sugerido"], "fecha": str(fecha_salida),
                "departamento_id": departamento_id, "proyecto_id": proyecto_id,
                "motivo_uso": motivo_uso.strip() or None,
                "tipo_receptor": mapa_tipo[tipo_receptor_label],
                "persona_id": persona_id, "entidad_id": entidad_id,
                "receptor_texto": receptor_texto.strip() if receptor_texto else None,
                "usuario_registro": st.session_state["usuario"], "nombre_registro": st.session_state["nombre"],
                "estado": "completada",
                "numero_documento": numero_documento.strip() or None,
                "documento_url": documento_url,
                "documento_nombre": documento_comprobante.name if documento_comprobante else None,
            }
            salida_id = crear_salida(payload)
            if salida_id:
                for linea in st.session_state["salida_detalle_lineas"]:
                    aplicar_salida_linea(linea, salida_id)
                registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"REGISTRAR SALIDA: {payload['folio']}")
                for k in ["salida_persona_sel", "salida_entidad_sel", "salida_receptor_texto", "salida_depto_otro_sel"]:
                    st.session_state.pop(k, None)
                st.session_state["salida_detalle_lineas"] = []
                del st.session_state["salida_folio_sugerido"]
                st.session_state["_msg_salida"] = f"Salida {payload['folio']} guardada correctamente."
                st.rerun()

def actualizar_salida(id_registro, payload):
    try:
        supabase.table("almacen_salidas").update(payload).eq("id", id_registro).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar la salida: {e}")
        return False


@st.dialog("✏️ Editar Salida")
def ventana_editar_salida(salida):
    st.caption(f"Folio: `{salida['folio']}`  ·  Los artículos ya no se pueden modificar — solo los datos abajo.")

    departamentos = cargar_departamentos_activos()
    proyectos = cargar_proyectos_activos()

    opciones_depto = {"— Ninguno —": None, **{d["nombre"]: d["id"] for d in departamentos}}
    nombres_depto = list(opciones_depto.keys())
    idx_depto = nombres_depto.index(salida["departamento_nombre"]) if salida.get("departamento_nombre") in nombres_depto else 0
    sel_depto = st.selectbox("Departamento / Área", nombres_depto, index=idx_depto)
    departamento_id = opciones_depto.get(sel_depto)

    opciones_proy = {"— Sin proyecto —": None, **{p["numero_proyecto"]: p["id"] for p in proyectos}}
    nombres_proy = list(opciones_proy.keys())
    label_proy_actual = next((l for l, i in opciones_proy.items() if i == salida.get("proyecto_id")), "— Sin proyecto —")
    idx_proy = nombres_proy.index(label_proy_actual) if label_proy_actual in nombres_proy else 0
    sel_proy = st.selectbox("Proyecto", nombres_proy, index=idx_proy)
    proyecto_id = opciones_proy.get(sel_proy)

    numero_documento = st.text_input("Número de documento (vale/remisión)", value=salida.get("numero_documento") or "")
    motivo_uso = st.text_area("Motivo / Uso", value=salida.get("motivo_uso") or "", height=60)

    if salida.get("documento_url"):
        st.caption(f"📎 Documento actual: [{salida.get('documento_nombre') or 'archivo'}]({salida['documento_url']})")
    nuevo_documento = st.file_uploader("Reemplazar documento adjunto (opcional)", type=["pdf", "png", "jpg", "jpeg"])

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Guardar Cambios", type="primary", width="stretch"):
            payload = {
                "departamento_id": departamento_id, "proyecto_id": proyecto_id,
                "numero_documento": numero_documento.strip() or None,
                "motivo_uso": motivo_uso.strip() or None,
            }
            if nuevo_documento:
                payload["documento_url"] = subir_documento_salida(nuevo_documento, salida["folio"])
                payload["documento_nombre"] = nuevo_documento.name
            if actualizar_salida(salida["id"], payload):
                registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"EDITAR SALIDA: {salida['folio']}")
                st.session_state["_msg_salida"] = f"Salida {salida['folio']} actualizada."
                st.rerun()
    with c2:
        if st.button("❌ Cancelar", width="stretch"):
            st.rerun()


@st.dialog("📄 Detalle de Salida")
def ventana_ver_detalle_salida(salida):
    st.markdown(f"**Folio:** `{salida['folio']}`  ·  **Fecha:** {fmt_fecha(salida['fecha'])}")
    st.markdown(f"**Departamento:** {salida['departamento_nombre']}")
    if salida.get("numero_documento"):
        st.caption(f"📄 Documento: {salida['numero_documento']}")
    if salida.get("motivo_uso"):
        st.caption(salida["motivo_uso"])
    if salida.get("documento_url"):
        st.markdown(f"📎 [Ver documento adjunto: {salida.get('documento_nombre') or 'archivo'}]({salida['documento_url']})")
    st.divider()
    detalle = cargar_detalle_salida(salida["id"])
    if not detalle:
        st.info("Esta salida no tiene artículos registrados.")
    else:
        for d in detalle:
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"**{d['producto_codigo']}** — {d['producto_nombre']}")
            c2.markdown(f"`{d['activo_codigo']}`" if d.get("activo_codigo") else f"Cant: {d['cantidad']}")
    if st.button("Cerrar", width="stretch", key="cerrar_detalle_salida"):
        st.rerun()


def render_seccion_salidas():
    total = contar_salidas()
    hoy = contar_salidas(filtro_fecha=str(date.today()))

    st.markdown(f"""
        <div class="kpi-bar">
            <div class="kpi-pill"><span class="kpi-icon">📤</span><span class="kpi-val" style="color:#1E293B;">{total}</span><span class="kpi-lbl">Total salidas</span></div>
            <div class="kpi-sep"></div>
            <div class="kpi-pill"><span class="kpi-icon">📅</span><span class="kpi-val" style="color:#1D4ED8;">{hoy}</span><span class="kpi-lbl">Hoy</span></div>
        </div>
    """, unsafe_allow_html=True)

    if "salidas_pagina" not in st.session_state:
        st.session_state["salidas_pagina"] = 0
    TAM_PAGINA = 50

    panel_filtros = st.container(key="panel_filtros")
    with panel_filtros:
        c_busq, c_fecha, c_nuevo = st.columns([4, 2.2, 1.6])
        with c_busq:
            busqueda = st.text_input("buscar", placeholder="🔍  Buscar por folio, departamento o producto...", label_visibility="collapsed", key="busq_salidas")
        with c_fecha:
            desde, hasta = filtro_rango_fechas("salidas")
        with c_nuevo:
            if st.button("➕ Nueva Salida", type="primary", width="stretch"):
                ventana_nueva_salida()

    filtro_actual = (busqueda, desde, hasta)
    if st.session_state.get("salidas_filtro_anterior") != filtro_actual:
        st.session_state["salidas_pagina"] = 0
        st.session_state["salidas_filtro_anterior"] = filtro_actual

    datos, total_filtrado = cargar_salidas(
        pagina=st.session_state["salidas_pagina"], tam_pagina=TAM_PAGINA,
        busqueda=busqueda, desde=desde, hasta=hasta
    )
    df_f = pd.DataFrame(datos)

    if not df_f.empty:
        cw, ths = [1.2, 1, 2.1, 1.5, 1.7, 1.3, 1, 0.7, 0.7], ["Folio", "Fecha", "Producto", "Departamento", "Motivo", "Documento", "Unidades", "✏️", "👁️"]
        panel_tabla = st.container(key="panel_tabla")
        with panel_tabla:
# ══ st.markdown('<div class="panel-card-titulo">📋 Salidas registradas</div>', unsafe_allow_html=True)
            c_titulo, c_indicador, c_excel, c_pdf = st.columns([2.3, 3.1, 2, 1.9])
            filtros_texto = " · ".join(p for p in [
                f"Búsqueda: '{busqueda}'" if busqueda.strip() else None,
                f"Desde {desde}" + (f" hasta {hasta}" if hasta else "") if desde else None,
            ] if p) or "Sin filtros (todo el historial)"
            with c_titulo:
                st.markdown('<div class="panel-card-titulo">📋 Salidas registradas</div>', unsafe_allow_html=True)
            with c_indicador:
                st.markdown(f"<p class='export-indicador'>Mostrando {len(df_f)} de {total_filtrado} registros con el filtro actual</p>", unsafe_allow_html=True)
            with c_excel:
                if st.button(f"⬇️ Exportar Excel ({total_filtrado})", width="stretch", key="sal_export_excel_btn"):
                    st.session_state["sal_generar_excel"] = True
            with c_pdf:
                if st.button(f"📄 Exportar PDF ({total_filtrado})", width="stretch", key="sal_export_pdf_btn"):
                    st.session_state["sal_generar_pdf"] = True
            if st.session_state.get("sal_generar_excel"):
                with st.spinner(f"Generando Excel de {total_filtrado} salidas..."):
                    excel_bytes = generar_excel_salidas(cargar_todas_salidas(busqueda, desde, hasta))
                st.download_button("✅ Descargar Excel", data=excel_bytes, file_name=f"salidas_{date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="sal_download_excel")
                st.session_state["sal_generar_excel"] = False
            if st.session_state.get("sal_generar_pdf"):
                with st.spinner(f"Generando PDF de {total_filtrado} salidas..."):
                    pdf_bytes = generar_pdf_salidas(cargar_todas_salidas(busqueda, desde, hasta), filtros_texto)
                st.download_button("✅ Descargar PDF", data=pdf_bytes, file_name=f"salidas_{date.today()}.pdf",
                    mime="application/pdf", key="sal_download_pdf")
                st.session_state["sal_generar_pdf"] = False
            h_cols = st.columns(cw)
            for idx, (col, txt) in enumerate(zip(h_cols, ths)):
                col.markdown(f"<p class='th'{' style=text-align:center;' if idx >= len(ths)-3 else ''}>{txt}</p>", unsafe_allow_html=True)
            for i, (_, row) in enumerate(df_f.iterrows()):
                cls = "td-alt" if i % 2 == 1 else "td"
                r = st.columns(cw)
                r[0].markdown(f"<div class='{cls}'><span class='folio-tag'>{row['folio']}</span></div>", unsafe_allow_html=True)
                r[1].markdown(f"<div class='{cls}'>{fmt_fecha(row['fecha'])}</div>", unsafe_allow_html=True)
                primer_producto = row.get("primer_producto") or "—"
                extra = row["total_articulos"] - 1
                texto_producto = f"{primer_producto} +{extra} más" if extra > 0 else primer_producto
                tooltip = (row.get("productos_completos") or "").replace('"', "&quot;")
                r[2].markdown(f"<div class='{cls}' title=\"{tooltip}\">{texto_producto}</div>", unsafe_allow_html=True)
                r[3].markdown(f"<div class='{cls}'>{row['departamento_nombre']}</div>", unsafe_allow_html=True)
                r[4].markdown(f"<div class='{cls}'>{val_or(row.get('motivo_uso'))}</div>", unsafe_allow_html=True)                
                doc_texto = val_or(row.get("numero_documento"))
                doc_icono = " 📎" if row.get("documento_url") else ""
                r[5].markdown(f"<div class='{cls}'>{doc_texto}{doc_icono}</div>", unsafe_allow_html=True)
                r[6].markdown(f"<div class='{cls}' style='text-align:center;'>{row['total_articulos']} art. · {row['total_unidades']:g} uds</div>", unsafe_allow_html=True)
                with r[7]:
                    if st.button("✏️", key=f"ed_sal_{row['id']}", width="stretch"):
                        ventana_editar_salida(row.to_dict())
                with r[8]:
                    if st.button("👁️", key=f"ver_sal_{row['id']}", width="stretch"):
                        ventana_ver_detalle_salida(row.to_dict())

            total_paginas = max(1, -(-total_filtrado // TAM_PAGINA))
            c1, c2, c3 = st.columns([1, 2, 1])
            with c1:
                if st.button("← Anterior", disabled=st.session_state["salidas_pagina"] <= 0, key="sal_pag_ant"):
                    st.session_state["salidas_pagina"] -= 1
                    st.rerun()
            with c2:
                st.markdown(f"<p style='text-align:center; font-size:12px; color:#64748B; margin-top:8px;'>Página {st.session_state['salidas_pagina'] + 1} de {total_paginas} · {total_filtrado} resultados</p>", unsafe_allow_html=True)
            with c3:
                if st.button("Siguiente →", disabled=st.session_state["salidas_pagina"] >= total_paginas - 1, key="sal_pag_sig"):
                    st.session_state["salidas_pagina"] += 1
                    st.rerun()
    else:
        st.info("📭 No hay salidas registradas todavía. ¡Crea la primera!")

    if "_msg_salida" in st.session_state:
        st.success(st.session_state.pop("_msg_salida"))


# ══════════════════════════════════════════════════════════════
# ══════════════════════════════ PRÉSTAMOS (INVENTARIO) ═════════
# ══════════════════════════════════════════════════════════════
def cargar_personas_con_departamento():
    try:
        res = supabase.table("almacen_personas").select(
            "id, nombres, apellidos, departamento_id, almacen_departamentos(nombre)"
        ).eq("activo", True).order("nombres").execute()
        data = res.data or []
        for p in data:
            d = p.pop("almacen_departamentos", None)
            p["nombre_completo"] = f"{p['nombres']} {p.get('apellidos') or ''}".strip()
            p["departamento_nombre"] = d["nombre"] if d else None
        return data
    except Exception as e:
        st.error(f"Error al cargar personas: {e}")
        return []

def cargar_personas_activas():
    try:
        res = supabase.table("almacen_personas").select("id, nombres, apellidos").eq("activo", True).order("nombres").execute()
        data = res.data if res.data else []
        for p in data:
            p["nombre_completo"] = f"{p['nombres']} {p.get('apellidos') or ''}".strip()
        return data
    except:
        return []


def crear_persona_rapida(nombres):
    try:
        res = supabase.table("almacen_personas").insert({"nombres": nombres.strip(), "activo": True}).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as e:
        st.error(f"No se pudo crear la persona: {e}")
        return None


def generar_folio_prestamo():
    try:
        return supabase.rpc("generar_folio_prestamo_inventario", {}).execute().data
    except Exception as e:
        st.error(f"Error al generar folio: {e}")
        return None

def cargar_activos_prestables():
    try:
        res = supabase.table("almacen_activos").select(
            "id, codigo_activo, serial, producto_id, almacen_productos(codigo, nombre, permite_prestamo)"
        ).eq("estado", "disponible").eq("activo", True).order("codigo_activo").execute()
        filas = []
        for a in (res.data or []):
            p = a.get("almacen_productos") or {}
            if not p.get("permite_prestamo"):
                continue
            filas.append({
                "id": a["id"], "codigo_activo": a["codigo_activo"], "serial": a.get("serial") or "",
                "producto_codigo": p.get("codigo", ""), "producto_nombre": p.get("nombre", ""),
            })
        return pd.DataFrame(filas)
    except Exception as e:
        st.error(f"Error al cargar activos disponibles: {e}")
        return pd.DataFrame(columns=["id", "codigo_activo", "serial", "producto_codigo", "producto_nombre"])

def buscar_activos_disponibles_prestamo(query):
    try:
        if not query.strip():
            return []

        # 1) Coincidencia directa por código de activo
        res_activo = supabase.table("almacen_activos").select(
            "id, codigo_activo, serial, producto_id, almacen_productos(nombre, permite_prestamo, codigo_barra)"
        ).eq("estado", "disponible").eq("activo", True).ilike("codigo_activo", f"%{query}%").limit(10).execute()

        # 2) Coincidencia por nombre o código de barras del producto
        productos_match = supabase.table("almacen_productos").select("id").or_(
            f"nombre.ilike.%{query}%,codigo_barra.ilike.%{query}%"
        ).execute().data
        ids_producto = [p["id"] for p in productos_match]

        res_producto = []
        if ids_producto:
            res_producto = supabase.table("almacen_activos").select(
                "id, codigo_activo, serial, producto_id, almacen_productos(nombre, permite_prestamo, codigo_barra)"
            ).eq("estado", "disponible").eq("activo", True).in_("producto_id", ids_producto).limit(10).execute().data

        # 3) Unir y deduplicar por id
        combinados = {a["id"]: a for a in (res_activo.data or []) + res_producto}

        resultado = []
        for r in combinados.values():
            p = r.pop("almacen_productos", None)
            if p and p.get("permite_prestamo"):
                r["producto_nombre"] = p["nombre"]
                resultado.append(r)
        return resultado[:10]
    except Exception as e:
        st.error(f"Error al buscar activos: {e}")
        return []

def crear_prestamo(payload):
    try:
        res = supabase.table("almacen_prestamos_inventario").insert(payload).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as e:
        st.error(f"Error al crear el préstamo: {e}")
        return None

def cargar_todos_prestamos(busqueda="", filtro_estado="Todos", desde=None, hasta=None):
    todos = []
    pagina = 0
    while True:
        datos, total = cargar_prestamos(pagina=pagina, tam_pagina=1000, busqueda=busqueda, filtro_estado=filtro_estado, desde=desde, hasta=hasta)
        todos.extend(datos)
        if len(datos) < 1000 or len(todos) >= total:
            break
        pagina += 1
    return todos

def generar_excel_prestamos(datos):
    filas = [{
        "Folio": p["folio"], "Responsable": p["persona_nombre"], "Fecha préstamo": fmt_fecha(p["fecha_prestamo"]),
        "Dev. estimada": fmt_fecha(p.get("fecha_estimada")), "Estado": p["estado"].capitalize(),
        "Activos": p.get("activos_completos") or "", "Total activos": p["total_activos"],
        "Devueltos": p["activos_devueltos"], "Observaciones": p.get("observaciones") or "",
    } for p in datos]
    buffer = BytesIO()
    pd.DataFrame(filas).to_excel(buffer, index=False, engine="openpyxl", sheet_name="Prestamos")
    return buffer.getvalue()


def generar_pdf_prestamos(datos, filtros_texto):
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "MSH-Hub - Reporte de Prestamos", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 6, f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    if filtros_texto:
        pdf.cell(0, 6, pdf_safe(f"Filtros: {filtros_texto}"), ln=True)
    pdf.cell(0, 6, f"Total de registros: {len(datos)}", ln=True)
    pdf.ln(3)
    headers = ["Folio", "Responsable", "F. Prestamo", "Dev. Est.", "Estado", "Activos", "Devueltos"]
    widths =  [26, 45, 24, 24, 24, 90, 22]
    pdf.set_font("Arial", "B", 8); pdf.set_fill_color(30, 52, 71); pdf.set_text_color(255, 255, 255)
    for h, w in zip(headers, widths):
        pdf.cell(w, 7, h, border=1, fill=True)
    pdf.ln()
    pdf.set_font("Arial", "", 7.5); pdf.set_text_color(30, 30, 30)
    for i, p in enumerate(datos):
        if i % 2 == 1:
            pdf.set_fill_color(250, 251, 252)
        else:
            pdf.set_fill_color(255, 255, 255)
        fila = [p["folio"], p["persona_nombre"][:26], fmt_fecha(p["fecha_prestamo"]), fmt_fecha(p.get("fecha_estimada")) or "-",
                p["estado"].capitalize(), (p.get("activos_completos") or "-")[:60],
                f"{p['activos_devueltos']}/{p['total_activos']}"]
        for val, w in zip(fila, widths):
            pdf.cell(w, 6, pdf_safe(val), border=1, fill=True)
        pdf.ln()
        if pdf.get_y() > 190:
            pdf.add_page()
            pdf.set_font("Arial", "B", 8); pdf.set_fill_color(30, 52, 71); pdf.set_text_color(255, 255, 255)
            for h, w in zip(headers, widths):
                pdf.cell(w, 7, h, border=1, fill=True)
            pdf.ln()
            pdf.set_font("Arial", "", 7.5); pdf.set_text_color(30, 30, 30)
    return pdf_output_bytes(pdf)

def cargar_prestamos(pagina=0, tam_pagina=50, busqueda="", filtro_estado="Todos", desde=None, hasta=None):
    try:
        q = supabase.table("almacen_prestamos_resumen").select("*", count="exact")
        if busqueda.strip():
            q = q.or_(f"folio.ilike.%{busqueda}%,persona_nombre.ilike.%{busqueda}%,activos_completos.ilike.%{busqueda}%")
        if filtro_estado != "Todos":
            q = q.eq("estado", filtro_estado.lower())
        if desde:
            q = q.gte("fecha_prestamo", desde)
        if hasta:
            q = q.lte("fecha_prestamo", hasta)
        inicio = pagina * tam_pagina
        fin = inicio + tam_pagina - 1
        res = q.order("fecha_prestamo", desc=True).range(inicio, fin).execute()
        return res.data or [], (res.count or 0)
    except Exception as e:
        st.error(f"Error al cargar préstamos: {e}")
        return [], 0


def contar_prestamos(filtro_estado=None):
    try:
        q = supabase.table("almacen_prestamos_resumen").select("id", count="exact")
        if filtro_estado:
            q = q.eq("estado", filtro_estado)
        res = q.range(0, 0).execute()
        return res.count or 0
    except:
        return 0


@st.dialog("↩️ Devolución Rápida", width="large")
def ventana_devolucion_rapida(prestamo):
    st.markdown(f"**Folio:** `{prestamo['folio']}`  ·  **Responsable:** {prestamo['persona_nombre']}")
    st.markdown(f"**Fecha de préstamo:** {fmt_fecha(prestamo['fecha_prestamo'])}")

    if "devrap_folio_sugerido" not in st.session_state:
        st.session_state["devrap_folio_sugerido"] = generar_folio_devolucion()
    st.caption(f"Folio de devolución: `{st.session_state['devrap_folio_sugerido']}`")

    fecha_dev = st.date_input("Fecha *", value=date.today(), format="DD/MM/YYYY", key="devrap_fecha")
    observaciones = st.text_area("Observaciones", key="devrap_observaciones", height=50)
    st.divider()

    detalle = cargar_detalle_prestamo(prestamo["id"])
    pendientes = [d for d in detalle if not d["devuelto"]]

    if not pendientes:
        st.info("Este préstamo ya no tiene activos pendientes por devolver.")
        return

    st.markdown("**Activos a devolver:**")
    seleccion = {}
    for d in pendientes:
        c1, c2 = st.columns([3, 2])
        marcar = c1.checkbox(f"{d['activo_codigo']} — {d['producto_nombre']}", key=f"devrap_check_{d['id']}")
        estado_recibido = c2.selectbox("Estado", ["bueno", "dañado", "perdido"], key=f"devrap_estado_{d['id']}", label_visibility="collapsed") if marcar else "bueno"
        if marcar:
            seleccion[d["id"]] = {"activo_id": d["activo_id"], "estado_recibido": estado_recibido}

    c_cancel, c_guardar = st.columns([1, 2])
    with c_cancel:
        if st.button("Cancelar", width="stretch", key="devrap_cancelar"):
            st.session_state.pop("devrap_folio_sugerido", None)
            st.rerun()

    with c_guardar:
        if st.button("✅ Guardar devolución", type="primary", width="stretch", key="devrap_guardar", disabled=not seleccion):
            payload = {
                "folio": st.session_state["devrap_folio_sugerido"], "prestamo_id": prestamo["id"],
                "fecha": str(fecha_dev), "usuario_registro": st.session_state["usuario"],
                "nombre_registro": st.session_state["nombre"], "observaciones": observaciones.strip() or None,
            }
            devolucion_id = crear_devolucion(payload)
            if devolucion_id:
                for detalle_id, info in seleccion.items():
                    procesar_devolucion_activo(devolucion_id, info["activo_id"], info["estado_recibido"])
                    supabase.table("almacen_prestamos_inventario_detalle").update({"devuelto": True}).eq("id", detalle_id).execute()

                todos_devueltos = len(seleccion) == len(pendientes)
                nuevo_estado = "devuelto" if todos_devueltos else "parcial"
                update_prestamo = {"estado": nuevo_estado}
                if todos_devueltos:
                    update_prestamo["fecha_real"] = str(fecha_dev)
                supabase.table("almacen_prestamos_inventario").update(update_prestamo).eq("id", prestamo["id"]).execute()

                registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"REGISTRAR DEVOLUCION: {payload['folio']}")
                st.session_state.pop("devrap_folio_sugerido", None)
                st.session_state["_msg_prestamo"] = f"Devolución {payload['folio']} guardada correctamente."
                st.rerun()


def cargar_detalle_prestamo(prestamo_id):
    try:
        res = supabase.table("almacen_prestamos_inventario_detalle").select("*, almacen_activos(codigo_activo, almacen_productos(nombre))").eq("prestamo_id", prestamo_id).execute()
        data = res.data if res.data else []
        for row in data:
            a = row.pop("almacen_activos", None)
            if a:
                p = a.pop("almacen_productos", None)
                row["activo_codigo"] = a["codigo_activo"]
                row["producto_nombre"] = p["nombre"] if p else "—"
            else:
                row["activo_codigo"] = "—"
                row["producto_nombre"] = "—"
        return data
    except:
        return []


if "prestamo_detalle_lineas" not in st.session_state:
    st.session_state["prestamo_detalle_lineas"] = []


@st.dialog("🤝 Nuevo Préstamo", width="large")
def ventana_nuevo_prestamo():
    personas = cargar_personas_activas()

    if "prestamo_folio_sugerido" not in st.session_state:
        st.session_state["prestamo_folio_sugerido"] = generar_folio_prestamo()
    st.caption(f"Folio sugerido: `{st.session_state['prestamo_folio_sugerido']}`")

    c1, c2, c3 = st.columns(3)
    with c1:
        opciones_persona = {p["nombre_completo"]: p["id"] for p in personas}
        sel_persona = st.selectbox("Responsable *", list(opciones_persona.keys()), key="prestamo_persona_sel") if opciones_persona else None
        persona_id = opciones_persona.get(sel_persona)
    with c2:
        fecha_prestamo = st.date_input("Fecha *", value=date.today(), format="DD/MM/YYYY", key="prestamo_fecha")
    with c3:
        fecha_estimada = st.date_input("Fecha devolución estimada", value=None, format="DD/MM/YYYY", key="prestamo_fecha_est")

    observaciones = st.text_area("Observaciones", key="prestamo_observaciones", height=60)
    st.divider()
    st.markdown("**Agregar activos a prestar**")

    if "prestamo_busqueda_expandida" not in st.session_state:
        st.session_state["prestamo_busqueda_expandida"] = True

    with st.expander("🔍 Buscar herramienta", expanded=st.session_state["prestamo_busqueda_expandida"]):
        query = st.text_input("Filtrar", placeholder="Filtrar por código de activo, código de producto o nombre...", key="prestamo_busqueda", label_visibility="collapsed")

        df_activos = cargar_activos_prestables()
        if query.strip():
            texto = (df_activos["codigo_activo"] + " " + df_activos["producto_codigo"] + " " + df_activos["producto_nombre"]).str.lower()
            mask = pd.Series(True, index=df_activos.index)
            for termino in query.lower().split():
                mask &= texto.str.contains(re.escape(termino), na=False)
            df_filtrado = df_activos[mask]
        else:
            df_filtrado = df_activos

        df_vista = df_filtrado.head(200).reset_index(drop=True)
        evento = st.dataframe(
            df_vista[["codigo_activo", "producto_codigo", "producto_nombre", "serial"]],
            hide_index=True, width="stretch", height=240,
            on_select="rerun", selection_mode="single-row", key="prestamo_tabla_activos",
            column_config={
                "codigo_activo": "Código activo", "producto_codigo": "Producto",
                "producto_nombre": "Nombre", "serial": "Serial",
            },
        )
        unidad_txt = "unidad" if len(df_activos) == 1 else "unidades"
        st.caption(f"{len(df_filtrado)} de {len(df_activos)} {unidad_txt} disponibles" if query.strip() else f"{len(df_activos)} {unidad_txt} disponibles para préstamo")
        filas_sel = evento.selection.rows if evento and evento.selection else []
        a = df_vista.iloc[filas_sel[0]].to_dict() if filas_sel else None

    if a:
        ya_agregado = any(l["activo_id"] == a["id"] for l in st.session_state["prestamo_detalle_lineas"])
        st.markdown(f"🛠️ **{a['codigo_activo']}** — {a['producto_nombre']}" + (f" ({a['serial']})" if a.get("serial") else ""))
        if st.button("➕ Agregar", key=f"pre_add_{a['id']}", width="stretch", disabled=ya_agregado):
            st.session_state["prestamo_detalle_lineas"].append({"activo_id": a["id"], "codigo_activo": a["codigo_activo"], "producto_nombre": a["producto_nombre"]})
            st.session_state["prestamo_busqueda_expandida"] = False
            st.rerun(scope="fragment")
    st.markdown("**Activos a prestar**")
    if not st.session_state["prestamo_detalle_lineas"]:
        st.info("Todavía no has agregado activos. Solo se muestran activos de productos con 'Permite préstamo' activado.")
    else:
        activo_a_eliminar = None
        for linea in st.session_state["prestamo_detalle_lineas"]:
            fila = st.empty()
            with fila.container():
                c1, c2 = st.columns([5, 0.6])
                c1.markdown(f"**{linea['codigo_activo']}** — {linea['producto_nombre']}")
                eliminar_click = c2.button("🗑️", key=f"pre_del_{linea['activo_id']}")
            if eliminar_click:
                activo_a_eliminar = linea["activo_id"]
                fila.empty()
        if activo_a_eliminar:
            st.session_state["prestamo_detalle_lineas"] = [
                l for l in st.session_state["prestamo_detalle_lineas"] if l["activo_id"] != activo_a_eliminar
            ]
        st.caption(f"Total de activos: **{len(st.session_state['prestamo_detalle_lineas'])}**")

    st.divider()
    c_cancel, c_guardar = st.columns([1, 2])
    with c_cancel:
        if st.button("Cancelar", width="stretch", key="pre_cancelar"):
            for k in ["prestamo_persona_sel", "prestamo_busqueda_expandida", "prestamo_folio_sugerido"]:
                st.session_state.pop(k, None)
            st.session_state["prestamo_detalle_lineas"] = []
            st.rerun()

    with c_guardar:
        if st.button("✅ Guardar préstamo", type="primary", width="stretch", key="pre_guardar",
                     disabled=not st.session_state["prestamo_detalle_lineas"] or not persona_id):
            if fecha_estimada and fecha_estimada < fecha_prestamo:
                st.error("La fecha de devolución estimada no puede ser anterior a la fecha del préstamo.")
            else:
                payload = {
                    "folio": st.session_state["prestamo_folio_sugerido"], "persona_id": persona_id,
                    "fecha_prestamo": str(fecha_prestamo),
                    "fecha_estimada": str(fecha_estimada) if fecha_estimada else None,
                    "estado": "prestado", "usuario_registro": st.session_state["usuario"],
                    "nombre_registro": st.session_state["nombre"], "observaciones": observaciones.strip() or None,
                }
                prestamo_id = crear_prestamo(payload)
                if prestamo_id:
                    for linea in st.session_state["prestamo_detalle_lineas"]:
                        try:
                            supabase.table("almacen_prestamos_inventario_detalle").insert({
                                "prestamo_id": prestamo_id, "activo_id": linea["activo_id"], "devuelto": False
                            }).execute()
                            supabase.table("almacen_activos").update({"estado": "prestado", "responsable_actual": persona_id}).eq("id", linea["activo_id"]).execute()
                        except Exception as e:
                            st.warning(f"No se pudo procesar el activo {linea['codigo_activo']}: {e}")
                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"REGISTRAR PRESTAMO: {payload['folio']}")
                    st.session_state["prestamo_detalle_lineas"] = []
                    del st.session_state["prestamo_folio_sugerido"]
                    st.session_state["_msg_prestamo"] = f"Préstamo {payload['folio']} guardado correctamente."
                    st.rerun()

def actualizar_prestamo(id_registro, payload):
    try:
        supabase.table("almacen_prestamos_inventario").update(payload).eq("id", id_registro).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar el préstamo: {e}")
        return False


@st.dialog("✏️ Editar Préstamo")
def ventana_editar_prestamo(prestamo):
    st.caption(f"Folio: `{prestamo['folio']}`  ·  Los activos prestados no se modifican aquí — usa Devoluciones para eso.")

    personas = cargar_personas_activas()
    opciones_persona = {p["nombre_completo"]: p["id"] for p in personas}
    nombres_persona = list(opciones_persona.keys())
    idx_persona = nombres_persona.index(prestamo["persona_nombre"]) if prestamo.get("persona_nombre") in nombres_persona else 0
    sel_persona = st.selectbox("Responsable", nombres_persona, index=idx_persona) if nombres_persona else None
    persona_id = opciones_persona.get(sel_persona)

    fecha_estimada = st.date_input("Fecha de devolución estimada", value=pd_date_or_none(prestamo.get("fecha_estimada")), format="DD/MM/YYYY")
    observaciones = st.text_area("Observaciones", value=prestamo.get("observaciones") or "", height=60)

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Guardar Cambios", type="primary", width="stretch"):
            fecha_prestamo_actual = datetime.strptime(prestamo["fecha_prestamo"], "%Y-%m-%d").date()
            if fecha_estimada and fecha_estimada < fecha_prestamo_actual:
                st.error("La fecha de devolución estimada no puede ser anterior a la fecha del préstamo.")
            else:
                payload = {
                    "persona_id": persona_id,
                    "fecha_estimada": str(fecha_estimada) if fecha_estimada else None,
                    "observaciones": observaciones.strip() or None,
                }
                if actualizar_prestamo(prestamo["id"], payload):
                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"EDITAR PRESTAMO: {prestamo['folio']}")
                    st.session_state["_msg_prestamo"] = f"Préstamo {prestamo['folio']} actualizado."
                    st.rerun()
    with c2:
        if st.button("❌ Cancelar", width="stretch"):
            st.rerun()

def pd_date_or_none(value):
    if not value:
        return None
    if isinstance(value, str):
        try:
            return datetime.strptime(value[:10], "%Y-%m-%d").date()
        except ValueError:
            return None
    if isinstance(value, (date, datetime)):
        return value
    return None

@st.dialog("📄 Detalle de Préstamo")
def ventana_ver_detalle_prestamo(prestamo):
    st.markdown(f"**Folio:** `{prestamo['folio']}`  ·  **Responsable:** {prestamo['persona_nombre']}")
    st.markdown(f"**Fecha:** {fmt_fecha(prestamo['fecha_prestamo'])}  ·  **Devolución estimada:** {fmt_fecha(prestamo.get('fecha_estimada')) or '—'}")
    st.markdown(f"**Estado:** {prestamo['estado'].capitalize()}")
    if prestamo.get("observaciones"):
        st.caption(prestamo["observaciones"])
    st.divider()
    detalle = cargar_detalle_prestamo(prestamo["id"])
    if not detalle:
        st.info("Este préstamo no tiene activos registrados.")
    else:
        for d in detalle:
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"**{d['activo_codigo']}** — {d['producto_nombre']}")
            c2.markdown("✅ Devuelto" if d["devuelto"] else "🔵 Prestado")
    if st.button("Cerrar", width="stretch", key="cerrar_detalle_prestamo"):
        st.rerun()

def render_seccion_prestamos():
    total = contar_prestamos()
    prestados = contar_prestamos(filtro_estado="prestado")
    devueltos = contar_prestamos(filtro_estado="devuelto")

    st.markdown(f"""
        <div class="kpi-bar">
            <div class="kpi-pill"><span class="kpi-icon">🤝</span><span class="kpi-val" style="color:#1E293B;">{total}</span><span class="kpi-lbl">Total préstamos</span></div>
            <div class="kpi-sep"></div>
            <div class="kpi-pill"><span class="kpi-icon">🔵</span><span class="kpi-val" style="color:#1D4ED8;">{prestados}</span><span class="kpi-lbl">Prestados</span></div>
            <div class="kpi-sep"></div>
            <div class="kpi-pill"><span class="kpi-icon">✅</span><span class="kpi-val" style="color:#15803D;">{devueltos}</span><span class="kpi-lbl">Devueltos</span></div>
        </div>
    """, unsafe_allow_html=True)

    if "prestamos_pagina" not in st.session_state:
        st.session_state["prestamos_pagina"] = 0
    TAM_PAGINA = 50

    panel_filtros = st.container(key="panel_filtros")
    with panel_filtros:
        c_busq, c_fecha, c_est, c_nuevo = st.columns([3, 2, 1.8, 1.6])
        with c_busq:
            busqueda = st.text_input("buscar", placeholder="🔍  Buscar por folio, responsable o activo...", label_visibility="collapsed", key="busq_prestamos")
        with c_fecha:
            desde, hasta = filtro_rango_fechas("prestamos")
        with c_est:
            filtro_est = st.selectbox("estado", ["Todos", "Prestado", "Parcial", "Devuelto", "Vencido"], label_visibility="collapsed", key="filtro_estado_prestamos")
        with c_nuevo:
            if st.button("➕ Nuevo Préstamo", type="primary", width="stretch"):
                ventana_nuevo_prestamo()

    filtro_actual = (busqueda, filtro_est, desde, hasta)
    if st.session_state.get("prestamos_filtro_anterior") != filtro_actual:
        st.session_state["prestamos_pagina"] = 0
        st.session_state["prestamos_filtro_anterior"] = filtro_actual

    datos, total_filtrado = cargar_prestamos(
        pagina=st.session_state["prestamos_pagina"], tam_pagina=TAM_PAGINA,
        busqueda=busqueda, filtro_estado=filtro_est, desde=desde, hasta=hasta
    )
    df_f = pd.DataFrame(datos)

    if not df_f.empty:
        cw, ths = [1.3, 1.6, 1.8, 1, 1.1, 1, 0.6, 0.6, 0.6], ["Folio", "Responsable", "Activos", "Fecha", "Dev. estimada", "Estado", "✏️", "👁️", "↩️"]
        panel_tabla = st.container(key="panel_tabla")
        with panel_tabla:
# ═            st.markdown('<div class="panel-card-titulo">📋 Préstamos registrados</div>', unsafe_allow_html=True)
            c_titulo, c_indicador, c_excel, c_pdf = st.columns([2.3, 3.1, 2, 1.9])
            filtros_texto = " · ".join(p for p in [
                f"Búsqueda: '{busqueda}'" if busqueda.strip() else None,
                f"Estado: {filtro_est}" if filtro_est != "Todos" else None,
                f"Desde {desde}" + (f" hasta {hasta}" if hasta else "") if desde else None,
            ] if p) or "Sin filtros (todo el historial)"
            with c_titulo:
                st.markdown('<div class="panel-card-titulo">📋 Préstamos registrados</div>', unsafe_allow_html=True)
            with c_indicador:
                st.markdown(f"<p class='export-indicador'>Mostrando {len(df_f)} de {total_filtrado} registros con el filtro actual</p>", unsafe_allow_html=True)
            with c_excel:
                if st.button(f"⬇️ Exportar Excel ({total_filtrado})", width="stretch", key="pre_export_excel_btn"):
                    st.session_state["pre_generar_excel"] = True
            with c_pdf:
                if st.button(f"📄 Exportar PDF ({total_filtrado})", width="stretch", key="pre_export_pdf_btn"):
                    st.session_state["pre_generar_pdf"] = True
            if st.session_state.get("pre_generar_excel"):
                with st.spinner(f"Generando Excel de {total_filtrado} préstamos..."):
                    excel_bytes = generar_excel_prestamos(cargar_todos_prestamos(busqueda, filtro_est, desde, hasta))
                st.download_button("✅ Descargar Excel", data=excel_bytes, file_name=f"prestamos_{date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="pre_download_excel")
                st.session_state["pre_generar_excel"] = False
            if st.session_state.get("pre_generar_pdf"):
                with st.spinner(f"Generando PDF de {total_filtrado} préstamos..."):
                    pdf_bytes = generar_pdf_prestamos(cargar_todos_prestamos(busqueda, filtro_est, desde, hasta), filtros_texto)
                st.download_button("✅ Descargar PDF", data=pdf_bytes, file_name=f"prestamos_{date.today()}.pdf",
                    mime="application/pdf", key="pre_download_pdf")
                st.session_state["pre_generar_pdf"] = False
            h_cols = st.columns(cw)
            for idx, (col, txt) in enumerate(zip(h_cols, ths)):
                col.markdown(f"<p class='th'{' style=text-align:center;' if idx >= len(ths)-2 else ''}>{txt}</p>", unsafe_allow_html=True)
            for i, (_, row) in enumerate(df_f.iterrows()):
                cls = "td-alt" if i % 2 == 1 else "td"
                r = st.columns(cw)
                r[0].markdown(f"<div class='{cls}'><span class='folio-tag'>{row['folio']}</span></div>", unsafe_allow_html=True)
                r[1].markdown(f"<div class='{cls}'>{row['persona_nombre']}</div>", unsafe_allow_html=True)
                activos = (row.get("activos_completos") or "").split(", ") if row.get("activos_completos") else []
                primer_activo = activos[0] if activos else "—"
                extra = len(activos) - 1
                texto_activos = f"{primer_activo} +{extra} más" if extra > 0 else primer_activo
                tooltip = (row.get("activos_completos") or "").replace('"', "&quot;")
                r[2].markdown(f"<div class='{cls}' title=\"{tooltip}\">{texto_activos}</div>", unsafe_allow_html=True)
                r[3].markdown(f"<div class='{cls}'>{fmt_fecha(row['fecha_prestamo'])}</div>", unsafe_allow_html=True)
                r[4].markdown(f"<div class='{cls}'>{fmt_fecha(row.get('fecha_estimada')) or '—'}</div>", unsafe_allow_html=True)
                badge_map = {"prestado": "badge-completada", "parcial": "badge-cancelada", "devuelto": "badge-completada", "vencido": "badge-cancelada"}
                r[5].markdown(f"<div class='{cls}'><span class='badge {badge_map.get(row['estado'],'')}'>{row['estado'].capitalize()}</span></div>", unsafe_allow_html=True)
                with r[6]:
                    if st.button("✏️", key=f"ed_pre_{row['id']}", width="stretch"):
                        ventana_editar_prestamo(row.to_dict())
                with r[7]:
                    if st.button("👁️", key=f"ver_pre_{row['id']}", width="stretch"):
                        ventana_ver_detalle_prestamo(row.to_dict())
                with r[8]:
                    if st.button("↩️", key=f"dev_rap_{row['id']}", width="stretch",
                                 disabled=row["estado"] not in ("prestado", "parcial"), help="Devolver"):
                        ventana_devolucion_rapida(row.to_dict())

            total_paginas = max(1, -(-total_filtrado // TAM_PAGINA))
            c1, c2, c3 = st.columns([1, 2, 1])
            with c1:
                if st.button("← Anterior", disabled=st.session_state["prestamos_pagina"] <= 0, key="pre_pag_ant"):
                    st.session_state["prestamos_pagina"] -= 1
                    st.rerun()
            with c2:
                st.markdown(f"<p style='text-align:center; font-size:12px; color:#64748B; margin-top:8px;'>Página {st.session_state['prestamos_pagina'] + 1} de {total_paginas} · {total_filtrado} resultados</p>", unsafe_allow_html=True)
            with c3:
                if st.button("Siguiente →", disabled=st.session_state["prestamos_pagina"] >= total_paginas - 1, key="pre_pag_sig"):
                    st.session_state["prestamos_pagina"] += 1
                    st.rerun()
    else:
        st.info("📭 No hay préstamos registrados todavía. ¡Crea el primero!")

    if "_msg_prestamo" in st.session_state:
        st.success(st.session_state.pop("_msg_prestamo"))


# ══════════════════════════════════════════════════════════════
# ══════════════════════ CUSTODIAS Y DEVOLUCIONES ═══════════════
# ══════════════════════════════════════════════════════════════
def generar_folio_custodia():
    try:
        return supabase.rpc("generar_folio_custodia", {}).execute().data
    except Exception as e:
        st.error(f"Error al generar folio: {e}")
        return None


def generar_folio_devolucion():
    try:
        return supabase.rpc("generar_folio_devolucion", {}).execute().data
    except Exception as e:
        st.error(f"Error al generar folio: {e}")
        return None

def crear_custodia(payload):
    try:
        res = supabase.table("almacen_custodias").insert(payload).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as e:
        st.error(f"Error al crear la custodia: {e}")
        return None

def generar_excel_custodias(datos):
    filas = [{
        "Folio": c["folio"], "Responsable": c["persona_nombre"], "Activo": c["activo_codigo"],
        "Producto": c["producto_nombre"], "Inicio": fmt_fecha(c["fecha_inicio"]), "Fin": fmt_fecha(c.get("fecha_fin")),
        "Estado": c["estado"].capitalize(), "Motivo liberación": c.get("motivo_liberacion") or "",
    } for c in datos]
    buffer = BytesIO()
    pd.DataFrame(filas).to_excel(buffer, index=False, engine="openpyxl", sheet_name="Custodias")
    return buffer.getvalue()

def generar_pdf_custodias(datos, filtros_texto):
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "MSH-Hub - Reporte de Custodias", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 6, f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    if filtros_texto:
        pdf.cell(0, 6, pdf_safe(f"Filtros: {filtros_texto}"), ln=True)
    pdf.cell(0, 6, f"Total de registros: {len(datos)}", ln=True)
    pdf.ln(3)
    headers = ["Folio", "Responsable", "Activo", "Producto", "Inicio", "Fin", "Estado"]
    widths =  [26, 40, 28, 55, 24, 24, 24]
    pdf.set_font("Arial", "B", 8); pdf.set_fill_color(30, 52, 71); pdf.set_text_color(255, 255, 255)
    for h, w in zip(headers, widths):
        pdf.cell(w, 7, h, border=1, fill=True)
    pdf.ln()
    pdf.set_font("Arial", "", 7.5); pdf.set_text_color(30, 30, 30)
    for i, c in enumerate(datos):
        if i % 2 == 1:
            pdf.set_fill_color(250, 251, 252)
        else:
            pdf.set_fill_color(255, 255, 255)
        fila = [c["folio"], c["persona_nombre"][:24], c["activo_codigo"], c["producto_nombre"][:34],
                fmt_fecha(c["fecha_inicio"]), fmt_fecha(c.get("fecha_fin")) or "-", c["estado"].capitalize()]
        for val, w in zip(fila, widths):
            pdf.cell(w, 6, pdf_safe(val), border=1, fill=True)
        pdf.ln()
        if pdf.get_y() > 190:
            pdf.add_page()
            pdf.set_font("Arial", "B", 8); pdf.set_fill_color(30, 52, 71); pdf.set_text_color(255, 255, 255)
            for h, w in zip(headers, widths):
                pdf.cell(w, 7, h, border=1, fill=True)
            pdf.ln()
            pdf.set_font("Arial", "", 7.5); pdf.set_text_color(30, 30, 30)
    return pdf_output_bytes(pdf)

def cargar_custodias(pagina=0, tam_pagina=50, busqueda="", filtro_estado="Todos"):
    try:
        q = supabase.table("almacen_custodias_resumen").select("*", count="exact")
        if busqueda.strip():
            q = q.or_(f"folio.ilike.%{busqueda}%,persona_nombre.ilike.%{busqueda}%,activo_codigo.ilike.%{busqueda}%")
        if filtro_estado != "Todos":
            q = q.eq("estado", filtro_estado.lower())
        inicio = pagina * tam_pagina
        fin = inicio + tam_pagina - 1
        res = q.order("fecha_inicio", desc=True).range(inicio, fin).execute()
        return res.data or [], (res.count or 0)
    except Exception as e:
        st.error(f"Error al cargar custodias: {e}")
        return [], 0

def contar_custodias(filtro_estado=None):
    try:
        q = supabase.table("almacen_custodias_resumen").select("id", count="exact")
        if filtro_estado:
            q = q.eq("estado", filtro_estado)
        res = q.range(0, 0).execute()
        return res.count or 0
    except:
        return 0

def generar_excel_devoluciones(datos):
    filas = [{
        "Folio": d["folio"], "Fecha": fmt_fecha(d["fecha"]), "Origen": d.get("folio_origen") or "",
        "Responsable": d["persona_nombre"], "Tipo": "Préstamo" if d["tipo"] == "prestamo" else "Custodia",
        "Activos": d.get("activos_completos") or "", "Total activos": d["total_activos"],
        "Observaciones": d.get("observaciones") or "",
    } for d in datos]
    buffer = BytesIO()
    pd.DataFrame(filas).to_excel(buffer, index=False, engine="openpyxl", sheet_name="Devoluciones")
    return buffer.getvalue()

def generar_pdf_devoluciones(datos, filtros_texto):
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "MSH-Hub - Reporte de Devoluciones", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 6, f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    if filtros_texto:
        pdf.cell(0, 6, pdf_safe(f"Filtros: {filtros_texto}"), ln=True)
    pdf.cell(0, 6, f"Total de registros: {len(datos)}", ln=True)
    pdf.ln(3)
    headers = ["Folio", "Fecha", "Origen", "Responsable", "Tipo", "Activos", "Cant."]
    widths =  [26, 22, 26, 40, 26, 80, 18]
    pdf.set_font("Arial", "B", 8); pdf.set_fill_color(30, 52, 71); pdf.set_text_color(255, 255, 255)
    for h, w in zip(headers, widths):
        pdf.cell(w, 7, h, border=1, fill=True)
    pdf.ln()
    pdf.set_font("Arial", "", 7.5); pdf.set_text_color(30, 30, 30)
    for i, d in enumerate(datos):
        if i % 2 == 1:
            pdf.set_fill_color(250, 251, 252)
        else:
            pdf.set_fill_color(255, 255, 255)
        tipo_txt = "Prestamo" if d["tipo"] == "prestamo" else "Custodia"
        fila = [d["folio"], fmt_fecha(d["fecha"]), d.get("folio_origen") or "-", d["persona_nombre"][:24],
                tipo_txt, (d.get("activos_completos") or "-")[:50], str(d["total_activos"])]
        for val, w in zip(fila, widths):
            pdf.cell(w, 6, pdf_safe(val), border=1, fill=True)
        pdf.ln()
        if pdf.get_y() > 190:
            pdf.add_page()
            pdf.set_font("Arial", "B", 8); pdf.set_fill_color(30, 52, 71); pdf.set_text_color(255, 255, 255)
            for h, w in zip(headers, widths):
                pdf.cell(w, 7, h, border=1, fill=True)
            pdf.ln()
            pdf.set_font("Arial", "", 7.5); pdf.set_text_color(30, 30, 30)
    return pdf_output_bytes(pdf)

def cargar_devoluciones(pagina=0, tam_pagina=50, busqueda="", desde=None, hasta=None):
    try:
        q = supabase.table("almacen_devoluciones_resumen").select("*", count="exact")
        if busqueda.strip():
            q = q.or_(f"folio.ilike.%{busqueda}%,persona_nombre.ilike.%{busqueda}%,folio_origen.ilike.%{busqueda}%,activos_completos.ilike.%{busqueda}%")
        if desde:
            q = q.gte("fecha", desde)
        if hasta:
            q = q.lte("fecha", hasta)
        inicio = pagina * tam_pagina
        fin = inicio + tam_pagina - 1
        res = q.order("fecha", desc=True).range(inicio, fin).execute()
        return res.data or [], (res.count or 0)
    except Exception as e:
        st.error(f"Error al cargar devoluciones: {e}")
        return [], 0


def contar_devoluciones():
    try:
        res = supabase.table("almacen_devoluciones_resumen").select("id", count="exact").range(0, 0).execute()
        return res.count or 0
    except:
        return 0


def cargar_prestamos_activos_para_devolucion():
    try:
        res = supabase.table("almacen_prestamos_inventario").select(
            "*, almacen_personas(nombres, apellidos)"
        ).in_("estado", ["prestado", "parcial"]).execute()
        data = res.data if res.data else []
        for row in data:
            p = row.pop("almacen_personas", None)
            row["persona_nombre"] = f"{p['nombres']} {p.get('apellidos') or ''}".strip() if p else "—"
        return data
    except:
        return []


def cargar_custodias_activas_para_devolucion():
    try:
        res = supabase.table("almacen_custodias").select(
            "*, almacen_personas(nombres, apellidos), almacen_activos(codigo_activo)"
        ).eq("estado", "activa").execute()
        data = res.data if res.data else []
        for row in data:
            p = row.pop("almacen_personas", None)
            a = row.pop("almacen_activos", None)
            row["persona_nombre"] = f"{p['nombres']} {p.get('apellidos') or ''}".strip() if p else "—"
            row["activo_codigo"] = a["codigo_activo"] if a else "—"
        return data
    except:
        return []


if "custodia_detalle_lineas" not in st.session_state:
    st.session_state["custodia_detalle_lineas"] = []


@st.dialog("🔒 Nueva Custodia / Asignación", width="large")
def ventana_nueva_custodia():

    if st.session_state.get("custodia_dialogo_abierto") != True:
        st.session_state["custodia_detalle_lineas"] = []
        st.session_state["custodia_dialogo_abierto"] = True

    personas = cargar_personas_activas()

    c1, c2 = st.columns(2)
    with c1:
        opciones_persona = {p["nombre_completo"]: p["id"] for p in personas}
        sel_persona = st.selectbox("Responsable *", list(opciones_persona.keys()), key="custodia_persona_sel") if opciones_persona else None
        persona_id = opciones_persona.get(sel_persona)
    with c2:
        fecha_inicio = st.date_input("Fecha de inicio *", value=date.today(), format="DD/MM/YYYY", key="custodia_fecha")

    observaciones = st.text_area("Observaciones", key="custodia_observaciones", height=60)
    st.divider()
    st.markdown("**Agregar activo a asignar (indefinido, sin fecha de devolución fija)**")

    if "custodia_busqueda_expandida" not in st.session_state:
        st.session_state["custodia_busqueda_expandida"] = True

    with st.expander("🔍 Buscar herramienta", expanded=st.session_state["custodia_busqueda_expandida"]):
        query = st.text_input("Filtrar", placeholder="Filtrar por código de activo, código de producto o nombre...", key="custodia_busqueda", label_visibility="collapsed")

        df_activos = cargar_activos_prestables()
        if query.strip():
            texto = (df_activos["codigo_activo"] + " " + df_activos["producto_codigo"] + " " + df_activos["producto_nombre"]).str.lower()
            mask = pd.Series(True, index=df_activos.index)
            for termino in query.lower().split():
                mask &= texto.str.contains(re.escape(termino), na=False)
            df_filtrado = df_activos[mask]
        else:
            df_filtrado = df_activos

        df_vista = df_filtrado.head(200).reset_index(drop=True)
        evento = st.dataframe(
            df_vista[["codigo_activo", "producto_codigo", "producto_nombre", "serial"]],
            hide_index=True, width="stretch", height=240,
            on_select="rerun", selection_mode="single-row", key="custodia_tabla_activos",
            column_config={
                "codigo_activo": "Código activo", "producto_codigo": "Producto",
                "producto_nombre": "Nombre", "serial": "Serial",
            },
        )
        unidad_txt = "unidad" if len(df_activos) == 1 else "unidades"
        st.caption(f"{len(df_filtrado)} de {len(df_activos)} {unidad_txt} disponibles" if query.strip() else f"{len(df_activos)} {unidad_txt} disponibles para préstamo")

        filas_sel = evento.selection.rows if evento and evento.selection else []
        a = df_vista.iloc[filas_sel[0]].to_dict() if filas_sel else None

    if a:
        ya_agregado = any(l["activo_id"] == a["id"] for l in st.session_state["custodia_detalle_lineas"])
        st.markdown(f"🛠️ **{a['codigo_activo']}** — {a['producto_nombre']}" + (f" ({a['serial']})" if a.get("serial") else ""))
        if st.button("➕ Agregar", key=f"cus_add_{a['id']}", width="stretch", disabled=ya_agregado):
            st.session_state["custodia_detalle_lineas"].append({"activo_id": a["id"], "codigo_activo": a["codigo_activo"], "producto_nombre": a["producto_nombre"]})
            st.session_state["custodia_busqueda_expandida"] = False
            st.rerun(scope="fragment")

    if st.session_state["custodia_detalle_lineas"]:
        # Deduplica por activo_id conservando el orden (evita keys repetidas)
        vistos = set()
        lineas_unicas = []
        for l in st.session_state["custodia_detalle_lineas"]:
            if l["activo_id"] not in vistos:
                vistos.add(l["activo_id"])
                lineas_unicas.append(l)
        st.session_state["custodia_detalle_lineas"] = lineas_unicas

        activo_a_eliminar = None
        for linea in lineas_unicas:
            fila = st.empty()
            with fila.container():
                c1, c2 = st.columns([5, 0.6])
                c1.markdown(f"**{linea['codigo_activo']}** — {linea['producto_nombre']}")
                eliminar_click = c2.button("🗑️", key=f"cus_del_{linea['activo_id']}")
            if eliminar_click:
                activo_a_eliminar = linea["activo_id"]
                fila.empty()
        if activo_a_eliminar:
            st.session_state["custodia_detalle_lineas"] = [
                l for l in st.session_state["custodia_detalle_lineas"] if l["activo_id"] != activo_a_eliminar
            ]



    st.divider()
    c_cancel, c_guardar = st.columns([1, 2])
    with c_cancel:
        if st.button("Cancelar", width="stretch", key="cus_cancelar"):
            for k in ["custodia_persona_sel", "custodia_busqueda_expandida", "custodia_dialogo_abierto"]:
                st.session_state.pop(k, None)
            st.session_state["custodia_detalle_lineas"] = []
            st.rerun()

    with c_guardar:
        if st.button("✅ Guardar custodia", type="primary", width="stretch", key="cus_guardar",
                     disabled=not st.session_state["custodia_detalle_lineas"] or not persona_id):
            exitos = []
            for linea in st.session_state["custodia_detalle_lineas"]:
                folio = generar_folio_custodia()
                payload = {
                    "folio": folio, "persona_id": persona_id, "activo_id": linea["activo_id"],
                    "fecha_inicio": str(fecha_inicio), "estado": "activa",
                    "usuario_registro": st.session_state["usuario"], "nombre_registro": st.session_state["nombre"],
                    "observaciones": observaciones.strip() or None,
                }
                if crear_custodia(payload):
                    supabase.table("almacen_activos").update({"estado": "custodia", "responsable_actual": persona_id}).eq("id", linea["activo_id"]).execute()
                    exitos.append(folio)
            if exitos:
                registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"REGISTRAR CUSTODIA: {', '.join(exitos)}")
                st.session_state["custodia_detalle_lineas"] = []
                st.session_state["custodia_dialogo_abierto"] = False
                st.session_state["_msg_custodia"] = f"Custodia(s) guardada(s): {', '.join(exitos)}"
                st.rerun()

@st.dialog("↩️ Nueva Devolución", width="large")
def ventana_nueva_devolucion():
    tipo_dev = st.radio("¿Qué se va a devolver?", ["Préstamo", "Custodia"], horizontal=True, key="dev_tipo")

    if "devolucion_folio_sugerido" not in st.session_state:
        st.session_state["devolucion_folio_sugerido"] = generar_folio_devolucion()
    st.caption(f"Folio sugerido: `{st.session_state['devolucion_folio_sugerido']}`")

    fecha_dev = st.date_input("Fecha *", value=date.today(), format="DD/MM/YYYY", key="dev_fecha")
    observaciones = st.text_area("Observaciones", key="dev_observaciones", height=50)
    st.divider()

    if tipo_dev == "Préstamo":
        prestamos = cargar_prestamos_activos_para_devolucion()
        if not prestamos:
            st.info("No hay préstamos activos por devolver.")
            return
        opciones_prestamo = {f"{p['folio']} — {p['persona_nombre']}": p for p in prestamos}
        sel = st.selectbox("Préstamo *", list(opciones_prestamo.keys()), key="dev_prestamo_sel")
        prestamo = opciones_prestamo[sel]
        detalle = cargar_detalle_prestamo(prestamo["id"])
        pendientes = [d for d in detalle if not d["devuelto"]]

        st.markdown("**Activos a devolver:**")
        seleccion = {}
        for d in pendientes:
            c1, c2 = st.columns([3, 2])
            marcar = c1.checkbox(f"{d['activo_codigo']} — {d['producto_nombre']}", key=f"dev_check_{d['id']}")
            estado_recibido = c2.selectbox("Estado", ["bueno", "dañado", "perdido"], key=f"dev_estado_{d['id']}", label_visibility="collapsed") if marcar else "bueno"
            if marcar:
                seleccion[d["id"]] = {"activo_id": d["activo_id"], "estado_recibido": estado_recibido}

        c_cancel, c_guardar = st.columns([1, 2])
        with c_cancel:
            if st.button("Cancelar", width="stretch", key="dev_cancelar_prestamo"):
                for k in ["devolucion_folio_sugerido", "dev_prestamo_sel"]:
                    st.session_state.pop(k, None)
                st.rerun()

        with c_guardar:
            if st.button("✅ Guardar devolución", type="primary", width="stretch", key="dev_guardar_prestamo", disabled=not seleccion):
                payload = {
                    "folio": st.session_state["devolucion_folio_sugerido"], "prestamo_id": prestamo["id"],
                    "fecha": str(fecha_dev), "usuario_registro": st.session_state["usuario"],
                    "nombre_registro": st.session_state["nombre"], "observaciones": observaciones.strip() or None,
                }
                devolucion_id = crear_devolucion(payload)
                if devolucion_id:
                    for detalle_id, info in seleccion.items():
                        procesar_devolucion_activo(devolucion_id, info["activo_id"], info["estado_recibido"])
                        supabase.table("almacen_prestamos_inventario_detalle").update({"devuelto": True}).eq("id", detalle_id).execute()

                    todos_devueltos = len(seleccion) == len(pendientes)
                    nuevo_estado = "devuelto" if todos_devueltos else "parcial"
                    update_prestamo = {"estado": nuevo_estado}
                    if todos_devueltos:
                        update_prestamo["fecha_real"] = str(fecha_dev)
                    supabase.table("almacen_prestamos_inventario").update(update_prestamo).eq("id", prestamo["id"]).execute()
 
                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"REGISTRAR DEVOLUCION: {payload['folio']}")
                    del st.session_state["devolucion_folio_sugerido"]
                    st.session_state["_msg_devolucion"] = f"Devolución {payload['folio']} guardada correctamente."
                    st.rerun()
    else:
        custodias = cargar_custodias_activas_para_devolucion()
        if not custodias:
            st.info("No hay custodias activas por liberar.")
            return
        opciones_custodia = {f"{c['folio']} — {c['persona_nombre']} — {c['activo_codigo']}": c for c in custodias}
        sel = st.selectbox("Custodia *", list(opciones_custodia.keys()), key="dev_custodia_sel")
        custodia = opciones_custodia[sel]
        estado_recibido = st.selectbox("Estado en que se recibe", ["bueno", "dañado", "perdido"], key="dev_custodia_estado")
        motivo_liberacion = st.text_input("Motivo de liberación", placeholder="Ej. Renuncia, cambio de puesto, devolución voluntaria", key="dev_motivo_liberacion")

        c_cancel, c_guardar = st.columns([1, 2])
        with c_cancel:
            if st.button("Cancelar", width="stretch", key="dev_cancelar_custodia"):
                for k in ["devolucion_folio_sugerido", "dev_custodia_sel"]:
                    st.session_state.pop(k, None)
                st.rerun()

        with c_guardar:
            if st.button("✅ Guardar devolución", type="primary", width="stretch", key="dev_guardar_custodia"):
                payload = {
                    "folio": st.session_state["devolucion_folio_sugerido"], "custodia_id": custodia["id"],
                    "fecha": str(fecha_dev), "usuario_registro": st.session_state["usuario"],
                    "nombre_registro": st.session_state["nombre"], "observaciones": observaciones.strip() or None,
                }
                devolucion_id = crear_devolucion(payload)
                if devolucion_id:
                    procesar_devolucion_activo(devolucion_id, custodia["activo_id"], estado_recibido)
                    supabase.table("almacen_custodias").update({
                        "estado": "liberada", "fecha_fin": str(fecha_dev),
                        "motivo_liberacion": motivo_liberacion.strip() or None
                    }).eq("id", custodia["id"]).execute()

                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"REGISTRAR DEVOLUCION: {payload['folio']}")
                    del st.session_state["devolucion_folio_sugerido"]
                    st.session_state["_msg_devolucion"] = f"Devolución {payload['folio']} guardada correctamente."
                    st.rerun()

def crear_devolucion(payload):
    try:
        res = supabase.table("almacen_devoluciones").insert(payload).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as e:
        st.error(f"Error al crear la devolución: {e}")
        return None


def procesar_devolucion_activo(devolucion_id, activo_id, estado_recibido):
    try:
        supabase.table("almacen_devoluciones_detalle").insert({
            "devolucion_id": devolucion_id, "activo_id": activo_id, "estado_recibido": estado_recibido
        }).execute()
        nuevo_estado_activo = "disponible" if estado_recibido == "bueno" else ("mantenimiento" if estado_recibido == "dañado" else "inactivo")
        supabase.table("almacen_activos").update({"estado": nuevo_estado_activo, "responsable_actual": None}).eq("id", activo_id).execute()
        return True
    except Exception as e:
        st.warning(f"No se pudo procesar la devolución del activo: {e}")
        return False


def actualizar_custodia(id_registro, payload):
    try:
        supabase.table("almacen_custodias").update(payload).eq("id", id_registro).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar la custodia: {e}")
        return False


@st.dialog("✏️ Editar Custodia")
def ventana_editar_custodia(custodia):
    st.caption(f"Folio: `{custodia['folio']}`  ·  Activo: `{custodia['activo_codigo']}` — {custodia['producto_nombre']}")

    personas = cargar_personas_activas()
    opciones_persona = {p["nombre_completo"]: p["id"] for p in personas}
    nombres_persona = list(opciones_persona.keys())
    idx_persona = nombres_persona.index(custodia["persona_nombre"]) if custodia.get("persona_nombre") in nombres_persona else 0
    sel_persona = st.selectbox("Responsable", nombres_persona, index=idx_persona) if nombres_persona else None
    persona_id = opciones_persona.get(sel_persona)

    observaciones = st.text_area("Observaciones", value=custodia.get("observaciones") or "", height=60)

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Guardar Cambios", type="primary", width="stretch"):
            payload = {"persona_id": persona_id, "observaciones": observaciones.strip() or None}
            if actualizar_custodia(custodia["id"], payload):
                registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"EDITAR CUSTODIA: {custodia['folio']}")
                st.session_state["_msg_custodia"] = f"Custodia {custodia['folio']} actualizada."
                st.rerun()
    with c2:
        if st.button("❌ Cancelar", width="stretch"):
            st.rerun()


def render_seccion_custodias_devoluciones():
    total_cus = contar_custodias()
    activas = contar_custodias(filtro_estado="activa")
    liberadas = contar_custodias(filtro_estado="liberada")
    total_dev = contar_devoluciones()

    st.markdown(f"""
        <div class="kpi-bar">
            <div class="kpi-pill"><span class="kpi-icon">🔒</span><span class="kpi-val" style="color:#1E293B;">{total_cus}</span><span class="kpi-lbl">Total custodias</span></div>
            <div class="kpi-sep"></div>
            <div class="kpi-pill"><span class="kpi-icon">🔵</span><span class="kpi-val" style="color:#1D4ED8;">{activas}</span><span class="kpi-lbl">Activas</span></div>
            <div class="kpi-sep"></div>
            <div class="kpi-pill"><span class="kpi-icon">✅</span><span class="kpi-val" style="color:#15803D;">{liberadas}</span><span class="kpi-lbl">Liberadas</span></div>
            <div class="kpi-sep"></div>
            <div class="kpi-pill"><span class="kpi-icon">↩️</span><span class="kpi-val" style="color:#7E22CE;">{total_dev}</span><span class="kpi-lbl">Devoluciones</span></div>
        </div>
    """, unsafe_allow_html=True)

    panel_filtros = st.container(key="panel_filtros")
    with panel_filtros:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔒 Nueva Custodia", type="primary", width="stretch"):
                ventana_nueva_custodia()
        with c2:
            if st.button("↩️ Nueva Devolución", type="primary", width="stretch"):
                ventana_nueva_devolucion()

    if "_msg_custodia" in st.session_state:
        st.success(st.session_state.pop("_msg_custodia"))
    if "_msg_devolucion" in st.session_state:
        st.success(st.session_state.pop("_msg_devolucion"))

    if "cus_dev_vista" not in st.session_state:
        st.session_state["cus_dev_vista"] = "custodias"

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔒 Ver Custodias", width="stretch"):
            st.session_state["cus_dev_vista"] = "custodias"
            st.rerun()
    with c2:
        if st.button("↩️ Ver Devoluciones", width="stretch"):
            st.session_state["cus_dev_vista"] = "devoluciones"
            st.rerun()

    TAM_PAGINA = 50

    if st.session_state["cus_dev_vista"] == "custodias":
        if "custodias_pagina" not in st.session_state:
            st.session_state["custodias_pagina"] = 0

        c_busq, c_est = st.columns([3, 2])
        with c_busq:
            busqueda = st.text_input("buscar_cus", placeholder="🔍  Buscar por folio, responsable o código de activo...", label_visibility="collapsed", key="busq_custodias")
        with c_est:
            filtro_est = st.selectbox("estado_cus", ["Todos", "Activa", "Liberada"], label_visibility="collapsed", key="filtro_estado_custodias")

        filtro_actual = (busqueda, filtro_est)
        if st.session_state.get("custodias_filtro_anterior") != filtro_actual:
            st.session_state["custodias_pagina"] = 0
            st.session_state["custodias_filtro_anterior"] = filtro_actual

        datos, total_filtrado = cargar_custodias(
            pagina=st.session_state["custodias_pagina"], tam_pagina=TAM_PAGINA,
            busqueda=busqueda, filtro_estado=filtro_est
        )
        df_f = pd.DataFrame(datos)

        if not df_f.empty:
            cw, ths = [1.4, 2, 2, 1.3, 1.3, 0.8], ["Folio", "Responsable", "Activo", "Inicio", "Estado", "✏️"]
            panel_tabla = st.container(key="panel_tabla")
            with panel_tabla:
#                st.markdown('<div class="panel-card-titulo">📋 Custodias registradas</div>', unsafe_allow_html=True)
                c_titulo, c_indicador, c_excel, c_pdf = st.columns([2.3, 3.1, 2, 1.9])
                with c_titulo:
                    st.markdown('<div class="panel-card-titulo">📋 Custodias registradas</div>', unsafe_allow_html=True)
                with c_indicador:
                    st.markdown(f"<p class='export-indicador'>Mostrando {len(df_f)} de {total_filtrado} registros</p>", unsafe_allow_html=True)
                with c_excel:
                    if st.button(f"⬇️ Exportar Excel ({total_filtrado})", width="stretch", key="cus_export_excel_btn"):
                        st.session_state["cus_generar_excel"] = True
                with c_pdf:
                    if st.button(f"📄 Exportar PDF ({total_filtrado})", width="stretch", key="cus_export_pdf_btn"):
                        st.session_state["cus_generar_pdf"] = True
                if st.session_state.get("cus_generar_excel"):
                    with st.spinner("Generando Excel..."):
                        excel_bytes = generar_excel_custodias(cargar_custodias(pagina=0, tam_pagina=100000, busqueda=busqueda, filtro_estado=filtro_est)[0])
                    st.download_button("✅ Descargar Excel", data=excel_bytes, file_name=f"custodias_{date.today()}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="cus_download_excel")
                    st.session_state["cus_generar_excel"] = False
                if st.session_state.get("cus_generar_pdf"):
                    with st.spinner("Generando PDF..."):
                        pdf_bytes = generar_pdf_custodias(cargar_custodias(pagina=0, tam_pagina=100000, busqueda=busqueda, filtro_estado=filtro_est)[0], f"Estado: {filtro_est}")
                    st.download_button("✅ Descargar PDF", data=pdf_bytes, file_name=f"custodias_{date.today()}.pdf",
                        mime="application/pdf", key="cus_download_pdf")
                    st.session_state["cus_generar_pdf"] = False
                h_cols = st.columns(cw)
                for idx, (col, txt) in enumerate(zip(h_cols, ths)):
                    col.markdown(f"<p class='th'{' style=text-align:center;' if idx == len(ths)-1 else ''}>{txt}</p>", unsafe_allow_html=True)
                for i, (_, row) in enumerate(df_f.iterrows()):
                    cls = "td-alt" if i % 2 == 1 else "td"
                    r = st.columns(cw)
                    r[0].markdown(f"<div class='{cls}'><span class='folio-tag'>{row['folio']}</span></div>", unsafe_allow_html=True)
                    r[1].markdown(f"<div class='{cls}'>{row['persona_nombre']}</div>", unsafe_allow_html=True)
                    r[2].markdown(f"<div class='{cls}'>{row['activo_codigo']} — {row['producto_nombre']}</div>", unsafe_allow_html=True)
                    r[3].markdown(f"<div class='{cls}'>{fmt_fecha(row['fecha_inicio'])}</div>", unsafe_allow_html=True)
                    badge_cls = "badge-completada" if row["estado"] == "activa" else "badge-cancelada"
                    r[4].markdown(f"<div class='{cls}'><span class='badge {badge_cls}'>{row['estado'].capitalize()}</span></div>", unsafe_allow_html=True)
                    with r[5]:
                        if row["estado"] == "activa":
                            if st.button("✏️", key=f"ed_cus_{row['id']}", width="stretch"):
                                ventana_editar_custodia(row.to_dict())

                total_paginas = max(1, -(-total_filtrado // TAM_PAGINA))
                c1, c2, c3 = st.columns([1, 2, 1])
                with c1:
                    if st.button("← Anterior", disabled=st.session_state["custodias_pagina"] <= 0, key="cus_pag_ant"):
                        st.session_state["custodias_pagina"] -= 1
                        st.rerun()
                with c2:
                    st.markdown(f"<p style='text-align:center; font-size:12px; color:#64748B; margin-top:8px;'>Página {st.session_state['custodias_pagina'] + 1} de {total_paginas} · {total_filtrado} resultados</p>", unsafe_allow_html=True)
                with c3:
                    if st.button("Siguiente →", disabled=st.session_state["custodias_pagina"] >= total_paginas - 1, key="cus_pag_sig"):
                        st.session_state["custodias_pagina"] += 1
                        st.rerun()
        else:
            st.info("📭 No hay custodias registradas todavía.")

    else:
        if "devoluciones_pagina" not in st.session_state:
            st.session_state["devoluciones_pagina"] = 0

        c_busq, c_fecha = st.columns([3, 2])
        with c_busq:
            busqueda = st.text_input("buscar_dev", placeholder="🔍  Buscar por folio, origen, responsable o activo...", label_visibility="collapsed", key="busq_devoluciones")
        with c_fecha:
            desde, hasta = filtro_rango_fechas("devoluciones")

        filtro_actual = (busqueda, desde, hasta)
        if st.session_state.get("devoluciones_filtro_anterior") != filtro_actual:
            st.session_state["devoluciones_pagina"] = 0
            st.session_state["devoluciones_filtro_anterior"] = filtro_actual

        datos, total_filtrado = cargar_devoluciones(
            pagina=st.session_state["devoluciones_pagina"], tam_pagina=TAM_PAGINA,
            busqueda=busqueda, desde=desde, hasta=hasta
        )
        df_f = pd.DataFrame(datos)

        if not df_f.empty:
            cw, ths = [1.3, 1, 1.3, 1.7, 1.9, 1, 1], ["Folio", "Fecha", "Origen", "Responsable", "Activos", "Tipo", "Cant."]
            panel_tabla = st.container(key="panel_tabla")
            with panel_tabla:
#                st.markdown('<div class="panel-card-titulo">📋 Devoluciones registradas</div>', unsafe_allow_html=True)
                c_titulo, c_indicador, c_excel, c_pdf = st.columns([2.3, 3.1, 2, 1.9])
                with c_titulo:
                    st.markdown('<div class="panel-card-titulo">📋 Devoluciones registradas</div>', unsafe_allow_html=True)
                with c_indicador:
                    st.markdown(f"<p class='export-indicador'>Mostrando {len(df_f)} de {total_filtrado} registros</p>", unsafe_allow_html=True)
                with c_excel:
                    if st.button(f"⬇️ Exportar Excel ({total_filtrado})", width="stretch", key="dev_export_excel_btn"):
                        st.session_state["dev_generar_excel"] = True
                with c_pdf:
                    if st.button(f"📄 Exportar PDF ({total_filtrado})", width="stretch", key="dev_export_pdf_btn"):
                        st.session_state["dev_generar_pdf"] = True
                if st.session_state.get("dev_generar_excel"):
                    with st.spinner("Generando Excel..."):
                        excel_bytes = generar_excel_devoluciones(cargar_devoluciones(pagina=0, tam_pagina=100000, busqueda=busqueda)[0])
                    st.download_button("✅ Descargar Excel", data=excel_bytes, file_name=f"devoluciones_{date.today()}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dev_download_excel")
                    st.session_state["dev_generar_excel"] = False
                if st.session_state.get("dev_generar_pdf"):
                    with st.spinner("Generando PDF..."):
                        pdf_bytes = generar_pdf_devoluciones(cargar_devoluciones(pagina=0, tam_pagina=100000, busqueda=busqueda)[0], "")
                    st.download_button("✅ Descargar PDF", data=pdf_bytes, file_name=f"devoluciones_{date.today()}.pdf",
                        mime="application/pdf", key="dev_download_pdf")
                    st.session_state["dev_generar_pdf"] = False
                h_cols = st.columns(cw)
                for idx, (col, txt) in enumerate(zip(h_cols, ths)):
                    col.markdown(f"<p class='th'{' style=text-align:center;' if idx == len(ths)-1 else ''}>{txt}</p>", unsafe_allow_html=True)
                for i, (_, row) in enumerate(df_f.iterrows()):
                    cls = "td-alt" if i % 2 == 1 else "td"
                    r = st.columns(cw)
                    r[0].markdown(f"<div class='{cls}'><span class='folio-tag'>{row['folio']}</span></div>", unsafe_allow_html=True)
                    r[1].markdown(f"<div class='{cls}'>{fmt_fecha(row['fecha'])}</div>", unsafe_allow_html=True)
                    r[2].markdown(f"<div class='{cls}'><span class='folio-tag'>{row.get('folio_origen') or '—'}</span></div>", unsafe_allow_html=True)
                    r[3].markdown(f"<div class='{cls}'>{row['persona_nombre']}</div>", unsafe_allow_html=True)
                    activos = (row.get("activos_completos") or "").split(", ") if row.get("activos_completos") else []
                    primer_activo = activos[0] if activos else "—"
                    extra = len(activos) - 1
                    texto_activos = f"{primer_activo} +{extra} más" if extra > 0 else primer_activo
                    tooltip = (row.get("activos_completos") or "").replace('"', "&quot;")
                    r[4].markdown(f"<div class='{cls}' title=\"{tooltip}\">{texto_activos}</div>", unsafe_allow_html=True)
                    tipo_icono = "🤝 Préstamo" if row["tipo"] == "prestamo" else "🔒 Custodia"
                    r[5].markdown(f"<div class='{cls}'>{tipo_icono}</div>", unsafe_allow_html=True)
                    r[6].markdown(f"<div class='{cls}' style='text-align:center;'>{row['total_activos']}</div>", unsafe_allow_html=True)

                total_paginas = max(1, -(-total_filtrado // TAM_PAGINA))
                c1, c2, c3 = st.columns([1, 2, 1])
                with c1:
                    if st.button("← Anterior", disabled=st.session_state["devoluciones_pagina"] <= 0, key="dev_pag_ant"):
                        st.session_state["devoluciones_pagina"] -= 1
                        st.rerun()
                with c2:
                    st.markdown(f"<p style='text-align:center; font-size:12px; color:#64748B; margin-top:8px;'>Página {st.session_state['devoluciones_pagina'] + 1} de {total_paginas} · {total_filtrado} resultados</p>", unsafe_allow_html=True)
                with c3:
                    if st.button("Siguiente →", disabled=st.session_state["devoluciones_pagina"] >= total_paginas - 1, key="dev_pag_sig"):
                        st.session_state["devoluciones_pagina"] += 1
                        st.rerun()
        else:
            st.info("📭 No hay devoluciones registradas todavía.")


# ══════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════
st.markdown(f"""
    <div class="msh-header">
        <div class="msh-header-left">
            <div class="msh-logo-box">🔄</div>
            <div>
                <div class="msh-title">MSH-Hub · Almacén · Movimientos</div>
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

# ══════════════════════════════════════════════
# SELECTOR DE SECCIÓN (sin st.tabs — solo carga la sección activa)
# ══════════════════════════════════════════════
if "movimientos_seccion" not in st.session_state:
    st.session_state["movimientos_seccion"] = "entradas"

panel_selector = st.container(key="panel_selector")
with panel_selector:
    c1, c2, c3, c4 = st.columns(4)
    secciones = [
        ("entradas", "📥 Entradas", c1),
        ("salidas", "📤 Salidas", c2),
        ("prestamos", "🤝 Préstamos", c3),
        ("custodias_devoluciones", "🔁 Custodias / Devoluciones", c4),
    ]
    for key, label, col in secciones:
        with col:
            es_activa = st.session_state["movimientos_seccion"] == key
            st.markdown(f'<div class="{"selector-btn-activo" if es_activa else ""}">', unsafe_allow_html=True)
            if st.button(label, width="stretch", key=f"btn_sec_{key}"):
                st.session_state["movimientos_seccion"] = key
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════
# RENDER SOLO DE LA SECCIÓN ACTIVA
# ══════════════════════════════════════════════
seccion = st.session_state["movimientos_seccion"]

if seccion == "entradas":
    render_seccion_entradas()
elif seccion == "salidas":
    render_seccion_salidas()
elif seccion == "prestamos":
    render_seccion_prestamos()
elif seccion == "custodias_devoluciones":
    render_seccion_custodias_devoluciones()

res = supabase.table("almacen_productos").select("id", count="exact").eq("activo", True).execute()
st.write(f"Total en BD: {res.count} — Filas traídas: {len(res.data)}")
