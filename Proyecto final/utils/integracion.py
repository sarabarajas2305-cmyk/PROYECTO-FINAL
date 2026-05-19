"""
integracion.py
Módulo para integrar los 4 DataFrames usando claves comunes.
"""

import pandas as pd


def detectar_columna_id(df: pd.DataFrame, posibles: list) -> str:
    """
    Detecta automáticamente la columna ID en un DataFrame.
    Parámetros:
        df: DataFrame donde buscar
        posibles: lista de posibles nombres de columna
    Retorna:
        Nombre de la columna encontrada o None
    """
    cols_lower = {c.lower(): c for c in df.columns}
    for p in posibles:
        if p.lower() in cols_lower:
            return cols_lower[p.lower()]
    return None


def integrar_datos(
    df_estudiantes: pd.DataFrame,
    df_matriculas: pd.DataFrame,
    df_espacios: pd.DataFrame,
    df_asistencia: pd.DataFrame
) -> pd.DataFrame:
    """
    Integra los 4 DataFrames usando claves comunes.
    Parámetros:
        df_estudiantes, df_matriculas, df_espacios, df_asistencia
    Retorna:
        DataFrame integrado
    """
    posibles_id = ["id_estudiante", "id", "codigo_estudiante",
                   "estudiante_id", "cedula", "documento", "id_alumno"]
    posibles_materia = ["codigo_materia", "materia", "codigo_espacio",
                        "espacio", "id_materia", "asignatura"]

    id_est         = detectar_columna_id(df_estudiantes, posibles_id)
    id_mat_est     = detectar_columna_id(df_matriculas,  posibles_id)
    id_materia_mat = detectar_columna_id(df_matriculas,  posibles_materia)
    id_materia_esp = detectar_columna_id(df_espacios,    posibles_materia)
    id_est_asis    = detectar_columna_id(df_asistencia,  posibles_id)

    if id_est and id_mat_est:
        df_base = pd.merge(
            df_estudiantes, df_matriculas,
            left_on=id_est, right_on=id_mat_est,
            how="left", suffixes=("", "_matricula")
        )
    else:
        df_base = df_estudiantes.copy()

    if id_materia_mat and id_materia_esp:
        df_base = pd.merge(
            df_base, df_espacios,
            left_on=id_materia_mat, right_on=id_materia_esp,
            how="left", suffixes=("", "_espacio")
        )

    if id_est and id_est_asis:
        df_base = pd.merge(
            df_base, df_asistencia,
            left_on=id_est, right_on=id_est_asis,
            how="left", suffixes=("", "_asistencia")
        )

    return df_base


def obtener_resumen(df: pd.DataFrame) -> dict:
    """
    Genera un resumen básico del DataFrame integrado.
    Parámetros:
        df: DataFrame integrado
    Retorna:
        Diccionario con métricas de resumen
    """
    return {
        "total_registros": len(df),
        "total_columnas": len(df.columns),
        "columnas_con_nulos": int(df.isnull().any().sum()),
        "porcentaje_completo": round((1 - df.isnull().mean().mean()) * 100, 2)
    }