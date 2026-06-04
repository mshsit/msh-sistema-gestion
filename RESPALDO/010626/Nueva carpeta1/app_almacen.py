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
    .user-info { background-color: #F0FFF4; border-left: 4px solid #38A169; padding: 8px 12px; border-radius: 4px; font-size: 13px; color: #276749; margin-bottom: 8px; }
    
    /* Estilos para los paneles del formulario */
    .panel-registrar { background-color: #FAFAFA; border: 1px solid #E2E8F0; padding: 20px; border-radius: 8px; }
    .panel-editar { background-color: #F7FAFC; border: 2px solid #3182CE; padding: 20px; border-radius: 8px; }
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
# DIÁLOGO DE ELIMINACIÓN
# ══════════════════════════════════════════════
@st.dialog("Confirmar Eliminación")
def ventana_confirmar_eliminar(id_a_eliminar):
    st.warning(f"¿Estás seguro de eliminar el registro {id_a_eliminar}? Esta acción no se puede deshacer.")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Cancelar", key=f"btn_cancel_del_{id_a_eliminar}", use_container_width=True):
            st.rerun()
    with c2:
        if st.button("Sí, Eliminar", type="primary", key=f"btn_confirm_del_{id_a_eliminar}", use_container_width=True):
            if eliminar_prestamo(id_a_eliminar):
                registrar_acceso(
                    st.session_state["usuario"],
                    st.session_state["nombre"],
                    f"ELIMINAR_PRESTAMO: {id_a_eliminar}"
                )
                # Reseteamos variables para volver a modo Registro
                st.session_state["id_desde_tabla"] = ""
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
# DASHBOARD PRINCIPAL (PANTALLA ÚNICA)
# ══════════════════════════════════════════════
else:
    usuario_actual = st.session_state["usuario"]
    nombre_actual  = st.session_state["nombre"]
    rol_actual     = st.session_state["rol"]
    es_admin       = rol_actual == "admin"

    # HEADER
    col_titulo, col_usuario = st.columns([6, 2])
    with col_titulo:
        st.markdown("<h1 style='color:#1E3447; font-family:sans-serif; margin-bottom:5px;'>📦 MSH-Hub | Control de Almacén</h1>", unsafe_allow_html=True)
    with col_usuario:
        st.markdown(f'<div class="user-info">👤 <b>{nombre_actual}</b> | Rol: {rol_actual.upper()}</div>', unsafe_allow_html=True)
        if st.button("Cerrar Sesión", key="btn_logout"):
            registrar_acceso(usuario_actual, nombre_actual, "LOGOUT")
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # CARGAR DATOS GENERALES
    datos = cargar_prestamos()
    df_master = pd.DataFrame(datos)

    if not df_master.empty and 'alerta' in df_master.columns:
        df_master['alerta'] = df_master['alerta'].apply(normalizar_alerta)

    # INDICADORES (KPIs)
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

    st.divider()

    # ══════════════════════════════════════════════
    # DISTRIBUCIÓN EN COLUMNAS (DISEÑO UX MEJORADO)
    # ══════════════════════════════════════════════
    col_formulario, col_tabla = st.columns([1, 1.8], gap="large")

    # ────────────────────────────────────────────────────────
    # COLUMNA IZQUIERDA: FORMULARIO DINÁMICO (REGISTRO / EDICIÓN)
    # ────────────────────────────────────────────────────────
    with col_formulario:
        id_seleccionado = st.session_state.get("id_desde_tabla", "")
        modo_edicion = id_seleccionado != "" and es_admin
        
        if modo_edicion:
            st.markdown("### ✏️ Modificar Registro")
            fila_actual = df_master[df_master['id'] == id_seleccionado].iloc[0]
            fecha_texto = str(fila_actual.get('fecha', ''))
            try:
                fecha_def = datetime.strptime(fecha_texto, '%d/%m/%Y')
            except:
                fecha_def = datetime.now()
        else:
            st.markdown("### 📝 Registrar Nuevo Préstamo")
            fecha_def = datetime.now()

        # Contenedor visual del Formulario único
        with st.container(border=True):
            if modo_edicion:
                st.info(f"Editando Folio: `{id_seleccionado}`")

            fecha_input = st.date_input("Fecha", value=fecha_def, format="DD/MM/YYYY")
            
            resp_val = str(fila_actual.get('responsable', '')) if modo_edicion else ""
            resp_input = st.text_input("Responsable *", value=resp_val, placeholder="Nombre del trabajador")
            
            art_val = str(fila_actual.get('articulo', '')) if modo_edicion else ""
            art_input = st.text_input("Artículo / Herramienta *", value=art_val, placeholder="Nombre del artículo")
            
            cant_val = str(fila_actual.get('cantidad', '1')) if modo_edicion else "1"
            cant_input = st.text_input("Cantidad", value=cant_val)
            
            estados_opciones = ["Prestado", "Devuelto", "Asignado", "Proceso de asignacion"]
            estado_idx = estados_opciones.index(fila_actual.get('estado', 'Prestado')) if modo_edicion and fila_actual.get('estado') in estados_opciones else 0
            estado_input = st.selectbox("Estado", estados_opciones, index=estado_idx)
            
            obs_val = str(fila_actual.get('observaciones', '')) if modo_edicion else ""
            obs_input = st.text_input("Observaciones", value=obs_val, placeholder="Opcional")
            
            nota_val = str(fila_actual.get('nota', '')) if modo_edicion else ""
            nota_input = st.text_input("Nota Interna", value=nota_val, placeholder="Notas de administración")
            
            alerta_val = normalizar_alerta(fila_actual.get('alerta', 'NO')) if modo_edicion else "NO"
            alerta_idx = 1 if alerta_val == "SI" else 0
            alerta_input = st.selectbox("¿Activar Alerta?", ["NO", "SI"], index=alerta_idx)

            st.write("")
            
            # --- INTERRUPTOR DE BOTONES SEGÚN EL MODO ---
            if modo_edicion:
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("Guardar Cambios", type="primary", use_container_width=True):
                        if resp_input.strip() and art_input.strip():
                            payload_mod = {
                                "fecha": fecha_input.strftime('%d/%m/%Y'),
                                "responsable": resp_input.strip(),
                                "articulo": art_input.strip(),
                                "cantidad": int(cant_input) if cant_input.isdigit() else 1,
                                "estado": estado_input,
                                "observaciones": obs_input.strip(),
                                "nota": nota_input.strip(),
                                "alerta": alerta_input
                            }
                            if modificar_prestamo(id_seleccionado, payload_mod):
                                registrar_acceso(usuario_actual, nombre_actual, f"MODIFICAR_PRESTAMO: {id_seleccionado}")
                                st.success("¡Cambios guardados!")
                                st.session_state["id_desde_tabla"] = ""
                                st.rerun()
                        else:
                            st.error("Campos obligatorios vacíos.")
                
                with c_btn2:
                    if st.button("Eliminar Registro", type="secondary", use_container_width=True):
                        ventana_confirmar_eliminar(id_seleccionado)
                
                if st.button("← Cancelar y Crear Nuevo", use_container_width=True):
                    st.session_state["id_desde_tabla"] = ""
                    st.rerun()
            else:
                if es_admin:
                    if st.button("Registrar Entrada/Salida", type="primary", use_container_width=True):
                        if resp_input.strip() and art_input.strip():
                            payload_nuevo = {
                                "id": f"ID-{int(datetime.now().timestamp())}",
                                "fecha": fecha_input.strftime('%d/%m/%Y'),
                                "responsable": resp_input.strip(),
                                "articulo": art_input.strip(),
                                "cantidad": int(cant_input) if cant_input.isdigit() else 1,
                                "estado": estado_input,
                                "observaciones": obs_input.strip(),
                                "nota": nota_input.strip(),
                                "alerta": alerta_input
                            }
                            if agregar_prestamo(payload_nuevo):
                                registrar_acceso(usuario_actual, nombre_actual, f"AGREGAR_PRESTAMO: {payload_nuevo['id']}")
                                st.success("¡Registro guardado con éxito!")
                                st.rerun()
                        else:
                            st.warning("Completa los campos obligatorios (*)")
                else:
                    st.warning("Tu rol sólo permite visualización.")

    # ────────────────────────────────────────────────────────
    # COLUMNA DERECHA: CENTRO DE CONTROL (ÚNICO BUSCADOR Y HISTORIAL)
    # ────────────────────────────────────────────────────────
    with col_tabla:
        st.markdown("### 🔍 Historial e Inventario General")
        
        acc1, acc2, acc3 = st.columns([1.5, 1.5, 4])
        with acc1:
            if not df_master.empty:
                st.download_button("Exportar CSV", data=df_master.to_csv(index=False).encode('utf-8'),
                                   file_name="almacen_prestamos.csv", mime="text/csv", use_container_width=True)
        with acc2:
            if not df_master.empty:
                st.download_button("Generar PDF", data=generar_pdf(df_master),
                                   file_name="reporte_almacen.pdf", mime="application/pdf", use_container_width=True)
        with acc3:
            # EL ÚNICO BUSCADOR GLOBAL DE LA APLICACIÓN
            busqueda_global = st.text_input("Buscador", placeholder="Busca por trabajador, artículo o folio...", label_visibility="collapsed")

        if not df_master.empty:
            df_filtrado = df_master[
                df_master['responsable'].str.contains(busqueda_global, case=False, na=False) |
                df_master['articulo'].str.contains(busqueda_global, case=False, na=False) |
                df_master['id'].str.contains(busqueda_global, case=False, na=False)
            ].copy()
        else:
            df_filtrado = pd.DataFrame()

        if not df_filtrado.empty:
            st.markdown("<p style='font-size:12px; color:#7A8B99; margin-bottom:5px;'>Haz clic en el botón <b>✏️</b> de cualquier fila para cargarla y editarla a la izquierda.</p>", unsafe_allow_html=True)
            
            # Encabezado simulado de la tabla dinámica
            h1, h2, h3, h4, h5, h6 = st.columns([1.2, 1.8, 2.5, 2.5, 2, 0.6])
            for col, txt in zip([h1, h2, h3, h4, h5, h6], ["Fecha", "Folio", "Responsable", "Artículo", "Estado", ""]):
                col.markdown(f"<p style='font-size:12px; font-weight:bold; color:#4A5568; border-bottom:1px solid #E2E8F0; padding-bottom:3px; margin:0;'>{txt}</p>", unsafe_allow_html=True)

            # PAGINACIÓN
            FILAS_POR_PAGINA = 15
            total_filas = len(df_filtrado)
            total_paginas = max(1, -(-total_filas // FILAS_POR_PAGINA))

            if busqueda_global != st.session_state.get("ultima_busqueda", ""):
                st.session_state["pagina_actual"] = 1
                st.session_state["ultima_busqueda"] = busqueda_global

            pagina_actual = st.session_state["pagina_actual"]
            inicio = (pagina_actual - 1) * FILAS_POR_PAGINA
            fin = inicio + FILAS_POR_PAGINA
            df_pagina = df_filtrado.iloc[inicio:fin]

            # Renderizado de filas dinámicas con soporte visual de alertas y selección
            for _, row in df_pagina.iterrows():
                en_alerta = str(row.get('alerta', 'NO')).upper() == 'SI'
                
                if en_alerta:
                    bg_color = "#FEE2E2"
                    text_color = "#991B1B"
                elif row.get('id') == id_seleccionado:
                    bg_color = "#EBF8FF"
                    text_color = "#2B6CB0"
                else:
                    bg_color = "#F9FAFB"
                    text_color = "#2D3748"

                estilo_celda = f"background-color:{bg_color}; color:{text_color}; font-size:13px; padding:6px; border-radius:4px; margin-bottom:2px; height:32px; overflow:hidden; white-space:nowrap; text-overflow:ellipsis;"

                c_fec, c_fol, c_res, c_art, c_est, c_acc = st.columns([1.2, 1.8, 2.5, 2.5, 2, 0.6])
                c_fec.markdown(f"<div style='{estilo_celda}'>{row.get('fecha','')}</div>", unsafe_allow_html=True)
                c_fol.markdown(f"<div style='{estilo_celda}'>`{str(row.get('id',''))[:12]}`</div>", unsafe_allow_html=True)
                c_res.markdown(f"<div style='{estilo_celda}'><b>{row.get('responsable','')}</b></div>", unsafe_allow_html=True)
                c_art.markdown(f"<div style='{estilo_celda}'>{row.get('articulo','')} ({row.get('cantidad',1)})</div>", unsafe_allow_html=True)
                c_est.markdown(f"<div style='{estilo_celda}'>{row.get('estado','')}</div>", unsafe_allow_html=True)
                
                with c_acc:
                    if st.button("✏️", key=f"sel_prod_{row['id']}", help="Editar este registro", use_container_width=True):
                        st.session_state["id_desde_tabla"] = row['id']
                        st.rerun()

            # CONTROLES DE PAGINACIÓN
            st.write("")
            p1, p2, p3, p4, p5 = st.columns([1, 1, 3, 1, 1])
            with p1:
                if st.button("Subir ⏮️", disabled=(pagina_actual == 1), use_container_width=True):
                    st.session_state["pagina_actual"] = 1; st.rerun()
            with p2:
                if st.button("◀️ Ant.", disabled=(pagina_actual == 1), use_container_width=True):
                    st.session_state["pagina_actual"] -= 1; st.rerun()
            with p3:
                st.markdown(f"<p style='text-align:center; margin-top:5px; color:#7A8B99; font-size:13px;'>Página <b>{pagina_actual}</b> de <b>{total_paginas}</b> | <b>{total_filas}</b> registros</p>", unsafe_allow_html=True)
            with p4:
                if st.button("Sig. ▶️", disabled=(pagina_actual == total_paginas), use_container_width=True):
                    st.session_state["pagina_actual"] += 1; st.rerun()
            with p5:
                if st.button("Final ⏭️", disabled=(pagina_actual == total_paginas), use_container_width=True):
                    st.session_state["pagina_actual"] = total_paginas; st.rerun()
        else:
            st.info("No se encontraron registros en el historial.")