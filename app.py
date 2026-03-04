import streamlit as st
import pandas as pd
import uuid
from datetime import datetime, date
from gd_api import *

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Registro de Horas",
    page_icon="⏱️",
    layout="centered",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #F5F3EF;
    color: #1A1A1A;
}

.main .block-container {
    max-width: 680px;
    padding: 2.5rem 2rem 4rem 2rem;
}

h1, h2, h3 {
    font-family: 'DM Serif Display', serif;
}

/* Header card */
.header-card {
    background: linear-gradient(135deg, #1A1A2E 0%, #16213E 60%, #0F3460 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    color: white;
    box-shadow: 0 8px 32px rgba(15,52,96,0.25);
}
.header-card h1 {
    color: white;
    font-size: 2rem;
    margin: 0 0 0.25rem 0;
}
.header-card p {
    color: rgba(255,255,255,0.65);
    margin: 0;
    font-size: 0.95rem;
    font-weight: 300;
}

/* Section labels */
.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6B7280;
    margin-bottom: 0.5rem;
    margin-top: 1.5rem;
}

/* Divider */
.soft-divider {
    border: none;
    border-top: 1px solid #E5E0D8;
    margin: 1.75rem 0;
}

/* Success / error banners */
.success-banner {
    background: #ECFDF5;
    border-left: 4px solid #10B981;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    color: #065F46;
    font-weight: 500;
    margin-top: 1rem;
}
.error-banner {
    background: #FEF2F2;
    border-left: 4px solid #EF4444;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    color: #991B1B;
    font-weight: 500;
    margin-top: 1rem;
}

/* Streamlit widget overrides */
div[data-baseweb="select"] > div {
    border-radius: 10px !important;
    border-color: #D1CAC0 !important;
    background: white !important;
}
div[data-baseweb="input"] > div {
    border-radius: 10px !important;
    border-color: #D1CAC0 !important;
    background: white !important;
}
textarea {
    border-radius: 10px !important;
    border-color: #D1CAC0 !important;
    background: white !important;
}

/* Primary button */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0F3460, #1A1A2E);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.65rem 2.5rem;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    letter-spacing: 0.03em;
    transition: all 0.2s ease;
    width: 100%;
    margin-top: 0.5rem;
}
.stButton > button[kind="primary"]:hover {
    opacity: 0.88;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(15,52,96,0.3);
}

/* Number input */
input[type="number"] {
    border-radius: 10px !important;
}

/* Info hint */
.hint-text {
    font-size: 0.8rem;
    color: #9CA3AF;
    margin-top: -0.4rem;
    margin-bottom: 0.75rem;
}
</style>
""", unsafe_allow_html=True)



# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_empleados():
    return csv_to_df("empleados.csv")["NOMBRE"].dropna().tolist()

@st.cache_data(ttl=300)
def get_proyectos():
    return csv_to_df("proyectos.csv")["NOMBRE_PROYECTO"].dropna().tolist()

@st.cache_data(ttl=300)
def get_actividades():
    return csv_to_df("tipos_actividad.csv")["NOMBRE_TIPO"].dropna().tolist()


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "error_msg" not in st.session_state:
    st.session_state.error_msg = ""
if "nombre_busqueda" not in st.session_state:
    st.session_state.nombre_busqueda = ""

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-card">
    <h1>⏱ Registro de Horas</h1>
    <p>Registra tus horas de trabajo por día o por mes de forma rápida y sencilla.</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FORMULARIO
# ─────────────────────────────────────────────

# ── 1. EMPLEADO ──────────────────────────────
st.markdown('<div class="section-label">👤 Colaborador</div>', unsafe_allow_html=True)

busqueda = st.text_input(
    "Escribe tu nombre (mínimo 3 caracteres)",
    placeholder="Ej: Axe...",
    key="nombre_busqueda",
    label_visibility="collapsed"
)

nombre_seleccionado = None

if len(busqueda) >= 3:
    try:
        todos_empleados = get_empleados()
        filtrados = [n for n in todos_empleados if busqueda.lower() in n.lower()]
        if filtrados:
            nombre_seleccionado = st.selectbox(
                "Selecciona tu nombre",
                options=filtrados,
                key="empleado_select"
            )
        else:
            st.markdown('<div class="hint-text">⚠️ No se encontraron coincidencias.</div>', unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"No se pudo cargar la lista de empleados: {e}")
elif len(busqueda) > 0:
    st.markdown('<div class="hint-text">Escribe al menos 3 caracteres para buscar.</div>', unsafe_allow_html=True)

st.markdown('<hr class="soft-divider"/>', unsafe_allow_html=True)

# ── 2. FECHA Y PERIODO ───────────────────────
st.markdown('<div class="section-label">📅 Fecha y Período</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    fecha_registro = st.date_input(
        "Fecha de registro",
        value=date.today(),
        key="fecha"
    )
with col2:
    tipo_periodo = st.selectbox(
        "Tipo de período",
        options=["Día", "Semana"],
        key="tipo_periodo"
    )

if tipo_periodo == "Semana":
    # Calcular el lunes de la semana correspondiente a la fecha elegida
    lunes = fecha_registro - pd.Timedelta(days=fecha_registro.weekday())
    viernes = lunes + pd.Timedelta(days=4)
    periodo = f"Semana {lunes.strftime('%d/%m/%Y')} - {viernes.strftime('%d/%m/%Y')}"
    st.markdown(
        f'<div class="hint-text">📆 Semana: {lunes.strftime("%d/%m/%Y")} al {viernes.strftime("%d/%m/%Y")}</div>',
        unsafe_allow_html=True
    )
else:
    periodo = str(fecha_registro)

st.markdown('<hr class="soft-divider"/>', unsafe_allow_html=True)

# ── 3. ACTIVIDAD ─────────────────────────────
st.markdown('<div class="section-label">🗂 Tipo de Actividad</div>', unsafe_allow_html=True)

try:
    lista_actividades = get_actividades()
except Exception:
    lista_actividades = []

opciones_actividad = lista_actividades
actividad_sel = st.selectbox(
    "Selecciona el tipo de actividad",
    options=opciones_actividad,
    key="actividad_sel",
    label_visibility="collapsed"
)

actividad_custom = ""
if actividad_sel == "Otro:":
    actividad_custom = st.text_input(
        "Especifica la actividad",
        placeholder="Nombre de la actividad…",
        key="actividad_custom"
    )
    tipo_actividad_final = f"Otro: {actividad_custom}" if actividad_custom.strip() else "Otro:"
else:
    tipo_actividad_final = actividad_sel

# ── 4. PROYECTO (solo si actividad = Proyecto) ─
nombre_proyecto_final = ""

if actividad_sel == "Proyecto":
    st.markdown('<hr class="soft-divider"/>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">📁 Proyecto</div>', unsafe_allow_html=True)

    try:
        lista_proyectos = get_proyectos()
    except Exception:
        lista_proyectos = []

    opciones_proyecto = lista_proyectos
    proyecto_sel = st.selectbox(
        "Selecciona el proyecto",
        options=opciones_proyecto,
        key="proyecto_sel",
        label_visibility="collapsed"
    )

    if proyecto_sel == "Otros:":
        proyecto_custom = st.text_input(
            "Especifica el nombre del proyecto",
            placeholder="Nombre del proyecto…",
            key="proyecto_custom"
        )
        nombre_proyecto_final = f"Otro: {proyecto_custom}" if proyecto_custom.strip() else "Otro:"
    else:
        nombre_proyecto_final = proyecto_sel

st.markdown('<hr class="soft-divider"/>', unsafe_allow_html=True)

# ── 5. HORAS ─────────────────────────────────
st.markdown('<div class="section-label">⏳ Horas Trabajadas</div>', unsafe_allow_html=True)

horas = st.number_input(
    "Horas",
    min_value=0.0,
    max_value=744.0,
    step=0.5,
    value=8.0,
    format="%.1f",
    key="horas",
    label_visibility="collapsed"
)

st.markdown('<hr class="soft-divider"/>', unsafe_allow_html=True)

# ── 6. DESCRIPCION ───────────────────────────
st.markdown('<div class="section-label">📝 Descripción (opcional)</div>', unsafe_allow_html=True)

descripcion = st.text_area(
    "Descripción",
    placeholder="Breve descripción de las actividades realizadas…",
    height=100,
    key="descripcion",
    label_visibility="collapsed"
)

st.markdown("<br/>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# VALIDACIÓN Y GUARDADO
# ─────────────────────────────────────────────
def validar():
    if not nombre_seleccionado:
        return "Debes seleccionar tu nombre de la lista."
    if actividad_sel == "Otro:" and not actividad_custom.strip():
        return "Escribe el nombre de la actividad personalizada."
    if actividad_sel == "Proyecto" and not nombre_proyecto_final:
        return "Debes seleccionar o especificar un proyecto."
    if actividad_sel == "Proyecto" and nombre_proyecto_final == "Otro:" :
        return "Escribe el nombre del proyecto personalizado."
    if horas <= 0:
        return "Las horas deben ser mayores a 0."
    return None

if st.button("💾  Guardar Registro", type="primary", use_container_width=True):
    error = validar()
    if error:
        st.markdown(f'<div class="error-banner">⚠️ {error}</div>', unsafe_allow_html=True)
    else:
        try:
            id_reg = str(uuid.uuid4())
            agregar_registro_drive(
                empleado=nombre_seleccionado,
                actividad=tipo_actividad_final,
                proyecto=nombre_proyecto_final,
                horas_actividad=horas,
                desc_actividad=descripcion.replace("'", "''"),
                fecha_registro=str(fecha_registro),
                periodo=periodo
            )
            st.markdown("""
            <div class="success-banner">
                ✅ ¡Registro guardado exitosamente! Puedes capturar otro registro cuando quieras.
            </div>
            """, unsafe_allow_html=True)
            # Limpiar campos de texto editables manteniendo defaults
            st.rerun()
        except Exception as e:
            st.markdown(f'<div class="error-banner">❌ Error al guardar: {e}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("<br/><br/>", unsafe_allow_html=True)
st.markdown(
    '<p style="text-align:center;color:#C4BDB3;font-size:0.78rem;">Data Team · Registro de Horas</p>',
    unsafe_allow_html=True
)
