import streamlit as st
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sqlalchemy import create_engine, text
import plotly.express as px
from pmdarima import auto_arima

# --- 1. CONFIGURACIÓN E INYECCIÓN DE CSS/HTML ---
st.set_page_config(page_title="Control de Horas Extras", layout='wide')

# Inyección de CSS para mejorar tarjetas y contenedores
st.markdown("""
    <style>
    .kpi-card {
        background-color: #1E2130;
        padding: 20px;
        border-radius: 10px;
        border-left: 6px solid #29b5e8;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        text-align: left;
        margin-bottom: 20px;
    }
    .kpi-title {
        margin: 0;
        font-size: 16px;
        color: #A0AEC0;
        font-weight: 600;
    }
    .kpi-value {
        margin: 0;
        font-size: 42px !important; 
        color: #FFFFFF;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Configuración de conexión a la base de datos
DB_URL = st.secrets["DATABASE_URL"]

@st.cache_resource
def get_engine():
    return create_engine(DB_URL)

engine = get_engine()

st.title("Control y Registro de Horas Extras")

# Pestañas para organizar la app
tab1, tab2, tab3 = st.tabs(["Registrar Horas", "Ver Registros", "Ver Reporte Analítico"])

def mostrar_contadores(df):
    st.subheader("Resumen de Operaciones")
    
    total_horas = df['cantidad_horas'].sum()
    total_registros = len(df)
    promedio_por_persona = df.groupby('nombre')['cantidad_horas'].sum().mean() if not df.empty else 0

    col1, col2, col3 = st.columns(3)
    
    # Uso de HTML para tarjetas de métricas estilizadas
    with col1:
        st.markdown(f"""
            <div class="kpi-card" style="border-left-color: #29b5e8;">
                <p class="kpi-title">Total Horas Acumuladas</p>
                <p class="kpi-value">{total_horas:.1f} hrs</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <div class="kpi-card" style="border-left-color: #48BB78;">
                <p class="kpi-title">Total de Registros</p>
                <p class="kpi-value">{total_registros}</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div class="kpi-card" style="border-left-color: #ED8936;">
                <p class="kpi-title">Promedio x Empleado</p>
                <p class="kpi-value">{promedio_por_persona:.1f} hrs</p>
            </div>
        """, unsafe_allow_html=True)

with tab1:
    st.subheader("Formulario de Captura")
    try:
        df_empleados = pd.read_sql("SELECT numero_empleado, nombre FROM empleados ORDER BY nombre", engine)
        if df_empleados.empty:
            st.warning("No hay empleados registrados en la tabla 'empleados'.")
        else:
            num_empleado = df_empleados['numero_empleado'].tolist()
            seleccion = st.selectbox("Selecciona al empleado:", num_empleado)
            registro = df_empleados[df_empleados['numero_empleado'] == seleccion]
            id_empleado = registro['numero_empleado'].values[0]
            nombre_empleado = registro['nombre'].values[0]
            
            with st.form("form_captura"):
                st.info(f"Empleado seleccionado: **{nombre_empleado}**")
                horas = st.number_input("Cantidad de horas:", min_value=0, max_value=24, step=1)
                motivo = st.text_area("Justificación / Motivo:")
                enviar = st.form_submit_button("Guardar Registro", type="primary")
                
                if enviar:
                    with engine.connect() as conn:
                        query = text("""
                            INSERT INTO horas_extra (empleado_num, cantidad_horas, justificacion)
                            VALUES (:emp_num, :hrs, :just)
                        """)
                        conn.execute(query, {"emp_num": int(id_empleado), "hrs": horas, "just": motivo})
                        conn.commit()
                    st.success(f"¡Registrado exitosamente! {horas} horas para {nombre_empleado}")
    except Exception as e:
        st.error(f"Error de conexión: {e}")

with tab2:
    st.subheader("Historial de Horas Registradas")
    query_historial = """
        SELECT e.nombre, h.cantidad_horas, h.justificacion, h.fecha_registro
        FROM horas_extra h
        JOIN empleados e ON h.empleado_num = e.numero_empleado
        ORDER BY h.fecha_registro DESC
    """
    df_historial = pd.DataFrame()
    try:
        df_historial = pd.read_sql(query_historial, engine)
        st.dataframe(df_historial, use_container_width=True)
        
        csv = df_historial.to_csv(index=False).encode('utf-8')
        st.download_button("Descargar reporte CSV", csv, "reporte_horas.csv", "text/csv")
    except:
        st.info("Aún no hay registros para mostrar o hubo un problema de conexión.")

def predecir_sarima(df_historico, semanas_a_predecir=4):
    serie = df_historico.groupby(pd.Grouper(key='fecha_registro', freq='W'))['cantidad_horas'].sum()
    if len(serie) < 2:
        return pd.DataFrame() # Prevenir error si hay pocos datos
        
    modelo = auto_arima(serie, seasonal=True, m=12, suppress_warnings=True, stepwise=True)
    pronostico, conf_int = modelo.predict(n_periods=semanas_a_predecir, return_conf_int=True)
    
    fechas_futuras = pd.date_range(serie.index[-1] + pd.Timedelta(weeks=1), periods=semanas_a_predecir, freq='W')
    df_proyeccion = pd.DataFrame({
        'fecha_registro': fechas_futuras,
        'cantidad_horas': pronostico,
        'Limite_Inferior': conf_int[:, 0],
        'Limite_Superior': conf_int[:, 1]
    })
    return df_proyeccion

def mostrar_graficas(df):
    st.markdown("---")
    st.subheader("Análisis Visual de Tiempo Extra")
    df['fecha_registro'] = pd.to_datetime(df['fecha_registro'])

    dias = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
    meses = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 
             7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
    
    df['dia_semana'] = df['fecha_registro'].dt.dayofweek.map(dias)
    df['mes_nombre'] = df['fecha_registro'].dt.month.map(meses)

    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfica 1: Mejora de colores y estilo
        df_top = df.groupby("nombre")["cantidad_horas"].sum().reset_index()
        df_top = df_top.sort_values(by="cantidad_horas", ascending=False).head(5)
        fig_barras = px.bar(
            df_top, x="nombre", y="cantidad_horas", 
            color="cantidad_horas", color_continuous_scale="Tealgrn",
            title="Top 5 Empleados (Más horas)",
            text_auto='.1f'
        )
        fig_barras.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_barras, use_container_width=True)

    with col2:
        # Gráfica 2: Tendencia con área debajo de la línea
        df['fecha_registro'] = pd.to_datetime(df['fecha_registro'])
        df_tendencia = df.groupby('fecha_registro')['cantidad_horas'].sum().reset_index()
        fig_linea = px.area(
            df_tendencia.sort_values("fecha_registro"), 
            x="fecha_registro", y="cantidad_horas",
            title="Tendencia Diaria de Horas Extras",
            markers=True, color_discrete_sequence=['#48BB78']
        )
        fig_linea.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_linea, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Gráfica 3: Gráfico de dona (Donut chart) con colores específicos
        df_just = df.groupby("justificacion")["cantidad_horas"].sum().reset_index()
        fig_pie = px.pie(
            df_just, names="justificacion", values="cantidad_horas",
            title="Distribución por Justificación", hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col4:
        # Gráfica 4 NUEVA: Boxplot para ver la dispersión y valores atípicos
        fig_box = px.box(
            df, x="nombre", y="cantidad_horas", 
            color="nombre", title="Distribución y Dispersión de Horas por Empleado",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_box.update_layout(margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

    col5,col6 = st.columns(2)
    with col5:
        df_dia = df.groupby('dia_semana')['cantidad_horas'].sum().reset_index()
        orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        df_dia['dia_semana']=pd.Categorical(df_dia['dia_semana'], categories = orden_dias,ordered=True)
        df_dia = df_dia.sort_values('dia_semana')
        fig_dia = px.bar(
            df_dia, x = 'dia_semana', y = 'cantidad_horas',
            title='Axumulado por dia de la semana',
            text_auto='.1f',
            color_discrete_sequence=['#ED8936']
        )
        fig_dia.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_dia, use_container_width=True)
    
    with col6:
        # Agrupar y ordenar por mes
        df_mes = df.groupby('mes_nombre')['cantidad_horas'].sum().reset_index()
        orden_meses = list(meses.values())
        df_mes['mes_nombre'] = pd.Categorical(df_mes['mes_nombre'], categories=orden_meses, ordered=True)
        df_mes = df_mes.sort_values('mes_nombre')
        
        fig_mes = px.bar(
            df_mes, x='mes_nombre', y='cantidad_horas', 
            title='Acumulado Histórico por Mes',
            text_auto='.1f',
            color_discrete_sequence=['#9F7AEA'] # Morado para contrastar
        )
        fig_mes.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_mes, use_container_width=True)

    st.markdown("---")
    st.subheader("Pronóstico de Horas Extras (Próximas 4 semanas)")
    
    
    df_proyeccion = predecir_sarima(df)
    
    if not df_proyeccion.empty:
        df_historico_semanal = df.groupby(pd.Grouper(key="fecha_registro", freq="W"))["cantidad_horas"].sum().reset_index()
        
        fig_sarima = px.line(
            df_historico_semanal, x="fecha_registro", y="cantidad_horas",
            title="Pronóstico Avanzado SARIMA (Vista Semanal)", markers=True
        )
        fig_sarima.update_traces(line=dict(color="#29b5e8", width=3))

        # Pronóstico
        fig_sarima.add_scatter(
            x=df_proyeccion["fecha_registro"], y=df_proyeccion["cantidad_horas"],
            name="Pronóstico", mode="lines+markers",
            line=dict(color="#FF4B4B", dash="dash", width=3)
        )

        # Intervalos de confianza
        fig_sarima.add_scatter(
            x=df_proyeccion["fecha_registro"].tolist() + df_proyeccion["fecha_registro"].tolist()[::-1],
            y=df_proyeccion["Limite_Superior"].tolist() + df_proyeccion["Limite_Inferior"].tolist()[::-1],
            fill="toself", fillcolor="rgba(255, 75, 75, 0.15)",
            line=dict(color="rgba(255,255,255,0)"), name="Intervalo de Confianza"
        )
        fig_sarima.update_layout(hovermode="x unified")
        st.plotly_chart(fig_sarima, use_container_width=True)
    else:
        st.info("No hay suficientes datos históricos para generar un pronóstico SARIMA.")

with tab3:
    if not df_historial.empty:
        df_historial['fecha_registro'] = pd.to_datetime(df_historial['fecha_registro'])
        df_historial['mes'] = df_historial['fecha_registro'].dt.month_name()
        df_historial['year'] = df_historial['fecha_registro'].dt.year.astype(str)

        st.sidebar.header("Filtros")
        mes_seleccion = st.sidebar.selectbox("Selecciona un mes:", ["Todos"] + df_historial['mes'].unique().tolist())
        year_seleccion = st.sidebar.selectbox("Selecciona un año:", ["Todos"] + df_historial['year'].unique().tolist())

        df_filtrado = df_historial.copy()
        if mes_seleccion != "Todos":
            df_filtrado = df_filtrado[df_filtrado['mes'] == mes_seleccion]
        if year_seleccion != "Todos":
            df_filtrado = df_filtrado[df_filtrado['year'] == year_seleccion]

        mostrar_contadores(df_filtrado)
        mostrar_graficas(df_filtrado)
        
        with st.expander(f"Ver tabla de datos detallados ({mes_seleccion} {year_seleccion})"):
            st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.info("Aun no hay registros disponibles para el análisis.")