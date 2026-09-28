"""
main.py
--------------------------------------------------------------------
INTERFAZ DE CONSOLA del sistema.

Este archivo es el punto de entrada del programa. Se encarga de:
  - Mostrar las estaciones disponibles.
  - Pedir al usuario el origen y el destino.
  - Validar que ambas estaciones existan.
  - Llamar al buscador para encontrar la mejor ruta.
  - Mostrar los resultados de forma clara.

Se ejecuta con:  python main.py
"""

from base_conocimiento import existe_estacion, listar_estaciones
from buscador import buscar_mejor_ruta


def mostrar_estaciones():
    """Muestra en pantalla todas las estaciones disponibles."""
    print("\nEstaciones disponibles:")
    for numero, estacion in enumerate(listar_estaciones(), start=1):
        print(f"  {numero:2d}. {estacion}")
    print()


def mostrar_resultado(origen, destino, ruta, costo):
    """
    Muestra el resultado de la busqueda de forma clara y ordenada.
    """
    print("\n" + "=" * 50)
    print(f"  RUTA DE: {origen}  ->  {destino}")
    print("=" * 50)

    if ruta is None:
        # No existe camino que conecte origen y destino.
        print("  No existe una ruta que conecte esas dos estaciones.")
        print("=" * 50 + "\n")
        return

    # Mostramos la secuencia de estaciones.
    print("  Secuencia de estaciones:")
    print("    " + "  ->  ".join(ruta))

    # Mostramos costo total y numero de estaciones recorridas.
    print(f"\n  Costo total: {costo}")
    print(f"  Estaciones recorridas: {len(ruta)}")
    print("=" * 50 + "\n")


def pedir_estacion(mensaje):
    """
    Pide una estacion al usuario y valida que exista.
    Repite hasta recibir una estacion valida.
    """
    while True:
        estacion = input(mensaje).strip()

        # REGLA: validar que la estacion exista en la base de conocimiento.
        if existe_estacion(estacion):
            return estacion

        print(f"  '{estacion}' no existe. Escribela tal cual aparece en la lista.\n")


def main():
    """Flujo principal del programa."""
    print("=" * 50)
    print("  SISTEMA INTELIGENTE DE RUTAS - TRANSPORTE MASIVO")
    print("  (Sistema Basado en Conocimiento)")
    print("=" * 50)

    mostrar_estaciones()

    # 1) Pedir y validar origen y destino.
    origen = pedir_estacion("Estacion de ORIGEN: ")
    destino = pedir_estacion("Estacion de DESTINO: ")

    # 2) Buscar la mejor ruta usando el algoritmo de costo uniforme.
    ruta, costo = buscar_mejor_ruta(origen, destino)

    # 3) Mostrar los resultados.
    mostrar_resultado(origen, destino, ruta, costo)


# Punto de entrada estandar de Python.
if __name__ == "__main__":
    main()
