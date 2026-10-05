import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import date, datetime, timedelta

st.set_page_config(
    page_title="MSH-Hub | Dashboard",
    layout="wide",
    page_icon="📈",
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
.kpi-card {
    background: #ffffff; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 18px 22px; box-shadow: 0 2px 10px rgba(30,52,71,0.06); height: 100%;
}
.kpi-card-icon { font-size: 22px; margin-bottom: 6px; }
.kpi-card-val { font-size: 24px; font-weight: 700; color: #1E3447; line-height: 1.1; }
.kpi-card-lbl { font-size: 12px; color: #64748B; font-weight: 500; margin-top: 2px; }
.panel-card-titulo { font-size: 15px; font-weight: 700; color: #1E293B; margin-bottom: 2px; }
.panel-card-subtitulo { font-size: 12px; color: #94A3B8; margin-bottom: 16px; }
.badge {
    display: inline-flex; align-items: center; gap: 4px; padding: 3px 9px;
    border-radius: 99px; font-size: 10px; font-weight: 600; white-space: nowrap;
}
.badge-vencido { background:#FEE2E2; color:#B91C1C; }
.badge-critico { background:#FEF3E8; color:#C2410C; }
.badge-proximo { background:#FEF9C3; color:#854D0E; }
.folio-tag {
    font-family: 'DM Mono', monospace; font-size: 10px; color: #94A3B8;
    background: #F1F5F9; border-radius: 4px; padding: 1px 5px; display: inline-block;
}
div[class*="st-key-panel_alerta_lotes"],
div[class*="st-key-panel_alerta_mant"],
div[class*="st-key-panel_alerta_prestamos"],
div[class*="st-key-panel_grafica"] {
    background: #ffffff; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 20px 22px; margin-bottom: 18px;
    box-shadow: 0 2px 10px rgba(30,52,71,0.06);
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


def registrar_acceso(usuario, nombre, accion):
    try:
        supabase.table("usuarios_accesos").insert({
            "usuario": usuario, "nombre": nombre,
            "accion": accion, "fecha_hora": datetime.now().isoformat()
        }).execute()
    except:
        pass


def contar(tabla, filtros=None):
    try:
        q = supabase.table(tabla).select("id", count="exact")
        if filtros:
            for campo, valor in filtros.items():
                q = q.eq(campo, valor)
        res = q.range(0, 0).execute()
        return res.count or 0
    except:
        return 0


def obtener_valor_inventario():
    try:
        res = supabase.rpc("obtener_valor_inventario", {}).execute()
        return res.data or 0
    except Exception as e:
        st.error(f"Error al calcular el valor de inventario: {e}")
        return 0


def cargar_alertas_lotes():
    try:
        res = supabase.table("almacen_lotes_por_vencer").select("*").lte("dias_restantes", 30).order("fecha_vencimiento").limit(10).execute()
        return res.data or []
    except:
        return []


def cargar_alertas_mantenimientos():
    try:
        res = supabase.table("almacen_mantenimientos_proximos").select("*").lte("dias_restantes", 30).order("proximo_mantenimiento").limit(10).execute()
        return res.data or []
    except:
        return []


def cargar_prestamos_vencidos():
    try:
        res = supabase.table("almacen_prestamos_resumen").select("*").in_("estado", ["prestado", "parcial"]).lt("fecha_estimada", str(date.today())).order("fecha_estimada").limit(10).execute()
        return res.data or []
    except:
        return []


def cargar_movimientos_diarios(dias=30):
    try:
        res = supabase.rpc("obtener_movimientos_diarios", {"p_dias": dias}).execute()
        return res.data or []
    except Exception as e:
        st.error(f"Error al cargar movimientos diarios: {e}")
        return []


def cargar_top_productos(dias=30, limite=5):
    try:
        res = supabase.rpc("obtener_top_productos_movidos", {"p_dias": dias, "p_limite": limite}).execute()
        return res.data or []
    except Exception as e:
        st.error(f"Error al cargar top productos: {e}")
        return []


def cargar_distribucion_activos():
    try:
        res = supabase.rpc("obtener_distribucion_activos", {}).execute()
        return res.data or []
    except Exception as e:
        st.error(f"Error al cargar distribución de activos: {e}")
        return []


nombre_actual  = st.session_state.get("nombre", "")
rol_actual     = st.session_state.get("rol", "")
usuario_actual = st.session_state.get("usuario", "")
iniciales      = "".join([p[0].upper() for p in nombre_actual.split()[:2]]) if nombre_actual else "AD"

st.markdown(f"""
    <div class="msh-header">
        <div class="msh-header-left">
            <div class="msh-logo-box">📈</div>
            <div>
                <div class="msh-title">MSH-Hub · Almacén · Dashboard</div>
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

# ══════════════════════════════════════════════
# KPIs PRINCIPALES
# ══════════════════════════════════════════════
total_productos = contar("almacen_productos", {"activo": True})
total_activos = contar("almacen_activos", {"activo": True})
disponibles = contar("almacen_activos", {"activo": True, "estado": "disponible"})
proyectos_activos = contar("almacen_proyectos", {"estado": "activo", "activo": True})
valor_inventario = obtener_valor_inventario()

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-card-icon">📦</div><div class="kpi-card-val">{total_productos}</div><div class="kpi-card-lbl">Productos activos</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-card-icon">🔧</div><div class="kpi-card-val">{total_activos}</div><div class="kpi-card-lbl">Activos totales</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-card-icon">🟢</div><div class="kpi-card-val">{disponibles}</div><div class="kpi-card-lbl">Activos disponibles</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-card-icon">📁</div><div class="kpi-card-val">{proyectos_activos}</div><div class="kpi-card-lbl">Proyectos activos</div></div>', unsafe_allow_html=True)
with c5:
    st.markdown(f'<div class="kpi-card"><div class="kpi-card-icon">💰</div><div class="kpi-card-val">${valor_inventario:,.0f}</div><div class="kpi-card-lbl">Valor de inventario</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# ALERTAS CONSOLIDADAS
# ══════════════════════════════════════════════
st.markdown('<div class="panel-card-titulo">⚠️ Alertas consolidadas (próximos 30 días)</div>', unsafe_allow_html=True)

col_lotes, col_mant, col_pre = st.columns(3)

with col_lotes:
    with st.container(key="panel_alerta_lotes"):
        alertas_lotes = cargar_alertas_lotes()
        st.markdown(f"**📦 Vencimientos de lotes** ({len(alertas_lotes)})")
        if not alertas_lotes:
            st.caption("Sin lotes próximos a vencer.")
        for a in alertas_lotes[:6]:
            nivel = a["nivel_alerta"]
            badge_cls = {"vencido": "badge-vencido", "critico": "badge-critico", "proximo": "badge-proximo"}.get(nivel, "badge-proximo")
            st.markdown(
                f"<div style='font-size:12px; padding:5px 0; border-bottom:1px solid #F1F5F9;'>"
                f"<b>{a['producto_codigo']}</b> — {a['producto_nombre']}<br>"
                f"<span class='badge {badge_cls}'>{a['fecha_vencimiento']}</span></div>",
                unsafe_allow_html=True
            )

with col_mant:
    with st.container(key="panel_alerta_mant"):
        alertas_mant = cargar_alertas_mantenimientos()
        st.markdown(f"**🛠️ Mantenimientos próximos** ({len(alertas_mant)})")
        if not alertas_mant:
            st.caption("Sin mantenimientos próximos.")
        for a in alertas_mant[:6]:
            nivel = a["nivel_alerta"]
            badge_cls = {"vencido": "badge-vencido", "critico": "badge-critico", "proximo": "badge-proximo"}.get(nivel, "badge-proximo")
            st.markdown(
                f"<div style='font-size:12px; padding:5px 0; border-bottom:1px solid #F1F5F9;'>"
                f"<b>{a['codigo_activo']}</b> — {a['producto_nombre']}<br>"
                f"<span class='badge {badge_cls}'>{a['proximo_mantenimiento']}</span></div>",
                unsafe_allow_html=True
            )

with col_pre:
    with st.container(key="panel_alerta_prestamos"):
        vencidos = cargar_prestamos_vencidos()
        st.markdown(f"**🤝 Préstamos vencidos** ({len(vencidos)})")
        if not vencidos:
            st.caption("Sin préstamos vencidos.")
        for p in vencidos[:6]:
            st.markdown(
                f"<div style='font-size:12px; padding:5px 0; border-bottom:1px solid #F1F5F9;'>"
                f"<span class='folio-tag'>{p['folio']}</span> — {p['persona_nombre']}<br>"
                f"<span class='badge badge-vencido'>Debía: {p['fecha_estimada']}</span></div>",
                unsafe_allow_html=True
            )

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# GRÁFICAS
# ══════════════════════════════════════════════
col_g1, col_g2 = st.columns([2, 1])

with col_g1:
    with st.container(key="panel_grafica_entradas_salidas"):
        st.markdown('<div class="panel-card-titulo">📈 Entradas vs Salidas (últimos 30 días)</div>', unsafe_allow_html=True)
        movs = cargar_movimientos_diarios(30)
        if movs:
            df_mov = pd.DataFrame(movs).set_index("fecha")
            df_mov = df_mov.rename(columns={"entradas": "Entradas", "salidas": "Salidas"})
            st.line_chart(df_mov[["Entradas", "Salidas"]], color=["#15803D", "#B91C1C"])
        else:
            st.caption("Sin movimientos en los últimos 30 días.")

with col_g2:
    with st.container(key="panel_grafica_activos_estado"):
        st.markdown('<div class="panel-card-titulo">🔧 Activos por estado</div>', unsafe_allow_html=True)
        dist = cargar_distribucion_activos()
        if dist:
            df_dist = pd.DataFrame(dist).set_index("estado")
            st.bar_chart(df_dist["total"], color="#1E3447")
        else:
            st.caption("Sin activos registrados.")

with st.container(key="panel_grafica_top_productos"):
    st.markdown('<div class="panel-card-titulo">🏆 Top 5 productos más movidos (últimos 30 días)</div>', unsafe_allow_html=True)
    top = cargar_top_productos(30, 5)
    if top:
        df_top = pd.DataFrame(top)
        df_top["etiqueta"] = df_top["producto_codigo"] + " — " + df_top["producto_nombre"]
        df_top = df_top.set_index("etiqueta")
        st.bar_chart(df_top["total_movimientos"], color="#4A90D9")
    else:
        st.caption("Sin movimientos en los últimos 30 días.")
