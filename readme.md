# 📋 Registro de Actividades - Streamlit App

Aplicación web desarrollada con Streamlit para registrar actividades semanales por colaborador.

Permite capturar:

- Nombre del colaborador
- Tipo de actividad (POC, Demo, Proyecto, Otros)
- Proyecto asociado (si aplica)
- Horas dedicadas por semana
- Descripción de la actividad
- ID único automático por registro

---

## 🚀 Demo

Esta aplicación está diseñada para desplegarse en **Streamlit Community Cloud** y puede ejecutarse localmente o en la nube sin necesidad de autenticación.

---

## 🧠 Funcionalidades

### ✔ Selección de usuario
Dropdown con lista de nombres disponibles.

### ✔ Lógica dinámica según tipo de actividad

- **Proyecto**
  - Selección desde catálogo
  - Campo adicional si es "Otros"
- **POC / Demo**
  - Campo libre para nombre
- **Otros**
  - Campo libre

### ✔ Registro en sesión
Los datos se almacenan en `st.session_state`.

### ✔ Visualización en tabla
- Tabla dinámica con todos los registros
- Cálculo automático de total de horas semanales

---

## 📦 Estructura del Proyecto
