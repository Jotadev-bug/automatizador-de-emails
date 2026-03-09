import os
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# --- Configuration ---
st.set_page_config(page_title="Email Automation Dashboard", page_icon="📈", layout="wide")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DATA_DIR, 'logs.db')

# --- Data Fetching ---
@st.cache_data(ttl=60) # Cache for 60 seconds to prevent constant DB hits
def load_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM email_logs", conn)
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
        return df

df = load_data()

# --- UI Layout ---
st.title("🤖 Automatización de Correos - Panel de Control")

if df.empty:
    st.warning("No se encontraron datos en la base de datos. ¿Ha procesado algún correo el sistema?")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Filtros")
days_filter = st.sidebar.slider("Días a analizar", 1, 30, 7)
min_date = pd.Timestamp.now().tz_localize(None) - pd.Timedelta(days=days_filter)
filtered_df = df[df['timestamp'] >= min_date]

# --- Key Metrics (KPIs) ---
st.subheader("Indicadores Clave de Rendimiento (KPIs)")
col1, col2, col3 = st.columns(3)

total_processed = len(filtered_df)
invoices_count = len(filtered_df[filtered_df['predicted_class'] == 0])
# Assume each email processed saves 2 minutes of human time
hours_saved = round((total_processed * 2) / 60, 2)

col1.metric("Total Correos Procesados", total_processed)
col2.metric("Facturas Enrutadas", invoices_count)
col3.metric("Horas de Trabajo Ahorradas", f"{hours_saved} hrs")

st.divider()

# --- Visualizations ---
st.subheader("Rendimiento del Sistema y Enrutamiento")
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    class_counts = filtered_df['action_taken'].value_counts().reset_index()
    class_counts.columns = ['Action', 'Count']
    fig1 = px.pie(class_counts, values='Count', names='Action', title="Distribución de Acciones de Enrutamiento", hole=0.4)
    st.plotly_chart(fig1, width='stretch')

with col_chart2:
    if not filtered_df.empty:
        # Group by date for a timeline
        timeline = filtered_df.groupby(filtered_df['timestamp'].dt.date).size().reset_index(name='Correos Procesados')
        fig2 = px.line(timeline, x='timestamp', y='Correos Procesados', title="Volumen de Procesamiento a lo Largo del Tiempo", markers=True)
        st.plotly_chart(fig2, width='stretch')

st.divider()

# --- Interactive Data Grid ---
st.subheader("Decisiones Recientes de Enrutamiento (Tabla de Datos)")
# Sort by newest first
st.dataframe(
    filtered_df.sort_values(by='timestamp', ascending=False)
    .drop(columns=['id']) # Hide internal ID
    .style.map(lambda x: 'background-color: #d4edda;' if x == "INVOICE" else ('background-color: #f8d7da;' if x == "URGENT" else 'background-color: #e2e3e5;'), subset=['action_taken']),
    width='stretch',
    height=400
)
