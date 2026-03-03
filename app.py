import streamlit as st
import pandas as pd
import uuid

st.set_page_config(page_title="Encuesta Actividades", layout="centered")

st.title("📋 Registro de Actividades")

# =============================
# Estado
# =============================
if "registros" not in st.session_state:
    st.session_state.registros = []

# =============================
# 1️⃣ Nombre (Dropdown)
# =============================
nombres_disponibles = ["Axel", "Juan", "María", "Pedro"]

nombre = st.selectbox(
    "Selecciona tu nombre",
    [""] + nombres_disponibles,
    key="nombre"
)

st.markdown("---")
st.subheader("Agregar actividad")

# =============================
# 2️⃣ Tipo de actividad (FUERA del form para que refresque dinámicamente)
# =============================
tipo_actividad = st.selectbox(
    "Tipo de actividad",
    ["POC", "Demo", "Proyecto", "Otros"],
    key="tipo_actividad"
)

# Variables default NULL
nombre_actividad = None
id_proyecto = None
nombre_proyecto = None

# =============================
# Lógica dinámica
# =============================

if tipo_actividad == "Proyecto":

    proyectos_dict = {
        1: "Rentabilidad",
        2: "Administración y Control",
        3: "Transpais",
        999: "Otros"
    }

    proyecto_opcion = st.selectbox(
        "Selecciona el proyecto",
        list(proyectos_dict.keys()),
        format_func=lambda x: proyectos_dict[x],
        key="proyecto"
    )

    id_proyecto = proyecto_opcion

    if proyecto_opcion == 999:
        nombre_proyecto = st.text_input(
            "Especifica el nombre del proyecto",
            key="otro_proyecto"
        )
    else:
        nombre_proyecto = proyectos_dict[proyecto_opcion]


elif tipo_actividad in ["POC", "Demo"]:
    nombre_actividad = st.text_input(
        f"Nombre de la {tipo_actividad}",
        key="poc_demo"
    )


elif tipo_actividad == "Otros":
    nombre_actividad = st.text_input(
        "Especifica el nombre de la actividad",
        key="otros"
    )

# =============================
# Campos comunes
# =============================
horas_actividad = st.number_input(
    "Horas por semana",
    min_value=0.0,
    step=0.5,
    key="horas"
)

desc_actividad = st.text_area(
    "Descripción de la actividad",
    key="descripcion"
)

# =============================
# Botón agregar
# =============================
if st.button("Agregar actividad"):

    if not nombre:
        st.warning("Debes seleccionar tu nombre.")
    else:

        registro = {
            "nombre": nombre,
            "tipo_actividad": tipo_actividad,
            "id_actividad": str(uuid.uuid4()),
            "nombre_actividad": nombre_actividad if nombre_actividad else None,
            "horas_actividad": horas_actividad if horas_actividad else None,
            "desc_actividad": desc_actividad if desc_actividad else None,
            "id_proyecto": id_proyecto if tipo_actividad == "Proyecto" else None,
            "nombre_proyecto": nombre_proyecto if tipo_actividad == "Proyecto" else None,
        }

        st.session_state.registros.append(registro)

        st.success("Actividad agregada correctamente ✅")
        st.rerun()

# =============================
# Mostrar tabla
# =============================
if st.session_state.registros:

    st.markdown("---")
    st.subheader("Actividades registradas")

    df = pd.DataFrame(st.session_state.registros)
    st.dataframe(df, use_container_width=True)

    total_horas = df["horas_actividad"].fillna(0).sum()
    st.markdown(f"### ⏱ Total horas semanales: **{total_horas}**")