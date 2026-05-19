"""
calculos.py
Módulo para calcular indicadores clave:
- Promedio de notas
- Porcentaje de asistencia
- Estado de riesgo académico
"""

import pandas as pd


def detectar_columna(df: pd.DataFrame, posibles: list) -> str:
    """
    Busca la primera columna que coincida con los nombres posibles.
    Parámetros:
        df: DataFrame donde buscar
        posibles: lista de nombres posibles
    Retorna:
        Nombre de la columna encontrada o None
    """
    cols_lower = {c.lower(): c for c in df.columns}
    for p in posibles:
        if p.lower() in cols_lower:
            return cols_lower[p.lower()]
    return None


def calcular_promedio_notas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula el promedio de notas por estudiante.
    Parámetros:
        df: DataFrame con datos integrados
    Retorna:
        DataFrame con columna 'promedio_notas' añadida
    """
    posibles_nota = ["nota", "calificacion", "nota_final", "promedio",
                     "nota1", "nota2", "nota3", "parcial1", "parcial2", "final"]
    col_nota = detectar_columna(df, posibles_nota)

    if col_nota:
        df["promedio_notas"] = pd.to_numeric(df[col_nota], errors="coerce")
    else:
        cols_numericas = df.select_dtypes(include="number").columns.tolist()
        cols_notas = []
        for c in cols_numericas:
            vals = df[c].dropna()
            if len(vals) > 0 and vals.between(0, 5).mean() > 0.8:
                cols_notas.append(c)
        if cols_notas:
            df["promedio_notas"] = df[cols_notas].mean(axis=1)
        else:
            df["promedio_notas"] = None
    return df


def calcular_asistencia(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula el porcentaje de asistencia por estudiante.
    Parámetros:
        df: DataFrame con datos integrados
    Retorna:
        DataFrame con columna 'porcentaje_asistencia' añadida
    """
    posibles_asis    = ["asistencia", "porcentaje_asistencia", "pct_asistencia", "attendance"]
    posibles_total   = ["total_clases", "clases_totales", "total_sesiones"]
    posibles_presente = ["presentes", "clases_asistidas", "sesiones_asistidas"]

    col_pct      = detectar_columna(df, posibles_asis)
    col_total    = detectar_columna(df, posibles_total)
    col_presente = detectar_columna(df, posibles_presente)

    if col_pct:
        df["porcentaje_asistencia"] = pd.to_numeric(df[col_pct], errors="coerce")
        if df["porcentaje_asistencia"].dropna().between(0, 1).all():
            df["porcentaje_asistencia"] = df["porcentaje_asistencia"] * 100
    elif col_total and col_presente:
        total    = pd.to_numeric(df[col_total],    errors="coerce")
        presente = pd.to_numeric(df[col_presente], errors="coerce")
        df["porcentaje_asistencia"] = (presente / total * 100).round(2)
    else:
        df["porcentaje_asistencia"] = None
    return df


def calcular_riesgo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Determina el estado de riesgo académico.
    Criterios:
        ALTO:  nota < 3.0 o asistencia < 70%
        MEDIO: nota entre 3.0-3.5 o asistencia entre 70-80%
        BAJO:  nota >= 3.5 y asistencia >= 80%
    Parámetros:
        df: DataFrame con promedio_notas y porcentaje_asistencia
    Retorna:
        DataFrame con columna 'riesgo_academico' añadida
    """
    def clasificar(fila):
        nota      = fila.get("promedio_notas")
        asistencia = fila.get("porcentaje_asistencia")
        if pd.isna(nota) and pd.isna(asistencia):
            return "Sin datos"
        alto  = False
        medio = False
        if not pd.isna(nota):
            if nota < 3.0:   alto  = True
            elif nota < 3.5: medio = True
        if not pd.isna(asistencia):
            if asistencia < 70:   alto  = True
            elif asistencia < 80: medio = True
        if alto:  return "ALTO"
        if medio: return "MEDIO"
        return "BAJO"

    df["riesgo_academico"] = df.apply(clasificar, axis=1)
    return df


def calcular_indicadores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ejecuta todos los cálculos en secuencia.
    """
    df = calcular_promedio_notas(df)
    df = calcular_asistencia(df)
    df = calcular_riesgo(df)
    return df


def metricas_generales(df: pd.DataFrame) -> dict:
    """
    Calcula métricas globales para el dashboard.
    """
    metricas = {"total_estudiantes": len(df)}
    if "promedio_notas" in df.columns:
        notas = df["promedio_notas"].dropna()
        metricas["promedio_general"] = round(notas.mean(), 2) if len(notas) > 0 else 0
        metricas["nota_maxima"]      = round(notas.max(),  2) if len(notas) > 0 else 0
        metricas["nota_minima"]      = round(notas.min(),  2) if len(notas) > 0 else 0
    if "porcentaje_asistencia" in df.columns:
        asis = df["porcentaje_asistencia"].dropna()
        metricas["asistencia_promedio"] = round(asis.mean(), 2) if len(asis) > 0 else 0
    if "riesgo_academico" in df.columns:
        conteo = df["riesgo_academico"].value_counts()
        metricas["riesgo_alto"]  = int(conteo.get("ALTO",  0))
        metricas["riesgo_medio"] = int(conteo.get("MEDIO", 0))
        metricas["riesgo_bajo"]  = int(conteo.get("BAJO",  0))
    return metricas
