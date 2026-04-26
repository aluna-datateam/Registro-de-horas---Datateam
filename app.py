import streamlit as st
import pandas as pd
from gd_api import *
import time

from datetime import date, datetime, time as dt_time

def hora_media_hora_anterior():
    now = datetime.now()
    minutos = 0 if now.minute < 30 else 30
    return dt_time(now.hour, minutos)

# ───────────────────────── CONFIG ─────────────────────────
st.set_page_config(page_title="Registro de Horas", page_icon="⏱️", layout="centered")

# ───────────────────────── STATE ─────────────────────────
if "registros" not in st.session_state:
    st.session_state.registros = []

if "actividad_selector" not in st.session_state:
    st.session_state.actividad_selector = "Seleccionar..."

if "ultimo_guardado" not in st.session_state:
    st.session_state.ultimo_guardado = None

# ───────────────────────── HELPERS ─────────────────────────
@st.cache_data(ttl=300)
def get_empleados():
    return csv_to_df("empleados.csv")["NOMBRE"].dropna().tolist()

@st.cache_data(ttl=300)
def get_proyectos():
    return csv_to_df("proyectos.csv")["NOMBRE_PROYECTO"].dropna().tolist()

@st.cache_data(ttl=300)
def get_actividades():
    return csv_to_df("tipos_actividad.csv")["NOMBRE_TIPO"].str.strip().dropna().tolist()

# ───────────────────────── HEADER ─────────────────────────
st.title("⏱ Registro de Horas")

# ───────────────────────── EMPLEADO ─────────────────────────
busqueda = st.text_input("Buscar nombre")
nombre_seleccionado = None

if len(busqueda) >= 3:
    empleados = get_empleados()
    filtrados = [e for e in empleados if busqueda.lower() in e.lower()]
    if filtrados:
        nombre_seleccionado = st.selectbox("Selecciona tu nombre", filtrados)

# ───────────────────────── RENDER ─────────────────────────
lista_proyectos = get_proyectos()

default_time = hora_media_hora_anterior()

for i, r in enumerate(st.session_state.registros):

    st.markdown("---")

    actividad = r["actividad"]

    # 👇 TÍTULO
    st.markdown(f"### {actividad}")

    # ─────────────── HORAS DE CONSULTORÍA (SOPORTE) ───────────────
    if actividad == "Horas de consultoría (Soporte)":

        fecha = st.date_input(
            "Fecha",
            value=date.today(),
            key=f"f_{i}"
        )

        col1, col2 = st.columns(2)

        with col1:
            hora_i = st.time_input(
                "Hora inicio",
                value=default_time,
                step=1800,
                key=f"ti_{i}"
            )

        with col2:
            hora_f = st.time_input(
                "Hora fin",
                value=default_time,
                step=1800,
                key=f"tf_{i}"
            )

        inicio = datetime.combine(fecha, hora_i)
        fin = datetime.combine(fecha, hora_f)

        horas_calc = 0
        if fin > inicio:
            horas_calc = (fin - inicio).total_seconds() / 3600
            st.info(f"Horas calculadas: {round(horas_calc, 2)}h")
        else:
            st.warning("La hora fin debe ser mayor a la de inicio")

        proyecto = st.selectbox(
            "Proyecto",
            lista_proyectos,
            key=f"proy_{i}"
        )

        descripcion = st.text_input("Descripción", key=f"desc_{i}")

        st.session_state.registros[i] = {
            "tipo": "actividad",
            "actividad": actividad,
            "proyecto": proyecto,
            "nombre": descripcion,
            "horas": horas_calc,
            "fecha_inicio": inicio,
            "fecha_fin": fin
        }

    # ─────────────── ASIGNACIÓN FIJA ───────────────
    elif actividad == "Asignación Fija":

        fecha = st.date_input(
            "Fecha",
            value=date.today(),
            key=f"f_{i}"
        )

        proyecto = st.selectbox(
            "Proyecto",
            lista_proyectos,
            key=f"proy_{i}"
        )

        descripcion = st.text_input("Descripción", key=f"desc_{i}")

        horas = st.number_input(
            "Horas",
            min_value=0.0,
            step=1.0,
            key=f"horas_{i}"
        )

        st.session_state.registros[i] = {
            "tipo": "actividad",
            "actividad": actividad,
            "proyecto": proyecto,
            "nombre": descripcion,
            "horas": horas,
            "fecha_inicio": fecha,
            "fecha_fin": fecha
        }

    # ─────────────── RESTO DE ACTIVIDADES ───────────────
    elif actividad == "Proyecto":

        col_f1, col_f2 = st.columns(2)
        proyecto = st.selectbox(
            "Proyecto",
            lista_proyectos,
            key=f"proy_{i}"
        )
        with col_f1:
            fecha_inicio = st.date_input(
                "Inicio",
                value=date.today(),
                key=f"fi_{i}"
            )

        with col_f2:
            fecha_fin = st.date_input(
                "Fin",
                value=date.today(),
                key=f"ff_{i}"
            )

        descripcion = st.text_input("Descripción", key=f"desc_{i}")

        horas = st.number_input(
            "Horas",
            min_value=0.0,
            step=1.0,
            key=f"horas_{i}"
        )

        st.session_state.registros[i] = {
            "tipo": "actividad",
            "actividad": actividad,
            "proyecto": proyecto,
            "nombre": descripcion,
            "horas": horas,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        }

    else:

        col_f1, col_f2 = st.columns(2)

        with col_f1:
            fecha_inicio = st.date_input(
                "Inicio",
                value=date.today(),
                key=f"fi_{i}"
            )

        with col_f2:
            fecha_fin = st.date_input(
                "Fin",
                value=date.today(),
                key=f"ff_{i}"
            )

        descripcion = st.text_input("Descripción", key=f"desc_{i}")

        horas = st.number_input(
            "Horas",
            min_value=0.0,
            step=1.0,
            key=f"horas_{i}"
        )

        st.session_state.registros[i] = {
            "tipo": "actividad",
            "actividad": actividad,
            "proyecto": "",
            "nombre": descripcion,
            "horas": horas,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        }

    # ─────────────── ELIMINAR ───────────────
    if st.button("🗑 Eliminar", key=f"del_{i}"):
        st.session_state.registros.pop(i)
        st.rerun()

# ───────────────────────── AGREGAR ─────────────────────────
def agregar_item():
    val = st.session_state.actividad_selector
    if val != "Seleccionar...":
        st.session_state.registros.append({
            "tipo": "actividad",
            "actividad": val,
            "proyecto": "",
            "nombre": "",
            "horas": 0,
            "fecha_inicio": None,
            "fecha_fin": None
        })
        st.session_state.actividad_selector = "Seleccionar..."

st.selectbox(
    "Agregar actividad",
    ["Seleccionar..."] + get_actividades(),
    key="actividad_selector",
    on_change=agregar_item
)

# ───────────────────────── GUARDAR ─────────────────────────
if st.button("💾 Guardar", use_container_width=True):

# VALIDACIONES
    if not nombre_seleccionado:
        st.error("Selecciona tu nombre")
        st.stop()

    if not st.session_state.registros:
        st.error("Debes agregar al menos una actividad o proyecto")
        st.stop()
        
    for i, r in enumerate(st.session_state.registros):

        if r["horas"] <= 0:
            st.error(f"Registro {i+1}: Se deben agregar horas en el registro.")
            st.stop()

        if r["tipo"] == "actividad":
            if not r["nombre"] or r["nombre"].strip() == "":
                st.error(f"Registro {i+1}: debes capturar el nombre de la actividad")
                st.stop()

        if r["tipo"] == "proyecto":
            if not r["proyecto"] or r["proyecto"].strip() == "":
                st.error(f"Registro {i+1}: debes seleccionar o capturar el proyecto")
                st.stop()

    progress = st.progress(0)

    try:
        with st.spinner("Guardando registros..."):

            total = len(st.session_state.registros)

            resumen = []

            for i, r in enumerate(st.session_state.registros):

                agregar_registro_drive(
                    empleado=nombre_seleccionado,
                    actividad=r["actividad"] if r["tipo"] == "actividad" else "Proyecto",
                    proyecto=r["proyecto"],
                    horas_actividad=r["horas"],
                    desc_actividad=r["nombre"],
                    fecha_registro=str(r["fecha_fin"]),
                    periodo=str(r["fecha_inicio"])
                )

                resumen.append(r)
                progress.progress((i + 1) / total)
                time.sleep(0.05)

        st.session_state.ultimo_guardado = {
            "total": total,
            "data": resumen
        }

        st.session_state.registros = []
        st.rerun()

    except Exception as e:
        st.error(e)

# ───────────────────────── RESUMEN  ─────────────────────────
if st.session_state.ultimo_guardado:

    data = st.session_state.ultimo_guardado["data"]
    total = st.session_state.ultimo_guardado["total"]
    total_horas = sum(r["horas"] for r in data)

    with st.container():
        st.success(f"Se guardaron {total} registros · {total_horas}h")

        for r in data:

            col1, col2 = st.columns([6, 1])

            with col1:
                if r["tipo"] == "actividad":
                    st.markdown(f"**{r['actividad']}**")
                    if r["nombre"]:
                        st.caption(r["nombre"])
                else:
                    st.markdown("**Proyecto**")
                    st.caption(r["proyecto"])

            with col2:
                st.markdown(f"**{r['horas']}h**")

            st.divider()