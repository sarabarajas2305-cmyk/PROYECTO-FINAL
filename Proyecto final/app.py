"""
app.py
Panel web de Seguimiento Académico
Ingeniería de Datos e Inteligencia Artificial - Lógica Computacional

Uso:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

from utils.carga_datos import (
    cargar_estudiantes,
    cargar_matriculas,
    cargar_espacios,
    cargar_asistencia,
    verificar_carga,
)
from utils.integracion import integrar_datos, obtener_resumen
from utils.calculos import calcular_indicadores, metricas_generales

st.set_page_config(
    page_title="Panel Académico",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 Panel de Análisis Académico")
st.markdown("**Ingeniería de Datos e Inteligencia Artificial · Lógica Computacional**")
st.divider()

st.sidebar.title("📁 Carga de archivos")
st.sidebar.info("Sube los 4 archivos del sistema académico para comenzar el análisis.")

archivo_est  = st.sidebar.file_uploader("📊 estudiantes.xlsx",       type=["xlsx"])
archivo_mat  = st.sidebar.file_uploader("📋 Matriculas.csv",          type=["csv"])
archivo_esp  = st.sidebar.file_uploader("📂 EspaciosAcademicos.json", type=["json"])
archivo_asis = st.sidebar.file_uploader("📄 Asistencia.prn",          type=["prn", "txt"])

archivos_listos = all([archivo_est, archivo_mat, archivo_esp, archivo_asis])

if not archivos_listos:
    st.info("⬅️  Sube los 4 archivos en el panel lateral para ver el análisis.")
    st.stop()

with st.spinner("Cargando archivos..."):
    try:
        df_est  = cargar_estudiantes(archivo_est)
        df_mat  = cargar_matriculas(archivo_mat)
        df_esp  = cargar_espacios(archivo_esp)
        df_asis = cargar_asistencia(archivo_asis)
    except ValueError as e:
        st.error(f"❌ {e}")
        st.stop()

errores = []
for df, nombre in [
    (df_est,  "estudiantes.xlsx"),
    (df_mat,  "Matriculas.csv"),
    (df_esp,  "EspaciosAcademicos.json"),
    (df_asis, "Asistencia.prn"),
]:
    if not verificar_carga(df, nombre):
        errores.append(nombre)

if errores:
    st.error(f"Archivos vacíos: {', '.join(errores)}")
    st.stop()

with st.spinner("Integrando datos y calculando indicadores..."):
    df_integrado = integrar_datos(df_est, df_mat, df_esp, df_asis)
    df_final     = calcular_indicadores(df_integrado)

metricas = metricas_generales(df_final)
resumen  = obtener_resumen(df_final)

st.sidebar.divider()
st.sidebar.subheader("🔍 Filtros")

opciones_riesgo = ["Todos"] + sorted(df_final["riesgo_academico"].dropna().unique().tolist())
filtro_riesgo   = st.sidebar.selectbox("Riesgo académico", opciones_riesgo)

if "promedio_notas" in df_final.columns and df_final["promedio_notas"].notna().any():
    nota_min = st.sidebar.slider("Nota mínima", min_value=0.0, max_value=5.0, value=0.0, step=0.1)
else:
    nota_min = 0.0

df_filtrado = df_final.copy()
if filtro_riesgo != "Todos":
    df_filtrado = df_filtrado[df_filtrado["riesgo_academico"] == filtro_riesgo]
if "promedio_notas" in df_filtrado.columns:
    df_filtrado = df_filtrado[
        df_filtrado["promedio_notas"].isna() | (df_filtrado["promedio_notas"] >= nota_min)
    ]

st.subheader("📊 Métricas generales")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("👥 Total estudiantes", metricas.get("total_estudiantes", 0))
col2.metric("📝 Promedio notas",    metricas.get("promedio_general", "N/A"))
col3.metric("🔴 Riesgo ALTO",       metricas.get("riesgo_alto", 0))
col4.metric("🟡 Riesgo MEDIO",      metricas.get("riesgo_medio", 0))
col5.metric("🟢 Riesgo BAJO",       metricas.get("riesgo_bajo", 0))

st.divider()
st.subheader("📈 Visualizaciones")
gcol1, gcol2 = st.columns(2)

with gcol1:
    st.markdown("#### Distribución de riesgo académico")
    conteo_riesgo = df_final["riesgo_academico"].value_counts()
    colores = {"ALTO": "#e74c3c", "MEDIO": "#f39c12", "BAJO": "#2ecc71", "Sin datos": "#bdc3c7"}
    fig1, ax1 = plt.subplots(figsize=(5, 4))
    ax1.pie(
        conteo_riesgo.values,
        labels=conteo_riesgo.index,
        autopct="%1.1f%%",
        colors=[colores.get(r, "#95a5a6") for r in conteo_riesgo.index],
        startangle=90,
    )
    ax1.axis("equal")
    st.pyplot(fig1)
    plt.close(fig1)

with gcol2:
    st.markdown("#### Distribución de promedios de notas")
    if "promedio_notas" in df_final.columns and df_final["promedio_notas"].notna().any():
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        notas = df_final["promedio_notas"].dropna()
        ax2.hist(notas, bins=10, color="#3498db", edgecolor="white", alpha=0.85)
        ax2.axvline(notas.mean(), color="#e74c3c", linestyle="--", linewidth=1.5, label=f"Promedio: {notas.mean():.2f}")
        ax2.set_xlabel("Nota")
        ax2.set_ylabel("Cantidad de estudiantes")
        ax2.legend()
        st.pyplot(fig2)
        plt.close(fig2)
    else:
        st.warning("No hay datos de notas disponibles.")

st.markdown("#### Asistencia promedio por nivel de riesgo")
if "porcentaje_asistencia" in df_final.columns and "riesgo_academico" in df_final.columns:
    asis_riesgo = (
        df_final.groupby("riesgo_academico")["porcentaje_asistencia"]
        .mean()
        .reindex(["BAJO", "MEDIO", "ALTO", "Sin datos"])
        .dropna()
    )
    fig3, ax3 = plt.subplots(figsize=(6, 3))
    colores_bar = ["#2ecc71", "#f39c12", "#e74c3c", "#bdc3c7"]
    bars = ax3.bar(asis_riesgo.index, asis_riesgo.values, color=colores_bar[:len(asis_riesgo)], edgecolor="white")
    ax3.set_ylabel("Asistencia promedio (%)")
    ax3.set_ylim(0, 110)
    for bar, val in zip(bars, asis_riesgo.values):
        ax3.text(bar.get_x() + bar.get_width() / 2, val + 1, f"{val:.1f}%", ha="center", fontsize=9)
    st.pyplot(fig3)
    plt.close(fig3)

st.divider()
st.subheader("📋 Tabla de estudiantes")
st.caption(f"Mostrando {len(df_filtrado)} de {len(df_final)} estudiantes")

cols_mostrar = [c for c in ["promedio_notas", "porcentaje_asistencia", "riesgo_academico"] if c in df_filtrado.columns]
otras_cols   = [c for c in df_filtrado.columns if c not in cols_mostrar]
df_mostrar   = df_filtrado[otras_cols + cols_mostrar].reset_index(drop=True)
st.dataframe(df_mostrar, use_container_width=True)

with st.expander("ℹ️ Información de integridad de datos"):
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Total registros",    resumen["total_registros"])
    col_b.metric("Columnas con nulos", resumen["columnas_con_nulos"])
    col_c.metric("Completitud",        f"{resumen['porcentaje_completo']}%")
    st.markdown("**Archivos cargados:**")
    for nombre, df in [
        ("estudiantes.xlsx",        df_est),
        ("Matriculas.csv",          df_mat),
        ("EspaciosAcademicos.json", df_esp),
        ("Asistencia.prn",          df_asis),
    ]:
        st.write(f"✅ `{nombre}` — {len(df)} filas, {len(df.columns)} columnas")