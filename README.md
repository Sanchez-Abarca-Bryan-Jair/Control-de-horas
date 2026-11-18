# Sistema Inteligente de Control de Horas Extras y Predicción de Presupuesto

https://sanchez-abarca-bryan-jair-control-de-horas-appapp-dcdwl1.streamlit.app/

Esta es una aplicación web interactiva desarrollada con **Streamlit** y conectada a una base de datos relacional en **PostgreSQL**, diseñada para optimizar el registro, control administrativo y planeación financiera del tiempo extra en entornos operativos de alta demanda.

El núcleo del sistema combina una interfaz de usuario intuitiva para la captura y auditoría de datos, junto con un módulo analítico avanzado basado en **Machine Learning** para la anticipación presupuestal.

---

## Características Principales

* **Formulario de Captura Seguro:** Registro validado de horas extras con campos de justificación operativa, enlazado directamente a los identificadores únicos de personal en base de datos.
* **Ficha Dinámica de Personal:** Consulta inmediata de información de solo lectura (nombre, apellidos, área asignada) al seleccionar un empleado, mitigando errores humanos en la captura.
* **Visualización en Cuadrícula (2x2):** Tablero interactivo con renderizado de alto rendimiento mediante **Plotly Express** para análisis inmediato:
    * *Top de Empleados:* Monitoreo de acumulación de horas para prevención de fatiga laboral (*burnout*).
    * *Flujo Temporal Lineal:* Rastreo preciso de registros ordenados cronológicamente sin distorsiones visuales.
* **Módulo Predictivo Avanzado:** Implementación del modelo estadístico **SARIMA** (*Seasonal AutoRegressive Integrated Moving Average*) para el pronóstico quincenal/mensual del consumo de horas, incluyendo el cálculo visual de intervalos de confianza (bandas de incertidumbre).

---

## Stack Tecnológico

* **Frontend / Dashboard:** Streamlit
* **Visualización de Datos:** Plotly Express
* **Base de Datos Relacional:** PostgreSQL (pgAdmin)
* **Manipulación de Datos:** Pandas & NumPy
* **Modelado Estadístico / ML:** `pmdarima` (Algoritmo Auto-ARIMA) & `statsmodels`
* **Conectividad:** SQLAlchemy

---

## Modelado de Datos y Arquitectura de Predicción

El sistema pasa de ser un software de registro descriptivo a una herramienta prescriptiva gracias al análisis de series temporales. 

1. **Agregación Estricta:** Para evitar desfases de escala en la visualización, tanto el histórico como el pronóstico se procesan bajo una misma frecuencia de muestreo temporal (Vista Semanal/Quincenal).
2. **Entrenamiento Automatizado:** La librería `pmdarima` evalúa dinámicamente las métricas de información (AIC) para seleccionar de manera óptima los parámetros autorregresivos, de integración y de media móvil $(p, d, q) \times (P, D, Q)_s$, aislando las tendencias del ruido operativo.

---


<img width="1864" height="875" alt="image" src="https://github.com/user-attachments/assets/39e69636-c38d-47a7-843a-e128f9024078" />
<img width="1908" height="868" alt="image" src="https://github.com/user-attachments/assets/d54d9416-f828-4f41-9303-1a12da5a6ddb" />
<img width="1839" height="906" alt="image" src="https://github.com/user-attachments/assets/d8464503-39ec-4f6e-888b-e94f56d80fce" />
<img width="1468" height="592" alt="image" src="https://github.com/user-attachments/assets/209ad21a-bd50-4bb9-a209-d51a951be060" />
<img width="1411" height="629" alt="image" src="https://github.com/user-attachments/assets/ef182d36-ad12-472e-82dc-9ecd678b418c" />
<img width="1491" height="644" alt="image" src="https://github.com/user-attachments/assets/09f97f75-7e10-4a22-aec1-5fd590ca36b1" />







