"""
generar_dataset.py
--------------------------------------------------------------------
GENERADOR DEL DATASET de muestra (datos simulados con fines academicos).

NO forma parte del modelo. Es solo una ayuda para CREAR el archivo
'datos_transporte.csv' de forma reproducible, con una logica razonable
y algo de variabilidad (ruido), para que el dataset parezca realista.

Idea:
  - Usamos las MISMAS estaciones del proyecto anterior (base_conocimiento).
  - Para cada registro inventamos: origen, destino, hora, dia, pasajeros,
    lluvia y hora_pico.
  - Calculamos una "puntuacion de congestion" con reglas sencillas:
      * mas pasajeros          -> mas congestion
      * hora pico              -> mas congestion
      * lluvia                 -> un poco mas de congestion y de tiempo
  - Convertimos esa puntuacion en la etiqueta: Baja / Media / Alta.
  - Agregamos ALGO de ruido para que el modelo NO acierte el 100%
    (asi es mas realista y mas honesto academicamente).

Se ejecuta UNA sola vez para generar el CSV:
    python generar_dataset.py

Usa 'random' con una semilla fija para que el resultado sea siempre
el mismo (reproducible). Solo depende de la libreria estandar.
"""

import csv
import os
import random

# Semilla fija: garantiza que el dataset generado sea SIEMPRE el mismo.
random.seed(42)

# Las mismas 15 estaciones del proyecto anterior (sistema de rutas).
# Se escriben aqui para que este generador no dependa de importar el
# otro modulo (y asi funcione aunque se ejecute suelto).
ESTACIONES = [
    "Portal Norte", "Toberin", "Calle 142", "Calle 100", "Heroes",
    "Calle 72", "Calle 45", "Calle 26", "Av. Jimenez", "Suba",
    "Av. Boyaca", "Tercer Milenio", "Ricaurte", "Portal Sur", "Bosa",
]

DIAS = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]

# Cuantos registros generar (el enunciado pide entre 120 y 200).
CANTIDAD = 160


def es_hora_pico(hora):
    """Horas pico tipicas: manana (6-8) y tarde (17-19)."""
    return 1 if (6 <= hora <= 8 or 17 <= hora <= 19) else 0


def calcular_tiempo(pasajeros, lluvia, hora_pico):
    """
    Tiempo estimado de viaje (en minutos) de forma simple:
      - base de 3 minutos
      - sube segun pasajeros
      - sube un poco si llueve
      - sube un poco en hora pico
      - mas un pequeno ruido aleatorio
    """
    tiempo = 3
    tiempo += pasajeros / 25        # mas pasajeros -> mas tiempo
    tiempo += 2 if lluvia else 0    # lluvia -> +2 min
    tiempo += 2 if hora_pico else 0  # hora pico -> +2 min
    tiempo += random.randint(-1, 1)  # ruido pequeno
    return max(2, int(round(tiempo)))


def calcular_puntuacion(pasajeros, lluvia, hora_pico):
    """
    Puntuacion interna de congestion (NO se guarda en el CSV).
    Combina las variables con una logica clara:
      - pasajeros es el factor mas importante
      - hora pico y lluvia suman puntos
    """
    puntuacion = 0.0
    puntuacion += pasajeros * 0.6     # factor principal
    puntuacion += 25 if hora_pico else 0
    puntuacion += 12 if lluvia else 0
    # Ruido: hace que casos parecidos a veces caigan en otra clase.
    puntuacion += random.uniform(-12, 12)
    return puntuacion


def clasificar(puntuacion):
    """Convierte la puntuacion numerica en la etiqueta de clase.

    Los umbrales se eligieron para que las tres clases queden
    razonablemente representadas en el dataset generado.
    """
    if puntuacion < 50:
        return "Baja"
    elif puntuacion < 80:
        return "Media"
    else:
        return "Alta"


def generar():
    """Genera la lista de registros (filas) del dataset."""
    filas = []
    for _ in range(CANTIDAD):
        # Elegimos origen y destino distintos.
        origen = random.choice(ESTACIONES)
        destino = random.choice([e for e in ESTACIONES if e != origen])

        hora = random.randint(5, 22)          # franja de operacion
        dia = random.choice(DIAS)
        hp = es_hora_pico(hora)

        # Los fines de semana suele haber menos pasajeros.
        if dia in ("Sabado", "Domingo"):
            pasajeros = random.randint(10, 90)
        else:
            pasajeros = random.randint(20, 160)

        lluvia = random.choice([0, 0, 0, 1])  # ~25% de probabilidad de lluvia

        tiempo = calcular_tiempo(pasajeros, lluvia, hp)
        puntuacion = calcular_puntuacion(pasajeros, lluvia, hp)
        nivel = clasificar(puntuacion)

        filas.append([
            origen, destino, hora, dia, pasajeros,
            lluvia, hp, tiempo, nivel,
        ])
    return filas


def main():
    filas = generar()

    # Guardamos el CSV junto a este archivo.
    ruta_csv = os.path.join(os.path.dirname(__file__), "datos_transporte.csv")

    with open(ruta_csv, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        # Encabezados (nombres de las columnas).
        escritor.writerow([
            "origen", "destino", "hora", "dia_semana", "pasajeros",
            "lluvia", "hora_pico", "tiempo_estimado", "nivel_congestion",
        ])
        escritor.writerows(filas)

    # Resumen por consola.
    print(f"Dataset generado: {ruta_csv}")
    print(f"Registros: {len(filas)}")
    conteo = {"Baja": 0, "Media": 0, "Alta": 0}
    for fila in filas:
        conteo[fila[-1]] += 1
    print(f"Distribucion de clases: {conteo}")


if __name__ == "__main__":
    main()
