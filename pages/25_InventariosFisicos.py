import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import date, datetime

st.set_page_config(
    page_title="MSH-Hub | Inventarios Físicos",
    layout="wide",
    page_icon="📊",
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
.badge-abierto  { background:#EFF6FF; color:#1D4ED8; }
.badge-cerrado  { background:#F1F5F9; color:#64748B; }
.badge-ok       { background:#DCFCE7; color:#15803D; }
.badge-dif      { background:#FEF3E8; color:#C2410C; }
.badge-pendiente{ background:#FEF9C3; color:#854D0E; }
.folio-tag {
    font-family: 'DM Mono', monospace; font-size: 10px; color: #94A3B8;
    background: #F1F5F9; border-radius: 4px; padding: 1px 5px; display: inline-block;
}
.dif-pos { color: #1D4ED8; font-weight: 700; }
.dif-neg { color: #B91C1C; font-weight: 700; }
.dif-cero { color: #15803D; font-weight: 700; }
.panel-card-titulo { font-size: 15px; font-weight: 700; color: #1E293B; margin-bottom: 2px; }
.panel-card-subtitulo { font-size: 12px; color: #94A3B8; margin-bottom: 16px; }
.inv-card {
    background: #ffffff; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 20px 24px; margin-bottom: 18px; box-shadow: 0 2px 10px rgba(30,52,71,0.06);
}
div[class*="st-key-panel_filtros"],
div[class*="st-key-panel_tabla"] {
    background: #ffffff; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 22px 24px; margin-bottom: 18px;
    box-shadow: 0 2px 10px rgba(30,52,71,0.06);
}
div[data-testid="stDialog"] div[role="dialog"] {
    width: 45vw !important; max-width: 560px !important;
    min-width: 340px !important; border-radius: 16px !important;
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


def registrar_acceso(usuario, nombre, accion):
    try:
        supabase.table("usuarios_accesos").insert({
            "usuario": usuario, "nombre": nombre,
            "accion": accion, "fecha_hora": datetime.now().isoformat()
        }).execute()
    except:
        pass


# ══════════════════════════════════════════════
# ACCESO A DATOS · INVENTARIOS (encabezado)
# ══════════════════════════════════════════════
def generar_folio_inventario():
    try:
        return supabase.rpc("generar_folio_inventario", {}).execute().data
    except Exception as e:
        st.error(f"Error al generar folio: {e}")
        return None


def crear_inventario(payload):
    try:
        res = supabase.table("almacen_inventarios").insert(payload).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as e:
        st.error(f"Error al crear el inventario: {e}")
        return None


def cargar_inventarios(pagina=0, tam_pagina=50, busqueda="", filtro_estado="Todos"):
    try:
        q = supabase.table("almacen_inventarios").select(
            "*, almacen_inventarios_detalle(id, diferencia, cantidad_fisica)", count="exact"
        )
        if busqueda.strip():
            q = q.ilike("folio", f"%{busqueda}%")
        if filtro_estado != "Todos":
            q = q.eq("estado", filtro_estado.lower())
        inicio = pagina * tam_pagina
        fin = inicio + tam_pagina - 1
        res = q.order("fecha_inicio", desc=True).range(inicio, fin).execute()
        data = res.data or []
        for row in data:
            detalle = row.pop("almacen_inventarios_detalle", None) or []
            row["total_lineas"] = len(detalle)
            row["contadas"] = len([d for d in detalle if d.get("cantidad_fisica") is not None])
            row["con_diferencia"] = len([d for d in detalle if d.get("diferencia") not in (None, 0)])
        return data, (res.count or 0)
    except Exception as e:
        st.error(f"Error al cargar inventarios: {e}")
        return [], 0


def contar_inventarios(filtro_estado=None):
    try:
        q = supabase.table("almacen_inventarios").select("id", count="exact")
        if filtro_estado:
            q = q.eq("estado", filtro_estado)
        res = q.range(0, 0).execute()
        return res.count or 0
    except:
        return 0


def cerrar_inventario(inventario_id):
    try:
        supabase.table("almacen_inventarios").update({
            "estado": "cerrado", "fecha_fin": str(date.today())
        }).eq("id", inventario_id).execute()
        return True
    except Exception as e:
        st.error(f"Error al cerrar el inventario: {e}")
        return False


# ══════════════════════════════════════════════
# ACCESO A DATOS · DETALLE (líneas de conteo)
# ══════════════════════════════════════════════
def buscar_productos(query):
    try:
        q = supabase.table("almacen_productos").select("id, codigo, nombre, tipo_producto").eq("activo", True)
        if query.strip():
            q = q.or_(f"codigo.ilike.%{query}%,nombre.ilike.%{query}%")
        res = q.order("nombre").limit(8).execute()
        return res.data or []
    except Exception as e:
        st.error(f"Error al buscar productos: {e}")
        return []


def buscar_activos_de_producto(producto_id, query=""):
    try:
        q = supabase.table("almacen_activos").select("id, codigo_activo, estado").eq("producto_id", producto_id).eq("activo", True)
        if query.strip():
            q = q.ilike("codigo_activo", f"%{query}%")
        res = q.order("codigo_activo").limit(15).execute()
        return res.data or []
    except:
        return []


def obtener_cantidad_sistema_insumo(producto_id):
    try:
        res = supabase.table("almacen_existencias").select("cantidad").eq("producto_id", producto_id).execute().data
        return res[0]["cantidad"] if res else 0
    except:
        return 0


def agregar_linea_inventario(inventario_id, producto_id, activo_id, cantidad_sistema):
    try:
        supabase.table("almacen_inventarios_detalle").insert({
            "inventario_id": inventario_id, "producto_id": producto_id, "activo_id": activo_id,
            "cantidad_sistema": cantidad_sistema,
        }).execute()
        return True
    except Exception as e:
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            st.warning("Ese producto/activo ya está en este inventario.")
        else:
            st.error(f"Error al agregar la línea: {e}")
        return False


def cargar_detalle_inventario(inventario_id, pagina=0, tam_pagina=50, solo_con_diferencia=False):
    try:
        q = supabase.table("almacen_inventarios_detalle_resumen").select("*", count="exact").eq("inventario_id", inventario_id)
        if solo_con_diferencia:
            q = q.not_.is_("diferencia", "null").neq("diferencia", 0)
        inicio = pagina * tam_pagina
        fin = inicio + tam_pagina - 1
        res = q.order("producto_nombre").range(inicio, fin).execute()
        return res.data or [], (res.count or 0)
    except Exception as e:
        st.error(f"Error al cargar el detalle: {e}")
        return [], 0


def actualizar_cantidad_fisica(detalle_id, cantidad_fisica):
    try:
        supabase.table("almacen_inventarios_detalle").update({
            "cantidad_fisica": cantidad_fisica, "contado_at": datetime.now().isoformat()
        }).eq("id", detalle_id).execute()
        return True
    except Exception as e:
        st.error(f"Error al guardar el conteo: {e}")
        return False


def aplicar_ajuste_existencia(detalle_id, producto_id, cantidad_fisica):
    try:
        existente = supabase.table("almacen_existencias").select("id").eq("producto_id", producto_id).execute().data
        if existente:
            supabase.table("almacen_existencias").update({"cantidad": cantidad_fisica}).eq("producto_id", producto_id).execute()
        else:
            supabase.table("almacen_existencias").insert({"producto_id": producto_id, "cantidad": cantidad_fisica}).execute()
        supabase.table("almacen_inventarios_detalle").update({"ajustado": True}).eq("id", detalle_id).execute()
        return True
    except Exception as e:
        st.error(f"Error al aplicar el ajuste: {e}")
        return False


# ══════════════════════════════════════════════
# DIÁLOGO: NUEVO INVENTARIO
# ══════════════════════════════════════════════
@st.dialog("📊 Nuevo Inventario Físico")
def ventana_nuevo_inventario():
    observaciones = st.text_area("Observaciones (opcional)", placeholder="Ej. Conteo trimestral de herramientas eléctricas", height=70)
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Crear e Iniciar", type="primary", width="stretch"):
            folio = generar_folio_inventario()
            if folio:
                payload = {
                    "folio": folio, "fecha_inicio": str(date.today()), "estado": "abierto",
                    "observaciones": observaciones.strip() or None,
                    "usuario_registro": st.session_state["usuario"], "nombre_registro": st.session_state["nombre"],
                }
                inventario_id = crear_inventario(payload)
                if inventario_id:
                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"CREAR INVENTARIO: {folio}")
                    st.session_state["inv_activo_id"] = inventario_id
                    st.session_state["inv_activo_folio"] = folio
                    st.rerun()
    with c2:
        if st.button("❌ Cancelar", width="stretch"):
            st.rerun()


nombre_actual  = st.session_state.get("nombre", "")
rol_actual     = st.session_state.get("rol", "")
usuario_actual = st.session_state.get("usuario", "")
iniciales      = "".join([p[0].upper() for p in nombre_actual.split()[:2]]) if nombre_actual else "AD"

st.markdown(f"""
    <div class="msh-header">
        <div class="msh-header-left">
            <div class="msh-logo-box">📊</div>
            <div>
                <div class="msh-title">MSH-Hub · Almacén · Inventarios Físicos</div>
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

# ══════════════════════════════════════════════════════════════
# VISTA DE DETALLE (gestionar un inventario específico)
# ══════════════════════════════════════════════════════════════
if st.session_state.get("inv_activo_id"):
    inventario_id = st.session_state["inv_activo_id"]
    folio = st.session_state.get("inv_activo_folio", "")

    inv_res = supabase.table("almacen_inventarios").select("*").eq("id", inventario_id).execute().data
    inventario = inv_res[0] if inv_res else None

    if not inventario:
        st.error("No se encontró el inventario.")
        st.session_state["inv_activo_id"] = None
        st.stop()

    esta_abierto = inventario["estado"] == "abierto"

    with st.container(key="inv_card"):
        st.markdown('<div class="inv-card">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3, 2, 1.3])
        with c1:
            st.markdown(f"### 📊 {inventario['folio']}")
            st.caption(f"Iniciado: {inventario['fecha_inicio']}" + (f" · Cerrado: {inventario['fecha_fin']}" if inventario.get("fecha_fin") else ""))
        with c2:
            badge_cls = "badge-abierto" if esta_abierto else "badge-cerrado"
            st.markdown(f"<span class='badge {badge_cls}'>{'Abierto' if esta_abierto else 'Cerrado'}</span>", unsafe_allow_html=True)
            if inventario.get("observaciones"):
                st.caption(inventario["observaciones"])
        with c3:
            if st.button("← Volver a Inventarios", width="stretch"):
                st.session_state["inv_activo_id"] = None
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if esta_abierto:
        st.markdown('<div class="panel-card-titulo">➕ Agregar producto o activo al conteo</div>', unsafe_allow_html=True)
        query = st.text_input("buscar_inv", placeholder="🔍  Buscar por código o nombre de producto...", label_visibility="collapsed", key="inv_busqueda")

        if query.strip():
            for p in buscar_productos(query):
                if p["tipo_producto"] == "insumo":
                    c1, c2 = st.columns([4, 1])
                    cant_sistema = obtener_cantidad_sistema_insumo(p["id"])
                    c1.markdown(f"📦 **{p['codigo']}** — {p['nombre']} · sistema: {cant_sistema:g}")
                    with c2:
                        if st.button("➕ Agregar", key=f"inv_add_prod_{p['id']}", width="stretch"):
                            if agregar_linea_inventario(inventario_id, p["id"], None, cant_sistema):
                                st.rerun()
                else:
                    st.markdown(f"🛠️ **{p['codigo']}** — {p['nombre']} (elige unidades específicas abajo)")
                    activos = buscar_activos_de_producto(p["id"])
                    for a in activos:
                        c1, c2 = st.columns([4, 1])
                        c1.caption(f"　`{a['codigo_activo']}` · estado: {a['estado']}")
                        with c2:
                            if st.button("➕ Agregar", key=f"inv_add_act_{a['id']}", width="stretch"):
                                if agregar_linea_inventario(inventario_id, p["id"], a["id"], 1):
                                    st.rerun()
        st.divider()

    if "inv_detalle_pagina" not in st.session_state:
        st.session_state["inv_detalle_pagina"] = 0
    TAM_PAGINA = 50

    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown('<div class="panel-card-titulo">📋 Líneas del conteo</div>', unsafe_allow_html=True)
    with c2:
        solo_dif = st.checkbox("Mostrar solo líneas con diferencia", value=False)

    detalle, total_detalle = cargar_detalle_inventario(
        inventario_id, pagina=st.session_state["inv_detalle_pagina"], tam_pagina=TAM_PAGINA, solo_con_diferencia=solo_dif
    )
    df_d = pd.DataFrame(detalle)

    if not df_d.empty:
        cw = [2.5, 1.3, 1.1, 1.1, 1, 1.3] if esta_abierto else [2.5, 1.3, 1.1, 1.1, 1]
        ths = ["Producto/Activo", "Sistema", "Física", "Diferencia", "Estado", "⚙️"] if esta_abierto else ["Producto/Activo", "Sistema", "Física", "Diferencia", "Estado"]
        panel_tabla = st.container(key="panel_tabla")
        with panel_tabla:
            h_cols = st.columns(cw)
            for col, txt in zip(h_cols, ths):
                col.markdown(f"<p class='th'>{txt}</p>", unsafe_allow_html=True)
            for i, (_, row) in enumerate(df_d.iterrows()):
                cls = "td-alt" if i % 2 == 1 else "td"
                r = st.columns(cw)
                etiqueta = f"{row['producto_codigo']} — {row['producto_nombre']}"
                if row.get("codigo_activo"):
                    etiqueta += f" (`{row['codigo_activo']}`)"
                r[0].markdown(f"<div class='{cls}'>{etiqueta}</div>", unsafe_allow_html=True)
                r[1].markdown(f"<div class='{cls}'>{row['cantidad_sistema']:g}</div>", unsafe_allow_html=True)

                if esta_abierto:
                    with r[2]:
                        nueva_fisica = st.number_input(
                            "fisica", min_value=0.0, step=1.0,
                            value=float(row["cantidad_fisica"]) if row.get("cantidad_fisica") is not None else 0.0,
                            key=f"inv_fisica_{row['id']}", label_visibility="collapsed"
                        )
                        valor_previo = row.get("cantidad_fisica") if row.get("cantidad_fisica") is not None else 0.0
                        if nueva_fisica != valor_previo:
                            if st.button("💾", key=f"inv_save_{row['id']}", help="Guardar conteo"):
                                if actualizar_cantidad_fisica(row["id"], nueva_fisica):
                                    st.rerun()
                else:
                    valor_fisica = f"{row['cantidad_fisica']:g}" if row.get("cantidad_fisica") is not None else "—"
                    r[2].markdown(f"<div class='{cls}'>{valor_fisica}</div>", unsafe_allow_html=True)

                dif = row.get("diferencia")
                if dif is None:
                    r[3].markdown(f"<div class='{cls}'>—</div>", unsafe_allow_html=True)
                else:
                    dif_cls = "dif-cero" if dif == 0 else ("dif-pos" if dif > 0 else "dif-neg")
                    dif_txt = f"+{dif:g}" if dif > 0 else f"{dif:g}"
                    r[3].markdown(f"<div class='{cls}'><span class='{dif_cls}'>{dif_txt}</span></div>", unsafe_allow_html=True)

                if row.get("cantidad_fisica") is None:
                    estado_txt, estado_cls = "Pendiente", "badge-pendiente"
                elif dif == 0:
                    estado_txt, estado_cls = "Cuadra", "badge-ok"
                else:
                    estado_txt, estado_cls = "Diferencia", "badge-dif"
                r[4].markdown(f"<div class='{cls}'><span class='badge {estado_cls}'>{estado_txt}</span></div>", unsafe_allow_html=True)

                if esta_abierto:
                    with r[5]:
                        if dif not in (None, 0) and not row.get("activo_id") and not row.get("ajustado"):
                            if st.button("⚖️ Ajustar", key=f"inv_ajuste_{row['id']}", width="stretch"):
                                if aplicar_ajuste_existencia(row["id"], row["producto_id"], row["cantidad_fisica"]):
                                    st.success("Ajuste aplicado a Existencias.")
                                    st.rerun()
                        elif row.get("ajustado"):
                            st.caption("✅ Ajustado")

            total_paginas = max(1, -(-total_detalle // TAM_PAGINA))
            c1, c2, c3 = st.columns([1, 2, 1])
            with c1:
                if st.button("← Anterior", disabled=st.session_state["inv_detalle_pagina"] <= 0, key="invd_pag_ant"):
                    st.session_state["inv_detalle_pagina"] -= 1
                    st.rerun()
            with c2:
                st.markdown(f"<p style='text-align:center; font-size:12px; color:#64748B; margin-top:8px;'>Página {st.session_state['inv_detalle_pagina'] + 1} de {total_paginas} · {total_detalle} líneas</p>", unsafe_allow_html=True)
            with c3:
                if st.button("Siguiente →", disabled=st.session_state["inv_detalle_pagina"] >= total_paginas - 1, key="invd_pag_sig"):
                    st.session_state["inv_detalle_pagina"] += 1
                    st.rerun()
    else:
        st.info("📭 Este inventario todavía no tiene líneas. Agrega productos o activos arriba para empezar a contar.")

    if esta_abierto:
        st.divider()
        st.warning("⚠️ Al cerrar el inventario, ya no podrás agregar ni editar líneas de conteo.")
        if st.button("🔒 Cerrar Inventario", type="primary"):
            if cerrar_inventario(inventario_id):
                registrar_acceso(usuario_actual, nombre_actual, f"CERRAR INVENTARIO: {inventario['folio']}")
                st.session_state["_msg"] = f"Inventario {inventario['folio']} cerrado."
                st.rerun()

    st.stop()

# ══════════════════════════════════════════════════════════════
# VISTA DE LISTADO (cuando no hay inventario activo seleccionado)
# ══════════════════════════════════════════════════════════════
total = contar_inventarios()
abiertos = contar_inventarios(filtro_estado="abierto")
cerrados = contar_inventarios(filtro_estado="cerrado")

st.markdown(f"""
    <div class="kpi-bar">
        <div class="kpi-pill"><span class="kpi-icon">📊</span><span class="kpi-val" style="color:#1E293B;">{total}</span><span class="kpi-lbl">Total</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">🔵</span><span class="kpi-val" style="color:#1D4ED8;">{abiertos}</span><span class="kpi-lbl">Abiertos</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">⚪</span><span class="kpi-val" style="color:#64748B;">{cerrados}</span><span class="kpi-lbl">Cerrados</span></div>
    </div>
""", unsafe_allow_html=True)

if "inv_pagina" not in st.session_state:
    st.session_state["inv_pagina"] = 0
TAM_PAGINA = 50

panel_filtros = st.container(key="panel_filtros")
with panel_filtros:
    c1, c2, c3 = st.columns([4, 2, 1.6])
    with c1:
        busqueda = st.text_input("buscar", placeholder="🔍  Buscar por folio...", label_visibility="collapsed")
    with c2:
        filtro_est = st.selectbox("estado", ["Todos", "Abierto", "Cerrado"], label_visibility="collapsed")
    with c3:
        if st.button("➕ Nuevo Inventario", type="primary", width="stretch"):
            ventana_nuevo_inventario()

filtro_actual = (busqueda, filtro_est)
if st.session_state.get("inv_filtro_anterior") != filtro_actual:
    st.session_state["inv_pagina"] = 0
    st.session_state["inv_filtro_anterior"] = filtro_actual

datos, total_filtrado = cargar_inventarios(
    pagina=st.session_state["inv_pagina"], tam_pagina=TAM_PAGINA, busqueda=busqueda, filtro_estado=filtro_est
)
df_f = pd.DataFrame(datos)

if not df_f.empty:
    cw, ths = [1.5, 1.3, 1.5, 1.3, 1.3, 1.3, 1.2], ["Folio", "Inicio", "Cierre", "Líneas", "Contadas", "Con dif.", "Estado"]
    panel_tabla = st.container(key="panel_tabla")
    with panel_tabla:
        st.markdown('<div class="panel-card-titulo">📋 Inventarios registrados</div>', unsafe_allow_html=True)
        h_cols = st.columns(cw)
        for col, txt in zip(h_cols, ths):
            col.markdown(f"<p class='th'>{txt}</p>", unsafe_allow_html=True)
        for i, (_, row) in enumerate(df_f.iterrows()):
            cls = "td-alt" if i % 2 == 1 else "td"
            r = st.columns(cw)
            with r[0]:
                if st.button(row["folio"], key=f"abrir_inv_{row['id']}", width="stretch"):
                    st.session_state["inv_activo_id"] = row["id"]
                    st.session_state["inv_activo_folio"] = row["folio"]
                    st.session_state["inv_detalle_pagina"] = 0
                    st.rerun()
            r[1].markdown(f"<div class='{cls}'>{row['fecha_inicio']}</div>", unsafe_allow_html=True)
            r[2].markdown(f"<div class='{cls}'>{row.get('fecha_fin') or '—'}</div>", unsafe_allow_html=True)
            r[3].markdown(f"<div class='{cls}'>{row['total_lineas']}</div>", unsafe_allow_html=True)
            r[4].markdown(f"<div class='{cls}'>{row['contadas']}</div>", unsafe_allow_html=True)
            r[5].markdown(f"<div class='{cls}'>{row['con_diferencia']}</div>", unsafe_allow_html=True)
            badge_cls = "badge-abierto" if row["estado"] == "abierto" else "badge-cerrado"
            r[6].markdown(f"<div class='{cls}'><span class='badge {badge_cls}'>{row['estado'].capitalize()}</span></div>", unsafe_allow_html=True)

        total_paginas = max(1, -(-total_filtrado // TAM_PAGINA))
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if st.button("← Anterior", disabled=st.session_state["inv_pagina"] <= 0, key="inv_pag_ant"):
                st.session_state["inv_pagina"] -= 1
                st.rerun()
        with c2:
            st.markdown(f"<p style='text-align:center; font-size:12px; color:#64748B; margin-top:8px;'>Página {st.session_state['inv_pagina'] + 1} de {total_paginas} · {total_filtrado} resultados</p>", unsafe_allow_html=True)
        with c3:
            if st.button("Siguiente →", disabled=st.session_state["inv_pagina"] >= total_paginas - 1, key="inv_pag_sig"):
                st.session_state["inv_pagina"] += 1
                st.rerun()
else:
    st.info("📭 No hay inventarios registrados todavía. ¡Crea el primero!")
