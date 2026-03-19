import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from src.rfm_logic import calcular_rfm

# 1. Configuración visual
st.set_page_config(page_title="Analítica de Clientes", layout="wide")
plt.style.use('ggplot')

st.title("📊 Dashboard de Segmentación RFM")
st.markdown("---")

@st.cache_data
def obtener_datos(ruta):
    df_raw = pd.read_csv(ruta, encoding='ISO-8859-1')
    return calcular_rfm(df_raw)

try:
    ruta_csv = 'data/online_retail.csv' 
    rfm = obtener_datos(ruta_csv)

    # --- SIDEBAR (Filtros Avanzados) ---
    st.sidebar.header("Configuración del Dashboard")
    
    # Filtro por Nombre de Segmento
    segmentos_disponibles = rfm['Segmento'].unique()
    segmentos_elegidos = st.sidebar.multiselect(
        "Ver Segmentos:",
        options=segmentos_disponibles,
        default=list(segmentos_disponibles)
    )
    
    # Filtro por Rango de Ventas
    min_v, max_v = int(rfm['Monetary'].min()), int(rfm['Monetary'].max())
    rango_venta = st.sidebar.slider("Rango de Ventas ($)", min_v, max_v, (min_v, 5000))

    # Aplicar filtros
    mask = (rfm['Segmento'].isin(segmentos_elegidos)) & \
           (rfm['Monetary'] >= rango_venta[0]) & \
           (rfm['Monetary'] <= rango_venta[1])
           
    df_filtrado = rfm[mask].copy()

    # Botón de descarga en el Sidebar
    csv = df_filtrado.to_csv(index=True).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Descargar Lista de Marketing",
        data=csv,
        file_name='clientes_segmentados.csv',
        key='download-csv'
    )

    # --- CUERPO PRINCIPAL ---
    # 1. Métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Clientes", f"{len(df_filtrado):,}")
    with col2:
        tp = df_filtrado['Monetary'].mean() if not df_filtrado.empty else 0
        st.metric("Ticket Promedio", f"${tp:,.2f}")
    with col3:
        st.metric("Venta Total Segmento", f"${df_filtrado['Monetary'].sum():,.2f}")

    # 2. Gráficas
    col_chart1, col_chart2 = st.columns([2, 1])

    with col_chart1:
        st.subheader("Análisis Visual: Recencia vs Frecuencia")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(
            data=df_filtrado, 
            x='Recency', 
            y='Frequency', 
            hue='Segmento', 
            size='Monetary', 
            sizes=(20, 400),
            alpha=0.6, 
            ax=ax
        )
        st.pyplot(fig)

    with col_chart2:
        st.subheader("Distribución de Segmentos")
        # Gráfico de pastel para ver la salud del negocio
        fig_pie, ax_pie = plt.subplots()
        df_filtrado['Segmento'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax_pie, colors=sns.color_palette('viridis'))
        ax_pie.set_ylabel('')
        st.pyplot(fig_pie)

    # 3. Tabla interactiva
    st.markdown("### Detalle de Clientes Filtrados")
    st.dataframe(df_filtrado.style.format(subset=['Monetary'], formatter="${:,.2f}"), use_container_width=True)

except FileNotFoundError:
    st.error(f"❌ No se encontró el archivo en: `{ruta_csv}`")
except Exception as e:
    st.error(f"⚠️ Error: {e}")