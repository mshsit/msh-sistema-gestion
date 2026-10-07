import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="MSH-Hub | Tablero de Proyectos",
    layout="wide",
    page_icon="🚦",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════
# Auto-refresh cada 13 segundos — avanza la página y refresca datos
# a la vez. requiere streamlit-autorefresh: pip install streamlit-autorefresh
# ══════════════════════════════════════════════
FILAS_POR_PAGINA = 8
INTERVALO_MS = 13_000

try:
    from streamlit_autorefresh import st_autorefresh
    conteo_refrescos = st_autorefresh(interval=INTERVALO_MS, key="tv_autorefresh")
except ImportError:
    conteo_refrescos = 0
    st.warning("Falta instalar streamlit-autorefresh (`pip install streamlit-autorefresh`) para el refresco automático.")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=DM+Mono:wght@500;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }
[data-testid="stAppViewContainer"] {
    background: #0F1E2E;
    background-image: radial-gradient(circle at 15% 10%, rgba(74,144,217,0.10) 0%, transparent 45%);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainMenu"]              { display: none !important; }
[data-testid="stSidebar"]              { display: none !important; }
[data-testid="stSidebarCollapseButton"]{ display: none !important; }
[data-testid="collapsedControl"]       { display: none !important; }
footer                                  { display: none !important; }
#MainMenu                               { display: none !important; }
.block-container { padding-top: 1.2rem !important; padding-bottom: 1rem !important; max-width: 100% !important; }

.tv-header {
    background: #1E3447; border-radius: 16px; padding: 18px 28px;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 18px; box-shadow: 0 6px 24px rgba(0,0,0,0.35);
}
.tv-header-left { display: flex; align-items: center; gap: 16px; }
.tv-logo-box {
    width: 48px; height: 48px; background: rgba(255,255,255,0.12);
    border-radius: 12px; display: flex; align-items: center; justify-content: center;
    font-size: 24px;
}
.tv-title { font-size: 22px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.3px; }
.tv-subtitle { font-size: 13px; color: rgba(255,255,255,0.5); font-weight: 500; }
.tv-reloj { font-size: 15px; color: rgba(255,255,255,0.75); font-family: 'DM Mono', monospace; }

.tv-kpi-bar { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 18px; }
.tv-kpi {
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px; padding: 16px 20px;
}
.tv-kpi-lbl { font-size: 12px; color: rgba(255,255,255,0.55); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.tv-kpi-val { font-size: 34px; font-weight: 800; line-height: 1; }

.tv-tabla-wrap { background: #15263A; border-radius: 16px; overflow: hidden; box-shadow: 0 6px 24px rgba(0,0,0,0.3); }
.tv-th {
    font-size: 12px !important; font-weight: 700 !important; color: rgba(255,255,255,0.45) !important;
    text-transform: uppercase; letter-spacing: 0.6px; padding: 14px 16px !important;
    margin: 0 !important; background: rgba(255,255,255,0.03);
}
.tv-td {
    font-size: 16px !important; color: #FFFFFF !important; padding: 16px !important;
    border-bottom: 1px solid rgba(255,255,255,0.06); margin: 0 !important;
    overflow: hidden; white-space: nowrap; text-overflow: ellipsis;
}
.tv-td-alt { background: rgba(255,255,255,0.025); }
.tv-folio { font-family: 'DM Mono', monospace; font-weight: 700; color: #FFFFFF; }
.tv-badge { font-size: 13px; font-weight: 700; padding: 5px 14px; border-radius: 99px; display: inline-block; white-space: nowrap; }
.tv-badge-verde    { background: #DCFCE7; color: #14532D; }
.tv-badge-amarillo { background: #FEF3C7; color: #78350F; }
.tv-badge-rojo     { background: #FEE2E2; color: #7F1D1D; }
.tv-badge-azul     { background: #DBEAFE; color: #1E3A5F; }
.tv-footer { display: flex; align-items: center; justify-content: space-between; margin-top: 14px; }
.tv-footer-txt { font-size: 12px; color: rgba(255,255,255,0.35); }
.tv-vacio { text-align: center; padding: 60px 20px; color: rgba(255,255,255,0.4); font-size: 16px; }
</style>
""", unsafe_allow_html=True)

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://unsugrcleytqroxuuhaf.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")


@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_supabase()

COLORES_PRIORIDAD = {"rojo": 0, "amarillo": 1, "azul": 2, "verde": 3}
EMOJI_COLOR = {"verde": "🟢", "amarillo": "🟡", "rojo": "🔴", "azul": "🔵"}
ETIQUETA_COLOR = {"verde": "PROGRAMADO", "amarillo": "EN PROCESO", "rojo": "URGENTE", "azul": "LISTO"}


def cargar_tablero():
    try:
        res = supabase.table("seguimiento_proyectos").select(
            "equipo_servicio, area_actual, color_semaforo, fecha_entrega, "
            "almacen_proyectos!inner(numero_proyecto, cliente_ubicacion), "
            "almacen_personas(nombres, apellidos)"
        ).eq("estado_ciclo", "activo").execute()
        filas = []
        for s in (res.data or []):
            proy = s.get("almacen_proyectos") or {}
            persona = s.get("almacen_personas") or {}
            filas.append({
                "numero_proyecto": proy.get("numero_proyecto", "—"),
                "cliente": proy.get("cliente_ubicacion") or "—",
                "equipo_servicio": s.get("equipo_servicio") or "—",
                "area_actual": s.get("area_actual") or "—",
                "color_semaforo": s.get("color_semaforo", "verde"),
                "responsable": f"{persona.get('nombres', '')} {persona.get('apellidos') or ''}".strip() or "—",
            })
        filas.sort(key=lambda f: (COLORES_PRIORIDAD.get(f["color_semaforo"], 9), f["numero_proyecto"] or ""))
        return filas
    except Exception as e:
        st.error(f"Error al cargar el tablero: {e}")
        return []


datos = cargar_tablero()
total = len(datos)
conteo = {c: sum(1 for d in datos if d["color_semaforo"] == c) for c in COLORES_PRIORIDAD}

ahora = datetime.now()
st.markdown(f"""
    <div class="tv-header">
        <div class="tv-header-left">
            <div class="tv-logo-box">🚦</div>
            <div>
                <div class="tv-title">Proyectos en Proceso</div>
                <div class="tv-subtitle">Mendoza Servicios y Herramientas</div>
            </div>
        </div>
        <div class="tv-reloj">📅 {ahora.strftime('%d %b %Y')} · {ahora.strftime('%H:%M')}</div>
    </div>

    <div class="tv-kpi-bar">
        <div class="tv-kpi">
            <div class="tv-kpi-lbl">Proyectos Activos</div>
            <div class="tv-kpi-val" style="color:#FFFFFF;">{total}</div>
        </div>
        <div class="tv-kpi">
            <div class="tv-kpi-lbl">🟡 En Proceso</div>
            <div class="tv-kpi-val" style="color:#FBBF24;">{conteo.get('amarillo', 0)}</div>
        </div>
        <div class="tv-kpi">
            <div class="tv-kpi-lbl">🔵 Listos</div>
            <div class="tv-kpi-val" style="color:#60A5FA;">{conteo.get('azul', 0)}</div>
        </div>
        <div class="tv-kpi">
            <div class="tv-kpi-lbl">🔴 Urgentes</div>
            <div class="tv-kpi-val" style="color:#F87171;">{conteo.get('rojo', 0)}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

if not datos:
    st.markdown('<div class="tv-tabla-wrap"><div class="tv-vacio">📭 No hay proyectos activos en este momento.</div></div>', unsafe_allow_html=True)
else:
    total_paginas = max(1, -(-len(datos) // FILAS_POR_PAGINA))  # redondeo hacia arriba
    pagina_actual = conteo_refrescos % total_paginas
    inicio = pagina_actual * FILAS_POR_PAGINA
    datos_pagina = datos[inicio:inicio + FILAS_POR_PAGINA]

    filas_html = ""
    for i, d in enumerate(datos_pagina):
        cls = "tv-td tv-td-alt" if i % 2 == 1 else "tv-td"
        badge = f'<span class="tv-badge tv-badge-{d["color_semaforo"]}">{EMOJI_COLOR.get(d["color_semaforo"], "")} {ETIQUETA_COLOR.get(d["color_semaforo"], "")}</span>'
        filas_html += f"""
        <div style="display:grid; grid-template-columns: 1.3fr 1.6fr 1.8fr 1.3fr 1.5fr 1.2fr;">
            <div class="{cls} tv-folio">{d['numero_proyecto']}</div>
            <div class="{cls}">{d['cliente']}</div>
            <div class="{cls}">{d['equipo_servicio']}</div>
            <div class="{cls}">{badge}</div>
            <div class="{cls}">{d['area_actual']}</div>
            <div class="{cls}">{d['responsable']}</div>
        </div>"""

    st.markdown(f"""
        <div class="tv-tabla-wrap">
            <div style="display:grid; grid-template-columns: 1.3fr 1.6fr 1.8fr 1.3fr 1.5fr 1.2fr;">
                <div class="tv-th"># Proyecto</div>
                <div class="tv-th">Cliente</div>
                <div class="tv-th">Equipo / Servicio</div>
                <div class="tv-th">Estado</div>
                <div class="tv-th">Área actual</div>
                <div class="tv-th">Responsable</div>
            </div>
            {filas_html}
        </div>
    """, unsafe_allow_html=True)

pagina_txt = f" · Página {pagina_actual + 1} de {total_paginas}" if datos and total_paginas > 1 else ""
st.markdown(f"""
    <div class="tv-footer">
        <span class="tv-footer-txt">🔄 Actualización automática cada 13 seg{pagina_txt}</span>
        <span class="tv-footer-txt">Fuente: MSH-Hub</span>
    </div>
""", unsafe_allow_html=True)
