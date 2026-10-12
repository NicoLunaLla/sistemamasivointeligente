"""
modelo_agrupamiento.py
--------------------------------------------------------------------
APRENDIZAJE NO SUPERVISADO - AGRUPAMIENTO CON K-MEANS

Esta es la TERCERA parte del proyecto. A diferencia del aprendizaje
supervisado (donde el modelo aprendia con una respuesta ya conocida,
el nivel_congestion), aqui NO usamos ninguna respuesta: dejamos que el
algoritmo descubra por si solo GRUPOS de trayectos parecidos.

Algoritmo: K-MEANS (scikit-learn).
  - Agrupa los registros en 'k' grupos (clusters) segun que tan
    parecidos son entre si en sus caracteristicas.
  - Nosotros usamos k=3 (tres grupos).

IMPORTANTE:
  - Reutilizamos el MISMO dataset del aprendizaje supervisado
    (aprendizaje_supervisado/datos_transporte.csv).
  - NO usamos la columna 'nivel_congestion', porque en aprendizaje NO
    supervisado no se usan etiquetas/respuestas.
  - No modificamos nada del proyecto anterior.

Se ejecuta con:
    python aprendizaje_no_supervisado/modelo_agrupamiento.py
"""

import os

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


# --------------------------------------------------------------------
# CONFIGURACION
# --------------------------------------------------------------------
# Carpeta donde esta este archivo.
CARPETA_ACTUAL = os.path.dirname(os.path.abspath(__file__))

# Ruta al dataset (vive en la carpeta del aprendizaje supervisado).
# Subimos un nivel y entramos a 'aprendizaje_supervisado'.
RUTA_CSV = os.path.join(
    os.path.dirname(CARPETA_ACTUAL),
    "aprendizaje_supervisado",
    "datos_transporte.csv",
)

# Variables (columnas) que usamos para agrupar.
# OJO: NO incluimos 'nivel_congestion' (eso seria supervisado).
VARIABLES = [
    "hora",
    "pasajeros",
    "lluvia",
    "hora_pico",
    "tiempo_estimado",
    "dia_laboral",  # la creamos nosotros a partir de dia_semana
]

# Dias laborales (lunes a viernes).
DIAS_LABORALES = {"Lunes", "Martes", "Miercoles", "Jueves", "Viernes"}


def cargar_datos():
    """
    Carga el CSV y crea la columna 'dia_laboral':
      - 1 si es de lunes a viernes
      - 0 si es sabado o domingo
    """
    datos = pd.read_csv(RUTA_CSV)
    datos["dia_laboral"] = datos["dia_semana"].apply(
        lambda dia: 1 if dia in DIAS_LABORALES else 0
    )
    return datos


def main():
    print("=" * 60)
    print("  APRENDIZAJE NO SUPERVISADO - AGRUPAMIENTO (K-MEANS)")
    print("=" * 60)

    # 1) Cargar los datos.
    datos = cargar_datos()
    print(f"\nCantidad total de registros: {len(datos)}")

    # 2) Tomar solo las variables que vamos a usar para agrupar.
    X = datos[VARIABLES]

    # 3) Escalar los datos con StandardScaler.
    #    ¿Por que escalar? Porque las variables tienen rangos muy
    #    distintos (ej: 'pasajeros' llega a 160, 'lluvia' es 0 o 1).
    #    Si no escalamos, 'pasajeros' pesaria mucho mas que el resto.
    #    StandardScaler deja todas las variables en una escala comparable.
    escalador = StandardScaler()
    X_escalado = escalador.fit_transform(X)

    # 4) Entrenar K-Means con 3 grupos.
    #    - n_clusters=3: queremos tres grupos de trayectos.
    #    - random_state=42: resultado reproducible (siempre igual).
    #    - n_init=10: prueba 10 inicios y se queda con el mejor.
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    etiquetas = kmeans.fit_predict(X_escalado)

    # 5) Agregar la columna 'cluster' al dataset.
    datos["cluster"] = etiquetas

    # 6) Mostrar cuantos registros quedaron en cada cluster.
    print("\nCantidad de registros por cluster:")
    print(datos["cluster"].value_counts().sort_index().to_string())

    # 7) Mostrar los promedios de cada variable por cluster.
    #    Esto ayuda a "interpretar" que representa cada grupo.
    print("\nPromedios de las variables por cluster:")
    promedios = datos.groupby("cluster")[VARIABLES].mean().round(1)
    print(promedios.to_string())

    # 8) Guardar el dataset con la columna cluster.
    ruta_resultados = os.path.join(CARPETA_ACTUAL, "resultados_clusters.csv")
    datos.to_csv(ruta_resultados, index=False, encoding="utf-8")
    print(f"\nResultados guardados en: {ruta_resultados}")

    # 9) y 10) Crear y guardar UNA grafica: pasajeros vs tiempo_estimado,
    #    coloreada segun el cluster.
    _graficar(datos, kmeans, escalador)

    print("\nListo. Los trayectos quedaron agrupados en 3 clusters.\n")


def _graficar(datos, kmeans, escalador):
    """
    Dibuja un grafico de dispersion: pasajeros (eje X) contra
    tiempo_estimado (eje Y), con un color por cada cluster.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n(matplotlib no esta instalado: se omite la grafica)")
        return

    plt.figure(figsize=(9, 6))

    # Dibujamos los puntos de cada cluster con un color distinto.
    colores = ["#2d6cdf", "#e67e22", "#2ecc71"]  # azul, naranja, verde
    for numero in sorted(datos["cluster"].unique()):
        grupo = datos[datos["cluster"] == numero]
        plt.scatter(
            grupo["pasajeros"], grupo["tiempo_estimado"],
            s=50, c=colores[numero % len(colores)],
            label=f"Cluster {numero}", alpha=0.7, edgecolors="white",
        )

    plt.xlabel("Pasajeros")
    plt.ylabel("Tiempo estimado (min)")
    plt.title("Agrupamiento de trayectos (K-Means) - pasajeros vs tiempo")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()

    ruta_img = os.path.join(CARPETA_ACTUAL, "clusters.png")
    plt.savefig(ruta_img, dpi=120)
    print(f"Grafica guardada en: {ruta_img}")

    # Mostramos la ventana si el entorno lo permite.
    try:
        plt.show()
    except Exception:
        pass


if __name__ == "__main__":
    main()
