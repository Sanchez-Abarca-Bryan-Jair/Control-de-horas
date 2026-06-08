# 📊 Sistema Inteligente de Control de Horas Extras y Predicción de Presupuesto

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
<img width="1867" height="690" alt="image" src="https://github.com/user-attachments/assets/6e7ca29e-417e-495b-90d8-427da5d9647a" />
<img width="1463" height="660" alt="image" src="https://github.com/user-attachments/assets/548b9edc-aba0-4465-99dd-d842373a44d6" />
<img width="1535" height="882" alt="image" src="https://github.com/user-attachments/assets/ea231235-347b-4632-8f8a-735cac33fc41" />
<img width="1542" height="902" alt="image" src="https://github.com/user-attachments/assets/2d9d41a7-8505-4d7a-aa5d-318a8cfdef6e" />
<img width="1518" height="551" alt="image" src="https://github.com/user-attachments/assets/b7c44c43-ffd0-476c-8a0f-acbcd5a54700" />




