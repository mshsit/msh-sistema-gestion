import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import threading  # Para guardar en segundo plano sin congelar la app

# 1. CONFIGURACIÓN E INYECCIÓN DE ESTILO
st.set_page_config(page_title="Control de Préstamos de Almacén", layout="wide")

st.markdown("""
    <style>
    .kpi-title { font-size: 11px !important; font-weight: bold !important; color: #7A8B99 !important; text-align: center; margin-bottom: 5px; text-transform: uppercase; }
    .kpi-value { font-size: 32px !important; font-weight: bold !important; text-align: center; margin-top: -10px; }
    .card { background-color: white; padding: 12px; border-radius: 6px; box-shadow: 0px 1px 3px rgba(0,0,0,0.1); border: 1px solid #E2E8F0; }
    /* Suavizado visual para eliminar saltos bruscos */
    .stApp { scroll-behavior: smooth; }
    </style>
    """, unsafe_allow_html=True)

# CONTRASEÑA DE ACCESO AL DASHBOARD
CONTRASENA_CORRECTA = "Almacen2026"

# INICIALIZAR LA URL EN EL ESTADO DE LA SESIÓN
if "google_script_url" not in st.session_state:
    st.session_state["google_script_url"] = "https://script.google.com/macros/s/AKfycbzx00GpTiNyJP4uOIZxFAIxxg2huDe7JB6IksCRd9aGtH8oBytvJIZMaLJYt4Jq-SGSVQ/exec"

# FUNCIÓN AUXILIAR PARA ENVIAR PETICIONES HTTP EN SEGUNDO PLANO
def enviar_peticion_asincrona(url, data):
    try:
        requests.post(url, data=data, timeout=10)
    except:
        pass

# VENTANA EMERGENTE DE CONFIGURACIÓN
@st.dialog("Configurar URL de Google Sheets")
def ventana_configuracion():
    st.write("Pega la nueva URL de tu Google Apps Script para enlazar la base de datos:")
    nueva_url = st.text_input("URL Google Apps Script:", value=st.session_state["google_script_url"])
    st.write("")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Cancelar", key="btn_cancel_url"):
            st.rerun()
    with c2:
        if st.button("Guardar URL", type="primary", key="btn_save_url"):
            st.session_state["google_script_url"] = nueva_url.strip()
            st.success("URL actualizada con exito!")
            st.rerun()

# VENTANA DE CONFIRMACIÓN PARA ELIMINAR
@st.dialog("Confirmar Eliminacion")
def ventana_confirmar_eliminar(id_a_eliminar, url):
    st.warning(f"Estas seguro de que deseas eliminar el registro {id_a_eliminar}? Esta accion no se puede deshacer.")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Cancelar", key="btn_cancel_del", use_container_width=True):
            st.rerun()
    with c2:
        if st.button("Si, Eliminar", type="primary", key="btn_confirm_del", use_container_width=True):
            try:
                requests.post(url, data={"accion": "eliminar", "id": id_a_eliminar}, timeout=8)
            except:
                pass
            st.rerun()

# GENERADOR DE PDF
def generar_pdf(df):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_margins(10, 10, 10)
    pdf.add_page()

    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(30, 52, 71)
    pdf.cell(0, 8, "SISTEMA DE CONTROL DE ALMACEN", ln=True, align='L')
    pdf.set_font("Arial", '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Reporte generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='L')
    pdf.ln(4)

    widths =   [32,  24,   40,   48,   14,   32,   72,  15]
    columnas = ["Folio", "Fecha", "Responsable", "Articulo", "Cant", "Estado", "Observaciones", "Alerta"]

    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(30, 52, 71)
    pdf.set_text_color(255, 255, 255)
    for i, col in enumerate(columnas):
        pdf.cell(widths[i], 8, col, border=1, ln=0, align='C' if i in [4, 7] else 'L', fill=True)
    pdf.ln()

    for _, row in df.iterrows():
        esta_en_alerta = str(row.get('alerta', 'NO')).upper().strip() == 'SI'

        if esta_en_alerta:
            pdf.set_fill_color(254, 226, 226)
            pdf.set_text_color(153, 27, 27)
            fondo = True
        else:
            pdf.set_text_color(0, 0, 0)
            fondo = False

        def celda(texto, ancho, align='L'):
            t = str(texto)
            pdf.set_font("Arial", '', 6 if len(t) * (8.5 * 0.6) / 2.834 > (ancho - 2) else 8.5)
            pdf.cell(ancho, 7, t, 1, 0, align, fondo)

        celda(row.get('id', ''),           widths[0], 'L')
        celda(row.get('fecha', ''),         widths[1], 'C')
        celda(row.get('responsable', ''),   widths[2], 'L')
        celda(row.get('articulo', ''),      widths[3], 'L')
        celda(row.get('cantidad', '1'),     widths[4], 'C')
        celda(row.get('estado', ''),        widths[5], 'L')
        celda(row.get('observaciones', ''), widths[6], 'L')
        pdf.set_font("Arial", '', 8.5)
        pdf.cell(widths[7], 7, "SI" if esta_en_alerta else "NO", 1, 0, 'C', fondo)
        pdf.ln()

    return pdf.output(dest='S').encode('latin-1', errors='ignore')

# NORMALIZAR ALERTA
def normalizar_alerta(val):
    return 'SI' if str(val).upper().strip() in ['SI', 'TRUE', '1'] else 'NO'

# CONTROL DE SESIÓN
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h2 style='text-align: center; margin-top: 50px;'>Acceso al Sistema</h2>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 1.5, 1])
    with col_center:
        psw = st.text_input("Contrasena de Almacen:", type="password")
        if st.button("Ingresar al Sistema", type="primary", use_container_width=True):
            if psw == CONTRASENA_CORRECTA:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Contrasena incorrecta")
else:
    st.markdown("<h1 style='text-align: center; color: #1E3447; font-family: sans-serif; margin-bottom: 25px;'>Control de Prestamos de Almacen</h1>", unsafe_allow_html=True)

    URL_ACTUAL = st.session_state["google_script_url"]

    datos_json = []
    conexion_exitosa = False
    if URL_ACTUAL.strip() not in ["", "TU_URL_DE_APPS_SCRIPT_AQUI"]:
        try:
            res = requests.get(URL_ACTUAL, timeout=5)
            if res.status_code == 200:
                datos_json = res.json()
                conexion_exitosa = True
        except:
            pass

    df_master = pd.DataFrame(datos_json)

    # NORMALIZAR COLUMNA ALERTA
    if conexion_exitosa and not df_master.empty:
        if 'alerta' not in df_master.columns:
            df_master['alerta'] = 'NO'
        else:
            df_master['alerta'] = df_master['alerta'].apply(normalizar_alerta)

    # PARSEO DE FECHAS
    if conexion_exitosa and not df_master.empty and 'fecha' in df_master.columns:
        df_master['fecha'] = df_master['fecha'].astype(str).str.strip()
        meses_en = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',
                    'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}

        def limpiar_fecha_gmt(texto_fecha):
            if len(texto_fecha) > 15 and "GMT" in texto_fecha:
                try:
                    p = texto_fecha.split()
                    return f"{p[2].zfill(2)}/{meses_en.get(p[1], '01')}/{p[3]}"
                except:
                    return texto_fecha
            elif "-" in texto_fecha and len(texto_fecha) >= 10:
                try:
                    p = texto_fecha.split("-")
                    return f"{p[2][:2]}/{p[1]}/{p[0]}"
                except:
                    return texto_fecha
            return texto_fecha

        df_master['fecha'] = df_master['fecha'].apply(limpiar_fecha_gmt)

    # KPIs
    total_reg    = len(df_master)
    prestados    = len(df_master[df_master['estado'] == 'Prestado'])              if conexion_exitosa and not df_master.empty else 0
    devueltos    = len(df_master[df_master['estado'] == 'Devuelto'])              if conexion_exitosa and not df_master.empty else 0
    asignados    = len(df_master[df_master['estado'] == 'Asignado'])              if conexion_exitosa and not df_master.empty else 0
    proceso_asig = len(df_master[df_master['estado'] == 'Proceso de asignacion']) if conexion_exitosa and not df_master.empty else 0
    alertas      = len(df_master[df_master['alerta'] == 'SI'])                   if conexion_exitosa and not df_master.empty else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: st.markdown(f'<div class="card"><p class="kpi-title">TOTAL REGISTROS</p><p class="kpi-value" style="color:#2D3748;">{total_reg}</p></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="card"><p class="kpi-title">PRESTADOS</p><p class="kpi-value" style="color:#DD6B20;">{prestados}</p></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="card"><p class="kpi-title">DEVUELTOS</p><p class="kpi-value" style="color:#38A169;">{devueltos}</p></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="card"><p class="kpi-title">ASIGNADOS</p><p class="kpi-value" style="color:#3182CE;">{asignados}</p></div>', unsafe_allow_html=True)
    with c5: st.markdown(f'<div class="card"><p class="kpi-title">EN PROCESO</p><p class="kpi-value" style="color:#805AD5;">{proceso_asig}</p></div>', unsafe_allow_html=True)
    with c6: st.markdown(f'<div class="card"><p class="kpi-title">EN ALERTA</p><p class="kpi-value" style="color:#E53E3E;">{alertas}</p></div>', unsafe_allow_html=True)

    st.write("")
    st.markdown("### Formulario de Operaciones")
    tab_agregar, tab_modificar_eliminar = st.tabs(["Registrar Nuevo", "Modificar o Eliminar Registro Existente"])

    # ── TAB AGREGAR ──────────────────────────────────────────────────────────
    with tab_agregar:
        with st.container():
            f1, f2, f3, f4, f5, f6 = st.columns([1.4, 2, 2, 1, 1.5, 2.5])
            with f1: fecha_add = st.date_input("Fecha", datetime.now(), format="DD/MM/YYYY", key="f_add")
            with f2: resp_add  = st.text_input("Responsable", placeholder="Nombre", key="r_add")
            with f3: art_add   = st.text_input("Articulo", placeholder="Herramienta", key="a_add")
            with f4: cant_add  = st.text_input("Cantidad", value="1", key="c_add")
            with f5: est_add   = st.selectbox("Estado", ["Prestado", "Devuelto", "Asignado", "Proceso de asignacion"], key="e_add")
            with f6: obs_add   = st.text_input("Observaciones Iniciales", placeholder="Opcional", key="o_add")

            fa, fb, fc = st.columns([6, 2, 1])
            with fa: nota_add  = st.text_input("Nota interna...", placeholder="Nota adicional", key="n_add")
            with fb: alerta_add = st.selectbox("Alerta?", ["NO", "SI"], key="al_add")
            with fc:
                st.write("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
                if st.button("Agregar", type="primary", use_container_width=True):
                    if resp_add.strip() and art_add.strip():
                        payload = {
                            "accion": "agregar",
                            "id": f"ID-{int(datetime.now().timestamp())}",
                            "fecha": fecha_add.strftime('%d/%m/%Y'),
                            "responsable": resp_add,
                            "articulo": art_add,
                            "cantidad": str(cant_add),
                            "estado": est_add,
                            "observaciones": obs_add,
                            "nota": nota_add,
                            "alerta": alerta_add
                        }
                        if conexion_exitosa:
                            requests.post(URL_ACTUAL, data=payload)
                            st.success("Registro agregado!")
                            st.rerun()
                    else:
                        st.warning("Rellena los campos obligatorios.")

    # ── TAB MODIFICAR / ELIMINAR ─────────────────────────────────────────────
    with tab_modificar_eliminar:
        if conexion_exitosa and not df_master.empty:
            m1, _ = st.columns([2, 6])
            with m1:
                id_seleccionado = st.selectbox(
                    "Selecciona el Folio / ID a operar:",
                    [""] + list(df_master['id'].unique()),
                    key="id_selector_mod"
                )

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
                        if st.button("Guardar Cambios", type="primary", use_container_width=True, key=f"btn_guardar_{_k}"):
                            payload_mod = {
                                "accion":        "modificar",
                                "id":            str(id_seleccionado),
                                "fecha":         fecha_mod_dt.strftime('%d/%m/%Y'),
                                "responsable":   str(resp_mod),
                                "articulo":      str(art_mod),
                                "cantidad":      str(cant_mod),
                                "estado":        str(est_mod),
                                "observaciones": str(obs_mod),
                                "nota":          str(nota_mod),
                                "alerta":        str(alerta_mod)
                            }
                            try:
                                requests.post(URL_ACTUAL, data=payload_mod, timeout=8)
                                st.success("Registro modificado correctamente!")
                            except:
                                st.error("Error al conectar con la base de datos.")

                            for suffix in ["al_mod", "e_mod", "f_mod", "r_mod", "a_mod", "c_mod", "o_mod", "n_mod"]:
                                key_w = f"{suffix}_{_k}"
                                if key_w in st.session_state:
                                    del st.session_state[key_w]
                            st.rerun()

                    with btn_col2:
                        if st.button("Eliminar Registro", type="secondary", use_container_width=True, key=f"btn_eliminar_{_k}"):
                            ventana_confirmar_eliminar(id_seleccionado, URL_ACTUAL)

    st.divider()

    # ACCIONES GENERALES
    a1, a2, a3, a4, a5, a6, a7 = st.columns([1.3, 1.3, 1.3, 1.3, 1.3, 1.5, 3.5])
    with a1:
        if conexion_exitosa and not df_master.empty:
            st.download_button("Exportar CSV", data=df_master.to_csv(index=False).encode('utf-8'),
                               file_name="inventario.csv", mime="text/csv", use_container_width=True)
        else:
            st.button("Exportar CSV", disabled=True, use_container_width=True)

    with a2:
        st.button("Publicar CSV", use_container_width=True)

    with a3:
        if conexion_exitosa and not df_master.empty:
            st.download_button("Generar PDF", data=generar_pdf(df_master),
                               file_name="reporte_prestamos.pdf", mime="application/pdf", use_container_width=True)
        else:
            st.button("Generar PDF", disabled=True, use_container_width=True)

    with a4:
        if st.button("Notificar Jefe", use_container_width=True):
            if conexion_exitosa:
                try:
                    requests.post(URL_ACTUAL, data={"accion": "notificar_jefe_general"}, timeout=8)
                    st.toast("Notificacion enviada al Jefe")
                except:
                    st.toast("Error al enviar notificacion")

    with a5:
        if st.button("Notificar Almacen", use_container_width=True):
            if conexion_exitosa:
                try:
                    requests.post(URL_ACTUAL, data={"accion": "notificar_almacen_general"}, timeout=8)
                    st.toast("Notificacion enviada al Almacen")
                except:
                    st.toast("Error al enviar notificacion")

    with a6:
        if st.button("Configurar URL", use_container_width=True):
            ventana_configuracion()

    with a7:
        busqueda = st.text_input("Buscar...", placeholder="Buscar responsable o articulo...", label_visibility="collapsed")

    # VISUALIZADOR IN SITU (Edición Directa Instantánea sin parpadeos)
    if conexion_exitosa and not df_master.empty:
        df_filtrado = df_master[
            df_master['responsable'].str.contains(busqueda, case=False, na=False) |
            df_master['articulo'].str.contains(busqueda, case=False, na=False)
        ].copy()

        def colorear_alertas(fila):
            if str(fila['alerta']).upper().strip() == 'SI':
                return ['background-color: #FEE2E2; color: #991B1B; font-weight: bold;'] * len(fila)
            return [''] * len(fila)

        df_para_mostrar = df_filtrado[["id", "fecha", "responsable", "articulo", "cantidad", "estado", "observaciones", "nota", "alerta"]].reset_index(drop=True)

        # PAGINACION
        FILAS_POR_PAGINA = 20
        total_filas   = len(df_para_mostrar)
        total_paginas = max(1, -(-total_filas // FILAS_POR_PAGINA))

        if "pagina_actual" not in st.session_state:
            st.session_state["pagina_actual"] = 1
        if busqueda != st.session_state.get("ultima_busqueda", ""):
            st.session_state["pagina_actual"] = 1
            st.session_state["ultima_busqueda"] = busqueda

        pagina_actual = st.session_state["pagina_actual"]
        inicio = (pagina_actual - 1) * FILAS_POR_PAGINA
        fin    = inicio + FILAS_POR_PAGINA
        df_pagina = df_para_mostrar.iloc[inicio:fin].reset_index(drop=True)

        st.markdown("<small style='color: #2B6CB0;'>📝 <b>Edición en Vivo Silenciosa:</b> Haz doble clic en cualquier celda para modificarla. Los cambios se guardan automáticamente en la nube sin parpadear.</small>", unsafe_allow_html=True)

        # LA GRILLA INTERACTIVA
        tabla_editada = st.data_editor(
            df_pagina.style.apply(colorear_alertas, axis=1),
            width="stretch",
            hide_index=True,
            column_config={
                "id": st.column_config.TextColumn("Folio / ID", disabled=True),
                "fecha": "Fecha",
                "responsable": "Responsable",
                "articulo": "Artículo",
                "cantidad": "Cant.",
                "estado": st.column_config.SelectboxColumn("Estado", options=["Prestado", "Devuelto", "Asignado", "Proceso de asignacion"]),
                "observaciones": "Observaciones",
                "nota": "Nota",
                "alerta": st.column_config.SelectboxColumn("Alerta", options=["NO", "SI"])
            },
            key="grilla_hoja_directa"
        )

        # CAPTURA DE CAMBIOS EN SEGUNDO PLANO (Cero recargas de pantalla)
        if "grilla_hoja_directa" in st.session_state:
            cambios = st.session_state["grilla_hoja_directa"]
            if cambios.get("edited_rows"):
                for idx_str, celdas_modificadas in cambios["edited_rows"].items():
                    idx = int(idx_str)
                    fila_original = df_pagina.iloc[idx]
                    id_llave = str(fila_original["id"])

                    # Construimos el payload de actualización mezclando lo modificado con lo actual
                    payload_directo = {
                        "accion": "modificar",
                        "id": id_llave,
                        "fecha": str(celdas_modificadas.get("fecha", fila_original["fecha"])),
                        "responsable": str(celdas_modificadas.get("responsable", fila_original["responsable"])),
                        "articulo": str(celdas_modificadas.get("articulo", fila_original["articulo"])),
                        "cantidad": str(celdas_modificadas.get("cantidad", fila_original["cantidad"])),
                        "estado": str(celdas_modificadas.get("estado", fila_original["estado"])),
                        "observaciones": str(celdas_modificadas.get("observaciones", fila_original["observaciones"])),
                        "nota": str(celdas_modificadas.get("nota", fila_original["nota"])),
                        "alerta": str(celdas_modificadas.get("alerta", fila_original["alerta"]))
                    }

                    # Ejecutar en segundo plano mediante un Thread aislado (ELIMINA EL PARPADEO)
                    hilo_guardado = threading.Thread(target=enviar_peticion_asincrona, args=(URL_ACTUAL, payload_directo))
                    hilo_guardado.start()
                    
                    # Mensaje flotante discreto sin recargar la pantalla
                    st.toast(f"Sincronizando Folio {id_llave}...")

        # CONTROLES DE PAGINACIÓN
        p1, p2, p3, p4, p5 = st.columns([1, 1, 3, 1, 1])
        with p1:
            if st.button("Primera", disabled=(pagina_actual == 1), use_container_width=True):
                st.session_state["pagina_actual"] = 1
                st.rerun()
        with p2:
            if st.button("Anterior", disabled=(pagina_actual == 1), use_container_width=True):
                st.session_state["pagina_actual"] -= 1
                st.rerun()
        with p3:
            st.markdown(
                f"<p style='text-align:center; margin-top:8px; color:#555;'>"
                f"Pagina <b>{pagina_actual}</b> de <b>{total_paginas}</b> "
                f"&nbsp;|&nbsp; {total_filas} registros encontrados</p>",
                unsafe_allow_html=True
            )
        with p4:
            if st.button("Siguiente", disabled=(pagina_actual == total_paginas), use_container_width=True):
                st.session_state["pagina_actual"] += 1
                st.rerun()
        with p5:
            if st.button("Ultima", disabled=(pagina_actual == total_paginas), use_container_width=True):
                st.session_state["pagina_actual"] = total_paginas
                st.rerun()
    else:
        if URL_ACTUAL.strip() in ["", "TU_URL_DE_APPS_SCRIPT_AQUI"]:
            st.info("Por favor, haz clic en Configurar URL para vincular tu Google Apps Script.")
        else:
            st.warning("Sin conexion con la base de datos. Verifica tu URL en el boton de Configuracion.")