🚆 Sistema Inteligente de Rutas - Transporte Masivo

Un sistema basado en conocimiento desarrollado en Python para calcular la ruta óptima de menor costo entre estaciones de una red de transporte masivo (inspirada en sistemas tipo TransMilenio).

El proyecto utiliza el algoritmo de Búsqueda de Costo Uniforme (Uniform Cost Search - UCS) sobre una estructura de datos orientada a grafos.

📸 Vista Previa (Consola)

Actualmente, el sistema interactúa de manera robusta y validada a través de la interfaz de consola:

==================================================
  SISTEMA INTELIGENTE DE RUTAS - TRANSPORTE MASIVO
  (Sistema Basado en Conocimiento)
==================================================

Estaciones disponibles:
   1. Portal Norte
   2. Toberin
   ...
  15. Bosa

Estacion de ORIGEN: Portal Norte
Estacion de DESTINO: Portal Sur

==================================================
  RUTA DE: Portal Norte  ->  Portal Sur
==================================================
  Secuencia de estaciones:
    Portal Norte  ->  Suba  ->  Portal Sur

  Costo total: 27
  Estaciones recorridas: 3
==================================================


🛠️ Arquitectura y Componentes

El proyecto está diseñado bajo una arquitectura modular que separa el conocimiento, la lógica de búsqueda y las interfaces:

base_conocimiento.py: Representa la Base de Conocimiento (BC). Contiene la topología del grafo (conexiones y costos/tiempos) y las reglas básicas de inferencia (existe_estacion, obtener_conexiones, etc.).

buscador.py: El Motor de Inferencia/Búsqueda. Implementa el algoritmo de Búsqueda de Costo Uniforme utilizando colas de prioridad (heapq).

main.py: Punto de entrada actual por interfaz de consola (CLI). Solicita datos, valida las entradas del usuario y presenta la ruta generada.

interfaz.py: (En desarrollo / Próximamente) Módulo destinado a la representación gráfica interactiva.

🚀 Algoritmo de Búsqueda

El núcleo del razonamiento utiliza Búsqueda de Costo Uniforme (UCS):

Mantiene una cola de prioridad ordenada por el costo acumulado.

Evalúa progresivamente la ruta más barata.

Evita ciclos mediante el control de nodos visitados.

Garantiza encontrar la ruta óptima en grafos con pesos o costos positivos.

🗂️ Requisitos e Instalación

Este proyecto fue construido utilizando únicamente la librería estándar de Python, por lo que no requiere dependencias ni paquetes externos.

Prerrequisitos

Python 3.8 o superior instalado.

Instalación

Clona este repositorio:

git clone https://github.com/tu-usuario/tu-repositorio.git
cd tu-repositorio


Ejecuta la versión de consola:

python main.py


🚧 Estado del Proyecto y Próximos Pasos

[x] Base de conocimiento con estaciones, relaciones y coordenadas.

[x] Motor de búsqueda basado en Costo Uniforme (UCS).

[x] Interfaz de consola (CLI) funcional con validaciones.

[ ] Interfaz Gráfica (GUI) (En Desarrollo):

Renderizado del mapa interactivo mediante Canvas en Tkinter.

Visualización y animación en tiempo real del proceso de exploración del algoritmo.

📄 Licencia

Este proyecto está bajo la licencia MIT. Siéntete libre de utilizarlo con fines académicos o educativos.
