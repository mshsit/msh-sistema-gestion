import streamlit as st
from supabase import create_client
from datetime import datetime, date
import pandas as pd
import re

st.set_page_config(
    page_title="MSH-Hub | Seguimiento de Proyectos",
    layout="wide",
    page_icon="🚦",
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
div[class*="st-key-panel_filtros"], div[class*="st-key-panel_tabla"] {
    background: #ffffff; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 22px 24px; margin-bottom: 18px;
    box-shadow: 0 2px 10px rgba(30,52,71,0.06);
}
.panel-card-titulo { font-size: 15px; font-weight: 700; color: #1E293B; margin-bottom: 2px; }
.panel-card-subtitulo { font-size: 12px; color: #94A3B8; margin-bottom: 16px; }
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
.folio-tag {
    font-family: 'DM Mono', monospace; font-size: 10px; color: #94A3B8;
    background: #F1F5F9; border-radius: 4px; padding: 1px 5px; display: inline-block;
}
.badge { font-size: 10px; font-weight: 700; padding: 3px 9px; border-radius: 99px; white-space: nowrap; }
.badge-verde    { background: #DCFCE7; color: #15803D; }
.badge-amarillo { background: #FEF3C7; color: #92400E; }
.badge-rojo     { background: #FEE2E2; color: #B91C1C; }
.badge-azul     { background: #DBEAFE; color: #1D4ED8; }
.badge-borrador { background: #F1F5F9; color: #64748B; }
.aviso-box {
    background: #FEF3E8; color: #C2410C; border-radius: 8px; padding: 10px 14px;
    font-size: 12px; margin-bottom: 14px;
}
[data-testid="stButton"] button {
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 12px !important;
}
</style>
""", unsafe_allow_html=True)

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://unsugrcleytqroxuuhaf.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")


@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_supabase()

AREAS = ["Torno / CNC", "Soldadura", "Sandblast / Pintura", "Inspección API", "Patios", "Recepción", "Otro"]
COLORES = {"verde": "🟢 Verde — Programado", "amarillo": "🟡 Amarillo — En Proceso",
           "rojo": "🔴 Rojo — Urgente / Detenido", "azul": "🔵 Azul — Listo"}
EMOJI_COLOR = {"verde": "🟢", "amarillo": "🟡", "rojo": "🔴", "azul": "🔵"}


def registrar_acceso(usuario, nombre, accion):
    try:
        supabase.table("usuarios_accesos").insert({
            "usuario": usuario, "nombre": nombre,
            "accion": accion, "fecha_hora": datetime.now().isoformat()
        }).execute()
    except Exception:
        pass


def fmt_fecha(valor):
    if not valor or (isinstance(valor, float) and pd.isna(valor)):
        return ""
    try:
        return datetime.fromisoformat(str(valor)[:10]).strftime("%d/%m/%Y")
    except ValueError:
        return str(valor)


def val_or(valor, default="—"):
    if valor is None or valor == "" or (isinstance(valor, float) and pd.isna(valor)):
        return default
    return valor


def generar_numero_ot():
    try:
        return supabase.rpc("generar_numero_ot", {}).execute().data
    except Exception as e:
        st.error(f"Error al generar número de OT: {e}")
        return None


def siguiente_numero_ot():
    try:
        return supabase.rpc("siguiente_numero_ot_preview", {}).execute().data
    except Exception:
        return "OT-????-???"


def cargar_proyectos_activos():
    try:
        res = supabase.table("almacen_proyectos").select("id, numero_proyecto, nombre, cliente_ubicacion") \
            .eq("estado", "activo").eq("activo", True).order("numero_proyecto").execute()
        return res.data if res.data else []
    except Exception:
        return []


def cargar_personas_activas():
    try:
        res = supabase.table("almacen_personas").select("id, nombres, apellidos").eq("activo", True).execute()
        personas = res.data if res.data else []
        for p in personas:
            p["nombre_completo"] = f"{p['nombres']} {p.get('apellidos') or ''}".strip()
        return sorted(personas, key=lambda p: p["nombre_completo"])
    except Exception:
        return []


def cargar_seguimientos():
    try:
        res = supabase.table("seguimiento_proyectos").select(
            "*, almacen_proyectos(numero_proyecto, nombre, cliente_ubicacion), almacen_personas(nombres, apellidos)"
        ).order("created_at", desc=True).execute()
        filas = []
        for s in (res.data or []):
            proy = s.get("almacen_proyectos") or {}
            persona = s.get("almacen_personas") or {}
            filas.append({
                **s,
                "numero_proyecto": proy.get("numero_proyecto"),
                "proyecto_nombre": proy.get("nombre"),
                "cliente": proy.get("cliente_ubicacion") or s.get("cliente_provisional"),
                "responsable_nombre": f"{persona.get('nombres', '')} {persona.get('apellidos') or ''}".strip() or None,
            })
        return filas
    except Exception as e:
        st.error(f"Error al cargar seguimiento de proyectos: {e}")
        return []


def crear_seguimiento(payload):
    try:
        res = supabase.table("seguimiento_proyectos").insert(payload).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return None


def actualizar_seguimiento(id_registro, payload):
    try:
        payload["updated_at"] = datetime.now().isoformat()
        supabase.table("seguimiento_proyectos").update(payload).eq("id", id_registro).execute()
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

def subir_documento_seguimiento(archivo, numero_ot):
    try:
        ruta = f"{numero_ot}/{datetime.now().strftime('%Y%m%d%H%M%S')}_{archivo.name}"
        supabase.storage.from_("proyectos-documentos").upload(
            ruta, archivo.getvalue(), {"content-type": archivo.type or "application/octet-stream"}
        )
        return ruta
    except Exception as e:
        st.warning(f"No se pudo subir el documento: {e}")
        return None


def subir_imagen_seguimiento(archivo, numero_ot):
    try:
        ruta = f"{numero_ot}/{datetime.now().strftime('%Y%m%d%H%M%S')}_{archivo.name}"
        supabase.storage.from_("proyectos-imagenes").upload(
            ruta, archivo.getvalue(), {"content-type": archivo.type or "application/octet-stream"}
        )
        return ruta
    except Exception as e:
        st.warning(f"No se pudo subir la imagen: {e}")
        return None

def url_firmada_documento(ruta, expira_seg=14400):
    try:
        res = supabase.storage.from_("proyectos-documentos").create_signed_url(ruta, expira_seg)
        return res.get("signedURL") or res.get("signed_url") or res.get("signedUrl")
    except Exception:
        return None


def url_firmada_imagen(ruta, expira_seg=14400):
    try:
        res = supabase.storage.from_("proyectos-imagenes").create_signed_url(ruta, expira_seg)
        return res.get("signedURL") or res.get("signed_url") or res.get("signedUrl")
    except Exception:
        return None

def cargar_documentos(seguimiento_id):
    try:
        res = supabase.table("seguimiento_documentos").select("*").eq("seguimiento_id", seguimiento_id).order("subido_at").execute()
        return res.data if res.data else []
    except Exception:
        return []


def cargar_imagenes(seguimiento_id):
    try:
        res = supabase.table("seguimiento_imagenes").select("*").eq("seguimiento_id", seguimiento_id).order("orden").execute()
        return res.data if res.data else []
    except Exception:
        return []


def eliminar_documento(doc_id):
    try:
        supabase.table("seguimiento_documentos").delete().eq("id", doc_id).execute()
    except Exception:
        pass


def eliminar_imagen(img_id):
    try:
        supabase.table("seguimiento_imagenes").delete().eq("id", img_id).execute()
    except Exception:
        pass


@st.dialog("🚦 Nueva OT", width="large")
def ventana_nueva_ot():
    st.caption(f"Número de OT sugerido: `{siguiente_numero_ot()}`")

    tiene_proyecto = st.radio("¿Ya tiene número de proyecto asignado?", ["Sí", "No, crear como borrador"],
                               horizontal=True, key="ot_tiene_proyecto")

    proyecto_id, nombre_provisional, cliente_provisional = None, None, None
    if tiene_proyecto == "Sí":
        proyectos = cargar_proyectos_activos()
        if not proyectos:
            st.warning("No hay proyectos activos registrados. Puedes crear esta OT como borrador mientras tanto.")
        else:
            opciones_proy = {f"{p['numero_proyecto']} — {p['nombre']}": p["id"] for p in proyectos}
            sel_proy = st.selectbox("Proyecto *", list(opciones_proy.keys()), key="ot_proyecto_sel")
            proyecto_id = opciones_proy[sel_proy]
    else:
        st.markdown('<div class="aviso-box">⚠️ Esta OT se creará como borrador, sin número de proyecto. No aparecerá en el tablero TV hasta que la vincules.</div>', unsafe_allow_html=True)
        nombre_provisional = st.text_input("Nombre del proyecto (provisional) *", key="ot_nombre_prov")
        cliente_provisional = st.text_input("Cliente (provisional)", key="ot_cliente_prov")

    c1, c2 = st.columns(2)
    with c1:
        equipo_servicio = st.text_input("Equipo / Servicio *", placeholder='Ej. Válvula 4"')
        sel_area = st.selectbox("Área actual *", AREAS, key="ot_area_sel")
        area_actual = st.text_input("Especifica el área", key="ot_area_otro") if sel_area == "Otro" else sel_area
    with c2:
        personas = cargar_personas_activas()
        opciones_resp = {p["nombre_completo"]: p["id"] for p in personas}
        sel_resp = st.selectbox("Responsable *", ["— Selecciona —"] + list(opciones_resp.keys()), key="ot_resp_sel")
        responsable_id = opciones_resp.get(sel_resp)
        fecha_entrega = st.date_input("Fecha de entrega", value=None, format="DD/MM/YYYY", key="ot_fecha_entrega")

    c1, c2 = st.columns(2)
    with c1:
        color_semaforo = st.selectbox("Semáforo *", list(COLORES.keys()), format_func=lambda c: COLORES[c], key="ot_color_sel")
    with c2:
        categoria = st.text_input("Categoría", placeholder="Ej. Fabricación", key="ot_categoria")

    descripcion = st.text_area("Descripción / Observaciones", height=60, key="ot_descripcion")

    st.divider()
    c1, c2 = st.columns([1, 2])
    with c1:
        if st.button("Cancelar", width="stretch", key="ot_cancelar"):
            st.rerun()
    with c2:
        campos_ok = equipo_servicio.strip() and area_actual and responsable_id and (
            proyecto_id or nombre_provisional.strip()
        )
        if st.button("✅ Crear OT", type="primary", width="stretch", disabled=not campos_ok, key="ot_crear"):
            numero_ot = generar_numero_ot()
            if not numero_ot:
                st.error("No se pudo generar el número de OT, intenta de nuevo.")
            else:
                payload = {
                    "numero_ot": numero_ot, "proyecto_id": proyecto_id,
                    "nombre_provisional": nombre_provisional.strip() if nombre_provisional else None,
                    "cliente_provisional": cliente_provisional.strip() if cliente_provisional else None,
                    "equipo_servicio": equipo_servicio.strip(), "area_actual": area_actual,
                    "categoria": categoria.strip() or None, "responsable_id": responsable_id,
                    "color_semaforo": color_semaforo, "estado_ciclo": "activo",
                    "fecha_entrega": str(fecha_entrega) if fecha_entrega else None,
                    "descripcion": descripcion.strip() or None,
                    "usuario_registro": st.session_state["usuario"], "nombre_registro": st.session_state["nombre"],
                }
                seguimiento_id = crear_seguimiento(payload)
                if seguimiento_id:
                    registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"CREAR OT: {numero_ot}")
                    st.session_state["_msg_seg"] = f"OT {numero_ot} creada correctamente."
                    st.rerun()


@st.dialog("✏️ Editar OT", width="large")
def ventana_editar_ot(seg):
    es_borrador = seg.get("proyecto_id") is None
    st.markdown(f"**OT:** `{seg['numero_ot']}`" + ("  ·  ⚠️ Borrador — sin proyecto vinculado" if es_borrador else f"  ·  Proyecto: `{seg.get('numero_proyecto', '—')}`"))

    if es_borrador:
        with st.expander("🔗 Vincular a número de proyecto"):
            proyectos = cargar_proyectos_activos()
            if not proyectos:
                st.caption("No hay proyectos activos disponibles todavía.")
            else:
                opciones_proy = {f"{p['numero_proyecto']} — {p['nombre']}": p["id"] for p in proyectos}
                sel_proy = st.selectbox("Proyecto", list(opciones_proy.keys()), key=f"vinc_proy_{seg['id']}")
                if st.button("Vincular", key=f"vinc_btn_{seg['id']}"):
                    if actualizar_seguimiento(seg["id"], {"proyecto_id": opciones_proy[sel_proy], "nombre_provisional": None, "cliente_provisional": None}):
                        registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"VINCULAR OT: {seg['numero_ot']}")
                        st.session_state["_msg_seg"] = f"OT {seg['numero_ot']} vinculada correctamente."
                        st.rerun()

    c1, c2 = st.columns(2)
    with c1:
        equipo_servicio = st.text_input("Equipo / Servicio *", value=seg.get("equipo_servicio") or "")
        idx_area = AREAS.index(seg["area_actual"]) if seg.get("area_actual") in AREAS else len(AREAS) - 1
        sel_area = st.selectbox("Área actual *", AREAS, index=idx_area, key=f"ed_area_{seg['id']}")
        area_actual = st.text_input("Especifica el área", value=seg.get("area_actual") or "", key=f"ed_area_otro_{seg['id']}") if sel_area == "Otro" else sel_area
    with c2:
        personas = cargar_personas_activas()
        opciones_resp = {p["nombre_completo"]: p["id"] for p in personas}
        nombres_resp = list(opciones_resp.keys())
        idx_resp = nombres_resp.index(seg["responsable_nombre"]) if seg.get("responsable_nombre") in nombres_resp else 0
        sel_resp = st.selectbox("Responsable *", nombres_resp, index=idx_resp if nombres_resp else 0, key=f"ed_resp_{seg['id']}")
        responsable_id = opciones_resp.get(sel_resp)
        fecha_entrega = st.date_input("Fecha de entrega", value=date.fromisoformat(seg["fecha_entrega"]) if seg.get("fecha_entrega") else None, format="DD/MM/YYYY", key=f"ed_fecha_{seg['id']}")

    c1, c2 = st.columns(2)
    with c1:
        idx_color = list(COLORES.keys()).index(seg.get("color_semaforo", "verde"))
        color_semaforo = st.selectbox("Semáforo *", list(COLORES.keys()), index=idx_color, format_func=lambda c: COLORES[c], key=f"ed_color_{seg['id']}")
    with c2:
        categoria = st.text_input("Categoría", value=seg.get("categoria") or "", key=f"ed_cat_{seg['id']}")

    descripcion = st.text_area("Descripción / Observaciones", value=seg.get("descripcion") or "", height=60, key=f"ed_desc_{seg['id']}")

    estado_ciclo = st.selectbox("Estado", ["activo", "cerrado", "cancelado"],
                                 index=["activo", "cerrado", "cancelado"].index(seg.get("estado_ciclo", "activo")),
                                 format_func=lambda v: v.capitalize(), key=f"ed_estado_{seg['id']}")

    st.divider()
    st.markdown("**📎 Documentos**")
    for doc in cargar_documentos(seg["id"]):
        dc1, dc2 = st.columns([5, 1])
        link = url_firmada_documento(doc["url"])
        dc1.markdown(f"[{doc['nombre_archivo']}]({link})" if link else f"{doc['nombre_archivo']} (no disponible)")
        if dc2.button("🗑️", key=f"del_doc_{doc['id']}"):
            eliminar_documento(doc["id"])
            st.rerun(scope="fragment")
    nuevo_doc = st.file_uploader("Agregar documento", key=f"up_doc_{seg['id']}", label_visibility="collapsed")
    if nuevo_doc and st.button("⬆️ Subir documento", key=f"btn_doc_{seg['id']}"):
        url = subir_documento_seguimiento(nuevo_doc, seg["numero_ot"])
        if url:
            supabase.table("seguimiento_documentos").insert({
                "seguimiento_id": seg["id"], "nombre_archivo": nuevo_doc.name, "url": url,
                "tamano_kb": round(nuevo_doc.size / 1024),
            }).execute()
            st.rerun(scope="fragment")

    st.markdown("**🖼️ Galería de imágenes**")
    imagenes = cargar_imagenes(seg["id"])
    if imagenes:
        cols_img = st.columns(4)
        for i, img in enumerate(imagenes):
            with cols_img[i % 4]:
                link = url_firmada_imagen(img["url"])
                if link:
                    st.image(link, width="stretch")
                if st.button("🗑️", key=f"del_img_{img['id']}", width="stretch"):
                    eliminar_imagen(img["id"])
                    st.rerun(scope="fragment")
    nueva_img = st.file_uploader("Agregar imagen", type=["png", "jpg", "jpeg"], key=f"up_img_{seg['id']}", label_visibility="collapsed")
    if nueva_img and st.button("⬆️ Subir imagen", key=f"btn_img_{seg['id']}"):
        url = subir_imagen_seguimiento(nueva_img, seg["numero_ot"])
        if url:
            supabase.table("seguimiento_imagenes").insert({
                "seguimiento_id": seg["id"], "url": url, "orden": len(imagenes),
            }).execute()
            st.rerun(scope="fragment")

    st.divider()
    c1, c2 = st.columns([1, 2])
    with c1:
        if st.button("Cancelar", width="stretch", key=f"ed_cancelar_{seg['id']}"):
            st.rerun()
    with c2:
        if st.button("💾 Guardar Cambios", type="primary", width="stretch", key=f"ed_guardar_{seg['id']}"):
            payload = {
                "equipo_servicio": equipo_servicio.strip(), "area_actual": area_actual,
                "categoria": categoria.strip() or None, "responsable_id": responsable_id,
                "color_semaforo": color_semaforo, "estado_ciclo": estado_ciclo,
                "fecha_entrega": str(fecha_entrega) if fecha_entrega else None,
                "descripcion": descripcion.strip() or None,
            }
            if actualizar_seguimiento(seg["id"], payload):
                registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"EDITAR OT: {seg['numero_ot']}")
                st.session_state["_msg_seg"] = f"OT {seg['numero_ot']} actualizada."
                st.rerun()


nombre_actual  = st.session_state.get("nombre", "")
rol_actual     = st.session_state.get("rol", "")
usuario_actual = st.session_state.get("usuario", "")
iniciales      = "".join([p[0].upper() for p in nombre_actual.split()[:2]]) if nombre_actual else "AD"

st.markdown(f"""
    <div class="msh-header">
        <div class="msh-header-left">
            <div class="msh-logo-box">🚦</div>
            <div>
                <div class="msh-title">MSH-Hub · Seguimiento de Proyectos</div>
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

if "_msg_seg" in st.session_state:
    st.success(st.session_state.pop("_msg_seg"))

df_master = pd.DataFrame(cargar_seguimientos())
total = len(df_master) if not df_master.empty else 0
activos = len(df_master[df_master["estado_ciclo"] == "activo"]) if not df_master.empty else 0
borradores = len(df_master[df_master["proyecto_id"].isna()]) if not df_master.empty else 0
urgentes = len(df_master[(df_master["color_semaforo"] == "rojo") & (df_master["estado_ciclo"] == "activo")]) if not df_master.empty else 0

st.markdown(f"""
    <div class="kpi-bar">
        <div class="kpi-pill"><span class="kpi-icon">🚦</span><span class="kpi-val" style="color:#1E293B;">{total}</span><span class="kpi-lbl">Total OTs</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">🟢</span><span class="kpi-val" style="color:#15803D;">{activos}</span><span class="kpi-lbl">Activas</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">🔴</span><span class="kpi-val" style="color:#B91C1C;">{urgentes}</span><span class="kpi-lbl">Urgentes</span></div>
        <div class="kpi-sep"></div>
        <div class="kpi-pill"><span class="kpi-icon">⚠️</span><span class="kpi-val" style="color:#C2410C;">{borradores}</span><span class="kpi-lbl">Borradores</span></div>
    </div>
""", unsafe_allow_html=True)

panel_filtros = st.container(key="panel_filtros")
with panel_filtros:
    st.markdown('<div class="panel-card-titulo">🔍 Filtros y búsqueda</div>', unsafe_allow_html=True)
    c_busq, c_color, c_nuevo = st.columns([4, 2.2, 1.8])
    with c_busq:
        busqueda = st.text_input("buscar", placeholder="🔍  Buscar por OT, proyecto, cliente o equipo...", label_visibility="collapsed")
    with c_color:
        filtro_color = st.selectbox("color", ["Todos"] + list(COLORES.keys()), format_func=lambda c: "Todos" if c == "Todos" else COLORES[c], label_visibility="collapsed")
    with c_nuevo:
        if st.button("➕ Nueva OT", type="primary", width="stretch"):
            ventana_nueva_ot()

df_f = df_master.copy() if not df_master.empty else pd.DataFrame()
if not df_f.empty:
    if busqueda.strip():
        texto = (df_f["numero_ot"].fillna("") + " " + df_f["numero_proyecto"].fillna("") + " " +
                 df_f["cliente"].fillna("") + " " + df_f["equipo_servicio"].fillna("")).str.lower()
        mask = pd.Series(True, index=df_f.index)
        for termino in busqueda.lower().split():
            mask &= texto.str.contains(re.escape(termino), na=False)
        df_f = df_f[mask]
    if filtro_color != "Todos":
        df_f = df_f[df_f["color_semaforo"] == filtro_color]

if not df_f.empty:
    cw = [1.3, 1.4, 1.8, 1.6, 1.3, 1.2, 1.1, 1.1, 0.7]
    ths = ["OT", "Proyecto", "Cliente", "Equipo/Servicio", "Área actual", "Semáforo", "Responsable", "F. entrega", "✏️"]
    panel_tabla = st.container(key="panel_tabla")
    with panel_tabla:
        st.markdown('<div class="panel-card-titulo">📋 OTs registradas</div>', unsafe_allow_html=True)
        h_cols = st.columns(cw)
        for idx, (col, txt) in enumerate(zip(h_cols, ths)):
            col.markdown(f"<p class='th'{' style=text-align:center;' if idx == len(ths) - 1 else ''}>{txt}</p>", unsafe_allow_html=True)
        for i, (_, row) in enumerate(df_f.iterrows()):
            cls = "td-alt" if i % 2 == 1 else "td"
            r = st.columns(cw)
            r[0].markdown(f"<div class='{cls}'><span class='folio-tag'>{row['numero_ot']}</span></div>", unsafe_allow_html=True)
            if pd.isna(row.get("proyecto_id")):
                r[1].markdown(f"<div class='{cls}'><span class='badge badge-borrador'>⚠️ Borrador</span></div>", unsafe_allow_html=True)
            else:
                r[1].markdown(f"<div class='{cls}'><b>{val_or(row.get('numero_proyecto'))}</b></div>", unsafe_allow_html=True)
            r[2].markdown(f"<div class='{cls}'>{val_or(row.get('cliente') or row.get('cliente_provisional'))}</div>", unsafe_allow_html=True)
            r[3].markdown(f"<div class='{cls}'>{val_or(row.get('equipo_servicio'))}</div>", unsafe_allow_html=True)
            r[4].markdown(f"<div class='{cls}'>{val_or(row.get('area_actual'))}</div>", unsafe_allow_html=True)
            color = row.get("color_semaforo", "verde")
            etiqueta = COLORES.get(color, "").split("— ")[-1] if row["estado_ciclo"] == "activo" else row["estado_ciclo"].capitalize()
            clase_badge = f"badge-{color}" if row["estado_ciclo"] == "activo" else "badge-borrador"
            emoji = EMOJI_COLOR.get(color, "⚪") if row["estado_ciclo"] == "activo" else "⚪"
            r[5].markdown(f"<div class='{cls}'><span class='badge {clase_badge}'>{emoji} {etiqueta}</span></div>", unsafe_allow_html=True)
            r[6].markdown(f"<div class='{cls}'>{val_or(row.get('responsable_nombre'))}</div>", unsafe_allow_html=True)
            r[7].markdown(f"<div class='{cls}'>{fmt_fecha(row.get('fecha_entrega')) or '—'}</div>", unsafe_allow_html=True)
            with r[8]:
                if st.button("✏️", key=f"ed_seg_{row['id']}", width="stretch"):
                    ventana_editar_ot(row.to_dict())
else:
    st.info("📭 No hay OTs registradas todavía. ¡Crea la primera!")
