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
            "usuario": usuario, "nombre": nombre, "accion": accion, "fecha_hora": datetime.now().isoformat()
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
    pdf.ln(4)
    widths   = [35, 25, 45, 50, 15, 35, 65, 15]
    columnas = ["Folio", "Fecha", "Responsable", "Articulo", "Cant", "Estado", "Observaciones", "Alerta"]
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(30, 52, 71); pdf.set_text_color(255, 255, 255)
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
            pdf.set_font("Arial", '', 8)
            pdf.cell(ancho, 7, t, 1, 0, align, fondo)
        celda(row.get('id', ''),           widths[0], 'L')
        celda(row.get('fecha', ''),         widths[1], 'C')
        celda(row.get('responsable', ''),   widths[2], 'L')
        celda(row.get('articulo', ''),      widths[3], 'L')
        celda(str(row.get('cantidad', 1)),  widths[4], 'C')
        celda(row.get('estado', ''),        widths[5], 'L')
        celda(row.get('observaciones', ''), widths[6], 'L')
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
                registrar_acceso(st.session_state["usuario"], st.session_state["nombre"], f"ELIMINAR_PRESTAMO: {id_a_eliminar}")
                st.session_state["id_desde_tabla"] = ""
                st.rerun()

# ══════════════════════════════════════════════
# INICIALIZAR STATE
# ══════════════════════════════════════════════
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if "id_desde_tabla" not in st.session_state: st.session_state["id_desde_tabla"] = ""
if "pagina_actual" not in st.session_state: st.session_state["pagina_actual"] = 1
if "form_reset_counter" not in st.session_state: st.session_state["form_reset_counter"] = 0
if "ejecutar_scroll" not in st.session_state: st.session_state["ejecutar_scroll"] = False

# ══════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════
if not st.session_state["autenticado"]:
    st.markdown("<div style='text-align:center; margin-top:60px;'><h1>MSH-Hub</h1><p>Mendoza Servicios y Herramientas</p></div>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 1.2, 1])
    with col_center:
        with st.container(border=True):
            st.markdown("### Acceso al Sistema")
            usuario_input = st.text_input("Usuario:")
            contrasena_input = st.text_input("Contraseña:", type="password")
            if st.button("Ingresar", type="primary", use_container_width=True):
                user_data = verificar_usuario(usuario_input.strip(), contrasena_input.strip())
                if user_data:
                    st.session_state.update({"autenticado": True, "usuario": user_data["usuario"], "nombre": user_data["nombre"], "rol": user_data["rol"]})
                    st.rerun()
                else: st.error("Credenciales incorrectas")
else:
    usuario_actual, nombre_actual, rol_actual = st.session_state["usuario"], st.session_state["nombre"], st.session_state["rol"]
    es_admin = rol_actual == "admin"

    # HEADER COMPACTO
    col_titulo, col_usuario = st.columns([6, 2])
    with col_titulo:
        st.markdown("<h3 style='color:#1E3447; margin-top:5px;'>📦 MSH-Hub | Control de Almacén</h3>", unsafe_allow_html=True)
    with col_usuario:
        st.markdown(f'<div class="user-info">👤 <b>{nombre_actual}</b> | {rol_actual.upper()}</div>', unsafe_allow_html=True)
        if st.button("Cerrar Sesión", use_container_width=True):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

    datos = cargar_prestamos()
    df_master = pd.DataFrame(datos)
    if not df_master.empty and 'alerta' in df_master.columns:
        df_master['alerta'] = df_master['alerta'].apply(normalizar_alerta)

    # 📊 INDICADORES (KPIs)
    total_reg = len(df_master)
    prestados = len(df_master[df_master['estado'] == 'Prestado']) if not df_master.empty else 0
    devueltos = len(df_master[df_master['estado'] == 'Devuelto']) if not df_master.empty else 0
    asignados = len(df_master[df_master['estado'] == 'Asignado']) if not df_master.empty else 0
    proceso_asig = len(df_master[df_master['estado'] == 'Proceso de asignacion']) if not df_master.empty else 0
    alertas = len(df_master[df_master['alerta'] == 'SI']) if not df_master.empty else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: st.markdown(f'<div class="card"><p class="kpi-title">TOTAL</p><p class="kpi-value">{total_reg}</p></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="card"><p class="kpi-title">PRESTADOS</p><p class="kpi-value" style="color:#DD6B20;">{prestados}</p></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="card"><p class="kpi-title">DEVUELTOS</p><p class="kpi-value" style="color:#38A169;">{devueltos}</p></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="card"><p class="kpi-title">ASIGNADOS</p><p class="kpi-value" style="color:#3182CE;">{asignados}</p></div>', unsafe_allow_html=True)
    with c5: st.markdown(f'<div class="card"><p class="kpi-title">EN PROCESO</p><p class="kpi-value" style="color:#805AD5;">{proceso_asig}</p></div>', unsafe_allow_html=True)
    with c6: st.markdown(f'<div class="card"><p class="kpi-title">EN ALERTA</p><p class="kpi-value" style="color:#E53E3E;">{alertas}</p></div>', unsafe_allow_html=True)

    st.write("")

    # ══════════════════════════════════════════════
    # FORMULARIO EN LA PARTE DE ARRIBA
    # ══════════════════════════════════════════════
    id_seleccionado = st.session_state.get("id_desde_tabla", "")
    modo_edicion = id_seleccionado != "" and es_admin

    llave_formulario = f"{id_seleccionado}_{st.session_state['form_reset_counter']}"

    if modo_edicion and not df_master.empty:
        fila_actual = df_master[df_master['id'] == id_seleccionado].iloc[0]
        try: fecha_def = datetime.strptime(str(fila_actual.get('fecha', '')), '%d/%m/%Y')
        except: fecha_def = datetime.now()
    else:
        fila_actual = {}
        fecha_def = datetime.now()

    # 📍 DEFINIMOS EL IDENTIFICADOR HTML AQUÍ EN EL TÍTULO (id="formulario-top")
    st.markdown(f'<div id="formulario-top"></div>', unsafe_allow_html=True)
    st.markdown(f"#### {'✏️ Modificar Registro Seleccionado' if modo_edicion else '📝 Registrar Nuevo Préstamo / Movimiento'}")
    
    # 💥 Script JS que hace el scroll automático al formulario de arriba de manera fluida si está activado
    if st.session_state["ejecutar_scroll"]:
        st.components.v1.html("""
            <script>
                window.parent.document.getElementById('formulario-top').scrollIntoView({behavior: 'smooth'});
            </script>
        """, height=0)
        st.session_state["ejecutar_scroll"] = False # Apagar después de ejecutar

    with st.container(border=True):
        if modo_edicion:
            st.info(f"✏️ Cargado Folio para Editar: `{id_seleccionado}`")

        col_form_est, col_form_fec, col_form_resp = st.columns([1, 1, 2])
        with col_form_est:
            estados_opciones = ["Prestado", "Devuelto", "Asignado", "Proceso de asignacion"]
            estado_idx = estados_opciones.index(fila_actual.get('estado', 'Prestado')) if modo_edicion and fila_actual.get('estado') in estados_opciones else 0
            estado_input = st.selectbox("Estado del Registro", estados_opciones, index=estado_idx, key=f"est_{llave_formulario}")
        
        with col_form_fec:
            if estado_input == "Devuelto":
                etiqueta_fecha = "Fecha de Devolución"
            elif estado_input == "Asignado":
                etiqueta_fecha = "Fecha de Asignación"
            elif estado_input == "Proceso de asignacion":
                etiqueta_fecha = "Fecha de Inicio de Proceso"
            else:
                etiqueta_fecha = "Fecha de Préstamo"
                
            fecha_input = st.date_input(etiqueta_fecha, value=fecha_def, format="DD/MM/YYYY", key=f"fec_{llave_formulario}")
            
        with col_form_resp:
            resp_val = str(fila_actual.get('responsable', '')) if modo_edicion else ""
            resp_input = st.text_input("Responsable *", value=resp_val, placeholder="Nombre del trabajador", key=f"resp_{llave_formulario}")

        col_form_art, col_form_cant, col_form_ale = st.columns([2, 1, 1])
        with col_form_art:
            art_val = str(fila_actual.get('articulo', '')) if modo_edicion else ""
            art_input = st.text_input("Artículo / Herramienta *", value=art_val, placeholder="Nombre de la herramienta", key=f"art_{llave_formulario}")
        with col_form_cant:
            cant_val = str(fila_actual.get('cantidad', '1')) if modo_edicion else "1"
            cant_input = st.text_input("Cantidad", value=cant_val, key=f"cant_{llave_formulario}")
        with col_form_ale:
            alerta_val = normalizar_alerta(fila_actual.get('alerta', 'NO')) if modo_edicion else "NO"
            alerta_input = st.selectbox("Alerta", ["NO", "SI"], index=(1 if alerta_val == "SI" else 0), key=f"ale_{llave_formulario}")

        col_form_obs, col_form_not = st.columns([1, 1])
        with col_form_obs:
            obs_val = str(fila_actual.get('observaciones', '')) if modo_edicion else ""
            obs_input = st.text_input("Observaciones (Público)", value=obs_val, placeholder="Detalles visibles", key=f"obs_{llave_formulario}")
        with col_form_not:
            nota_val = str(fila_actual.get('nota', '')) if modo_edicion else ""
            nota_input = st.text_input("Nota Interna (Admin)", value=nota_val, placeholder="Notas internas privadas", key=f"not_{llave_formulario}")

        # Botones de Acción
        st.write("")
        col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
        with col_btn1:
            if modo_edicion:
                if st.button("💾 Guardar Cambios Actuales", type="primary", use_container_width=True):
                    if resp_input.strip() and art_input.strip() and cant_input.isdigit():
                        payload_mod = {
                            "fecha": fecha_input.strftime('%d/%m/%Y'), "responsable": resp_input.strip(),
                            "articulo": art_input.strip(), "cantidad": int(cant_input), "estado": estado_input,
                            "observaciones": obs_input.strip(), "nota": nota_input.strip(), "alerta": alerta_input
                        }
                        if modificar_prestamo(id_seleccionado, payload_mod):
                            st.session_state["id_desde_tabla"] = ""
                            st.rerun()
                    else:
                        st.error("Por favor completa de forma válida los campos (*)")
            else:
                if st.button("➕ Registrar Entrada/Salida en Almacén", type="primary", use_container_width=True, disabled=not es_admin):
                    if not resp_input.strip() or not art_input.strip() or not cant_input.isdigit():
                        st.error("Por favor completa los campos requeridos (*)")
                    else:
                        payload_nuevo = {
                            "id": f"ID-{int(datetime.now().timestamp())}", "fecha": fecha_input.strftime('%d/%m/%Y'),
                            "responsable": resp_input.strip(), "articulo": art_input.strip(), "cantidad": int(cant_input),
                            "estado": estado_input, "observaciones": obs_input.strip(), "nota": nota_input.strip(), "alerta": alerta_input
                        }
                        if agregar_prestamo(payload_nuevo):
                            st.session_state["form_reset_counter"] += 1  # Limpieza automática
                            st.rerun()
        with col_btn2:
            if modo_edicion and st.button("🗑️ Eliminar Registro", type="secondary", use_container_width=True):
                ventana_confirmar_eliminar(id_seleccionado)
        with col_btn3:
            if modo_edicion and st.button("❌ Cancelar Edición", use_container_width=True):
                st.session_state["id_desde_tabla"] = ""
                st.rerun()

    st.divider()

    # ══════════════════════════════════════════════
    # HISTORIAL EN LA PARTE DE ABAJO
    # ══════════════════════════════════════════════
    st.markdown("### 🔍 Historial e Inventario General")
    
    col_acc1, col_acc2, col_acc3, col_acc4 = st.columns([1, 1, 2, 4])
    with col_acc1:
        if not df_master.empty:
            st.download_button("Exportar CSV", data=df_master.to_csv(index=False).encode('utf-8'), file_name="almacen.csv", mime="text/csv", use_container_width=True)
    with col_acc2:
        if not df_master.empty:
            st.download_button("Exportar PDF", data=generar_pdf(df_master), file_name="reporte.pdf", mime="application/pdf", use_container_width=True)
    with col_acc3:
        filtro_estado = st.selectbox("Filtrar Estado", ["Todos", "Prestado", "Devuelto", "Asignado", "Proceso de asignacion"], label_visibility="collapsed")
    with col_acc4:
        busqueda_global = st.text_input("Buscador", placeholder="Busca por trabajador, artículo o folio...", label_visibility="collapsed")

    if not df_master.empty:
        df_filtrado = df_master.copy()
        if filtro_estado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['estado'] == filtro_estado]
        if busqueda_global:
            df_filtrado = df_filtrado[
                df_filtrado['responsable'].str.contains(busqueda_global, case=False, na=False) |
                df_filtrado['articulo'].str.contains(busqueda_global, case=False, na=False) |
                df_filtrado['id'].str.contains(busqueda_global, case=False, na=False)
            ]
    else:
        df_filtrado = pd.DataFrame()

    if df_filtrado.empty:
        if not df_master.empty:
            st.warning(f"⚠️ No se encontraron resultados para la búsqueda '{busqueda_global}' con el estado '{filtro_estado}'.")
        else:
            st.info("No hay registros en el almacén.")
    else:
        h1, h2, h3, h4, h5, h6, h7, h8 = st.columns([1.2, 1.5, 2.5, 3.0, 0.8, 1.8, 1.5, 0.5])
        for col, txt in zip([h1, h2, h3, h4, h5, h6, h7, h8], ["Fecha Mov.", "Folio", "Responsable", "Artículo / Material", "Cant.", "Estado", "Tiempo Activo", ""]):
            col.markdown(f"<p style='font-size:12px; font-weight:bold; color:#4A5568; border-bottom:1px solid #E2E8F0; padding-bottom:3px; margin:0;'>{txt}</p>", unsafe_allow_html=True)

        FILAS_POR_PAGINA = 15
        total_filas = len(df_filtrado)
        total_paginas = max(1, -(-total_filas // FILAS_POR_PAGINA))
        
        if busqueda_global != st.session_state.get("ultima_busqueda", ""):
            st.session_state["pagina_actual"] = 1
            st.session_state["ultima_busqueda"] = busqueda_global

        pagina_actual = st.session_state["pagina_actual"]
        df_pagina = df_filtrado.iloc[(pagina_actual - 1) * FILAS_POR_PAGINA : pagina_actual * FILAS_POR_PAGINA]

        for _, row in df_pagina.iterrows():
            id_fila = row.get('id')
            en_alerta = str(row.get('alerta', 'NO')).upper() == 'SI'
            
            bg_color = "#FEE2E2" if en_alerta else ("#EBF8FF" if id_fila == id_seleccionado else "#F9FAFB")
            text_color = "#991B1B" if en_alerta else ("#2B6CB0" if id_fila == id_seleccionado else "#2D3748")
            
            estilo_celda = f"background-color:{bg_color}; color:{text_color}; font-size:13px; padding:6px; border-radius:4px; margin-bottom:2px; height:32px; overflow:hidden; white-space:nowrap; text-overflow:ellipsis;"

            if row.get('estado') == 'Devuelto':
                tiempo_transcurrido = "🟢 Completado"
            else:
                try:
                    fecha_reg = datetime.strptime(str(row.get('fecha', '')), '%d/%m/%Y').date()
                    dias = (datetime.now().date() - fecha_reg).days
                    tiempo_transcurrido = f"⏱️ {dias} días" if dias >= 0 else "Fecha futura"
                except: tiempo_transcurrido = "—"

            c_fec, c_fol, c_res, c_art, c_cant, c_est, c_dias, c_acc = st.columns([1.2, 1.5, 2.5, 3.0, 0.8, 1.8, 1.5, 0.5])
            c_fec.markdown(f"<div style='{estilo_celda}'>{row.get('fecha','')}</div>", unsafe_allow_html=True)
            c_fol.markdown(f"<div style='{estilo_celda}'>{id_fila}</div>", unsafe_allow_html=True)
            c_res.markdown(f"<div style='{estilo_celda}'><b>{row.get('responsable','')}</b></div>", unsafe_allow_html=True)
            c_art.markdown(f"<div style='{estilo_celda}'>{row.get('articulo','')}</div>", unsafe_allow_html=True)
            c_cant.markdown(f"<div style='{estilo_celda}; text-align:center;'>{row.get('cantidad',1)}</div>", unsafe_allow_html=True)
            c_est.markdown(f"<div style='{estilo_celda}'>{row.get('estado','')}</div>", unsafe_allow_html=True)
            c_dias.markdown(f"<div style='{estilo_celda}'>{tiempo_transcurrido}</div>", unsafe_allow_html=True)
            
            with c_acc:
                if st.button("✏️", key=f"sel_prod_{id_fila}", use_container_width=True):
                    st.session_state["id_desde_tabla"] = id_fila
                    # Activamos el flag de scroll para el siguiente ciclo
                    st.session_state["ejecutar_scroll"] = True
                    st.rerun()

        st.write("")
        p1, p2, p3, p4, p5 = st.columns([1, 1, 3, 1, 1])
        with p1:
            if st.button("⏮ Primera", disabled=(pagina_actual == 1), use_container_width=True):
                st.session_state["pagina_actual"] = 1; st.rerun()
        with p2:
            if st.button("◀ Anterior", disabled=(pagina_actual == 1), use_container_width=True):
                st.session_state["pagina_actual"] -= 1; st.rerun()
        with p3:
            st.markdown(f"<p style='text-align:center; color:#7A8B99; font-size:13px;'>Página <b>{pagina_actual}</b> de <b>{total_paginas}</b> | <b>{total_filas}</b> registros</p>", unsafe_allow_html=True)
        with p4:
            if st.button("Siguiente ▶", disabled=(pagina_actual == total_paginas), use_container_width=True):
                st.session_state["pagina_actual"] += 1; st.rerun()
        with p5:
            if st.button("Última ⏭", disabled=(pagina_actual == total_paginas), use_container_width=True):
                st.session_state["pagina_actual"] = total_paginas; st.rerun()