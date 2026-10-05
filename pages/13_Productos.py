import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import date, datetime
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw
import io

st.set_page_config(
    page_title="MSH-Hub | Productos",
    layout="wide",
    page_icon="📦",
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
.badge-activo    { background:#DCFCE7; color:#15803D; }
.badge-inactivo  { background:#F1F5F9; color:#64748B; }
.badge-tipo-activo  { background:#EFF6FF; color:#1D4ED8; }
.badge-tipo-insumo  { background:#FEF3E8; color:#C2410C; }
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
    width: 72vw !important; max-width: 980px !important;
    min-width: 480px !important; border-radius: 16px !important;
    max-height: 85vh !important; overflow-y: auto !important;
}
div[data-testid="stDialog"] [data-testid="stWidgetLabel"] p {
    font-size: 11px !important; font-weight: 600 !important; color: #64748B !important;
    text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: -2px !important;
}
[data-testid="stButton"] button {
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 12px !important;
}
[data-testid="stButton"] button[kind="primary"] {
    background: #1E3447 !important; border: none !important;
    box-shadow: 0 2px 8px rgba(30,52,71,0.25) !important;
}
.side-photo-box {
    width: 100%; aspect-ratio: 1/1; background: #F1F5F9; border: 1px dashed #CBD5E0;
    border-radius: 12px; display: flex; align-items: center; justify-content: center;
    flex-direction: column; color: #94A3B8; font-size: 12px; overflow: hidden;
}
.tab-hint {
    background: #EFF6FF; color: #1D4ED8; border-radius: 8px; padding: 8px 12px;
    font-size: 12px; margin-bottom: 14px;
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

TABLE = "almacen_productos"

# TODO: confirma el nombre real del bucket de Supabase Storage donde
# quieres guardar fotos/documentos de productos. Uso "productos" como
# placeholder — créalo en Supabase > Storage si no existe todavía.
BUCKET_FOTOS = "productos"
BUCKET_DOCS = "productos-documentos"


# ══════════════════════════════════════════════
# FUNCIONES DE ACCESO A DATOS
# ══════════════════════════════════════════════
def generar_etiqueta_codigo(codigo, texto_secundario=None):
    """Genera una imagen PNG con código de barras Code128 + texto legible debajo.
    Sirve tanto para codigo de producto (PRO-0001) como codigo_activo (A1HITAL1501)."""
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


def registrar_acceso(usuario, nombre, accion):
    try:
        supabase.table("usuarios_accesos").insert({
            "usuario": usuario, "nombre": nombre,
            "accion": accion, "fecha_hora": datetime.now().isoformat()
        }).execute()
    except:
        pass


def cargar_clasificaciones_activas():
    try:
        res = supabase.table("almacen_clasificaciones").select("id, nombre").eq("activo", True).order("nombre").execute()
        return res.data if res.data else []
    except:
        return []


def cargar_categorias_activas(clasificacion_id=None):
    try:
        q = supabase.table("almacen_categorias").select("id, nombre, clasificacion_id").eq("activo", True)
        if clasificacion_id:
            q = q.eq("clasificacion_id", clasificacion_id)
        res = q.order("nombre").execute()
        return res.data if res.data else []
    except:
        return []


def cargar_marcas_activas():
    try:
        res = supabase.table("almacen_marcas").select("id, nombre").eq("activo", True).order("nombre").execute()
        return res.data if res.data else []
    except:
        return []


def cargar_modelos_activos(marca_id=None):
    try:
        q = supabase.table("almacen_modelos").select("id, nombre, marca_id").eq("activo", True)
        if marca_id:
            q = q.eq("marca_id", marca_id)
        res = q.order("nombre").execute()
        return res.data if res.data else []
    except:
        return []


def cargar_unidades_activas():
    try:
        res = supabase.table("almacen_unidades_medida").select("id, nombre, abreviatura").eq("activo", True).order("nombre").execute()
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


def cargar_productos(pagina=0, tam_pagina=50, busqueda="", filtro_tipo="Todos", filtro_est="Todos"):
    try:
        q = supabase.table(TABLE).select(
            "*, almacen_categorias(nombre), almacen_marcas(nombre)", count="exact"
        )
        if busqueda.strip():
            q = q.or_(f"codigo.ilike.%{busqueda}%,nombre.ilike.%{busqueda}%")
        if filtro_tipo != "Todos":
            q = q.eq("tipo_producto", filtro_tipo.lower())
        if filtro_est == "Activos":
            q = q.eq("activo", True)
        elif filtro_est == "Inactivos":
            q = q.eq("activo", False)
        inicio = pagina * tam_pagina
        fin = inicio + tam_pagina - 1
        res = q.order("nombre").range(inicio, fin).execute()
        data = res.data if res.data else []
        for row in data:
            cat = row.pop("almacen_categorias", None)
            marca = row.pop("almacen_marcas", None)
            row["categoria_nombre"] = cat["nombre"] if cat else "—"
            row["marca_nombre"] = marca["nombre"] if marca else "—"
        return data, (res.count or 0)
    except Exception as e:
        st.error(f"Error al cargar productos: {e}")
        return [], 0


def contar_productos(filtro_tipo=None, filtro_activo=None):
    try:
        q = supabase.table(TABLE).select("id", count="exact")
        if filtro_tipo:
            q = q.eq("tipo_producto", filtro_tipo)
        if filtro_activo is not None:
            q = q.eq("activo", filtro_activo)
        res = q.range(0, 0).execute()
        return res.count or 0
    except:
        return 0


def codigo_producto_existe(codigo, excluir_id=None):
    try:
        q = supabase.table(TABLE).select("id").eq("codigo", codigo).execute().data
        if excluir_id:
            q = [r for r in q if r["id"] != excluir_id]
        return len(q) > 0
    except:
        return False


def subir_archivo(bucket, carpeta, archivo):
    """Sube un archivo de Streamlit (UploadedFile) a Supabase Storage y regresa la URL pública."""
    try:
        ruta = f"{carpeta}/{datetime.now().strftime('%Y%m%d%H%M%S')}_{archivo.name}"
        supabase.storage.from_(bucket).upload(
            ruta, archivo.getvalue(),
            {"content-type": archivo.type or "application/octet-stream"}
        )
        return supabase.storage.from_(bucket).get_public_url(ruta)
    except Exception as e:
        st.warning(f"No se pudo subir '{archivo.name}': {e}")
        return None


def generar_codigo_activo(producto_id):
    try:
        res = supabase.rpc("generar_codigo_activo", {"p_producto_id": producto_id}).execute()
        return res.data
    except Exception as e:
        st.error(f"Error al generar código de activo: {e}")
        return None


def generar_codigo_producto():
    try:
        res = supabase.rpc("generar_codigo_producto", {}).execute()
        return res.data
    except Exception as e:
        st.error(f"Error al generar código de producto: {e}")
        return None


def crear_producto(payload):
    try:
        res = supabase.table(TABLE).insert(payload).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as e:
        st.error(f"Error al crear producto: {e}")
        return None


def actualizar_producto(id_registro, payload):
    try:
        supabase.table(TABLE).update(payload).eq("id", id_registro).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar producto: {e}")
        return False


def crear_existencia_inicial(producto_id, payload):
    try:
        supabase.table("almacen_existencias").insert({"producto_id": producto_id, **payload}).execute()
        return True
    except Exception as e:
        st.warning(f"No se pudo crear la existencia inicial: {e}")
        return False


def crear_lote_inicial(producto_id, payload):
    try:
        supabase.table("almacen_lotes").insert({"producto_id": producto_id, **payload}).execute()
        return True
    except Exception as e:
        st.warning(f"No se pudo crear el lote inicial: {e}")
        return False


def crear_activos_iniciales(producto_id, cantidad, condicion, ubicacion_id, series_texto):
    series = [s.strip() for s in (series_texto or "").splitlines() if s.strip()]
    creados = []
    for i in range(int(cantidad)):
        codigo = generar_codigo_activo(producto_id)
        if not codigo:
            continue
        serial = series[i] if i < len(series) else None
        try:
            supabase.table("almacen_activos").insert({
                "producto_id": producto_id,
                "codigo_activo": codigo,
                "serial": serial,
                "condicion": condicion,
                "ubicacion_actual": ubicacion_id,
                "estado": "disponible"
            }).execute()
            creados.append(codigo)
        except Exception as e:
            st.warning(f"No se pudo crear el activo {codigo}: {e}")
    return creados


# ══════════════════════════════════════════════
# ESTADO DEL FORMULARIO (compartido entre Nuevo/Editar)
# ══════════════════════════════════════════════
def resetear_formulario_producto(modo, datos=None):
    defaults = {
        "np_id": None,
        "np_codigo": "", "np_nombre": "", "np_descripcion": "",
        "np_clasificacion_id": None, "np_categoria_id": None,
        "np_marca_id": None, "np_modelo_id": None, "np_unidad_id": None,
        "np_tipo_producto": "activo",
        "np_codigo_qr": "",
        "np_estado_activo": True,
        "np_permite_prestamo": False, "np_permite_custodia": False,
        "np_requiere_serie": False, "np_requiere_mantenimiento": False,
        "np_controla_garantia": False, "np_vida_util_meses": None,
        "np_controla_stock_minimo": False, "np_stock_minimo": 0.0,
        "np_stock_maximo": None, "np_punto_reorden": None,
        "np_controla_lote": False, "np_controla_vencimiento": False,
        "np_cantidad_inicial": 0.0, "np_ubicacion_inicial_id": None,
        "np_costo_inicial": None, "np_numero_lote": "",
        "np_fecha_vencimiento_lote": None, "np_fecha_ingreso_lote": date.today(),
        "np_cantidad_activos": 1, "np_series_texto": "",
        "np_condicion_inicial": "nuevo", "np_ubicacion_activos_id": None,
        "np_costo_referencia": None, "np_proveedor_texto": "",
        "np_garantia_meses": None, "np_fecha_compra_ref": None,
        "np_fotografia_url_actual": None,
    }
    for k, v in defaults.items():
        st.session_state[k] = v

    if modo == "editar" and datos:
        st.session_state.update({
            "np_id": datos["id"],
            "np_codigo": datos.get("codigo", ""),
            "np_nombre": datos.get("nombre", ""),
            "np_descripcion": datos.get("descripcion") or "",
            "np_clasificacion_id": datos.get("clasificacion_id"),
            "np_categoria_id": datos.get("categoria_id"),
            "np_marca_id": datos.get("marca_id"),
            "np_modelo_id": datos.get("modelo_id"),
            "np_unidad_id": datos.get("unidad_medida_id"),
            "np_tipo_producto": datos.get("tipo_producto", "activo"),
            "np_codigo_qr": datos.get("codigo_qr") or "",
            "np_estado_activo": datos.get("activo", True),
            "np_permite_prestamo": datos.get("permite_prestamo", False),
            "np_permite_custodia": datos.get("permite_custodia", False),
            "np_requiere_serie": datos.get("requiere_serie", False),
            "np_requiere_mantenimiento": datos.get("requiere_mantenimiento", False),
            "np_controla_garantia": datos.get("controla_garantia", False),
            "np_vida_util_meses": datos.get("vida_util_meses"),
            "np_controla_stock_minimo": datos.get("controla_stock_minimo", False),
            "np_controla_lote": datos.get("controla_lote", False),
            "np_controla_vencimiento": datos.get("controla_vencimiento", False),
            "np_costo_referencia": datos.get("costo_referencia"),
            "np_garantia_meses": datos.get("garantia_meses"),
            "np_fotografia_url_actual": datos.get("fotografia"),
        })

    st.session_state["np_form_loaded_for"] = "nuevo" if modo == "nuevo" else datos["id"]


# ══════════════════════════════════════════════
# RENDER DEL FORMULARIO (panel lateral + 5 pestañas)
# ══════════════════════════════════════════════
def renderizar_formulario_producto(modo):
    clasifs = cargar_clasificaciones_activas()
    marcas = cargar_marcas_activas()
    unidades = cargar_unidades_activas()
    ubicaciones = cargar_ubicaciones_activas()

    col_form, col_side = st.columns([3, 1.1])

    # ── PANEL LATERAL FIJO ──
    with col_side:
        st.markdown("**Imagen del Producto**")
        foto_nueva = st.file_uploader("Foto principal", type=["png", "jpg", "jpeg"], key="np_fotografia_file", label_visibility="collapsed")
        if foto_nueva:
            st.image(foto_nueva, width="stretch")
        elif st.session_state.get("np_fotografia_url_actual"):
            st.image(st.session_state["np_fotografia_url_actual"], width="stretch")
        else:
            st.markdown('<div class="side-photo-box">📷<br>Sin imagen</div>', unsafe_allow_html=True)

        st.markdown("<br>**Estado del Producto**", unsafe_allow_html=True)
        st.toggle("Activo", key="np_estado_activo")

    # ── PESTAÑAS ──
    with col_form:
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Información General", "⚙️ Configuración",
            "📦 Existencias/Activos", "🖼️ Imágenes y Docs", "ℹ️ Info. Adicional"
        ])

        # PESTAÑA 1 · INFORMACIÓN GENERAL
        with tab1:
            c1, c2 = st.columns(2)
            with c1:
                if modo == "nuevo":
                    st.text_input("Código", value="Se generará automáticamente al guardar", disabled=True)
                else:
                    st.text_input("Código", value=st.session_state["np_codigo"], disabled=True)
            with c2:
                st.text_input("Nombre *", key="np_nombre", placeholder="Ej. Taladro Inalámbrico")

            if modo == "editar" and st.session_state.get("np_codigo"):
                st.image(generar_etiqueta_codigo(st.session_state["np_codigo"]), width=220)
            st.text_area("Descripción", key="np_descripcion", height=70)

            c1, c2, c3 = st.columns(3)
            with c1:
                opciones_clasif = {c["nombre"]: c["id"] for c in clasifs}
                nombres_clasif = list(opciones_clasif.keys())
                sel = st.selectbox("Clasificación *", nombres_clasif, key="np_clasificacion_sel") if nombres_clasif else None
                st.session_state["np_clasificacion_id"] = opciones_clasif.get(sel)
                if not nombres_clasif:
                    st.caption("⚠️ No hay Clasificaciones activas — créalas primero en el catálogo.")
            with c2:
                categs = cargar_categorias_activas(st.session_state["np_clasificacion_id"])
                opciones_cat = {c["nombre"]: c["id"] for c in categs}
                nombres_cat = list(opciones_cat.keys())
                sel = st.selectbox("Categoría *", nombres_cat, key="np_categoria_sel") if nombres_cat else None
                st.session_state["np_categoria_id"] = opciones_cat.get(sel)
                if not nombres_cat:
                    st.caption("⚠️ Elige una Clasificación con categorías activas.")
            with c3:
                opciones_marca = {"— Ninguna —": None, **{m["nombre"]: m["id"] for m in marcas}}
                sel = st.selectbox("Marca", list(opciones_marca.keys()), key="np_marca_sel")
                st.session_state["np_marca_id"] = opciones_marca.get(sel)

            c1, c2, c3 = st.columns(3)
            with c1:
                modelos = cargar_modelos_activos(st.session_state["np_marca_id"]) if st.session_state["np_marca_id"] else []
                opciones_modelo = {"— Ninguno —": None, **{m["nombre"]: m["id"] for m in modelos}}
                sel = st.selectbox("Modelo", list(opciones_modelo.keys()), key="np_modelo_sel")
                st.session_state["np_modelo_id"] = opciones_modelo.get(sel)
            with c2:
                opciones_uni = {u["nombre"]: u["id"] for u in unidades}
                nombres_uni = list(opciones_uni.keys())
                sel = st.selectbox("Unidad de medida *", nombres_uni, key="np_unidad_sel") if nombres_uni else None
                st.session_state["np_unidad_id"] = opciones_uni.get(sel)
                if not nombres_uni:
                    st.caption("⚠️ No hay Unidades de medida activas — créalas primero en el catálogo.")
            with c3:
                st.selectbox(
                    "Tipo de producto *",
                    options=["activo", "insumo"],
                    format_func=lambda v: "🛠️ Activo individual" if v == "activo" else "📦 Insumo (existencias)",
                    key="np_tipo_producto"
                )

            st.text_input("Código QR", key="np_codigo_qr", placeholder="Se puede generar después")

        # PESTAÑA 2 · CONFIGURACIÓN
        with tab2:
            tipo = st.session_state["np_tipo_producto"]
            if tipo == "activo":
                st.markdown('<div class="tab-hint">⚙️ Comportamiento para productos tipo <b>Activo individual</b></div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.toggle("Permite préstamo", key="np_permite_prestamo")
                    st.toggle("Permite custodia", key="np_permite_custodia")
                    st.toggle("Requiere número de serie", key="np_requiere_serie")
                with c2:
                    st.toggle("Requiere mantenimiento", key="np_requiere_mantenimiento")
                    st.toggle("Controlar garantía", key="np_controla_garantia")
                    if st.session_state["np_controla_garantia"]:
                        st.number_input("Vida útil (meses)", min_value=0, step=1, key="np_vida_util_meses")
            else:
                st.markdown('<div class="tab-hint">⚙️ Comportamiento para productos tipo <b>Insumo (existencias)</b></div>', unsafe_allow_html=True)
                st.toggle("Controlar stock mínimo", key="np_controla_stock_minimo")
                if st.session_state["np_controla_stock_minimo"]:
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.number_input("Stock mínimo", min_value=0.0, step=1.0, key="np_stock_minimo")
                    with c2:
                        st.number_input("Stock máximo", min_value=0.0, step=1.0, key="np_stock_maximo")
                    with c3:
                        st.number_input("Punto de reorden", min_value=0.0, step=1.0, key="np_punto_reorden")
                st.toggle("Manejo por lote", key="np_controla_lote")
                st.toggle(
                    "Manejo por fecha de vencimiento",
                    key="np_controla_vencimiento",
                    disabled=not st.session_state["np_controla_lote"],
                    help="Requiere activar primero 'Manejo por lote'"
                )

        # PESTAÑA 3 · EXISTENCIAS / ACTIVOS INICIALES
        with tab3:
            if modo == "editar":
                st.info("📦 Las existencias y activos se gestionan desde los módulos de Entradas, Salidas y Activos — no se modifican aquí.")
            else:
                tipo = st.session_state["np_tipo_producto"]
                if tipo == "insumo":
                    st.markdown('<div class="tab-hint">📦 Cantidad con la que este insumo entra al sistema hoy</div>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.number_input("Cantidad inicial", min_value=0.0, step=1.0, key="np_cantidad_inicial")
                    with c2:
                        opciones_ubi = {u["breadcrumb"]: u["id"] for u in ubicaciones}
                        sel = st.selectbox("Ubicación inicial", list(opciones_ubi.keys()), key="np_ubicacion_sel") if opciones_ubi else None
                        st.session_state["np_ubicacion_inicial_id"] = opciones_ubi.get(sel)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.number_input("Costo inicial (unitario)", min_value=0.0, step=0.01, key="np_costo_inicial")
                    with c2:
                        st.date_input("Fecha de ingreso", key="np_fecha_ingreso_lote")
                    if st.session_state["np_controla_lote"]:
                        c1, c2 = st.columns(2)
                        with c1:
                            st.text_input("Número de lote", key="np_numero_lote")
                        with c2:
                            if st.session_state["np_controla_vencimiento"]:
                                st.date_input("Fecha de vencimiento", key="np_fecha_vencimiento_lote")
                else:
                    st.markdown('<div class="tab-hint">🔧 Se creará un activo individual por cada unidad</div>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.number_input("Cantidad de activos a registrar", min_value=1, step=1, key="np_cantidad_activos")
                    with c2:
                        opciones_ubi = {u["breadcrumb"]: u["id"] for u in ubicaciones}
                        sel = st.selectbox("Ubicación inicial", list(opciones_ubi.keys()), key="np_ubicacion_activos_sel") if opciones_ubi else None
                        st.session_state["np_ubicacion_activos_id"] = opciones_ubi.get(sel)
                    st.selectbox("Estado inicial", ["nuevo", "usado", "reacondicionado"],
                                 format_func=lambda v: v.capitalize(), key="np_condicion_inicial")
                    st.text_area(
                        "Números de serie (opcional)", key="np_series_texto", height=80,
                        help="Uno por línea. Si escribes menos líneas que la cantidad, el resto queda sin serie."
                    )

        # PESTAÑA 4 · IMÁGENES Y DOCUMENTOS
        with tab4:
            st.markdown('<div class="tab-hint">🖼️ Fotos adicionales y fichas técnicas — aparte de la foto principal del panel lateral</div>', unsafe_allow_html=True)
            st.file_uploader("Fotos adicionales", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="np_fotos_adicionales")
            st.file_uploader("Manuales / fichas técnicas (PDF)", type=["pdf"], accept_multiple_files=True, key="np_documentos")

        # PESTAÑA 5 · INFORMACIÓN ADICIONAL
        with tab5:
            c1, c2 = st.columns(2)
            with c1:
                st.number_input("Costo de referencia", min_value=0.0, step=0.01, key="np_costo_referencia")
            with c2:
                st.text_input("Proveedor preferido", key="np_proveedor_texto", placeholder="Se vinculará al módulo de Entidades")
            c1, c2 = st.columns(2)
            with c1:
                st.number_input("Garantía (meses)", min_value=0, step=1, key="np_garantia_meses")
            with c2:
                st.date_input("Fecha de compra (referencia)", key="np_fecha_compra_ref", value=None)

def construir_payload_producto():
    g = st.session_state.get  # lectura segura: None/default si el widget no está dibujado
    es_activo = g("np_tipo_producto", "activo") == "activo"
    es_insumo = not es_activo
    return {
        "nombre": g("np_nombre", "").strip(),
        "descripcion": (g("np_descripcion", "") or "").strip() or None,
        "clasificacion_id": g("np_clasificacion_id"),
        "categoria_id": g("np_categoria_id"),
        "marca_id": g("np_marca_id"),
        "modelo_id": g("np_modelo_id"),
        "unidad_medida_id": g("np_unidad_id"),
        "tipo_producto": g("np_tipo_producto", "activo"),
        "codigo_qr": (g("np_codigo_qr", "") or "").strip() or None,
        # Solo aplican a Activo — en Insumo se fuerzan a False
        "permite_prestamo": bool(g("np_permite_prestamo", False)) if es_activo else False,
        "permite_custodia": bool(g("np_permite_custodia", False)) if es_activo else False,
        "requiere_serie": bool(g("np_requiere_serie", False)) if es_activo else False,
        "requiere_mantenimiento": bool(g("np_requiere_mantenimiento", False)) if es_activo else False,
        "controla_garantia": bool(g("np_controla_garantia", False)) if es_activo else False,
        "vida_util_meses": g("np_vida_util_meses") or None,
        # Solo aplican a Insumo — en Activo se fuerzan a False
        "controla_stock_minimo": bool(g("np_controla_stock_minimo", False)) if es_insumo else False,
        "controla_lote": bool(g("np_controla_lote", False)) if es_insumo else False,
        "controla_vencimiento": bool(g("np_controla_vencimiento", False)) if es_insumo else False,
        "costo_referencia": g("np_costo_referencia") or None,
        "garantia_meses": g("np_garantia_meses") or None,
        "fecha_compra_referencia": str(g("np_fecha_compra_ref")) if g("np_fecha_compra_ref") else None,
        "activo": bool(g("np_estado_activo", True)),
    }


def validar_formulario_producto():
    if not st.session_state["np_nombre"].strip():
        return "El nombre es obligatorio."
    if not st.session_state["np_clasificacion_id"]:
        return "Selecciona una Clasificación."
    if not st.session_state["np_categoria_id"]:
        return "Selecciona una Categoría."
    if not st.session_state["np_unidad_id"]:
        return "Selecciona una Unidad de medida."
    return None


@st.dialog("🏷️ Etiqueta de Producto")
def ventana_etiqueta_producto(producto):
    st.markdown(f"**{producto['nombre']}**")
    st.caption(f"Código: {producto['codigo']}")

    imagen_bytes = generar_etiqueta_codigo(producto["codigo"], producto["nombre"])
    st.image(imagen_bytes)

    st.download_button(
        "⬇️ Descargar etiqueta (PNG)",
        data=imagen_bytes,
        file_name=f"etiqueta_{producto['codigo']}.png",
        mime="image/png",
        type="primary",
        width="stretch"
    )
    st.caption("Imprime esta imagen en tu impresora de etiquetas o en papel adhesivo normal.")

    if st.button("Cerrar", width="stretch"):
        st.rerun()


# ══════════════════════════════════════════════
# DIÁLOGOS
# ══════════════════════════════════════════════
@st.dialog("📦 Nuevo Producto", width="large")
def ventana_nuevo_producto():
    if st.session_state.get("np_form_loaded_for") != "nuevo":
        resetear_formulario_producto("nuevo")

    renderizar_formulario_producto("nuevo")
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("❌ Cancelar", width="stretch"):
            st.rerun()
    with c2:
        if st.button("✅ Crear Producto", type="primary", width="stretch"):
            error = validar_formulario_producto()
            if error:
                st.error(error)
            else:
                foto_url = None
                if st.session_state.get("np_fotografia_file"):
                    foto_url = subir_archivo(BUCKET_FOTOS, "principales", st.session_state["np_fotografia_file"])

                codigo_generado = generar_codigo_producto()
                if not codigo_generado:
                    st.stop()

                payload = construir_payload_producto()
                payload["codigo"] = codigo_generado
                payload["codigo_barra"] = codigo_generado
                payload["fotografia"] = foto_url

                producto_id = crear_producto(payload)
                if not producto_id:
                    st.stop()

                # Fotos y documentos adicionales
                for f in st.session_state.get("np_fotos_adicionales") or []:
                    subir_archivo(BUCKET_FOTOS, f"adicionales/{producto_id}", f)
                for d in st.session_state.get("np_documentos") or []:
                    subir_archivo(BUCKET_DOCS, f"{producto_id}", d)

                # Existencias / Activos iniciales
                if st.session_state["np_tipo_producto"] == "insumo":
                    crear_existencia_inicial(producto_id, {
                        "cantidad": st.session_state["np_cantidad_inicial"],
                        "stock_minimo": st.session_state["np_stock_minimo"] or 0,
                        "stock_maximo": st.session_state["np_stock_maximo"] or None,
                        "punto_reorden": st.session_state["np_punto_reorden"] or None,
                        "costo_unitario": st.session_state["np_costo_inicial"] or None,
                        "ubicacion_id": st.session_state["np_ubicacion_inicial_id"],
                        "fecha_ingreso_inicial": str(st.session_state["np_fecha_ingreso_lote"]),
                    })
                    if st.session_state["np_controla_lote"] and st.session_state["np_numero_lote"].strip():
                        crear_lote_inicial(producto_id, {
                            "numero_lote": st.session_state["np_numero_lote"].strip(),
                            "fecha_vencimiento": str(st.session_state["np_fecha_vencimiento_lote"]) if st.session_state.get("np_fecha_vencimiento_lote") else None,
                            "cantidad_inicial": st.session_state["np_cantidad_inicial"],
                            "cantidad_actual": st.session_state["np_cantidad_inicial"],
                            "costo_unitario": st.session_state["np_costo_inicial"] or None,
                            "fecha_ingreso": str(st.session_state["np_fecha_ingreso_lote"]),
                            "ubicacion_id": st.session_state["np_ubicacion_inicial_id"],
                        })
                else:
                    creados = crear_activos_iniciales(
                        producto_id,
                        st.session_state["np_cantidad_activos"],
                        st.session_state["np_condicion_inicial"],
                        st.session_state["np_ubicacion_activos_id"],
                        st.session_state["np_series_texto"],
                    )
                    if creados:
                        st.session_state["_msg_activos_creados"] = creados

                registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"AGREGAR PRODUCTO: {payload['codigo']}")
                st.session_state["_msg"] = f"Producto '{payload['nombre']}' creado correctamente."
                st.rerun()


@st.dialog("✏️ Editar Producto", width="large")
def ventana_editar_producto(producto):
    if st.session_state.get("np_form_loaded_for") != producto["id"]:
        resetear_formulario_producto("editar", producto)

    renderizar_formulario_producto("editar")
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("❌ Cerrar", width="stretch"):
            st.rerun()
    with c2:
        if st.button("💾 Guardar Cambios", type="primary", width="stretch"):
            error = validar_formulario_producto()
            if error:
                st.error(error)
            else:
                foto_url = st.session_state.get("np_fotografia_url_actual")
                if st.session_state.get("np_fotografia_file"):
                    foto_url = subir_archivo(BUCKET_FOTOS, "principales", st.session_state["np_fotografia_file"])

                payload = construir_payload_producto()
                payload["fotografia"] = foto_url

                for f in st.session_state.get("np_fotos_adicionales") or []:
                    subir_archivo(BUCKET_FOTOS, f"adicionales/{producto['id']}", f)
                for d in st.session_state.get("np_documentos") or []:
                    subir_archivo(BUCKET_DOCS, f"{producto['id']}", d)

                if actualizar_producto(producto["id"], payload):
                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"EDITAR PRODUCTO: {producto['codigo']}")
                    st.session_state["_msg"] = f"Producto '{payload['nombre']}' actualizado."
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
            <div class="msh-logo-box">📦</div>
            <div>
                <div class="msh-title">MSH-Hub · Almacén · Productos</div>
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
if "_msg_activos_creados" in st.session_state:
    codigos = st.session_state.pop("_msg_activos_creados")
    st.info("Activos generados: " + ", ".join(f"`{c}`" for c in codigos))

# ══════════════════════════════════════════════
# PANEL DE FILTROS
# ══════════════════════════════════════════════
panel_filtros = st.container(key="panel_filtros")
with panel_filtros:
    st.markdown('<div class="panel-card-titulo">🔍 Filtros y búsqueda</div>', unsafe_allow_html=True)
    c_busq, c_tipo, c_est, c_nuevo = st.columns([4, 2, 2, 1.6])
    with c_busq:
        busqueda = st.text_input("buscar", placeholder="🔍  Buscar por código o nombre...", label_visibility="collapsed")
    with c_tipo:
        filtro_tipo = st.selectbox("tipo", ["Todos", "Activo", "Insumo"], label_visibility="collapsed")
    with c_est:
        filtro_est = st.selectbox("estado", ["Todos", "Activos", "Inactivos"], label_visibility="collapsed")
    with c_nuevo:
        if es_admin:
            if st.button("➕ Nuevo Producto", type="primary", width="stretch"):
                ventana_nuevo_producto()

# ══════════════════════════════════════════════
# KPIs (consultas ligeras, no dependen de la página actual)
# ══════════════════════════════════════════════
total     = contar_productos()
activos_t = contar_productos(filtro_tipo="activo")
insumos_t = contar_productos(filtro_tipo="insumo")
inactivos = contar_productos(filtro_activo=False)

st.markdown(f"""
    <div class="kpi-bar">
        <div class="kpi-pill"><span class="kpi-icon">📦</span><span class="kpi-val" style="color:#1E293B;">{total}</span><span class="kpi-lbl">Total</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">🛠️</span><span class="kpi-val" style="color:#1D4ED8;">{activos_t}</span><span class="kpi-lbl">Tipo Activo</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">📥</span><span class="kpi-val" style="color:#C2410C;">{insumos_t}</span><span class="kpi-lbl">Tipo Insumo</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">⚪</span><span class="kpi-val" style="color:#64748B;">{inactivos}</span><span class="kpi-lbl">Inactivos</span></div>
    </div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# CARGA PAGINADA Y TABLA
# ══════════════════════════════════════════════
if "productos_pagina" not in st.session_state:
    st.session_state["productos_pagina"] = 0
TAM_PAGINA = 50

filtro_actual = (busqueda, filtro_tipo, filtro_est)
if st.session_state.get("productos_filtro_anterior") != filtro_actual:
    st.session_state["productos_pagina"] = 0
    st.session_state["productos_filtro_anterior"] = filtro_actual

datos, total_filtrado = cargar_productos(
    pagina=st.session_state["productos_pagina"], tam_pagina=TAM_PAGINA,
    busqueda=busqueda, filtro_tipo=filtro_tipo, filtro_est=filtro_est
)
df_f = pd.DataFrame(datos)

if not df_f.empty:
    cw  = [1.3, 3, 1.7, 2, 1, 1, 1.3] if es_admin else [1.3, 3, 1.7, 2, 1, 1]
    ths = ["Código", "Nombre", "Tipo", "Categoría", "Marca", "Estado", "⚙️"] if es_admin else ["Código", "Nombre", "Tipo", "Categoría", "Marca", "Estado"]

    panel_tabla = st.container(key="panel_tabla")
    with panel_tabla:
        st.markdown('<div class="panel-card-titulo">📋 Catálogo de productos</div>', unsafe_allow_html=True)

        h_cols = st.columns(cw)
        for idx, (col, txt) in enumerate(zip(h_cols, ths)):
            estilo = " style='text-align:center;'" if (es_admin and idx == len(ths) - 1) else ""
            col.markdown(f"<p class='th'{estilo}>{txt}</p>", unsafe_allow_html=True)

        for i, (_, row) in enumerate(df_f.iterrows()):
            cls = "td-alt" if i % 2 == 1 else "td"
            r = st.columns(cw)
            r[0].markdown(f"<div class='{cls}'><span class='folio-tag'>{row['codigo']}</span></div>", unsafe_allow_html=True)
            r[1].markdown(f"<div class='{cls}'><b>{row['nombre']}</b></div>", unsafe_allow_html=True)
            tipo_cls = "badge-tipo-activo" if row["tipo_producto"] == "activo" else "badge-tipo-insumo"
            tipo_txt = "🛠️ Activo" if row["tipo_producto"] == "activo" else "📦 Insumo"
            r[2].markdown(f"<div class='{cls}'><span class='badge {tipo_cls}'>{tipo_txt}</span></div>", unsafe_allow_html=True)
            r[3].markdown(f"<div class='{cls}'>{row['categoria_nombre']}</div>", unsafe_allow_html=True)
            r[4].markdown(f"<div class='{cls}'>{row['marca_nombre']}</div>", unsafe_allow_html=True)
            badge_cls = "badge-activo" if row["activo"] else "badge-inactivo"
            badge_txt = "Activo" if row["activo"] else "Inactivo"
            r[5].markdown(f"<div class='{cls}'><span class='badge {badge_cls}'>{badge_txt}</span></div>", unsafe_allow_html=True)
            if es_admin:
                with r[6]:
                    b1, b2 = st.columns(2)
                    if b1.button("✏️", key=f"ed_{row['id']}", help=f"Editar {row['codigo']}", width="stretch"):
                        ventana_editar_producto(row.to_dict())
                    if b2.button("🏷️", key=f"lbl_{row['id']}", help=f"Imprimir etiqueta {row['codigo']}", width="stretch"):
                        ventana_etiqueta_producto(row.to_dict())

        total_paginas = max(1, -(-total_filtrado // TAM_PAGINA))
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if st.button("← Anterior", disabled=st.session_state["productos_pagina"] <= 0, key="prod_pag_ant"):
                st.session_state["productos_pagina"] -= 1
                st.rerun()
        with c2:
            st.markdown(f"<p style='text-align:center; font-size:12px; color:#64748B; margin-top:8px;'>Página {st.session_state['productos_pagina'] + 1} de {total_paginas} · {total_filtrado} resultados</p>", unsafe_allow_html=True)
        with c3:
            if st.button("Siguiente →", disabled=st.session_state["productos_pagina"] >= total_paginas - 1, key="prod_pag_sig"):
                st.session_state["productos_pagina"] += 1
                st.rerun()

elif total == 0:
    st.info("📭 No hay productos registrados todavía. ¡Crea el primero!")
else:
    st.info("🔍 No se encontraron productos con los filtros aplicados.")
