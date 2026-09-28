"""
buscador.py
--------------------------------------------------------------------
MOTOR DE BUSQUEDA (la parte que "razona" para encontrar la ruta).

Aqui se implementa el algoritmo que usa la base de conocimiento para
encontrar la MEJOR ruta (la de MENOR COSTO) entre dos estaciones.

Algoritmo usado: BUSQUEDA DE COSTO UNIFORME (Uniform Cost Search).
  - Es una variante de Dijkstra guiada por el costo acumulado.
  - Usa una cola de prioridad (heapq) para expandir siempre primero
    el camino mas barato encontrado hasta el momento.
  - Garantiza encontrar la ruta de menor costo total.
"""

import heapq  # Cola de prioridad de la libreria estandar de Python.

from base_conocimiento import obtener_conexiones, es_destino


def buscar_mejor_ruta(origen, destino):
    """
    Encuentra la ruta de menor costo entre 'origen' y 'destino'.

    Devuelve una tupla (ruta, costo_total):
      - ruta: lista de estaciones desde el origen hasta el destino.
      - costo_total: suma de los costos de las conexiones usadas.

    Si NO existe ruta, devuelve (None, None).

    Idea del algoritmo (paso a paso):
      1) Guardamos en una cola de prioridad los caminos por explorar,
         ordenados por su costo acumulado (el mas barato sale primero).
      2) Sacamos el camino mas barato. Si su ultima estacion es el
         destino -> encontramos la mejor ruta.
      3) Si esa estacion ya fue visitada, la ignoramos (regla: una
         estacion visitada no se vuelve a evaluar).
      4) Si no, la marcamos como visitada y agregamos a la cola los
         caminos que resultan de ir a cada estacion vecina.
      5) Repetimos hasta llegar al destino o quedarnos sin caminos.
    """

    # Cola de prioridad. Cada elemento es una tupla:
    #   (costo_acumulado, ruta_hasta_aqui)
    # heapq ordena por el primer valor de la tupla (el costo).
    frontera = [(0, [origen])]

    # Conjunto de estaciones ya evaluadas (para no repetir trabajo).
    visitadas = set()

    while frontera:
        # 1) Sacamos el camino de MENOR costo acumulado.
        costo_actual, ruta = heapq.heappop(frontera)

        # La estacion en la que estamos es la ultima de la ruta.
        estacion_actual = ruta[-1]

        # 2) REGLA: si la estacion actual es el destino, terminamos.
        if es_destino(estacion_actual, destino):
            return ruta, costo_actual

        # 3) REGLA: si ya visitamos esta estacion, la saltamos.
        if estacion_actual in visitadas:
            continue

        # Marcamos la estacion como visitada.
        visitadas.add(estacion_actual)

        # 4) Expandimos: revisamos las estaciones vecinas.
        for vecina, costo in obtener_conexiones(estacion_actual):
            if vecina not in visitadas:
                nueva_ruta = ruta + [vecina]
                nuevo_costo = costo_actual + costo
                heapq.heappush(frontera, (nuevo_costo, nueva_ruta))

    # 5) Si vaciamos la frontera sin llegar al destino, no hay ruta.
    return None, None


def buscar_con_historial(origen, destino):
    """
    Igual que buscar_mejor_ruta, pero ademas registra el ORDEN en que
    el algoritmo va evaluando las estaciones. Sirve para ANIMAR el mapa
    y ver como se arma el recorrido paso a paso.

    Devuelve una tupla (ruta, costo, historial):
      - ruta: lista de estaciones de la mejor ruta (o None).
      - costo: costo total (o None).
      - historial: lista de estaciones en el orden en que fueron
        visitadas (evaluadas) por el algoritmo.

    La logica del algoritmo es EXACTAMENTE la misma que buscar_mejor_ruta;
    lo unico que agregamos es ir guardando cada estacion visitada.
    """
    frontera = [(0, [origen])]
    visitadas = set()
    historial = []  # orden de estaciones evaluadas

    while frontera:
        costo_actual, ruta = heapq.heappop(frontera)
        estacion_actual = ruta[-1]

        if es_destino(estacion_actual, destino):
            historial.append(estacion_actual)
            return ruta, costo_actual, historial

        if estacion_actual in visitadas:
            continue

        visitadas.add(estacion_actual)
        historial.append(estacion_actual)  # registramos el paso

        for vecina, costo in obtener_conexiones(estacion_actual):
            if vecina not in visitadas:
                nueva_ruta = ruta + [vecina]
                nuevo_costo = costo_actual + costo
                heapq.heappush(frontera, (nuevo_costo, nueva_ruta))

    return None, None, historial
