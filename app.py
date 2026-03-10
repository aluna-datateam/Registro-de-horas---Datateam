import streamlit as st
import pandas as pd
from datetime import date
from gd_api import *

# ───────────────────────── CONFIG ─────────────────────────
st.set_page_config(
    page_title="Registro de Horas",
    page_icon="⏱️",
    layout="centered"
)

# ───────────────────────── CSS ─────────────────────────
st.markdown("""
<style>
body { background-color:#F5F3EF; }
.block-container { max-width:700px; }
.section-label{
    font-size:0.75rem;
    font-weight:600;
    letter-spacing:0.12em;
    color:#6B7280;
    margin-top:1.5rem;
}
.soft-divider{
    border:none;
    border-top:1px solid #E5E0D8;
    margin:1.5rem 0;
}
.header-card{
    background:linear-gradient(135deg,#1A1A2E,#0F3460);
    border-radius:16px;
    padding:2rem;
    margin-bottom:2rem;
    color:white;
}
.stButton>button{border-radius:10px;}
</style>
""", unsafe_allow_html=True)

# ───────────────────────── DATA HELPERS ─────────────────────────
@st.cache_data(ttl=300)
def get_empleados():
    return csv_to_df("empleados.csv")["NOMBRE"].dropna().tolist()

@st.cache_data(ttl=300)
def get_proyectos():
    return csv_to_df("proyectos.csv")["NOMBRE_PROYECTO"].dropna().tolist()

@st.cache_data(ttl=300)
def get_actividades():
    return csv_to_df("tipos_actividad.csv")["NOMBRE_TIPO"].str.strip().dropna().tolist()

# ───────────────────────── SESSION STATE ─────────────────────────
if "actividades_registro" not in st.session_state:
    st.session_state.actividades_registro = []

if "proyectos_registro" not in st.session_state:
    st.session_state.proyectos_registro = []

if "actividad_selector" not in st.session_state:
    st.session_state.actividad_selector = "Seleccionar..."

# ───────────────────────── HEADER ─────────────────────────
st.markdown("""
<div class="header-card">
<h2>⏱ Registro de Horas</h2>
<p>Registro semanal de actividades</p>
</div>
""", unsafe_allow_html=True)

# ───────────────────────── EMPLEADO ─────────────────────────
st.markdown('<div class="section-label">👤 Colaborador</div>', unsafe_allow_html=True)

busqueda = st.text_input(
    "Buscar nombre",
    placeholder="Escribe al menos 3 caracteres"
)

nombre_seleccionado = None

if len(busqueda) >= 3:

    empleados = get_empleados()

    filtrados = [
        e for e in empleados
        if busqueda.lower() in e.lower()
    ]

    if filtrados:
        nombre_seleccionado = st.selectbox(
            "Selecciona tu nombre",
            filtrados
        )

# ───────────────────────── FECHA ─────────────────────────
st.markdown('<hr class="soft-divider"/>', unsafe_allow_html=True)
st.markdown('<div class="section-label">📅 Fecha de Registro</div>', unsafe_allow_html=True)

fecha_registro = st.date_input(
    "Fecha",
    value=date.today()
)

lunes = fecha_registro - pd.Timedelta(days=fecha_registro.weekday())
viernes = lunes + pd.Timedelta(days=4)

periodo = f"Semana {lunes.strftime('%d/%m/%Y')} - {viernes.strftime('%d/%m/%Y')}"

st.caption(f"Periodo semanal: {periodo}")

# ───────────────────────── FUNCION AGREGAR ACTIVIDAD ─────────────────────────
def agregar_actividad():

    actividad = st.session_state.actividad_selector

    if actividad == "Seleccionar...":
        return

    if actividad == "Proyecto":

        st.session_state.proyectos_registro.append({
            "proyecto":"",
            "nombre":"",
            "horas":0
        })

    else:

        st.session_state.actividades_registro.append({
            "actividad":actividad,
            "nombre":"",
            "horas":0
        })

    st.session_state.actividad_selector = "Seleccionar..."

# ───────────────────────── AGREGAR ACTIVIDAD ─────────────────────────
st.markdown('<hr class="soft-divider"/>', unsafe_allow_html=True)
st.markdown('<div class="section-label">🗂 Actividades</div>', unsafe_allow_html=True)

actividades = get_actividades()

st.selectbox(
    "Agregar actividad",
    ["Seleccionar..."] + actividades,
    key="actividad_selector",
    on_change=agregar_actividad
)

# ───────────────────────── ACTIVIDADES DINAMICAS ─────────────────────────
for i, act in enumerate(st.session_state.actividades_registro):

    st.markdown(f"**{act['actividad']}**")

    nombre = st.text_input(
        "Nombre",
        key=f"act_nombre_{i}"
    )

    horas = st.number_input(
        "Horas",
        min_value=0.0,
        step=1.0,
        key=f"act_horas_{i}"
    )

    col1,col2 = st.columns([4,1])

    with col2:
        if st.button("❌", key=f"del_act_{i}"):

            st.session_state.actividades_registro.pop(i)
            st.rerun()

    st.session_state.actividades_registro[i]["nombre"] = nombre
    st.session_state.actividades_registro[i]["horas"] = horas

# ───────────────────────── PROYECTOS ─────────────────────────
if st.session_state.proyectos_registro:

    st.markdown('<hr class="soft-divider"/>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">📁 Proyectos</div>', unsafe_allow_html=True)

    lista_proyectos = get_proyectos()

    proyectos_usados = []

    for i,p in enumerate(st.session_state.proyectos_registro):

        disponibles = [
            x for x in lista_proyectos
            if x not in proyectos_usados
        ]

        proyecto = st.selectbox(
            "Proyecto",
            disponibles,
            key=f"proy_sel_{i}"
        )

        proyectos_usados.append(proyecto)

        nombre_extra = ""

        if proyecto == "Otros:":
            nombre_extra = st.text_input(
                "Nombre del proyecto",
                key=f"proy_nombre_{i}"
            )

        horas = st.number_input(
            "Horas",
            min_value=0.0,
            step=1.0,
            key=f"proy_horas_{i}"
        )

        col1,col2 = st.columns([4,1])

        with col2:
            if st.button("❌", key=f"del_proy_{i}"):

                st.session_state.proyectos_registro.pop(i)
                st.rerun()

        st.session_state.proyectos_registro[i] = {
            "proyecto":proyecto,
            "nombre":nombre_extra,
            "horas":horas
        }

# ───────────────────────── GUARDAR ─────────────────────────
st.markdown('<hr class="soft-divider"/>', unsafe_allow_html=True)

if st.button("💾 Guardar Registros", use_container_width=True):

    if not nombre_seleccionado:
        st.error("Selecciona tu nombre")
        st.stop()

    registros = []

    for a in st.session_state.actividades_registro:

        registros.append({
            "actividad":a["actividad"],
            "proyecto":"",
            "horas":a["horas"],
            "nombre":a["nombre"]
        })

    for p in st.session_state.proyectos_registro:

        nombre_proy = p["proyecto"]

        if nombre_proy == "Otro:":
            nombre_proy = p["nombre"]

        registros.append({
            "actividad":"Proyecto",
            "proyecto":nombre_proy,
            "horas":p["horas"],
            "nombre":""
        })

    try:

        for r in registros:

            agregar_registro_drive(
                empleado=nombre_seleccionado,
                actividad=r["actividad"],
                proyecto=r["proyecto"],
                horas_actividad=r["horas"],
                desc_actividad=r["nombre"],
                fecha_registro=str(fecha_registro),
                periodo=periodo
            )

        st.success(f"{len(registros)} registros guardados")

        st.session_state.actividades_registro = []
        st.session_state.proyectos_registro = []

        st.rerun()

    except Exception as e:

        st.error(e)

# ───────────────────────── FOOTER ─────────────────────────
st.markdown(
    "<p style='text-align:center;color:#C4BDB3;font-size:0.8rem;'>Data Team · Registro de Horas</p>",
    unsafe_allow_html=True
)
