"""
modelo_congestion.py
--------------------------------------------------------------------
APRENDIZAJE SUPERVISADO - PREDICCION DEL NIVEL DE CONGESTION

Este es el "cerebro de aprendizaje" del nuevo componente. A partir de
un dataset de trayectos (datos_transporte.csv) ENTRENA un modelo de
ARBOL DE DECISION (DecisionTreeClassifier de scikit-learn) que aprende
a predecir el NIVEL DE CONGESTION de un trayecto:

    Baja  /  Media  /  Alta       <-- variable objetivo: nivel_congestion

Es una EVOLUCION del sistema de rutas anterior:
  - El proyecto anterior (base_conocimiento.py, buscador.py, etc.)
    encuentra la ruta de MENOR COSTO usando reglas y un grafo.
  - Este componente NO toca ese algoritmo. Agrega una capacidad nueva:
    APRENDER de datos para estimar la congestion.
  - En el README se explica como, en una version futura, esta prediccion
    podria usarse para ajustar los costos de las conexiones.

Pasos que realiza (los mismos de un flujo tipico de ML supervisado):
  1. Cargar el CSV con pandas.
  2. Preparar los datos (convertir texto a numeros donde haga falta).
  3. Separar variables de entrada (X) y variable objetivo (y).
  4. Dividir en entrenamiento y prueba (train_test_split).
  5. Crear y entrenar un DecisionTreeClassifier.
  6. Predecir sobre los datos de prueba.
  7. Medir la precision (accuracy_score) y la matriz de confusion.
  8. Predecir casos NUEVOS escritos a mano.

Se ejecuta con:
    python modelo_congestion.py
"""

import os

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report


# --------------------------------------------------------------------
# CONFIGURACION
# --------------------------------------------------------------------
# Ruta al dataset (siempre junto a este archivo, sin importar desde
# donde se ejecute el programa).
RUTA_CSV = os.path.join(os.path.dirname(__file__), "datos_transporte.csv")

# Columnas que el modelo usara para APRENDER (variables de entrada).
# Nota: 'origen' y 'destino' (nombres de estacion) NO se usan como
# entrada del modelo para mantenerlo simple y facil de explicar.
# Lo importante para la congestion son las condiciones del viaje.
COLUMNAS_ENTRADA = [
    "hora",
    "pasajeros",
    "lluvia",
    "hora_pico",
    "tiempo_estimado",
    "dia_laboral",  # columna que creamos nosotros a partir de dia_semana
]

# Columna que el modelo debe PREDECIR (variable objetivo).
COLUMNA_OBJETIVO = "nivel_congestion"

# Dias que consideramos laborales (lunes a viernes).
DIAS_LABORALES = {"Lunes", "Martes", "Miercoles", "Jueves", "Viernes"}


# --------------------------------------------------------------------
# 1) CARGA Y PREPARACION DE LOS DATOS
# --------------------------------------------------------------------
def cargar_datos(ruta_csv=RUTA_CSV):
    """
    Carga el CSV con pandas y hace una preparacion basica:
      - Lee el archivo en un DataFrame.
      - Crea una columna numerica 'dia_laboral' (1 = lunes a viernes,
        0 = fin de semana) a partir de 'dia_semana'.

    Devuelve el DataFrame listo para usarse.

    ¿Por que convertir el dia a numero? Un arbol de decision trabaja
    con numeros. En vez de usar el texto del dia, lo resumimos en una
    idea sencilla y util: si es dia laboral o no.
    """
    datos = pd.read_csv(ruta_csv)

    # Convertimos el dia (texto) en una variable 0/1 facil de entender.
    datos["dia_laboral"] = datos["dia_semana"].apply(
        lambda dia: 1 if dia in DIAS_LABORALES else 0
    )

    return datos


# --------------------------------------------------------------------
# 2) SEPARAR ENTRADAS (X) Y OBJETIVO (y)
# --------------------------------------------------------------------
def separar_variables(datos):
    """
    Separa el DataFrame en:
      - X: las variables de entrada (lo que el modelo observa).
      - y: la variable objetivo (lo que el modelo debe predecir).
    """
    X = datos[COLUMNAS_ENTRADA]
    y = datos[COLUMNA_OBJETIVO]
    return X, y


# --------------------------------------------------------------------
# 3) ENTRENAR EL ARBOL DE DECISION
# --------------------------------------------------------------------
def entrenar_modelo(X_entrenamiento, y_entrenamiento):
    """
    Crea y entrena un ARBOL DE DECISION.

    - max_depth=4: limitamos la profundidad del arbol para que:
        * no se "aprenda de memoria" los datos (sobreajuste),
        * sea pequeno y FACIL de dibujar y explicar en el video.
    - random_state=42: hace que el entrenamiento sea reproducible
      (siempre crece el mismo arbol con los mismos datos).

    Devuelve el modelo ya entrenado.
    """
    modelo = DecisionTreeClassifier(max_depth=4, random_state=42)
    modelo.fit(X_entrenamiento, y_entrenamiento)
    return modelo


# --------------------------------------------------------------------
# 4) PREDECIR UN CASO NUEVO (escrito a mano)
# --------------------------------------------------------------------
def predecir_caso(modelo, hora, pasajeros, lluvia, hora_pico,
                  tiempo_estimado, dia_laboral):
    """
    Predice el nivel de congestion de UN trayecto nuevo.

    Los parametros son las mismas variables de entrada del modelo:
      - hora:            hora del dia (0-23)
      - pasajeros:       cantidad estimada de pasajeros
      - lluvia:          0 = no, 1 = si
      - hora_pico:       0 = no, 1 = si
      - tiempo_estimado: minutos estimados de viaje
      - dia_laboral:     1 = lunes a viernes, 0 = fin de semana

    Devuelve la etiqueta predicha: "Baja", "Media" o "Alta".
    """
    # El modelo espera los datos en el MISMO orden que COLUMNAS_ENTRADA.
    # Usamos un DataFrame para conservar los nombres de las columnas.
    caso = pd.DataFrame(
        [[hora, pasajeros, lluvia, hora_pico, tiempo_estimado, dia_laboral]],
        columns=COLUMNAS_ENTRADA,
    )
    prediccion = modelo.predict(caso)
    return prediccion[0]


# --------------------------------------------------------------------
# 5) VISUALIZACION OPCIONAL DEL ARBOL
# --------------------------------------------------------------------
def dibujar_arbol(modelo):
    """
    Dibuja el arbol de decision con matplotlib (OPCIONAL).

    Si matplotlib no esta instalado, simplemente avisa y continua
    (el resto del programa funciona igual sin la imagen).
    """
    try:
        import matplotlib.pyplot as plt
        from sklearn.tree import plot_tree
    except ImportError:
        print("\n(matplotlib no esta instalado: se omite el dibujo del arbol)")
        return

    plt.figure(figsize=(16, 8))
    plot_tree(
        modelo,
        feature_names=COLUMNAS_ENTRADA,
        class_names=modelo.classes_,
        filled=True,       # colorea los nodos por clase
        rounded=True,
        fontsize=8,
    )
    plt.title("Arbol de Decision - Prediccion del Nivel de Congestion")
    plt.tight_layout()

    # Guardamos la imagen junto a este archivo.
    ruta_img = os.path.join(os.path.dirname(__file__), "arbol_decision.png")
    plt.savefig(ruta_img, dpi=120)
    print(f"\nArbol guardado como imagen en: {ruta_img}")
    # Mostramos la ventana (si el entorno lo permite).
    plt.show()


# --------------------------------------------------------------------
# FUNCION PRINCIPAL: une todos los pasos
# --------------------------------------------------------------------
def main(mostrar_arbol=False):
    print("=" * 60)
    print("  APRENDIZAJE SUPERVISADO - PREDICCION DE CONGESTION")
    print("  Modelo: Arbol de Decision (scikit-learn)")
    print("=" * 60)

    # 1) Cargar y preparar los datos.
    datos = cargar_datos()
    print(f"\nRegistros cargados: {len(datos)}")
    print("Distribucion de clases (nivel_congestion):")
    print(datos[COLUMNA_OBJETIVO].value_counts().to_string())

    # 2) Separar entradas y objetivo.
    X, y = separar_variables(datos)

    # 3) Dividir en entrenamiento (70%) y prueba (30%).
    #    - stratify=y: mantiene la proporcion de clases en ambos grupos.
    #    - random_state=42: division reproducible.
    X_entrenamiento, X_prueba, y_entrenamiento, y_prueba = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )
    print(f"\nDatos de entrenamiento: {len(X_entrenamiento)}")
    print(f"Datos de prueba:        {len(X_prueba)}")

    # 4) Entrenar el arbol de decision.
    modelo = entrenar_modelo(X_entrenamiento, y_entrenamiento)

    # 5) Predecir sobre los datos de prueba (que el modelo NO vio).
    predicciones = modelo.predict(X_prueba)

    # 6) Medir la precision (accuracy).
    precision = accuracy_score(y_prueba, predicciones)
    print("\n" + "-" * 60)
    print(f"PRECISION (accuracy) sobre datos de prueba: {precision:.2%}")
    print("-" * 60)

    # 7) Matriz de confusion: muestra aciertos y confusiones por clase.
    #    Las filas son la realidad, las columnas la prediccion.
    clases = sorted(y.unique())  # ['Alta', 'Baja', 'Media']
    matriz = confusion_matrix(y_prueba, predicciones, labels=clases)
    print("\nMatriz de confusion (filas=real, columnas=prediccion):")
    print("Clases:", clases)
    print(matriz)

    # Reporte detallado (precision, recall, f1 por clase).
    print("\nReporte por clase:")
    print(classification_report(y_prueba, predicciones, zero_division=0))

    # 8) Mostrar algunas predicciones de ejemplo del conjunto de prueba.
    print("Ejemplos de prediccion (datos de prueba):")
    print(f"  {'real':>6}  {'prediccion':>12}")
    for real, pred in list(zip(y_prueba, predicciones))[:8]:
        marca = "OK" if real == pred else "X"
        print(f"  {real:>6}  {pred:>12}   {marca}")

    # 9) Predecir CASOS NUEVOS escritos a mano (demostracion).
    print("\n" + "=" * 60)
    print("  PREDICCION DE CASOS NUEVOS")
    print("=" * 60)

    # Caso A: muchos pasajeros, hora pico, con lluvia -> deberia ser Alta.
    caso_a = predecir_caso(
        modelo, hora=18, pasajeros=150, lluvia=1, hora_pico=1,
        tiempo_estimado=12, dia_laboral=1,
    )
    print("\nCaso A -> hora=18, pasajeros=150, lluvia=Si, hora_pico=Si")
    print(f"  Congestion estimada: {caso_a}")

    # Caso B: pocos pasajeros, fuera de hora pico, sin lluvia -> Baja.
    caso_b = predecir_caso(
        modelo, hora=11, pasajeros=30, lluvia=0, hora_pico=0,
        tiempo_estimado=4, dia_laboral=1,
    )
    print("\nCaso B -> hora=11, pasajeros=30, lluvia=No, hora_pico=No")
    print(f"  Congestion estimada: {caso_b}")

    # Caso C: valores intermedios -> probablemente Media.
    caso_c = predecir_caso(
        modelo, hora=15, pasajeros=85, lluvia=0, hora_pico=0,
        tiempo_estimado=7, dia_laboral=1,
    )
    print("\nCaso C -> hora=15, pasajeros=85, lluvia=No, hora_pico=No")
    print(f"  Congestion estimada: {caso_c}")

    # 10) Dibujo opcional del arbol.
    if mostrar_arbol:
        dibujar_arbol(modelo)

    print("\nListo. El modelo quedo entrenado y evaluado.\n")

    # Devolvemos el modelo por si otro archivo (pruebas_modelo.py) lo usa.
    return modelo


# --------------------------------------------------------------------
# INTEGRACION CON EL SISTEMA DE RUTAS (parte 1 del proyecto)
# --------------------------------------------------------------------
# Esta seccion CONECTA las dos partes del proyecto: usa la prediccion de
# congestion para AJUSTAR los costos de las conexiones del grafo y asi
# sugerir una ruta que tenga en cuenta la congestion estimada.
#
# NO modifica base_conocimiento.py ni buscador.py: solo los reutiliza.
# La interfaz grafica (interfaz.py) usa estas funciones cuando el usuario
# activa los checks de "Hora pico" y "Lluvia".

import sys
import heapq

# Permite importar los modulos del proyecto anterior (carpeta de arriba).
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_conocimiento import obtener_conexiones_unicas, ESTACIONES

# Factor por el que se multiplica el costo base segun la congestion.
FACTORES = {
    "Baja": 1.0,
    "Media": 1.5,
    "Alta": 2.0,
}

# Estaciones "centricas" de alta demanda. En hora pico y con lluvia estas
# zonas se saturan MUCHO mas que los ramales perifericos. Esto hace que,
# al activar las condiciones, convenga DESVIARSE por rutas alternativas.
ESTACIONES_ALTA_DEMANDA = {
    "Calle 26", "Av. Jimenez", "Heroes", "Calle 72", "Calle 100",
}


def preparar_modelo():
    """Entrena el modelo de congestion una sola vez y lo devuelve."""
    datos = cargar_datos()
    X, y = separar_variables(datos)
    X_entrenamiento, _, y_entrenamiento, _ = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )
    return entrenar_modelo(X_entrenamiento, y_entrenamiento)


def _congestion_de_conexion(modelo, costo_base, hora_pico, lluvia,
                            alta_demanda=False):
    """
    Predice la congestion de UNA conexion segun las condiciones.
    En hora pico y con lluvia viaja mas gente y el trayecto tarda mas,
    asi que esas condiciones suben los pasajeros y el tiempo del tramo.

    Si la conexion toca una estacion de ALTA DEMANDA (zona centrica),
    la cantidad de pasajeros estimada sube todavia mas: esas zonas se
    saturan antes. Esto hace que convenga desviarse por los ramales.

    En condiciones NORMALES (sin hora pico ni lluvia) consideramos la
    congestion como Baja. Asi la ruta "sin condiciones" coincide con la
    del buscador original, y cualquier cambio de ruta se debe UNICAMENTE
    a las condiciones que active el usuario.
    """
    # Sin condiciones criticas: tramo tranquilo -> congestion Baja.
    if not hora_pico and not lluvia:
        return "Baja"

    # Base moderada de pasajeros. La idea es que SOLO las zonas de alta
    # demanda lleguen a niveles altos de congestion, mientras los ramales
    # perifericos se quedan en niveles bajos o medios. Ese desnivel es lo
    # que hace que, al activar las condiciones, convenga otra ruta.
    pasajeros = 20 + costo_base * 2
    pasajeros += 25 if hora_pico else 0
    pasajeros += 15 if lluvia else 0
    # Las zonas centricas reciben una carga extra fuerte de pasajeros.
    pasajeros += 80 if alta_demanda else 0

    tiempo = costo_base + (2 if hora_pico else 0) + (2 if lluvia else 0)
    hora = 7 if hora_pico else 11

    caso = pd.DataFrame(
        [[hora, pasajeros, lluvia, hora_pico, tiempo, 1]],
        columns=COLUMNAS_ENTRADA,
    )
    return modelo.predict(caso)[0]


def _red_ajustada(modelo, hora_pico, lluvia):
    """Construye el grafo con los costos AJUSTADOS por congestion."""
    red = {estacion: [] for estacion in ESTACIONES}
    for origen, destino, costo_base in obtener_conexiones_unicas():
        # ¿La conexion toca una zona centrica de alta demanda?
        alta_demanda = (origen in ESTACIONES_ALTA_DEMANDA or
                        destino in ESTACIONES_ALTA_DEMANDA)
        congestion = _congestion_de_conexion(
            modelo, costo_base, hora_pico, lluvia, alta_demanda)
        costo = round(costo_base * FACTORES[congestion], 1)
        red[origen].append((destino, costo))
        red[destino].append((origen, costo))
    return red


def _buscar_en_red(red, origen, destino):
    """Costo uniforme sobre una red dada (misma idea que buscador.py)."""
    frontera = [(0, [origen])]
    visitadas = set()
    while frontera:
        costo_actual, ruta = heapq.heappop(frontera)
        actual = ruta[-1]
        if actual == destino:
            return ruta, round(costo_actual, 1)
        if actual in visitadas:
            continue
        visitadas.add(actual)
        for vecina, costo in red.get(actual, []):
            if vecina not in visitadas:
                heapq.heappush(frontera, (costo_actual + costo, ruta + [vecina]))
    return None, None


def sugerir_ruta(modelo, origen, destino, hora_pico, lluvia):
    """
    Calcula la mejor ruta teniendo en cuenta la congestion estimada
    segun las condiciones. Devuelve {'ruta': [...], 'costo': n}.
    """
    red = _red_ajustada(modelo, hora_pico, lluvia)
    ruta, costo = _buscar_en_red(red, origen, destino)
    return {"ruta": ruta, "costo": costo}


if __name__ == "__main__":
    # Para ver el dibujo del arbol, cambia a: main(mostrar_arbol=True)
    main(mostrar_arbol=False)
