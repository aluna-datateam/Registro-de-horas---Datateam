import dataikuapi
import pandas as pd

client = dataikuapi.DSSClient("http://100.83.125.9:11000", "dkuaps-eIZgCHzWNpcbFiVuffXLXvlPiEmIiVd5")
project = client.get_project("REGISTRODEHORASDATATEAM")

def insert_registro(
    nombre_empleado,
    tipo_actividad,
    nombre_proyecto,
    horas_actividad,
    desc_actividad,
    fecha_registro,
    periodo
):
    
    query = f"""
    INSERT INTO registro_horas_bd (
        ID_REGISTRO,
        NOMBRE_EMPLEADO,
        TIPO_ACTIVIDAD,
        NOMBRE_PROYECTO,
        HORAS_ACTIVIDAD,
        DESC_ACTIVIDAD,
        FECHA_REGISTRO,
        PERIODO
    )
    VALUES (
        NULL,
        '{nombre_empleado}',
        '{tipo_actividad}',
        '{nombre_proyecto}',
        {horas_actividad},
        '{desc_actividad}',
        '{fecha_registro}',
        '{periodo}'
    )
    """
    print(query)

    client.sql_query(
        query,
        connection="DATATEAM",
        post_queries=["COMMIT"]
    )

    print("✅ Registro insertado correctamente")


def query_to_df(dataset_name):
    dataset = client.sql_query(
            f"SELECT * FROM {dataset_name}",
            connection="DATATEAM"
        )

    print(dataset.get_schema())
    # Obtener esquema para columnas
    schema = dataset.get_schema()
    columns = [col['name'] for col in schema]

    # Iterar filas
    rows = []
    for row in dataset.iter_rows():
        rows.append(row)
    df = pd.DataFrame(rows, columns=columns)

    return df


def ds_to_df(dataset_name):
    dataset = project.get_dataset(dataset_name)

    # Obtener esquema para columnas
    schema = dataset.get_schema()['columns']
    columns = [col['name'] for col in schema]

    # Iterar filas
    rows = []
    for row in dataset.iter_rows():
        rows.append(row)
    df = pd.DataFrame(rows, columns=columns)

    return df

