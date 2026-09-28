"""
base_conocimiento.py
--------------------------------------------------------------------
BASE DE CONOCIMIENTO del sistema.

Aqui vive TODO lo que el sistema "sabe" sobre la red de transporte:
  - Que estaciones existen.
  - Que estaciones estan conectadas entre si.
  - Cuanto "cuesta" viajar por cada conexion (peso).

Ademas contiene las FUNCIONES que representan las reglas basicas
de conocimiento (por ejemplo: saber si una estacion existe o saber
con quien esta conectada una estacion).

La red esta inspirada en un sistema masivo tipo TransMilenio, pero
es una version SIMPLIFICADA y FICTICIA con fines academicos.
"""

# --------------------------------------------------------------------
# 1) HECHOS DE LA BASE DE CONOCIMIENTO
# --------------------------------------------------------------------
# Representamos la red como un GRAFO usando un diccionario.
#
# Estructura:
#   red = {
#       "Estacion": [ ("EstacionVecina", costo), ... ],
#       ...
#   }
#
# Cada estacion tiene una lista de conexiones. Cada conexion es una
# tupla (estacion_destino, costo). El costo puede representar minutos,
# distancia o "esfuerzo" de viaje. Aqui lo tratamos como minutos.
#
# La red es NO dirigida: si A conecta con B, B tambien conecta con A.
# Por eso mas abajo agregamos las conexiones en ambos sentidos de forma
# automatica, para no tener que escribirlas dos veces a mano.

# Conexiones "base" (solo escritas en un sentido).
# Formato: (estacion_origen, estacion_destino, costo)
_CONEXIONES = [
    ("Portal Norte", "Toberin", 4),
    ("Toberin", "Calle 142", 3),
    ("Calle 142", "Calle 100", 5),
    ("Calle 100", "Heroes", 6),
    ("Heroes", "Calle 72", 3),
    ("Calle 72", "Calle 45", 4),
    ("Calle 45", "Calle 26", 5),
    ("Calle 26", "Av. Jimenez", 4),

    # Ramal occidente
    ("Portal Norte", "Suba", 7),
    ("Suba", "Av. Boyaca", 5),
    ("Av. Boyaca", "Calle 26", 8),

    # Ramal sur / centro
    ("Av. Jimenez", "Tercer Milenio", 3),
    ("Tercer Milenio", "Ricaurte", 4),
    ("Ricaurte", "Portal Sur", 9),
    ("Portal Sur", "Bosa", 5),

    # Conexiones alternativas (crean rutas diferentes entre A y B)
    ("Calle 100", "Av. Boyaca", 4),
    ("Calle 45", "Ricaurte", 10),
    ("Heroes", "Calle 26", 9),
    ("Suba", "Portal Sur", 20),
]

# Lista de todas las estaciones que existen en la red.
# Estan escritas explicitamente para que sea facil verlas y validarlas.
ESTACIONES = [
    "Portal Norte",
    "Toberin",
    "Calle 142",
    "Calle 100",
    "Heroes",
    "Calle 72",
    "Calle 45",
    "Calle 26",
    "Av. Jimenez",
    "Suba",
    "Av. Boyaca",
    "Tercer Milenio",
    "Ricaurte",
    "Portal Sur",
    "Bosa",
]


# --------------------------------------------------------------------
# 1.b) POSICIONES PARA EL MAPA (solo para dibujar la red)
# --------------------------------------------------------------------
# Coordenadas (x, y) de cada estacion dentro del mapa grafico.
# NO afectan el algoritmo: sirven unicamente para saber en que lugar
# de la ventana se dibuja cada estacion. Estan pensadas para un lienzo
# aproximado de 900 x 600 pixeles.
POSICIONES = {
    "Portal Norte":   (120, 60),
    "Toberin":        (120, 140),
    "Calle 142":      (120, 220),
    "Calle 100":      (200, 300),
    "Heroes":         (300, 360),
    "Calle 72":       (300, 450),
    "Calle 45":       (400, 500),
    "Calle 26":       (450, 380),
    "Av. Jimenez":    (560, 420),
    "Suba":           (320, 120),
    "Av. Boyaca":     (400, 240),
    "Tercer Milenio": (660, 360),
    "Ricaurte":       (620, 500),
    "Portal Sur":     (720, 560),
    "Bosa":           (820, 520),
}


def obtener_posicion(estacion):
    """Devuelve la coordenada (x, y) de una estacion para el mapa."""
    return POSICIONES.get(estacion, (0, 0))


def obtener_conexiones_unicas():
    """
    Devuelve la lista de conexiones sin duplicar (un solo sentido).
    Util para dibujar cada linea del mapa una sola vez.
    Formato: [(origen, destino, costo), ...]
    """
    return list(_CONEXIONES)


def construir_red():
    """
    Construye el grafo (la red) a partir de la lista de conexiones.

    Devuelve un diccionario donde cada estacion apunta a la lista de
    sus conexiones. Las conexiones se agregan en AMBOS sentidos porque
    la red es no dirigida (se puede ir y volver).
    """
    red = {estacion: [] for estacion in ESTACIONES}

    for origen, destino, costo in _CONEXIONES:
        # Sentido origen -> destino
        red[origen].append((destino, costo))
        # Sentido destino -> origen (misma via, mismo costo)
        red[destino].append((origen, costo))

    return red


# La red ya construida y lista para usarse desde otros archivos.
RED = construir_red()


# --------------------------------------------------------------------
# 2) REGLAS BASICAS DE CONOCIMIENTO (como funciones simples)
# --------------------------------------------------------------------
# Estas funciones representan reglas del tipo "SI ... ENTONCES ...".
# Son la forma en que el sistema "razona" sobre la red.

def existe_estacion(estacion):
    """
    REGLA: una estacion solo puede usarse si pertenece a la red.

    Devuelve True si la estacion existe en la base de conocimiento,
    False en caso contrario.
    """
    return estacion in RED


def obtener_conexiones(estacion):
    """
    REGLA: si una estacion A esta conectada con B, entonces se puede
    viajar de A a B.

    Devuelve la lista de conexiones [(vecina, costo), ...] de la
    estacion dada. Si la estacion no existe, devuelve una lista vacia.
    """
    return RED.get(estacion, [])


def es_destino(estacion_actual, destino):
    """
    REGLA: si la estacion actual es igual al destino, se detiene la
    busqueda (ya llegamos).

    Devuelve True cuando la estacion actual coincide con el destino.
    """
    return estacion_actual == destino


def listar_estaciones():
    """
    Devuelve la lista de estaciones disponibles.
    Util para mostrarsela al usuario en la consola.
    """
    return list(ESTACIONES)

