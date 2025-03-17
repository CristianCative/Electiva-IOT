import polars as pl
import streamlit as st
import matplotlib.pyplot as plt


# Aplicar una paleta de colores neutros
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f5f5;  /* Fondo gris claro */
        color: #333333;           /* Texto oscuro */
    }
    h1, h2, h3, h4, h5, h6 {
        color: #444444;           /* Color de títulos */
    }
    .st-bb, .st-at, .st-cb, .st-cc {
        background-color: #ffffff;  /* Fondo blanco para contenedores */
        border-radius: 10px;        /* Bordes redondeados */
        padding: 10px;              /* Espaciado interno */
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);  /* Sombra suave */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Cargar los datos
@st.cache_data  # Usamos st.cache_data para almacenar en caché los datos
def load_data():
    data = pl.read_csv("depositos_oinks.csv")
    return data

data = load_data()

# Título de la aplicación
st.title("Análisis de Desempeño de Usuarios en Coink")

# Mostrar los datos
st.header("1. Datos de Depósitos en Oinks")
st.write("""
Esta tabla muestra los datos brutos de los depósitos realizados por los usuarios en las máquinas Oinks. Incluye información como el `user_id`, el valor de la operación (`operation_value`), la fecha de la operación (`operation_date`), la ubicación de la máquina (`maplocation_name`), y la fecha de creación del usuario (`user_createddate`).

**Interpretación**: Esta tabla es útil para ver los datos originales y entender la estructura de la información. No está procesada, por lo que es el punto de partida para el análisis.
""")
st.write(data)

# Definir una métrica de desempeño
st.header("2. Métrica de Desempeño: Score de Usuarios (0 a 100)")
st.write("""
Esta tabla muestra el **score de desempeño** de cada usuario, calculado en una escala de 0 a 100. El score se basa en dos métricas:
1. **Total de depósitos normalizado**: El total de dinero depositado por el usuario, normalizado entre 0 y 100.
2. **Promedio de depósitos normalizado**: El promedio de dinero depositado por operación, normalizado entre 0 y 100.
El score final es un promedio ponderado de estas dos métricas (70% para el total de depósitos y 30% para el promedio de depósitos).

**Interpretación**: Un score más alto indica que el usuario ha realizado más depósitos y/o depósitos de mayor valor en promedio. Los usuarios con scores cercanos a 100 son los de mejor desempeño.
""")

# Calcular el total de depósitos y el número de depósitos por usuario
user_deposits = data.group_by("user_id").agg([
    pl.sum("operation_value").alias("total_deposits"),
    pl.count("operation_value").alias("num_deposits")
])

# Calcular el promedio de depósitos por usuario
user_deposits = user_deposits.with_columns([
    (pl.col("total_deposits") / pl.col("num_deposits")).alias("avg_deposit")
])

# Normalizar el total de depósitos y el promedio de depósitos entre 0 y 100
total_deposits_max = user_deposits["total_deposits"].max()
avg_deposit_max = user_deposits["avg_deposit"].max()

user_deposits = user_deposits.with_columns([
    (pl.col("total_deposits") / total_deposits_max * 100).alias("total_deposits_normalized"),
    (pl.col("avg_deposit") / avg_deposit_max * 100).alias("avg_deposit_normalized")
])

# Calcular el score (promedio ponderado)
user_deposits = user_deposits.with_columns([
    (0.7 * pl.col("total_deposits_normalized") + 0.3 * pl.col("avg_deposit_normalized")).alias("score")
])

# Mostrar la métrica
st.write(user_deposits)

# Agregar un slider para seleccionar el umbral mínimo de puntuación
st.header("3. Filtrar Usuarios por Umbral de Score")
st.write("""
Aquí se encuentra un **slider** que permite al usuario seleccionar un umbral mínimo de score (entre 0 y 100). Los usuarios con un score menor al umbral seleccionado se excluyen del análisis.

**Interpretación**: Esta funcionalidad permite enfocarse en los usuarios que cumplen con un nivel mínimo de desempeño. Por ejemplo, si el umbral se establece en 50, solo se considerarán los usuarios con un score de 50 o superior.
""")
umbral_minimo = st.slider("Selecciona el umbral mínimo de score (0 a 100):", 0, 100, 50)

# Filtrar usuarios que cumplen con el umbral mínimo
usuarios_filtrados = user_deposits.filter(pl.col("score") >= umbral_minimo)

# Mostrar los usuarios filtrados
st.header("4. Usuarios con Score Mayor o Igual al Umbral")
st.write(f"""
Esta tabla muestra los usuarios que cumplen con el umbral mínimo de score seleccionado. Incluye el `user_id`, el total de depósitos, el número de depósitos, el promedio de depósitos, las métricas normalizadas y el score final.

**Interpretación**: Esta tabla es útil para identificar rápidamente a los usuarios que están por encima del umbral de desempeño. Puede usarse para tomar decisiones estratégicas, como recompensar a los usuarios con mejores scores.
""")
st.write(usuarios_filtrados)

# Gráfica de distribución del score (filtrada por umbral)
st.header("5. Distribución del Score de Usuarios (Filtrada por Umbral)")
st.write("""
Este es un **histograma** que muestra la distribución de los scores de los usuarios que cumplen con el umbral mínimo seleccionado. El eje X representa el score (de 0 a 100), y el eje Y representa la frecuencia (número de usuarios en cada rango de score).

**Interpretación**:
- Si la distribución está sesgada hacia la izquierda (scores bajos), significa que la mayoría de los usuarios tienen un desempeño bajo.
- Si la distribución está sesgada hacia la derecha (scores altos), significa que la mayoría de los usuarios tienen un buen desempeño.
- Una distribución centrada indica que los usuarios están distribuidos de manera equilibrada entre scores bajos y altos.
""")

# Crear la gráfica
fig, ax = plt.subplots()
ax.hist(usuarios_filtrados["score"], bins=30, edgecolor='black', color='blue')
ax.set_xlabel("Score (0 a 100)")
ax.set_ylabel("Frecuencia")
ax.set_title(f"Distribución del Score de Usuarios (Score ≥ {umbral_minimo})")

# Mostrar la gráfica en Streamlit
st.pyplot(fig)

# Gráfica de los usuarios con mayores scores (filtrada por umbral)
st.header(f"6. Top 10 Usuarios con Mayores Scores (Score ≥ {umbral_minimo})")
st.write("""
Esta es una **gráfica de barras** que muestra los 10 usuarios con los scores más altos que cumplen con el umbral mínimo seleccionado. El eje X representa el `user_id`, y el eje Y representa el score.

**Interpretación**: Esta gráfica permite identificar rápidamente a los usuarios con el mejor desempeño. Puede usarse para reconocer a los usuarios más activos o para diseñar estrategias de retención y fidelización.
""")

# Ordenar los usuarios filtrados por score (en orden descendente)
top_users_filtrados = usuarios_filtrados.sort("score", descending=True).head(10)

# Crear la gráfica
fig, ax = plt.subplots()
ax.bar(top_users_filtrados["user_id"], top_users_filtrados["score"], color='green')
ax.set_xlabel("User ID")
ax.set_ylabel("Score")
ax.set_title(f"Top 10 Usuarios con Mayores Scores (Score ≥ {umbral_minimo})")
plt.xticks(rotation=45)

# Mostrar la gráfica en Streamlit
st.pyplot(fig)