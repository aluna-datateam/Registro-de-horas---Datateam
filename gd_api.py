from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import pandas as pd
from googleapiclient.http import MediaIoBaseUpload

import streamlit as st

import tempfile
import io

# =====================================================
# CONFIGURACIÓN
# =====================================================
SERVICE_ACCOUNT_FILE = "agile-binder-466615-v4-5a3244f57ef1.json"
SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER_NAME = "RegistroHoras"
LOCAL_DOWNLOAD_PATH = "drive_downloads"

os.makedirs(LOCAL_DOWNLOAD_PATH, exist_ok=True)

# =====================================================
# AUTENTICACIÓN
# =====================================================
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)

service = build("drive", "v3", credentials=creds)
pk = st.secrets["gcp_service_account"]["private_key"]

print(pk)
# =====================================================
# DESCARGA AUTOMÁTICA AL INICIAR SCRIPT
# =====================================================
def _download_all_csvs():
    # Buscar ID de carpeta
    query_folder = f"name = '{FOLDER_NAME}' and mimeType = 'application/vnd.google-apps.folder'"
    results = service.files().list(q=query_folder, fields="files(id)").execute()
    folders = results.get("files", [])

    if not folders:
        raise Exception("Carpeta RegistroHoras no encontrada o no compartida.")

    folder_id = folders[0]["id"]

    # Buscar CSV dentro de la carpeta
    query_files = f"'{folder_id}' in parents and mimeType = 'text/csv'"
    results = service.files().list(q=query_files, fields="files(id, name)").execute()
    files = results.get("files", [])

    for file in files:
        file_id = file["id"]
        file_name = file["name"]
        local_path = os.path.join(LOCAL_DOWNLOAD_PATH, file_name)

        request = service.files().get_media(fileId=file_id)
        file_content = request.execute()

        with open(local_path, "wb") as f:
            f.write(file_content)

        print(f"✅ Descargado: {file_name}")


# Ejecutar descarga automática
_download_all_csvs()


# =====================================================
# ÚNICA FUNCIÓN PÚBLICA
# =====================================================
def csv_to_df(nombre_archivo):
    """
    Lee un CSV previamente descargado desde la carpeta RegistroHoras
    y lo convierte en DataFrame.
    
    Parámetro:
        nombre_archivo (str): Ejemplo 'archivo1.csv'
        
    Retorna:
        pandas.DataFrame
    """
    ruta = os.path.join(LOCAL_DOWNLOAD_PATH, nombre_archivo)

    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No existe el archivo {nombre_archivo}")

    return pd.read_csv(ruta)

df = csv_to_df("empleados.csv")


def agregar_registro_drive(
    empleado,
    actividad,
    proyecto,
    horas_actividad,
    desc_actividad,
    fecha_registro,
    periodo
):
    """
    Agrega un nuevo registro al archivo registro_horas.csv en Google Drive.
    El ID_REGISTRO se autoincrementa automáticamente.
    """

    nombre_archivo = "registro_horas.csv"

    # 🔍 Buscar ID de carpeta
    query_folder = f"name = '{FOLDER_NAME}' and mimeType = 'application/vnd.google-apps.folder'"
    results = service.files().list(q=query_folder, fields="files(id)").execute()
    folders = results.get("files", [])

    if not folders:
        raise Exception("Carpeta RegistroHoras no encontrada.")

    folder_id = folders[0]["id"]

    # 🔍 Buscar archivo
    query_file = f"name = '{nombre_archivo}' and '{folder_id}' in parents"
    results = service.files().list(q=query_file, fields="files(id)").execute()
    files = results.get("files", [])

    if not files:
        raise FileNotFoundError("registro_horas.csv no encontrado en Drive.")

    file_id = files[0]["id"]

    # 📥 Descargar archivo
    request = service.files().get_media(fileId=file_id)
    file_content = request.execute()
    df = pd.read_csv(io.BytesIO(file_content), encoding="utf-8")

    # 🔢 Calcular siguiente ID
    if df.empty:
        nuevo_id = 1
    else:
        nuevo_id = df["ID_REGISTRO"].max() + 1

    # ➕ Crear nuevo registro
    nuevo_registro = {
        "ID_REGISTRO": nuevo_id,
        "EMPLEADO": empleado,
        "ACTIVIDAD": actividad,
        "PROYECTO": proyecto,
        "HORAS_ACTIVIDAD": horas_actividad,
        "DESC_ACTIVIDAD": desc_actividad,
        "FECHA_REGISTRO": fecha_registro,
        "PERIODO": periodo
    }
    print(df)
    df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
    print("-"*50)
    print(df)
    # 💾 Guardar temporalmente
    csv_buffer = io.BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    media = MediaIoBaseUpload(
        csv_buffer,
        mimetype="text/csv",
        resumable=True
    )

    service.files().update(
        fileId=file_id,
        media_body=media
    ).execute()

    print(f"✅ Registro agregado correctamente con ID {nuevo_id}")




