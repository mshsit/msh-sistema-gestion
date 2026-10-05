import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import date, datetime

st.set_page_config(
    page_title="MSH-Hub | Entradas",
    layout="wide",
    page_icon="📥",
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
.badge-completada { background:#DCFCE7; color:#15803D; }
.badge-borrador    { background:#FEF3E8; color:#C2410C; }
.badge-cancelada   { background:#FEE2E2; color:#B91C1C; }
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
.producto-card {
    background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px;
    padding: 10px 14px; margin-bottom: 10px;
}
.detalle-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 8px 4px; border-bottom: 1px solid #F1F5F9; font-size: 12px;
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


def cargar_proveedores_activos():
    try:
        res = supabase.table("almacen_entidades").select("id, nombre").eq("tipo", "proveedor").eq("activo", True).order("nombre").execute()
        return res.data if res.data else []
    except:
        return []


def crear_proveedor_rapido(nombre, telefono=None):
    try:
        res = supabase.table("almacen_entidades").insert({
            "tipo": "proveedor", "nombre": nombre.strip(), "telefono": telefono, "activo": True
        }).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as e:
        st.error(f"No se pudo crear el proveedor: {e}")
        return None


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


def generar_folio_entrada():
    try:
        res = supabase.rpc("generar_folio_entrada", {}).execute()
        return res.data
    except Exception as e:
        st.error(f"Error al generar folio: {e}")
        return None


def generar_codigo_activo(producto_id):
    try:
        res = supabase.rpc("generar_codigo_activo", {"p_producto_id": producto_id}).execute()
        return res.data
    except Exception as e:
        st.error(f"Error al generar código de activo: {e}")
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
            "entrada_id": entrada_id,
            "producto_id": linea["producto_id"],
            "cantidad": linea["cantidad"],
            "costo_unitario": linea.get("costo_unitario"),
            "ubicacion_id": linea.get("ubicacion_id"),
            "numero_lote": linea.get("numero_lote"),
            "fecha_vencimiento": linea.get("fecha_vencimiento"),
        }).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as e:
        st.error(f"Error al guardar el detalle: {e}")
        return None


def aplicar_linea_inventario(linea, detalle_id, fecha_entrada):
    """Aplica el efecto real en inventario: existencias/lotes o activos nuevos."""
    producto = linea["producto"]

    if producto["tipo_producto"] == "insumo":
        try:
            existente = supabase.table("almacen_existencias").select("*").eq("producto_id", producto["id"]).execute().data
            if existente:
                nueva_cantidad = existente[0]["cantidad"] + linea["cantidad"]
                supabase.table("almacen_existencias").update({"cantidad": nueva_cantidad}).eq("producto_id", producto["id"]).execute()
            else:
                supabase.table("almacen_existencias").insert({
                    "producto_id": producto["id"],
                    "cantidad": linea["cantidad"],
                    "costo_unitario": linea.get("costo_unitario"),
                    "ubicacion_id": linea.get("ubicacion_id"),
                }).execute()

            if producto.get("controla_lote") and linea.get("numero_lote"):
                supabase.table("almacen_lotes").insert({
                    "producto_id": producto["id"],
                    "numero_lote": linea["numero_lote"],
                    "fecha_vencimiento": linea.get("fecha_vencimiento"),
                    "cantidad_inicial": linea["cantidad"],
                    "cantidad_actual": linea["cantidad"],
                    "costo_unitario": linea.get("costo_unitario"),
                    "fecha_ingreso": str(fecha_entrada),
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
                    "producto_id": producto["id"],
                    "codigo_activo": codigo,
                    "condicion": "nuevo",
                    "estado": "disponible",
                    "ubicacion_actual": linea.get("ubicacion_id"),
                    "costo_adquisicion": linea.get("costo_unitario"),
                    "fecha_compra": str(fecha_entrada),
                    "fecha_ingreso": str(fecha_entrada),
                    "entrada_detalle_id": detalle_id,
                }).execute()
                creados.append(codigo)
            except Exception as e:
                st.warning(f"No se pudo crear el activo {codigo}: {e}")
        return creados


def cargar_entradas():
    try:
        res = supabase.table("almacen_entradas").select(
            "*, almacen_entidades(nombre)"
        ).order("fecha", desc=True).order("created_at", desc=True).execute()
        data = res.data if res.data else []
        for row in data:
            ent = row.pop("almacen_entidades", None)
            row["proveedor_nombre"] = ent["nombre"] if ent else "—"
        return data
    except Exception as e:
        st.error(f"Error al cargar entradas: {e}")
        return []


def cargar_detalle_entrada(entrada_id):
    try:
        res = supabase.table("almacen_entradas_detalle").select(
            "*, almacen_productos(codigo, nombre)"
        ).eq("entrada_id", entrada_id).execute()
        data = res.data if res.data else []
        for row in data:
            p = row.pop("almacen_productos", None)
            row["producto_codigo"] = p["codigo"] if p else "—"
            row["producto_nombre"] = p["nombre"] if p else "—"
        return data
    except:
        return []


# ══════════════════════════════════════════════
# ESTADO: DETALLE EN CONSTRUCCIÓN (dentro del diálogo)
# ══════════════════════════════════════════════
if "entrada_detalle_lineas" not in st.session_state:
    st.session_state["entrada_detalle_lineas"] = []


@st.dialog("📥 Nueva Entrada", width="large")
def ventana_nueva_entrada():
    proveedores = cargar_proveedores_activos()
    ubicaciones = cargar_ubicaciones_activas()

    if "entrada_folio_sugerido" not in st.session_state:
        st.session_state["entrada_folio_sugerido"] = generar_folio_entrada()

    st.caption(f"Folio sugerido: `{st.session_state['entrada_folio_sugerido']}`")

    c1, c2, c3 = st.columns(3)
    with c1:
        opciones_prov = {"— Ninguno —": None, **{p["nombre"]: p["id"] for p in proveedores}}
        sel_prov = st.selectbox("Proveedor / Origen", list(opciones_prov.keys()), key="entrada_prov_sel")
        entidad_id = opciones_prov.get(sel_prov)
    with c2:
        fecha_entrada = st.date_input("Fecha *", value=date.today(), key="entrada_fecha")
    with c3:
        tipo_entrada = st.selectbox(
            "Tipo de entrada *", ["compra", "donacion", "recepcion", "devolucion", "ajuste"],
            format_func=lambda v: v.capitalize(), key="entrada_tipo"
        )

    with st.expander("➕ Agregar nuevo proveedor rápido"):
        c1, c2 = st.columns([3, 1])
        with c1:
            nuevo_prov_nombre = st.text_input("Nombre del proveedor", key="entrada_nuevo_prov_nombre")
        with c2:
            st.write("")
            if st.button("Agregar", key="entrada_nuevo_prov_btn"):
                if nuevo_prov_nombre.strip():
                    nuevo_id = crear_proveedor_rapido(nuevo_prov_nombre)
                    if nuevo_id:
                        st.success("Proveedor agregado. Selecciónalo arriba.")
                        st.rerun()

    observaciones = st.text_area("Observaciones", key="entrada_observaciones", height=60)

    st.divider()
    st.markdown("**Agregar artículos**")

    c1, c2 = st.columns([3, 1])
    with c1:
        query = st.text_input("Buscar producto", placeholder="Buscar por código, nombre o código de barras...", key="entrada_busqueda", label_visibility="collapsed")
    with c2:
        buscar = st.button("🔍 Buscar", width="stretch")

    if query.strip():
        resultados = buscar_productos(query)
        for p in resultados:
            with st.container():
                c1, c2, c3 = st.columns([3, 1.2, 1])
                with c1:
                    tipo_icono = "🛠️" if p["tipo_producto"] == "activo" else "📦"
                    st.markdown(f"{tipo_icono} **{p['codigo']}** — {p['nombre']}")
                with c2:
                    cantidad_key = f"cant_{p['id']}"
                    st.number_input("Cant.", min_value=1.0 if p["tipo_producto"] == "activo" else 0.01,
                                    value=1.0, step=1.0, key=cantidad_key, label_visibility="collapsed")
                with c3:
                    if st.button("➕ Agregar", key=f"add_{p['id']}", width="stretch"):
                        st.session_state["entrada_detalle_lineas"].append({
                            "producto": p,
                            "producto_id": p["id"],
                            "cantidad": st.session_state[cantidad_key],
                            "costo_unitario": None,
                            "ubicacion_id": None,
                            "numero_lote": "",
                            "fecha_vencimiento": None,
                        })
                        st.rerun()

    st.divider()
    st.markdown("**Detalle de la entrada**")

    if not st.session_state["entrada_detalle_lineas"]:
        st.info("Todavía no has agregado artículos.")
    else:
        opciones_ubi = {"— Sin especificar —": None, **{u["breadcrumb"]: u["id"] for u in ubicaciones}}
        for idx, linea in enumerate(st.session_state["entrada_detalle_lineas"]):
            p = linea["producto"]
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([3, 1, 1.3, 1.6, 0.6])
                c1.markdown(f"**{p['codigo']}** — {p['nombre']}")
                c2.markdown(f"Cant: **{linea['cantidad']}**")
                linea["costo_unitario"] = c3.number_input(
                    "Costo unit.", min_value=0.0, step=0.01,
                    value=linea["costo_unitario"] or 0.0, key=f"costo_{idx}", label_visibility="collapsed"
                )
                sel_ubi = c4.selectbox(
                    "Ubicación", list(opciones_ubi.keys()), key=f"ubi_{idx}", label_visibility="collapsed"
                )
                linea["ubicacion_id"] = opciones_ubi.get(sel_ubi)
                if c5.button("🗑️", key=f"del_{idx}"):
                    st.session_state["entrada_detalle_lineas"].pop(idx)
                    st.rerun()

                if p.get("controla_lote"):
                    c1, c2 = st.columns(2)
                    linea["numero_lote"] = c1.text_input("Número de lote", value=linea.get("numero_lote", ""), key=f"lote_{idx}")
                    if p.get("controla_vencimiento"):
                        linea["fecha_vencimiento"] = str(c2.date_input("Fecha de vencimiento", key=f"venc_{idx}"))

        total_articulos = len(st.session_state["entrada_detalle_lineas"])
        total_unidades = sum(l["cantidad"] for l in st.session_state["entrada_detalle_lineas"])
        st.caption(f"Total de artículos: **{total_articulos}** · Total de unidades: **{total_unidades}**")

    st.divider()
    if st.button("✅ Guardar entrada", type="primary", width="stretch", disabled=not st.session_state["entrada_detalle_lineas"]):
        _guardar_entrada(entidad_id, fecha_entrada, tipo_entrada, observaciones, estado="completada")


def _guardar_entrada(entidad_id, fecha_entrada, tipo_entrada, observaciones, estado="completada"):
    payload = {
        "folio": st.session_state["entrada_folio_sugerido"],
        "fecha": str(fecha_entrada),
        "tipo_entrada": tipo_entrada,
        "entidad_id": entidad_id,
        "usuario_registro": st.session_state["usuario"],
        "nombre_registro": st.session_state["nombre"],
        "estado": estado,
        "observaciones": observaciones.strip() or None,
    }
    entrada_id = crear_entrada(payload)
    if not entrada_id:
        return

    codigos_generados = []
    for linea in st.session_state["entrada_detalle_lineas"]:
        detalle_id = crear_entrada_detalle(entrada_id, linea)
        if estado == "completada" and detalle_id:
            resultado = aplicar_linea_inventario(linea, detalle_id, fecha_entrada)
            if isinstance(resultado, list):
                codigos_generados.extend(resultado)

    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"REGISTRAR ENTRADA: {payload['folio']} ({estado})")
    st.session_state["entrada_detalle_lineas"] = []
    del st.session_state["entrada_folio_sugerido"]
    st.session_state["_msg"] = f"Entrada {payload['folio']} guardada como {estado}."
    if codigos_generados:
        st.session_state["_msg_activos_creados"] = codigos_generados
    st.rerun()


@st.dialog("📄 Detalle de Entrada")
def ventana_ver_detalle(entrada):
    st.markdown(f"**Folio:** `{entrada['folio']}`  ·  **Fecha:** {entrada['fecha']}")
    st.markdown(f"**Proveedor:** {entrada['proveedor_nombre']}  ·  **Tipo:** {entrada['tipo_entrada'].capitalize()}")
    if entrada.get("observaciones"):
        st.caption(entrada["observaciones"])
    st.divider()

    detalle = cargar_detalle_entrada(entrada["id"])
    if not detalle:
        st.info("Esta entrada no tiene artículos registrados.")
    else:
        for d in detalle:
            st.markdown(
                f"<div class='detalle-row'><span><b>{d['producto_codigo']}</b> — {d['producto_nombre']}</span>"
                f"<span>Cant: {d['cantidad']}</span></div>",
                unsafe_allow_html=True
            )

    if st.button("Cerrar", width="stretch"):
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
            <div class="msh-logo-box">📥</div>
            <div>
                <div class="msh-title">MSH-Hub · Almacén · Entradas</div>
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
# CARGA Y KPIs
# ══════════════════════════════════════════════
df_master = pd.DataFrame(cargar_entradas())

total       = len(df_master) if not df_master.empty else 0
hoy         = len(df_master[df_master["fecha"] == str(date.today())]) if not df_master.empty else 0
pendientes  = len(df_master[df_master["estado"] == "borrador"]) if not df_master.empty else 0
completas   = len(df_master[df_master["estado"] == "completada"]) if not df_master.empty else 0
canceladas  = len(df_master[df_master["estado"] == "cancelada"]) if not df_master.empty else 0

st.markdown(f"""
    <div class="kpi-bar">
        <div class="kpi-pill"><span class="kpi-icon">📥</span><span class="kpi-val" style="color:#1E293B;">{total}</span><span class="kpi-lbl">Total entradas</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">📅</span><span class="kpi-val" style="color:#1D4ED8;">{hoy}</span><span class="kpi-lbl">Hoy</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">📝</span><span class="kpi-val" style="color:#C2410C;">{pendientes}</span><span class="kpi-lbl">Pendientes</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">✅</span><span class="kpi-val" style="color:#15803D;">{completas}</span><span class="kpi-lbl">Completas</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">❌</span><span class="kpi-val" style="color:#B91C1C;">{canceladas}</span><span class="kpi-lbl">Canceladas</span></div>
    </div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# PANEL DE FILTROS
# ══════════════════════════════════════════════
panel_filtros = st.container(key="panel_filtros")
with panel_filtros:
    st.markdown('<div class="panel-card-titulo">🔍 Filtros y búsqueda</div>', unsafe_allow_html=True)
    c_busq, c_est, c_nuevo = st.columns([4, 2.5, 1.6])
    with c_busq:
        busqueda = st.text_input("buscar", placeholder="🔍  Buscar por folio o proveedor...", label_visibility="collapsed")
    with c_est:
        filtro_est = st.selectbox("estado", ["Todos", "Borrador", "Completada", "Cancelada"], label_visibility="collapsed")
    with c_nuevo:
        if st.button("➕ Nueva Entrada", type="primary", width="stretch"):
            ventana_nueva_entrada()

# ══════════════════════════════════════════════
# FILTRADO Y TABLA
# ══════════════════════════════════════════════
df_f = df_master.copy() if not df_master.empty else pd.DataFrame()
if not df_f.empty:
    if busqueda.strip():
        df_f = df_f[
            df_f["folio"].str.contains(busqueda, case=False, na=False) |
            df_f["proveedor_nombre"].str.contains(busqueda, case=False, na=False)
        ]
    if filtro_est != "Todos":
        df_f = df_f[df_f["estado"] == filtro_est.lower()]

if not df_f.empty:
    cw  = [1.4, 1.2, 2.2, 1.5, 1.3, 1]
    ths = ["Folio", "Fecha", "Proveedor", "Tipo", "Estado", "👁️"]

    panel_tabla = st.container(key="panel_tabla")
    with panel_tabla:
        st.markdown('<div class="panel-card-titulo">📋 Entradas registradas</div>', unsafe_allow_html=True)

        h_cols = st.columns(cw)
        for idx, (col, txt) in enumerate(zip(h_cols, ths)):
            estilo = " style='text-align:center;'" if idx == len(ths) - 1 else ""
            col.markdown(f"<p class='th'{estilo}>{txt}</p>", unsafe_allow_html=True)

        for i, (_, row) in enumerate(df_f.iterrows()):
            cls = "td-alt" if i % 2 == 1 else "td"
            r = st.columns(cw)
            r[0].markdown(f"<div class='{cls}'><span class='folio-tag'>{row['folio']}</span></div>", unsafe_allow_html=True)
            r[1].markdown(f"<div class='{cls}'>{row['fecha']}</div>", unsafe_allow_html=True)
            r[2].markdown(f"<div class='{cls}'>{row['proveedor_nombre']}</div>", unsafe_allow_html=True)
            r[3].markdown(f"<div class='{cls}'>{row['tipo_entrada'].capitalize()}</div>", unsafe_allow_html=True)
            badge_map = {"completada": "badge-completada", "borrador": "badge-borrador", "cancelada": "badge-cancelada"}
            r[4].markdown(f"<div class='{cls}'><span class='badge {badge_map.get(row['estado'], '')}'>{row['estado'].capitalize()}</span></div>", unsafe_allow_html=True)
            with r[5]:
                if st.button("👁️", key=f"ver_{row['id']}", help="Ver detalle", width="stretch"):
                    ventana_ver_detalle(row.to_dict())

elif not df_master.empty:
    st.info("🔍 No se encontraron entradas con los filtros aplicados.")
else:
    st.info("📭 No hay entradas registradas todavía. ¡Crea la primera!")
