# Sistema Inteligente de Rutas - Transporte Masivo

Proyecto académico para la materia de **Inteligencia Artificial**, tema **Sistemas Basados en Conocimiento (SBC)**.

## Objetivo

Construir un sistema inteligente que, a partir de una **base de conocimiento** representada con reglas lógicas y un grafo de estaciones, encuentre la **mejor ruta** (la de **menor costo**) para desplazarse desde un punto A hasta un punto B dentro de un sistema de transporte masivo urbano, inspirado en TransMilenio (red simplificada y ficticia).

## ¿Qué es la base de conocimiento?

La **base de conocimiento** es todo lo que el sistema "sabe" sobre el mundo del problema. En este proyecto está en `base_conocimiento.py` e incluye:

- **Hechos:** las estaciones que existen y las conexiones entre ellas.
- **Costos:** el peso de cada conexión (lo interpretamos como minutos de viaje).
- **Reglas:** funciones simples que representan cómo se puede razonar sobre esos hechos.

La red se modela como un **grafo no dirigido**: si la estación A se conecta con B, también se puede ir de B a A con el mismo costo.

## Las reglas lógicas

Las reglas se expresan como pequeñas funciones y condiciones dentro del código:

1. **Conexión:** *Si* la estación A está conectada con la estación B, *entonces* se puede viajar de A a B. → `obtener_conexiones()`
2. **No repetir:** *Si* una estación ya fue visitada, *entonces* no se vuelve a evaluar. → conjunto `visitadas` en `buscador.py`
3. **Llegada:** *Si* la estación actual es igual al destino, *entonces* se detiene la búsqueda. → `es_destino()`
4. **Prioridad por costo:** *Si* existen varias rutas posibles, *entonces* se prioriza la de menor costo acumulado. → cola de prioridad `heapq`
5. **Validación:** *Si* una estación no existe en la red, *entonces* no es una entrada válida. → `existe_estacion()`

## El algoritmo de búsqueda

Se usa **Búsqueda de Costo Uniforme** (Uniform Cost Search), una variante de Dijkstra:

- Mantiene una **cola de prioridad** (`heapq`) con los caminos por explorar, ordenados por su **costo acumulado**.
- Siempre expande primero el camino **más barato** encontrado hasta el momento.
- Marca las estaciones ya evaluadas para no repetir trabajo.
- Termina cuando saca de la cola un camino cuya última estación es el destino.

**¿Por qué encuentra la ruta de menor costo?** Porque siempre saca de la cola el camino de menor costo acumulado. Cuando el destino sale de la cola por primera vez, es imposible que exista otro camino más barato hacia él (cualquier otro camino pendiente ya tiene un costo mayor o igual). Por eso la primera vez que se alcanza el destino, se garantiza que es la mejor ruta.

## Requisitos

- **Python 3.8 o superior.**
- Solo se usa la **librería estándar** de Python (`heapq`). No hay dependencias externas.

## Instrucciones para ejecutar

Hay **dos formas** de usar el sistema. Ambas usan el mismo cerebro (base de conocimiento + algoritmo); solo cambia la forma de mostrar la información.

### Opción 1 - Consola (terminal)

```bash
python main.py
```

Muestra la lista de estaciones y pide el origen y el destino. Hay que escribir el nombre de la estación **tal cual aparece en la lista**.

### Opción 2 - Mapa gráfico (front visual)

```bash
python interfaz.py
```

Abre una ventana con un **mapa de la red** (tipo mapa de metro). Eliges el origen y el destino en los menús y presionas **"Buscar ruta"**. Entonces el mapa **anima** cómo el algoritmo va explorando las estaciones y finalmente resalta la mejor ruta.

Colores del mapa:

- **Gris:** estación normal.
- **Amarillo:** estación que el algoritmo está explorando (animación paso a paso).
- **Verde:** la mejor ruta encontrada.
- **Azul:** origen y destino.

Usa **Tkinter** (Canvas), incluido en la librería estándar de Python. No hay que instalar nada.

## Ejemplo de uso

```
==================================================
  SISTEMA INTELIGENTE DE RUTAS - TRANSPORTE MASIVO
  (Sistema Basado en Conocimiento)
==================================================

Estaciones disponibles:
   1. Portal Norte
   2. Toberin
   ...

Estacion de ORIGEN: Portal Norte
Estacion de DESTINO: Av. Jimenez

==================================================
  RUTA DE: Portal Norte  ->  Av. Jimenez
==================================================
  Secuencia de estaciones:
    Portal Norte  ->  Suba  ->  Av. Boyaca  ->  Calle 26  ->  Av. Jimenez

  Costo total: 24
  Estaciones recorridas: 5
==================================================
```

> Nota: la troncal directa (Portal Norte → Toberín → ... → Av. Jiménez) costaría 34.
> El algoritmo elige la ruta por Suba porque su costo (24) es menor. Esto demuestra
> que el sistema realmente compara rutas alternativas y prioriza la más barata.

## Estructura del proyecto

```
Sistema_Rutas_IA/
│
├── base_conocimiento.py   # Base de conocimiento: estaciones, conexiones, costos y reglas.
├── buscador.py            # Algoritmo de búsqueda de costo uniforme (heapq).
├── main.py                # Interfaz de CONSOLA: pide datos, valida y muestra resultados.
├── interfaz.py            # MAPA GRÁFICO (Tkinter Canvas): anima la búsqueda sobre la red.
├── README.md              # Este documento.
└── pruebas/
    └── pruebas_rutas.md   # Casos de prueba con entradas y resultados esperados.
```

## Conceptos de Sistemas Basados en Conocimiento aplicados

- **Base de conocimiento:** hechos (estaciones, conexiones) y reglas separados del motor que los usa.
- **Representación del conocimiento:** el grafo (diccionario) y las tuplas `(vecina, costo)`.
- **Motor de inferencia / razonamiento:** el algoritmo de `buscador.py` que combina las reglas para deducir la mejor ruta.
- **Separación conocimiento / razonamiento:** se puede cambiar la red sin tocar el algoritmo, y viceversa.
