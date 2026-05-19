"""
carga_datos.py
Módulo para leer los 4 archivos del sistema académico.
Formatos: Excel (.xlsx), CSV (.csv), JSON (.json), PRN (.prn)
"""

import pandas as pd
import json


def cargar_estudiantes(archivo_xlsx) -> pd.DataFrame:
    """
    Lee el archivo de estudiantes en formato Excel.
    Parámetros:
        archivo_xlsx: objeto de archivo subido por Streamlit
    Retorna:
        DataFrame con datos de estudiantes
    """
    try:
        df = pd.read_excel(archivo_xlsx)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        raise ValueError(f"Error al leer estudiantes.xlsx: {e}")


def cargar_matriculas(archivo_csv) -> pd.DataFrame:
    """
    Lee el archivo de matrículas en formato CSV.
    Parámetros:
        archivo_csv: objeto de archivo subido por Streamlit
    Retorna:
        DataFrame con datos de matrículas
    """
    try:
        df = pd.read_csv(archivo_csv, encoding="utf-8")
        df.columns = df.columns.str.strip()
        return df
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(archivo_csv, encoding="latin-1")
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            raise ValueError(f"Error al leer Matriculas.csv: {e}")
    except Exception as e:
        raise ValueError(f"Error al leer Matriculas.csv: {e}")


def cargar_espacios(archivo_json) -> pd.DataFrame:
    """
    Lee el archivo de espacios académicos en formato JSON.
    Parámetros:
        archivo_json: objeto de archivo subido por Streamlit
    Retorna:
        DataFrame con datos de espacios académicos
    """
    try:
        datos = json.load(archivo_json)
        if isinstance(datos, list):
            df = pd.DataFrame(datos)
        elif isinstance(datos, dict):
            for clave, valor in datos.items():
                if isinstance(valor, list):
                    df = pd.DataFrame(valor)
                    break
            else:
                df = pd.DataFrame([datos])
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        raise ValueError(f"Error al leer EspaciosAcademicos.json: {e}")


def cargar_asistencia(archivo_prn) -> pd.DataFrame:
    """
    Lee el archivo de asistencia en formato PRN.
    Parámetros:
        archivo_prn: objeto de archivo subido por Streamlit
    Retorna:
        DataFrame con datos de asistencia
    """
    try:
        df = pd.read_csv(archivo_prn, sep=r"\s+", engine="python", encoding="utf-8")
        df.columns = df.columns.str.strip()
        return df
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(archivo_prn, sep=r"\s+", engine="python", encoding="latin-1")
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            raise ValueError(f"Error al leer Asistencia.prn: {e}")
    except Exception as e:
        raise ValueError(f"Error al leer Asistencia.prn: {e}")


def verificar_carga(df: pd.DataFrame, nombre: str) -> bool:
    """
    Verifica que un DataFrame no esté vacío.
    Parámetros:
        df: DataFrame a verificar
        nombre: nombre del archivo
    Retorna:
        True si tiene datos, False si está vacío
    """
    if df is None or df.empty:
        return False
    return True