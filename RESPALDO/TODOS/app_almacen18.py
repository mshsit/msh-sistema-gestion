import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, date
from fpdf import FPDF

# ══════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════
st.set_page_config(page_title="MSH-Hub | Almacén", layout="wide", page_icon="📦")

st.markdown("""
    <style>
    .kpi-title { font-size: 11px !important; font-weight: bold !important; color: #7A8B99 !important; text-align: center; margin-bottom: 5px; text-transform: uppercase; }
    .kpi-value { font-size: 24px !important; font-weight: bold !important; text-align: center; margin-top: -10px; }
    .card { background-color: white; padding: 12px; border-radius: 6px; box-shadow: 0px 1px 3px rgba(0,0,0,0.1); border: 1px solid #E2E8F0; }
    .user-info { background-color: #F0FFF4; border-left: 4px solid #38A169; padding: 8px 12px; border-radius: 4px; font-size: 13px; color: #276749; margin-bottom: 8px; }
    .panel-registrar { background-color: #FAFAFA; border: 1px solid #E2E8F0; padding: 20px; border-radius: 8px; }
    .panel-editar { background-color: #F7FAFC; border: 2px solid #3182CE; padding: 20px; border-radius: 8px; }
    .badge-prestado { background:#FFF3E0; color:#E65100; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:bold; }
    .badge-devuelto { background:#E8F5E9; color:#2E7D32; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:bold; }
    .badge-asignado { background:#E3F2FD; color:#1565C0; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:bold; }
    .badge-proceso  { background:#F3E5F5; color:#6A1B9A; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:bold; }
    .dias-activo    { color:#E53E3E; font-weight:bold; font-size:12px; }
    .dias-ok        { color:#38A169; font-size:12px; }
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
    """Calcula días entre fecha inicio y fin (o hoy si no hay fin)"""
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
            fecha_fin = None
            for fmt in formatos:
                try:
                    fecha_fin = datetime.strptime(str(fecha_fin_str).strip(), fmt).date()
                    break
                except:
                    continue
            if fecha_fin:
                dias = (fecha_fin - fecha_inicio).days
                return dias, "ok"
        
        if estado in estados_activos:
            dias = (date.today() - fecha_inicio).days
            return dias, "activo"
        
        return None, ""
    except:
        return None, ""

# ══════════════════════════════════════════════
# GENERADOR PDF
# ══════════════════════════════════════════════
def generar_pdf(df):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_margins(8, 8, 8)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 13)
    pdf.set_text_color(30, 52, 71)
    pdf.cell(0, 7, "MSH-HUB | SISTEMA DE CONTROL DE ALMACEN", ln=True, align='L')
    pdf.set_font("Arial", '', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Reporte: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Usuario: {st.session_state.get('nombre', '')}", ln=True, align='L')
    pdf.ln(3)
    widths   = [28, 22, 35, 42, 10, 28, 22, 22, 50, 12]
    columnas = ["Folio", "Fecha", "Responsable", "Articulo", "Cant", "Estado", "F.Inicio", "F.Devol.", "Observaciones", "Alerta"]
    pdf.set_font("Arial", 'B', 8)
    pdf.set_fill_color(30, 52, 71)
    pdf.set_text_color(255, 255, 255)
    for i, col in enumerate(columnas):
        pdf.cell(widths[i], 7, col, border=1, ln=0, align='C' if i in [4, 9] else 'L', fill=True)
    pdf.ln()
    for _, row in df.iterrows():
        en_alerta = str(row.get('alerta', 'NO')).upper().strip() == 'SI'
        if en_alerta:
            pdf.set_fill_color(254, 226, 226); pdf.set_text_color(153, 27, 27); fondo = True
        else:
            pdf.set_text_color(0, 0, 0); fondo = False
        def celda(texto, ancho, align='L'):
            t = str(texto) if texto else ""
            pdf.set_font("Arial", '', 5.5 if len(t) * (8 * 0.6) / 2.834 > (ancho - 1) else 7.5)
            pdf.cell(ancho, 6, t, 1, 0, align, fondo)
        celda(row.get('id', ''),              widths[0], 'L')
        celda(row.get('fecha', ''),            widths[1], 'C')
        celda(row.get('responsable', ''),      widths[2], 'L')
        celda(row.get('articulo', ''),         widths[3], 'L')
        celda(str(row.get('cantidad', 1)),     widths[4], 'C')
        celda(row.get('estado', ''),           widths[5], 'L')
        celda(row.get('fecha', ''),            widths[6], 'C')
        celda(row.get('fecha_devolucion', ''), widths[7], 'C')
        celda(row.get('observaciones', ''),    widths[8], 'L')
        pdf.set_font("Arial", '', 7.5)
        pdf.cell(widths[9], 6, "SI" if en_alerta else "NO", 1, 0, 'C', fondo)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1', errors='ignore')

# ══════════════════════════════════════════════
# DIÁLOGO DE ELIMINACIÓN
# ══════════════════════════════════════════════
@st.dialog("Confirmar Eliminación")
def ventana_confirmar_eliminar(id_a_eliminar):
    st.warning(f"¿Estás seguro de eliminar el registro **{id_a_eliminar}**? Esta acción no se puede deshacer.")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Cancelar", key=f"btn_cancel_del_{id_a_eliminar}", use_container_width=True):
            st.rerun()
    with c2:
        if st.button("Sí, Eliminar", type="primary", key=f"btn_confirm_del_{id_a_eliminar}", use_container_width=True):
            if eliminar_prestamo(id_a_eliminar):
                registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"ELIMINAR_PRESTAMO: {id_a_eliminar}")
                st.session_state["id_desde_tabla"] = ""
                st.rerun()

# ══════════════════════════════════════════════
# INICIALIZAR SESSION STATE
# ══════════════════════════════════════════════
if "autenticado"    not in st.session_state: st.session_state["autenticado"]    = False
if "id_desde_tabla" not in st.session_state: st.session_state["id_desde_tabla"] = ""
if "pagina_actual"  not in st.session_state: st.session_state["pagina_actual"]  = 1
if "filtro_estado"  not in st.session_state: st.session_state["filtro_estado"]  = "Todos"
if "form_key"       not in st.session_state: st.session_state["form_key"]       = 0

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
            usuario_input   = st.text_input("Usuario:", placeholder="tu.usuario")
            contrasena_input = st.text_input("Contraseña:", type="password")
            st.write("")
            if st.button("Ingresar", type="primary", use_container_width=True):
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
                        st.error("Usuario o contraseña incorrectos")
                else:
                    st.warning("Ingresa tu usuario y contraseña")

# ══════════════════════════════════════════════
# DASHBOARD PRINCIPAL
# ══════════════════════════════════════════════
else:
    usuario_actual = st.session_state["usuario"]
    nombre_actual  = st.session_state["nombre"]
    rol_actual     = st.session_state["rol"]
    es_admin       = rol_actual == "admin"

    # HEADER COMPACTO
    col_titulo, col_usuario = st.columns([6, 2])
    with col_titulo:
        st.markdown("<h3 style='color:#1E3447; font-family:sans-serif; margin-bottom:0px; margin-top:5px;'>📦 MSH-Hub | Control de Almacén</h3>", unsafe_allow_html=True)
    with col_usuario:
        st.markdown(f'<div class="user-info" style="margin-top:5px;">👤 <b>{nombre_actual}</b> | {rol_actual.upper()}</div>', unsafe_allow_html=True)
        if st.button("Cerrar Sesión", key="btn_logout", use_container_width=True):
            registrar_acceso(usuario_actual, nombre_actual, "LOGOUT")
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # CARGAR DATOS
    with st.spinner("Cargando datos..."):
        datos     = cargar_prestamos()
        df_master = pd.DataFrame(datos)

    if not df_master.empty and 'alerta' in df_master.columns:
        df_master['alerta'] = df_master['alerta'].apply(normalizar_alerta)

    # KPIs
    total_reg    = len(df_master)
    prestados    = len(df_master[df_master['estado'] == 'Prestado'])               if not df_master.empty else 0
    devueltos    = len(df_master[df_master['estado'] == 'Devuelto'])               if not df_master.empty else 0
    asignados    = len(df_master[df_master['estado'] == 'Asignado'])               if not df_master.empty else 0
    proceso_asig = len(df_master[df_master['estado'] == 'Proceso de asignacion'])  if not df_master.empty else 0
    alertas      = len(df_master[df_master['alerta'] == 'SI'])                     if not df_master.empty else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: st.markdown(f'<div class="card"><p class="kpi-title">TOTAL</p><p class="kpi-value" style="color:#2D3748;">{total_reg}</p></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="card"><p class="kpi-title">PRESTADOS</p><p class="kpi-value" style="color:#DD6B20;">{prestados}</p></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="card"><p class="kpi-title">DEVUELTOS</p><p class="kpi-value" style="color:#38A169;">{devueltos}</p></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="card"><p class="kpi-title">ASIGNADOS</p><p class="kpi-value" style="color:#3182CE;">{asignados}</p></div>', unsafe_allow_html=True)
    with c5: st.markdown(f'<div class="card"><p class="kpi-title">EN PROCESO</p><p class="kpi-value" style="color:#805AD5;">{proceso_asig}</p></div>', unsafe_allow_html=True)
    with c6: st.markdown(f'<div class="card"><p class="kpi-title">EN ALERTA</p><p class="kpi-value" style="color:#E53E3E;">{alertas}</p></div>', unsafe_allow_html=True)

    st.divider()

    # LAYOUT PRINCIPAL
    col_formulario, col_tabla = st.columns([1, 1.8], gap="large")

    # ── COLUMNA IZQUIERDA: FORMULARIO ────────────────────────────────────────
    with col_formulario:
        id_seleccionado = st.session_state.get("id_desde_tabla", "")
        modo_edicion    = id_seleccionado != "" and es_admin
        form_key        = st.session_state.get("form_key", 0)

        if modo_edicion:
            st.markdown("### ✏️ Modificar Registro")
            if id_seleccionado not in df_master['id'].values:
                st.session_state["id_desde_tabla"] = ""
                st.rerun()
            fila_actual = df_master[df_master['id'] == id_seleccionado].iloc[0]
            fecha_texto = str(fila_actual.get('fecha', ''))
            try:
                fecha_def = datetime.strptime(fecha_texto, '%d/%m/%Y')
            except:
                fecha_def = datetime.now()
        else:
            st.markdown("### 📝 Registrar Nuevo Préstamo")
            fecha_def = datetime.now()

        with st.container(border=True):
            if modo_edicion:
                st.info(f"✏️ Editando Folio: `{id_seleccionado}`")

            # FILA 1: Fecha + Responsable
            col_f1, col_f2 = st.columns([1, 1])
            with col_f1:
                fecha_input = st.date_input("Fecha *", value=fecha_def, format="DD/MM/YYYY", key=f"fecha_{form_key}_{id_seleccionado}")
            with col_f2:
                resp_val   = str(fila_actual.get('responsable', '')) if modo_edicion else ""
                resp_input = st.text_input("Responsable *", value=resp_val, placeholder="Nombre del trabajador", key=f"resp_{form_key}_{id_seleccionado}")

            # FILA 2: Artículo + Cantidad
            col_f3, col_f4 = st.columns([2, 1])
            with col_f3:
                art_val   = str(fila_actual.get('articulo', '')) if modo_edicion else ""
                art_input = st.text_input("Artículo / Herramienta *", value=art_val, placeholder="Nombre del artículo", key=f"art_{form_key}_{id_seleccionado}")
            with col_f4:
                cant_val   = str(fila_actual.get('cantidad', '1')) if modo_edicion else "1"
                cant_input = st.text_input("Cantidad *", value=cant_val, key=f"cant_{form_key}_{id_seleccionado}")

            # FILA 3: Estado + Alerta
            col_f5, col_f6 = st.columns([2, 1])
            with col_f5:
                estados_opciones = ["Prestado", "Devuelto", "Asignado", "Proceso de asignacion"]
                estado_actual_val = fila_actual.get('estado', 'Prestado') if modo_edicion else 'Prestado'
                estado_idx   = estados_opciones.index(estado_actual_val) if estado_actual_val in estados_opciones else 0
                estado_input = st.selectbox("Estado *", estados_opciones, index=estado_idx, key=f"est_{form_key}_{id_seleccionado}")
            with col_f6:
                alerta_val   = normalizar_alerta(fila_actual.get('alerta', 'NO')) if modo_edicion else "NO"
                alerta_idx   = 1 if alerta_val == "SI" else 0
                alerta_input = st.selectbox("Alerta", ["NO", "SI"], index=alerta_idx, key=f"alerta_{form_key}_{id_seleccionado}")

            # FILA 4: Fecha Devolución (solo si estado es Devuelto o Asignado)
            if estado_input in ["Devuelto", "Asignado"]:
                fdev_val = str(fila_actual.get('fecha_devolucion', '')) if modo_edicion else ""
                try:
                    fdev_def = datetime.strptime(fdev_val, '%d/%m/%Y') if fdev_val else datetime.now()
                except:
                    fdev_def = datetime.now()
                fecha_dev_input = st.date_input(
                    f"Fecha de {'Devolución' if estado_input == 'Devuelto' else 'Asignación'} *",
                    value=fdev_def, format="DD/MM/YYYY",
                    key=f"fdev_{form_key}_{id_seleccionado}"
                )
                fecha_dev_str = fecha_dev_input.strftime('%d/%m/%Y')
            else:
                fecha_dev_str = ""

            # FILA 5: Observaciones
            obs_val   = str(fila_actual.get('observaciones', '')) if modo_edicion else ""
            obs_input = st.text_input("Observaciones", value=obs_val, placeholder="Opcional", key=f"obs_{form_key}_{id_seleccionado}")

            # FILA 6: Nota Interna
            nota_val   = str(fila_actual.get('nota', '')) if modo_edicion else ""
            nota_input = st.text_input("Nota Interna", value=nota_val, placeholder="Notas de administración", key=f"nota_{form_key}_{id_seleccionado}")

            st.write("")

            # ── BOTONES ──────────────────────────────────────────────────────
            def validar_campos():
                errores = []
                if not resp_input.strip():
                    errores.append("El campo Responsable es obligatorio.")
                elif len(resp_input.strip()) < 3:
                    errores.append("El Responsable debe tener al menos 3 caracteres.")
                if not art_input.strip():
                    errores.append("El campo Artículo es obligatorio.")
                elif len(art_input.strip()) < 2:
                    errores.append("El Artículo debe tener al menos 2 caracteres.")
                if not cant_input.isdigit() or int(cant_input) <= 0:
                    errores.append("La Cantidad debe ser un número mayor a 0.")
                if fecha_input > datetime.now().date():
                    errores.append("La Fecha de préstamo no puede ser futura.")
                return errores

            if modo_edicion:
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("💾 Guardar Cambios", type="primary", use_container_width=True):
                        errores = validar_campos()
                        if errores:
                            for e in errores: st.error(e)
                        else:
                            payload_mod = {
                                "fecha": fecha_input.strftime('%d/%m/%Y'),
                                "responsable": resp_input.strip(),
                                "articulo": art_input.strip(),
                                "cantidad": int(cant_input),
                                "estado": estado_input,
                                "observaciones": obs_input.strip(),
                                "nota": nota_input.strip(),
                                "alerta": alerta_input,
                                "fecha_devolucion": fecha_dev_str
                            }
                            if modificar_prestamo(id_seleccionado, payload_mod):
                                registrar_acceso(usuario_actual, nombre_actual, f"MODIFICAR_PRESTAMO: {id_seleccionado}")
                                st.success("¡Cambios guardados!")
                                st.session_state["id_desde_tabla"] = ""
                                st.session_state["form_key"] = form_key + 1
                                st.rerun()
                            else:
                                st.error("Error al guardar. Intenta de nuevo.")
                with c_btn2:
                    if st.button("🗑️ Eliminar Registro", type="secondary", use_container_width=True):
                        ventana_confirmar_eliminar(id_seleccionado)

                if st.button("← Cancelar y Crear Nuevo", use_container_width=True):
                    st.session_state["id_desde_tabla"] = ""
                    st.session_state["form_key"] = form_key + 1
                    st.rerun()
            else:
                if es_admin:
                    if st.button("✅ Registrar Entrada/Salida", type="primary", use_container_width=True):
                        errores = validar_campos()
                        if errores:
                            for e in errores: st.error(e)
                        else:
                            payload_nuevo = {
                                "id": f"ID-{int(datetime.now().timestamp())}",
                                "fecha": fecha_input.strftime('%d/%m/%Y'),
                                "responsable": resp_input.strip(),
                                "articulo": art_input.strip(),
                                "cantidad": int(cant_input),
                                "estado": estado_input,
                                "observaciones": obs_input.strip(),
                                "nota": nota_input.strip(),
                                "alerta": alerta_input,
                                "fecha_devolucion": fecha_dev_str
                            }
                            if agregar_prestamo(payload_nuevo):
                                registrar_acceso(usuario_actual, nombre_actual, f"AGREGAR_PRESTAMO: {payload_nuevo['id']}")
                                st.success("¡Registro guardado con éxito!")
                                # LIMPIAR formulario incrementando form_key
                                st.session_state["form_key"] = form_key + 1
                                st.rerun()
                            else:
                                st.error("Error al guardar. Intenta de nuevo.")
                else:
                    st.warning("Tu rol sólo permite visualización.")

    # ── COLUMNA DERECHA: HISTORIAL ───────────────────────────────────────────
    with col_tabla:
        st.markdown("### 📋 Historial de Préstamos")

        # ACCIONES + BUSCADOR
        acc1, acc2, acc3 = st.columns([1.5, 1.5, 4])
        with acc1:
            if not df_master.empty:
                st.download_button("📥 CSV", data=df_master.to_csv(index=False).encode('utf-8'),
                                   file_name="almacen_prestamos.csv", mime="text/csv", use_container_width=True)
        with acc2:
            if not df_master.empty:
                st.download_button("📕 PDF", data=generar_pdf(df_master),
                                   file_name="reporte_almacen.pdf", mime="application/pdf", use_container_width=True)
        with acc3:
            busqueda_global = st.text_input("Buscador", placeholder="🔍  Busca por trabajador, artículo o folio...", label_visibility="collapsed")

        # FILTRO POR ESTADO
        estados_filtro = ["Todos", "Prestado", "Devuelto", "Asignado", "Proceso de asignacion", "🚨 En Alerta"]
        filtro_sel = st.radio("Filtrar por:", estados_filtro, horizontal=True, key="filtro_estado_radio", label_visibility="collapsed")

        # APLICAR FILTROS
        if not df_master.empty:
            df_filtrado = df_master.copy()

            # Filtro por búsqueda
            if busqueda_global.strip():
                df_filtrado = df_filtrado[
                    df_filtrado['responsable'].str.contains(busqueda_global, case=False, na=False) |
                    df_filtrado['articulo'].str.contains(busqueda_global, case=False, na=False) |
                    df_filtrado['id'].str.contains(busqueda_global, case=False, na=False)
                ]

            # Filtro por estado
            if filtro_sel == "🚨 En Alerta":
                df_filtrado = df_filtrado[df_filtrado['alerta'] == 'SI']
            elif filtro_sel != "Todos":
                df_filtrado = df_filtrado[df_filtrado['estado'] == filtro_sel]

            df_filtrado = df_filtrado.copy()
        else:
            df_filtrado = pd.DataFrame()

        # TABLA
        if not df_filtrado.empty:
            if es_admin:
                st.markdown("<p style='font-size:11px; color:#7A8B99; margin-bottom:4px;'>Haz clic en <b>✏️</b> para editar el registro en el formulario.</p>", unsafe_allow_html=True)

            # PAGINACIÓN
            FILAS_POR_PAGINA = 15
            total_filas   = len(df_filtrado)
            total_paginas = max(1, -(-total_filas // FILAS_POR_PAGINA))

            if busqueda_global != st.session_state.get("ultima_busqueda", "") or filtro_sel != st.session_state.get("ultimo_filtro", ""):
                st.session_state["pagina_actual"]  = 1
                st.session_state["ultima_busqueda"] = busqueda_global
                st.session_state["ultimo_filtro"]   = filtro_sel

            pagina_actual = st.session_state["pagina_actual"]
            inicio    = (pagina_actual - 1) * FILAS_POR_PAGINA
            fin       = inicio + FILAS_POR_PAGINA
            df_pagina = df_filtrado.iloc[inicio:fin]

            # ENCABEZADOS
            cols_w = [1.2, 2, 2.2, 2, 0.7, 1.8, 1.5, 0.5] if es_admin else [1.2, 2, 2.2, 2, 0.7, 1.8, 1.5]
            headers = ["Fecha", "Responsable", "Artículo", "Estado", "Cant.", "Días", "Alerta", ""] if es_admin else ["Fecha", "Responsable", "Artículo", "Estado", "Cant.", "Días", "Alerta"]
            h_cols  = st.columns(cols_w)
            for col, txt in zip(h_cols, headers):
                col.markdown(f"<p style='font-size:11px; font-weight:bold; color:#4A5568; border-bottom:2px solid #CBD5E0; padding-bottom:3px; margin:0;'>{txt}</p>", unsafe_allow_html=True)

            # FILAS
            for _, row in df_pagina.iterrows():
                en_alerta    = str(row.get('alerta', 'NO')).upper() == 'SI'
                es_seleccion = row.get('id') == id_seleccionado

                if en_alerta:
                    bg, color = "#FEE2E2", "#991B1B"
                elif es_seleccion:
                    bg, color = "#EBF8FF", "#2B6CB0"
                else:
                    bg, color = "white", "#2D3748"

                s = f"background-color:{bg}; color:{color}; font-size:12px; padding:5px 4px; border-radius:3px; margin-bottom:2px; border-bottom:1px solid #EDF2F7; overflow:hidden; white-space:nowrap; text-overflow:ellipsis;"

                # Calcular días
                dias, tipo_dias = calcular_dias(
                    row.get('fecha', ''),
                    row.get('fecha_devolucion', ''),
                    row.get('estado', '')
                )
                if dias is not None:
                    if tipo_dias == "activo":
                        dias_html = f"<span class='dias-activo'>⏱ {dias}d</span>"
                    else:
                        dias_html = f"<span class='dias-ok'>✓ {dias}d</span>"
                else:
                    dias_html = "<span style='color:#CBD5E0;'>—</span>"

                # Badge de estado
                estado_val = row.get('estado', '')
                if estado_val == "Prestado":
                    estado_html = f"<span class='badge-prestado'>{estado_val}</span>"
                elif estado_val == "Devuelto":
                    estado_html = f"<span class='badge-devuelto'>{estado_val}</span>"
                elif estado_val == "Asignado":
                    estado_html = f"<span class='badge-asignado'>{estado_val}</span>"
                else:
                    estado_html = f"<span class='badge-proceso'>{estado_val}</span>"

                alerta_html = "🚨" if en_alerta else "<span style='color:#CBD5E0;'>—</span>"

                r_cols = st.columns(cols_w)
                r_cols[0].markdown(f"<div style='{s}'>{row.get('fecha','')}</div>", unsafe_allow_html=True)
                r_cols[1].markdown(f"<div style='{s}'><b>{row.get('responsable','')}</b></div>", unsafe_allow_html=True)
                r_cols[2].markdown(f"<div style='{s}'>{row.get('articulo','')}</div>", unsafe_allow_html=True)
                r_cols[3].markdown(f"<div style='{s}'>{estado_html}</div>", unsafe_allow_html=True)
                r_cols[4].markdown(f"<div style='{s}; text-align:center;'>{row.get('cantidad',1)}</div>", unsafe_allow_html=True)
                r_cols[5].markdown(f"<div style='{s}'>{dias_html}</div>", unsafe_allow_html=True)
                r_cols[6].markdown(f"<div style='{s}; text-align:center;'>{alerta_html}</div>", unsafe_allow_html=True)

                if es_admin:
                    with r_cols[7]:
                        if st.button("✏️", key=f"sel_{row['id']}", help=f"Editar {row['id']}", use_container_width=True):
                            st.session_state["id_desde_tabla"] = row['id']
                            st.rerun()

            # CONTROLES PAGINACIÓN
            st.write("")
            p1, p2, p3, p4, p5 = st.columns([1, 1, 3, 1, 1])
            with p1:
                if st.button("⏮ Primera", disabled=(pagina_actual == 1), use_container_width=True):
                    st.session_state["pagina_actual"] = 1; st.rerun()
            with p2:
                if st.button("◀ Anterior", disabled=(pagina_actual == 1), use_container_width=True):
                    st.session_state["pagina_actual"] -= 1; st.rerun()
            with p3:
                st.markdown(f"<p style='text-align:center; margin-top:5px; color:#7A8B99; font-size:12px;'>Página <b>{pagina_actual}</b> de <b>{total_paginas}</b> | <b>{total_filas}</b> registros</p>", unsafe_allow_html=True)
            with p4:
                if st.button("Siguiente ▶", disabled=(pagina_actual == total_paginas), use_container_width=True):
                    st.session_state["pagina_actual"] += 1; st.rerun()
            with p5:
                if st.button("Última ⏭", disabled=(pagina_actual == total_paginas), use_container_width=True):
                    st.session_state["pagina_actual"] = total_paginas; st.rerun()

        else:
            # MENSAJE CUANDO NO HAY RESULTADOS
            if busqueda_global.strip() or filtro_sel != "Todos":
                st.markdown("""
                    <div style='text-align:center; padding:40px; color:#7A8B99;'>
                        <p style='font-size:32px; margin-bottom:8px;'>🔍</p>
                        <p style='font-size:16px; font-weight:bold;'>Sin resultados</p>
                        <p style='font-size:13px;'>No se encontraron registros con ese criterio de búsqueda.</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style='text-align:center; padding:40px; color:#7A8B99;'>
                        <p style='font-size:32px; margin-bottom:8px;'>📦</p>
                        <p style='font-size:16px; font-weight:bold;'>Sin registros</p>
                        <p style='font-size:13px;'>Agrega el primer préstamo usando el formulario.</p>
                    </div>
                """, unsafe_allow_html=True)
