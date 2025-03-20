import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Cargar datos automáticamente desde el archivo CSV
st.title("Visualización de Resultados del Sistema de Clasificación de Monedas")

# Ruta del archivo CSV
csv_path = "datos.csv"  # Asegúrate de que el archivo esté en la misma carpeta que el script

try:
    df = pd.read_csv(csv_path, sep=';')  # Leer el archivo con separador correcto
    
    # Explicación de la tabla
    st.write("### Datos Registrados")
    st.write("La siguiente tabla muestra los datos capturados por los sensores, incluyendo la distancia medida por el sensor ultrasónico, el peso registrado por la celda de carga y el diámetro obtenido del sensor infrarrojo.")
    st.dataframe(df)
    
    # Mostrar nombres de las columnas disponibles
    st.write("### Columnas en el archivo CSV")
    st.write(df.columns.tolist())
    
    # Verificar si las columnas esperadas están presentes
    expected_columns = ["Tiempo (HH:MM:SS)", "Distancia (cm)", "Peso (kg)", "Diámetro (mm)"]
    available_columns = [col for col in expected_columns if col in df.columns]
    
    if len(available_columns) < len(expected_columns):
        st.error(f"Algunas columnas faltan en el archivo. Columnas detectadas: {df.columns.tolist()}")
    else:
        # Gráficos de distribución
        st.write("### Distribución de Distancia, Peso y Diámetro")
        st.write("Los siguientes gráficos muestran la distribución de los valores capturados por los sensores. Estos permiten analizar la variabilidad y el rango de las mediciones registradas.")
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        axes[0].hist(df["Distancia (cm)"], bins=10, color='blue', alpha=0.7)
        axes[0].set_title("Distribución de Distancia")
        axes[0].set_xlabel("Distancia (cm)")
        axes[0].set_ylabel("Frecuencia")
        
        axes[1].hist(df["Peso (kg)"], bins=10, color='green', alpha=0.7)
        axes[1].set_title("Distribución de Peso")
        axes[1].set_xlabel("Peso (kg)")
        
        axes[2].hist(df["Diámetro (mm)"], bins=10, color='red', alpha=0.7)
        axes[2].set_title("Distribución de Diámetro")
        axes[2].set_xlabel("Diámetro (mm)")
        
        st.pyplot(fig)
        
        # Mostrar estadísticas básicas
        st.write("### Estadísticas Básicas")
        st.write("En la siguiente tabla se presentan estadísticas descriptivas de los datos registrados, incluyendo valores promedio, mínimos, máximos y desviaciones estándar.")
        st.write(df.describe())

except FileNotFoundError:
    st.error("Error: No se encontró el archivo 'datos.csv'. Asegúrate de que esté en la misma carpeta que este script.")
