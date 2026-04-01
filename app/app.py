import streamlit as st
import pandas as pd
from sqlalchemy import create_engine,text
import plotly.express as px

#configuracion de conexion a la base de datos
DB_URL = "postgresql://postgres:Sanchabar1@localhost:5432/Horas_Extras"

@st.cache_resource
def get_engine():
    return create_engine(DB_URL)

engine = get_engine()

# --- 2. INTERFAZ DE USUARIO ---
st.set_page_config(page_title="Control de Horas Extras", layout='wide')
st.title("Registro de Horas Extras")

# Pestañas para organizar la app
tab1, tab2, tab3 = st.tabs(["Registrar Horas", "Ver Registros","Ver reporte"])

def mostrar_contadores(df):
    with st.container():
        st.subheader("Resumen de Operaciones")
        
        # 1. Cálculo de valores
        total_horas = df['cantidad_horas'].sum()
        total_registros = len(df)
        promedio_por_persona = df.groupby('nombre')['cantidad_horas'].sum().mean()

        # 2. Diseño en columnas
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Total Horas Acumuladas", f"{total_horas:.1f} hrs")
        col2.metric("Total de Registros", f"{total_registros}")
        col3.metric("Promedio x Empleado", f"{promedio_por_persona:.1f} hrs")

with tab1:
    st.subheader("Formulario de Captura")
    
    # Obtener lista de empleados de Postgres
    try:
        df_empleados = pd.read_sql("SELECT numero_empleado, nombre FROM empleados ORDER BY nombre", engine)
        
        if df_empleados.empty:
            st.warning("No hay empleados registrados en la tabla 'empleados'.")
        else:
            # Crear el selector

            num_empleado = df_empleados['numero_empleado'].tolist()
            seleccion = st.selectbox("Selecciona al empleado:", num_empleado)
            #aislar el registro del empleado seleccionado
            registro = df_empleados[df_empleados['numero_empleado'] == seleccion]
            # Obtener el ID correspondiente al nombre seleccionado
            id_empleado = df_empleados[df_empleados['numero_empleado'] == seleccion]['numero_empleado'].values[0]
            nombre_empleado = registro['nombre'].values[0]
            with st.form("form_captura"):
                st.info(f"Empleado seleccionado: **{nombre_empleado}**")
                horas = st.number_input("Cantidad de horas:", min_value=0, max_value=24, step=1)
                motivo = st.text_area("Justificación / Motivo:")
                
                enviar = st.form_submit_button("Guardar Registro")
                
                if enviar:
                    with engine.connect() as conn:
                        query = text("""
                            INSERT INTO horas_extra (empleado_num, cantidad_horas, justificacion)
                            VALUES (:emp_num, :hrs, :just)
                        """)
                        conn.execute(query, {"emp_num": id_empleado, "hrs": horas, "just": motivo})
                        conn.commit()
                    st.success(f" ¡Registrado! {horas} horas para {seleccion}")

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
    try:
        df_historial = pd.read_sql(query_historial, engine)
        st.dataframe(df_historial, width='stretch')
        
        # Botón para descargar a Excel/CSV
        csv = df_historial.to_csv(index=False).encode('utf-8')
        st.download_button("Descargar reporte CSV", csv, "reporte.csv", "text/csv")
    except:
        st.info("Aún no hay registros para mostrar.")
    

def mostrar_graficas(df):
        
        st.subheader("Análisis de Tiempo Extra")
        col1, col2 = st.columns(2)
        
        with col1:
                # --- GRÁFICA 1: TOP 5 EMPLEADOS ---
            st.markdown("**Top 5 Empleados (Más horas)**")
            df_top = df.groupby("nombre")["cantidad_horas"].sum().reset_index()
            df_top = df_top.sort_values(by="cantidad_horas", ascending=False).head(5)
                
            fig_barras = px.bar(
                df_top, 
                x="nombre", 
                y="cantidad_horas", 
                color="cantidad_horas",
                color_continuous_scale="Blues"
            )

            st.plotly_chart(fig_barras, width='stretch')
        with col2:
            # --- GRÁFICA 3: TENDENCIA EN EL TIEMPO ---
            st.markdown("**Tendencia de Horas Extras por Fecha**")
            df['fecha_registro'] = pd.to_datetime(df['fecha_registro'])
            fig_linea = px.line(
                df.sort_values("fecha_registro"), 
                x="fecha_registro", 
                y="cantidad_horas",
                markers=True,
                line_shape="linear"
            )
            st.plotly_chart(fig_linea, width='stretch')
        
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Distribución por Justificación")
            df_just = df.groupby("justificacion")["cantidad_horas"].sum().reset_index()
            fig_pie = px.pie(
                df_just, 
                names="justificacion", 
                values="cantidad_horas",
                title="Horas por Justificación"
            )
            st.plotly_chart(fig_pie, width='stretch')

with tab3:
    if not df_historial.empty:
        #FIltro de mes
        df_historial['fecha_registro'] = pd.to_datetime(df_historial['fecha_registro'])

        df_historial['mes'] = df_historial['fecha_registro'].dt.month_name()
        df_historial['year'] = df_historial['fecha_registro'].dt.year.astype(str)

        st.sidebar.header("Filtros")
        lista_meses = df_historial['mes'].unique().tolist()
        lista_years = df_historial['year'].unique().tolist()

        mes_seleccion = st.sidebar.selectbox("Seleccion un mes:",["Todos"]+lista_meses)
        year_seleccion = st.sidebar.selectbox("Seleccion un año:",["Todos"]+lista_years)

        if mes_seleccion != "Todos":
            df_filtrado = df_historial[df_historial['mes'] == mes_seleccion]
        else:
            df_filtrado = df_historial

        if year_seleccion != "Todos":
            df_filtrado = df_filtrado[df_filtrado['year'] == year_seleccion]
        else:
            df_filtrado = df_filtrado

        st.markdown('<div style="background-color: #262730; padding: 20px; border-radius: 10px;">', unsafe_allow_html=True)
        mostrar_contadores(df_filtrado)
        st.markdown('</div>', unsafe_allow_html=True)
        mostrar_graficas(df_filtrado)
        st.write(f"Mostrando datos de: {mes_seleccion}")
        st.dataframe(df_filtrado)
    else:
        st.info("Aun no hay registros")



