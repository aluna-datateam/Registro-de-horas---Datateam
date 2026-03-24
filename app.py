import streamlit as st
import pandas as pd
from datetime import date
from gd_api import *
import time

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
proyectos_usados = []

for i, r in enumerate(st.session_state.registros):

    st.markdown("---")

    col_f1, col_f2 = st.columns(2)

    with col_f1:
        fecha_inicio = st.date_input(
            "Inicio",
            value=r["fecha_inicio"] or date.today(),
            key=f"fi_{i}"
        )

    with col_f2:
        fecha_fin = st.date_input(
            "Fin",
            value=r["fecha_fin"] or date.today(),
            key=f"ff_{i}"
        )

    if r["tipo"] == "actividad":

        st.markdown(f"**{r['actividad']}**")

        nombre = st.text_input("Nombre", key=f"nombre_{i}")
        horas = st.number_input("Horas", min_value=0.0, step=1.0, key=f"horas_{i}")

        st.session_state.registros[i].update({
            "nombre": nombre,
            "horas": horas,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        })

    else:

        disponibles = [p for p in lista_proyectos if p not in proyectos_usados]

        proyecto = st.selectbox(
            "Proyecto",
            disponibles,
            key=f"proyecto_{i}"
        )

        proyectos_usados.append(proyecto)

        nombre_extra = ""
        if proyecto == "Otros:":
            nombre_extra = st.text_input("Nombre del proyecto", key=f"nombre_proy_{i}")

        horas = st.number_input("Horas", min_value=0.0, step=1.0, key=f"horas_proy_{i}")
        nombre = st.text_input("Descripción", key=f"desc_proy_{i}")

        st.session_state.registros[i] = {
            "tipo": "proyecto",
            "actividad": "",
            "proyecto": proyecto if proyecto != "Otros:" else nombre_extra,
            "nombre": nombre,
            "horas": horas,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        }

    if st.button("🗑 Eliminar", key=f"del_{i}"):
        st.session_state.registros.pop(i)
        st.rerun()

# ───────────────────────── AGREGAR ITEM ─────────────────────────
def agregar_item():
    val = st.session_state.actividad_selector

    if val == "Seleccionar...":
        return

    base = {
        "tipo": "actividad" if val != "Proyecto" else "proyecto",
        "actividad": val if val != "Proyecto" else "",
        "proyecto": "",
        "nombre": "",
        "horas": 0,
        "fecha_inicio": None,
        "fecha_fin": None
    }

    st.session_state.registros.append(base)
    st.session_state.actividad_selector = "Seleccionar..."

actividades = get_actividades()

st.selectbox(
    "Agregar actividad o proyecto",
    ["Seleccionar..."] + actividades,
    key="actividad_selector",
    on_change=agregar_item
)

# ───────────────────────── GUARDAR ─────────────────────────
if st.button("💾 Guardar", use_container_width=True):

    if not nombre_seleccionado:
        st.error("Selecciona tu nombre")
        st.stop()

    if not st.session_state.registros:
        st.error("Debes agregar al menos un registro")
        st.stop()

    for i, r in enumerate(st.session_state.registros):

        if r["horas"] <= 0:
            st.error(f"Registro {i+1}: horas inválidas")
            st.stop()

        if not r["fecha_inicio"] or not r["fecha_fin"]:
            st.error(f"Registro {i+1}: fechas requeridas")
            st.stop()

        if r["fecha_inicio"] > r["fecha_fin"]:
            st.error(f"Registro {i+1}: rango de fechas inválido")
            st.stop()

        if not r["nombre"] or not r["nombre"].strip():
            st.error(f"Registro {i+1}: debes capturar la descripción")
            st.stop()

        if r["tipo"] == "proyecto" and not r["proyecto"].strip():
            st.error(f"Registro {i+1}: falta proyecto")
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

# ───────────────────────── RESUMEN ─────────────────────────
if st.session_state.ultimo_guardado:

    data = st.session_state.ultimo_guardado["data"]
    total = st.session_state.ultimo_guardado["total"]
    total_horas = sum(r["horas"] for r in data)

    st.success(f"Se guardaron {total} registros · {total_horas}h")

    for r in data:

        col1, col2 = st.columns([6, 1])

        with col1:
            if r["tipo"] == "actividad":
                st.markdown(f"**{r['actividad']}**")
                st.caption(f"{r['nombre']} · {r['fecha_inicio']} → {r['fecha_fin']}")
            else:
                st.markdown("**Proyecto**")
                st.caption(f"{r['proyecto']} · {r['fecha_inicio']} → {r['fecha_fin']}")

        with col2:
            st.markdown(f"**{r['horas']}h**")

        st.divider()
