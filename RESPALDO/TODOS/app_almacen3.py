import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# ══════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════
st.set_page_config(page_title="MSH-Hub | Almacén", layout="wide", page_icon="📦")

st.markdown("""
    <style>
    .kpi-title { font-size: 11px !important; font-weight: bold !important; color: #7A8B99 !important; text-align: center; margin-bottom: 5px; text-transform: uppercase; }
    .kpi-value { font-size: 32px !important; font-weight: bold !important; text-align: center; margin-top: -10px; }
    .card { background-color: white; padding: 12px; border-radius: 6px; box-shadow: 0px 1px 3px rgba(0,0,0,0.1); border: 1px solid #E2E8F0; }
    .tip-clic { background-color: #EBF8FF; border-left: 4px solid #3182CE; padding: 8px 12px; border-radius: 4px; font-size: 13px; color: #2C5282; margin-bottom: 8px; }
    .user-info { background-color: #F0FFF4; border-left: 4px solid #38A169; padding: 8px 12px; border-radius: 4px; font-size: 13px; color: #276749; margin-bottom: 8px; }
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
        if res.data:
            return res.data[0]
        return None
    except:
        return None

def registrar_acceso(usuario, nombre, accion):
    try:
        supabase.table("usuarios_accesos").insert({
            "usuario": usuario,
            "nombre": nombre,
            "accion": accion,
            "fecha_hora": datetime.now().isoformat()
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

# ══════════════════════════════════════════════
# GENERADOR PDF
# ══════════════════════════════════════════════
def generar_pdf(df):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_margins(10, 10, 10)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(30, 52, 71)
    pdf.cell(0, 8, "MSH-HUB | SISTEMA DE CONTROL DE ALMACEN", ln=True, align='L')
    pdf.set_font("Arial", '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Reporte generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Usuario: {st.session_state.get('nombre', '')}", ln=True, align='L')
    pdf.ln(4)
    widths   = [32, 24, 40, 48, 14, 32, 60, 15]
    columnas = ["Folio", "Fecha", "Responsable", "Articulo", "Cant", "Estado", "Observaciones", "Alerta"]
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(30, 52, 71)
    pdf.set_text_color(255, 255, 255)
    for i, col in enumerate(columnas):
        pdf.cell(widths[i], 8, col, border=1, ln=0, align='C' if i in [4, 7] else 'L', fill=True)
    pdf.ln()
    for _, row in df.iterrows():
        en_alerta = str(row.get('alerta', 'NO')).upper().strip() == 'SI'
        if en_alerta:
            pdf.set_fill_color(254, 226, 226); pdf.set_text_color(153, 27, 27); fondo = True
        else:
            pdf.set_text_color(0, 0, 0); fondo = False
        def celda(texto, ancho, align='L'):
            t = str(texto)
            pdf.set_font("Arial", '', 6 if len(t) * (8.5 * 0.6) / 2.834 > (ancho - 2) else 8.5)
            pdf.cell(ancho, 7, t, 1, 0, align, fondo)
        celda(row.get('id', ''),           widths[0], 'L')
        celda(row.get('fecha', ''),         widths[1], 'C')
        celda(row.get('responsable', ''),   widths[2], 'L')
        celda(row.get('articulo', ''),      widths[3], 'L')
        celda(str(row.get('cantidad', 1)),  widths[4], 'C')
        celda(row.get('estado', ''),        widths[5], 'L')
        celda(row.get('observaciones', ''), widths[6], 'L')
        pdf.set_font("Arial", '', 8.5)
        pdf.cell(widths[7], 7, "SI" if en_alerta else "NO", 1, 0, 'C', fondo)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1', errors='ignore')

# ══════════════════════════════════════════════
# VENTANAS EMERGENTES
# ══════════════════════════════════════════════
@st.dialog("Confirmar Eliminacion")
def ventana_confirmar_eliminar(id_a_eliminar):
    st.warning(f"Estas seguro de eliminar el registro {id_a_eliminar}? Esta accion no se puede deshacer.")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Cancelar", key="btn_cancel_del", use_container_width=True):
            st.rerun()
    with c2:
        if st.button("Si, Eliminar", type="primary", key="btn_confirm_del", use_container_width=True):
            if eliminar_prestamo(id_a_eliminar):
                registrar_acceso(
                    st.session_state["usuario"],
                    st.session_state["nombre"],
                    f"ELIMINAR_PRESTAMO: {id_a_eliminar}"
                )
                st.session_state["id_desde_tabla"] = ""
                st.session_state["seccion_activa"] = "Modificar o Eliminar Registro"
                st.rerun()

# ══════════════════════════════════════════════
# INICIALIZAR SESSION STATE
# ══════════════════════════════════════════════
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "id_desde_tabla" not in st.session_state:
    st.session_state["id_desde_tabla"] = ""
if "pagina_actual" not in st.session_state:
    st.session_state["pagina_actual"] = 1

# ══════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════
if not st.session_state["autenticado"]:
    st.markdown("""
        <div style='text-align:center; margin-top:60px;'>
            <h1 style='color:#1E3447;'>MSH-Hub</h1>
            <p style='color:#7A8B99; font-size:16px;'>Mendoza Servicios y Herramientas</p>
        </div>
    """, unsafe_allow_html=True)

    _, col_center, _ = st.columns([1, 1.2, 1])
    with col_center:
        with st.container(border=True):
            st.markdown("### Acceso al Sistema")
            usuario_input = st.text_input("Usuario:", placeholder="tu.usuario")
            contrasena_input = st.text_input("Contrasena:", type="password")
            st.write("")
            if st.button("Ingresar", type="primary", width="stretch"):
                if usuario_input.strip() and contrasena_input.strip():
                    user_data = verificar_usuario(usuario_input.strip(), contrasena_input.strip())
                    if user_data:
                        st.session_state["autenticado"] = True
                        st.session_state["usuario"]     = user_data["usuario"]
                        st.session_state["nombre"]      = user_data["nombre"]
                        st.session_state["rol"]         = user_data["rol"]
                        registrar_acceso(user_data["usuario"], user_data["nombre"], "LOGIN")
                        st.rerun()
                    else:
                        st.error("Usuario o contrasena incorrectos")
                else:
                    st.warning("Ingresa tu usuario y contrasena")

# ══════════════════════════════════════════════
# DASHBOARD PRINCIPAL
# ══════════════════════════════════════════════
else:
    usuario_actual = st.session_state["usuario"]
    nombre_actual  = st.session_state["nombre"]
    rol_actual     = st.session_state["rol"]
    es_admin       = rol_actual == "admin"

    # HEADER
    col_titulo, col_usuario = st.columns([6, 2])
    with col_titulo:
        st.markdown("<h1 style='color:#1E3447; font-family:sans-serif; margin-bottom:5px;'>📦 MSH-Hub | Control de Almacen</h1>", unsafe_allow_html=True)
    with col_usuario:
        st.write("")
        st.markdown(f'<div class="user-info">👤 <b>{nombre_actual}</b> | Rol: {rol_actual.upper()}</div>', unsafe_allow_html=True)
        if st.button("Cerrar Sesion", key="btn_logout"):
            registrar_acceso(usuario_actual, nombre_actual, "LOGOUT")
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # CARGAR DATOS
    datos = cargar_prestamos()
    df_master = pd.DataFrame(datos)

    if not df_master.empty and 'alerta' in df_master.columns:
        df_master['alerta'] = df_master['alerta'].apply(normalizar_alerta)

    # KPIs
    total_reg    = len(df_master)
    prestados    = len(df_master[df_master['estado'] == 'Prestado'])              if not df_master.empty else 0
    devueltos    = len(df_master[df_master['estado'] == 'Devuelto'])              if not df_master.empty else 0
    asignados    = len(df_master[df_master['estado'] == 'Asignado'])              if not df_master.empty else 0
    proceso_asig = len(df_master[df_master['estado'] == 'Proceso de asignacion']) if not df_master.empty else 0
    alertas      = len(df_master[df_master['alerta'] == 'SI'])                    if not df_master.empty else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: st.markdown(f'<div class="card"><p class="kpi-title">TOTAL</p><p class="kpi-value" style="color:#2D3748;">{total_reg}</p></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="card"><p class="kpi-title">PRESTADOS</p><p class="kpi-value" style="color:#DD6B20;">{prestados}</p></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="card"><p class="kpi-title">DEVUELTOS</p><p class="kpi-value" style="color:#38A169;">{devueltos}</p></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="card"><p class="kpi-title">ASIGNADOS</p><p class="kpi-value" style="color:#3182CE;">{asignados}</p></div>', unsafe_allow_html=True)
    with c5: st.markdown(f'<div class="card"><p class="kpi-title">EN PROCESO</p><p class="kpi-value" style="color:#805AD5;">{proceso_asig}</p></div>', unsafe_allow_html=True)
    with c6: st.markdown(f'<div class="card"><p class="kpi-title">EN ALERTA</p><p class="kpi-value" style="color:#E53E3E;">{alertas}</p></div>', unsafe_allow_html=True)

    st.write("")

    # ── NAVEGACIÓN ──────────────────────────────────────────────────────────
    if es_admin:
        # Mantener sección activa en session_state
        if "seccion_activa" not in st.session_state:
            st.session_state["seccion_activa"] = "Registrar Nuevo"

        # Si viene un ID desde tabla, forzar sección modificar
        if st.session_state.get("id_desde_tabla", "") != "":
            st.session_state["seccion_activa"] = "Modificar o Eliminar Registro"

        seccion = st.radio(
            "Seccion:",
            ["Registrar Nuevo", "Modificar o Eliminar Registro"],
            horizontal=True,
            index=0 if st.session_state["seccion_activa"] == "Registrar Nuevo" else 1,
            label_visibility="collapsed"
        )
        # Actualizar session_state cuando el usuario cambia manualmente
        st.session_state["seccion_activa"] = seccion
        st.divider()

    # ── SECCIÓN AGREGAR (solo admin) ─────────────────────────────────────────
    if es_admin and seccion == "Registrar Nuevo":
        with st.container():
            f1, f2, f3, f4, f5, f6 = st.columns([1.4, 2, 2, 1, 1.5, 2.5])
            with f1: fecha_add  = st.date_input("Fecha", datetime.now(), format="DD/MM/YYYY", key="f_add")
            with f2: resp_add   = st.text_input("Responsable", placeholder="Nombre", key="r_add")
            with f3: art_add    = st.text_input("Articulo", placeholder="Herramienta", key="a_add")
            with f4: cant_add   = st.text_input("Cantidad", value="1", key="c_add")
            with f5: est_add    = st.selectbox("Estado", ["Prestado", "Devuelto", "Asignado", "Proceso de asignacion"], key="e_add")
            with f6: obs_add    = st.text_input("Observaciones", placeholder="Opcional", key="o_add")
            fa, fb, fc = st.columns([6, 2, 1])
            with fa: nota_add   = st.text_input("Nota interna...", placeholder="Nota adicional", key="n_add")
            with fb: alerta_add = st.selectbox("Alerta?", ["NO", "SI"], key="al_add")
            with fc:
                st.write("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
                if st.button("Agregar", type="primary", width="stretch"):
                    if resp_add.strip() and art_add.strip():
                        payload = {
                            "id": f"ID-{int(datetime.now().timestamp())}",
                            "fecha": fecha_add.strftime('%d/%m/%Y'),
                            "responsable": resp_add,
                            "articulo": art_add,
                            "cantidad": int(cant_add) if cant_add.isdigit() else 1,
                            "estado": est_add,
                            "observaciones": obs_add,
                            "nota": nota_add,
                            "alerta": alerta_add
                        }
                        if agregar_prestamo(payload):
                            registrar_acceso(usuario_actual, nombre_actual, f"AGREGAR_PRESTAMO: {payload['id']}")
                            st.success("Registro agregado correctamente!")
                            st.rerun()
                        else:
                            st.error("Error al agregar el registro.")
                    else:
                        st.warning("Rellena los campos obligatorios.")

    # ── SECCIÓN MODIFICAR / ELIMINAR ────────────────────────────────────────
    if es_admin and seccion == "Modificar o Eliminar Registro":
        with st.container():
            if not df_master.empty:
                m1, _ = st.columns([2, 6])
                with m1:
                    id_desde_tabla = st.session_state.get("id_desde_tabla", "")
                    lista_ids = [""] + list(df_master['id'].unique())
                    idx_default = lista_ids.index(id_desde_tabla) if id_desde_tabla in lista_ids else 0
                    id_seleccionado = st.selectbox(
                        "Selecciona el Folio / ID:",
                        lista_ids,
                        index=idx_default,
                        key="id_selector_mod"
                    )

                if id_seleccionado != st.session_state.get("id_desde_tabla", ""):
                    st.session_state["id_desde_tabla"] = id_seleccionado

                if id_seleccionado != "":
                    fila_actual = df_master[df_master['id'] == id_seleccionado].iloc[0]
                    fecha_texto = str(fila_actual.get('fecha', ''))
                    try:
                        fecha_objeto_mod = datetime.strptime(fecha_texto, '%d/%m/%Y')
                    except:
                        fecha_objeto_mod = datetime.now()

                    _k = id_seleccionado

                    with st.container():
                        st.markdown(f"**Editando Folio:** `{id_seleccionado}`")
                        f1, f2, f3, f4, f5, f6 = st.columns([1.4, 2, 2, 1, 1.5, 2.5])
                        with f1: fecha_mod_dt = st.date_input("Fecha", value=fecha_objeto_mod, format="DD/MM/YYYY", key=f"f_mod_{_k}")
                        with f2: resp_mod     = st.text_input("Responsable", value=str(fila_actual.get('responsable', '')), key=f"r_mod_{_k}")
                        with f3: art_mod      = st.text_input("Articulo",    value=str(fila_actual.get('articulo', '')),    key=f"a_mod_{_k}")
                        with f4: cant_mod     = st.text_input("Cantidad",    value=str(fila_actual.get('cantidad', '1')),   key=f"c_mod_{_k}")
                        estados_opciones = ["Prestado", "Devuelto", "Asignado", "Proceso de asignacion"]
                        estado_actual    = fila_actual.get('estado', 'Prestado')
                        estado_index     = estados_opciones.index(estado_actual) if estado_actual in estados_opciones else 0
                        with f5: est_mod  = st.selectbox("Estado", estados_opciones, index=estado_index, key=f"e_mod_{_k}")
                        with f6: obs_mod  = st.text_input("Observaciones", value=str(fila_actual.get('observaciones', '')), key=f"o_mod_{_k}")
                        fa, fb = st.columns([7, 3])
                        with fa: nota_mod = st.text_input("Nota interna...", value=str(fila_actual.get('nota', '')), key=f"n_mod_{_k}")
                        alerta_actual = normalizar_alerta(fila_actual.get('alerta', 'NO'))
                        alerta_index  = 1 if alerta_actual == "SI" else 0
                        with fb: alerta_mod = st.selectbox("Alerta:", ["NO", "SI"], index=alerta_index, key=f"al_mod_{_k}")

                        btn_col1, btn_col2, _ = st.columns([2, 2, 4])
                        with btn_col1:
                            if st.button("Guardar Cambios", type="primary", width="stretch", key=f"btn_guardar_{_k}"):
                                payload_mod = {
                                    "fecha":         fecha_mod_dt.strftime('%d/%m/%Y'),
                                    "responsable":   str(resp_mod),
                                    "articulo":      str(art_mod),
                                    "cantidad":      int(cant_mod) if str(cant_mod).isdigit() else 1,
                                    "estado":        str(est_mod),
                                    "observaciones": str(obs_mod),
                                    "nota":          str(nota_mod),
                                    "alerta":        str(alerta_mod)
                                }
                                if modificar_prestamo(id_seleccionado, payload_mod):
                                    registrar_acceso(usuario_actual, nombre_actual, f"MODIFICAR_PRESTAMO: {id_seleccionado}")
                                    st.success("Registro modificado correctamente!")
                                    for suffix in ["al_mod", "e_mod", "f_mod", "r_mod", "a_mod", "c_mod", "o_mod", "n_mod"]:
                                        key_w = f"{suffix}_{_k}"
                                        if key_w in st.session_state:
                                            del st.session_state[key_w]
                                    st.session_state["id_desde_tabla"] = ""
                                    st.rerun()
                                else:
                                    st.error("Error al modificar el registro.")
                        with btn_col2:
                            if st.button("Eliminar Registro", type="secondary", width="stretch", key=f"btn_eliminar_{_k}"):
                                ventana_confirmar_eliminar(id_seleccionado)
            else:
                st.info("No hay registros disponibles.")

    st.divider()

    # ── ACCIONES GENERALES ───────────────────────────────────────────────────
    a1, a2, a3, a4 = st.columns([1.5, 1.5, 1.5, 5])
    with a1:
        if not df_master.empty:
            st.download_button("Exportar CSV", data=df_master.to_csv(index=False).encode('utf-8'),
                               file_name="almacen_prestamos.csv", mime="text/csv", width="stretch")
        else:
            st.button("Exportar CSV", disabled=True, width="stretch")
    with a2:
        if not df_master.empty:
            st.download_button("Generar PDF", data=generar_pdf(df_master),
                               file_name="reporte_almacen.pdf", mime="application/pdf", width="stretch")
        else:
            st.button("Generar PDF", disabled=True, width="stretch")
    with a3:
        st.write("")
    with a4:
        busqueda = st.text_input("Buscar...", placeholder="Buscar responsable o articulo...", label_visibility="collapsed")

    # ── TABLA CON CLIC Y PAGINACIÓN ──────────────────────────────────────────
    if not df_master.empty:
        df_filtrado = df_master[
            df_master['responsable'].str.contains(busqueda, case=False, na=False) |
            df_master['articulo'].str.contains(busqueda, case=False, na=False)
        ].copy()

        def colorear_alertas(fila):
            if str(fila['alerta']).upper().strip() == 'SI':
                return ['background-color: #FEE2E2; color: #991B1B; font-weight: bold;'] * len(fila)
            return [''] * len(fila)

        columnas_mostrar = ["id", "fecha", "responsable", "articulo", "cantidad", "estado", "observaciones", "nota", "alerta"]
        columnas_existentes = [c for c in columnas_mostrar if c in df_filtrado.columns]
        df_para_mostrar = df_filtrado[columnas_existentes].reset_index(drop=True)

        # PAGINACION
        FILAS_POR_PAGINA = 20
        total_filas   = len(df_para_mostrar)
        total_paginas = max(1, -(-total_filas // FILAS_POR_PAGINA))

        if busqueda != st.session_state.get("ultima_busqueda", ""):
            st.session_state["pagina_actual"] = 1
            st.session_state["ultima_busqueda"] = busqueda

        pagina_actual = st.session_state["pagina_actual"]
        inicio    = (pagina_actual - 1) * FILAS_POR_PAGINA
        fin       = inicio + FILAS_POR_PAGINA
        df_pagina = df_para_mostrar.iloc[inicio:fin]

        if es_admin:
            st.markdown('<div class="tip-clic">Haz clic en cualquier fila para cargar ese registro en el formulario de modificacion.</div>', unsafe_allow_html=True)

        seleccion = st.dataframe(
            df_pagina.style.apply(colorear_alertas, axis=1),
            width="stretch",
            hide_index=True,
            on_select="rerun" if es_admin else "ignore",
            selection_mode="single-row",
            column_config={
                "id": "Folio / ID", "fecha": "Fecha", "responsable": "Responsable",
                "articulo": "Articulo", "cantidad": "Cant.", "estado": "Estado",
                "observaciones": "Observaciones", "nota": "Nota", "alerta": "Alerta"
            }
        )

        # DETECTAR CLIC EN FILA
        if es_admin:
            filas_seleccionadas = seleccion.selection.rows if seleccion.selection else []
            if filas_seleccionadas:
                idx_fila     = filas_seleccionadas[0]
                id_clickeado = df_pagina.iloc[idx_fila]["id"]
                if id_clickeado != st.session_state.get("id_desde_tabla", ""):
                    for suffix in ["al_mod", "e_mod", "f_mod", "r_mod", "a_mod", "c_mod", "o_mod", "n_mod"]:
                        key_w = f"{suffix}_{id_clickeado}"
                        if key_w in st.session_state:
                            del st.session_state[key_w]
                    st.session_state["id_desde_tabla"] = id_clickeado
                    if "id_selector_mod" in st.session_state:
                        del st.session_state["id_selector_mod"]
                    st.toast(f"Registro {id_clickeado} cargado en el formulario")
                    st.rerun()

        # CONTROLES PAGINACION
        p1, p2, p3, p4, p5 = st.columns([1, 1, 3, 1, 1])
        with p1:
            if st.button("Primera", disabled=(pagina_actual == 1), use_container_width=True):
                st.session_state["pagina_actual"] = 1; st.rerun()
        with p2:
            if st.button("Anterior", disabled=(pagina_actual == 1), use_container_width=True):
                st.session_state["pagina_actual"] -= 1; st.rerun()
        with p3:
            st.markdown(f"<p style='text-align:center; margin-top:8px; color:#555;'>Pagina <b>{pagina_actual}</b> de <b>{total_paginas}</b> &nbsp;|&nbsp; {total_filas} registros</p>", unsafe_allow_html=True)
        with p4:
            if st.button("Siguiente", disabled=(pagina_actual == total_paginas), use_container_width=True):
                st.session_state["pagina_actual"] += 1; st.rerun()
        with p5:
            if st.button("Ultima", disabled=(pagina_actual == total_paginas), use_container_width=True):
                st.session_state["pagina_actual"] = total_paginas; st.rerun()
    else:
        st.info("No hay registros en la base de datos. Agrega el primero usando el formulario.")
