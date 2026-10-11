"""
interfaz.py
--------------------------------------------------------------------
MAPA GRAFICO del sistema, hecho con Tkinter (Canvas).

Muestra la red de estaciones como un mapa (tipo metro) y ANIMA como el
algoritmo va explorando las estaciones y arma el recorrido paso a paso.

Tkinter viene incluido en la libreria estandar de Python: no hay que
instalar nada extra.

IMPORTANTE: el "cerebro" del sistema NO cambia. Se usa la misma base de
conocimiento (base_conocimiento.py) y el mismo algoritmo (buscador.py).
Aqui solo lo mostramos de forma visual.

Se ejecuta con:  python interfaz.py

Colores del mapa:
  - Gris claro : estacion normal.
  - Amarillo   : estacion que el algoritmo esta explorando (animacion).
  - Verde      : ruta final encontrada.
  - Azul       : origen y destino elegidos.
"""

import tkinter as tk
from tkinter import ttk

from base_conocimiento import (
    listar_estaciones,
    obtener_posicion,
    obtener_conexiones_unicas,
)
from buscador import buscar_con_historial

# --- Integracion con el modelo de congestion (parte 2 del proyecto) ---
# Se importa de forma OPCIONAL: si falta scikit-learn o el modelo, la
# interfaz sigue funcionando igual que antes (solo sin los checks).
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "aprendizaje_supervisado"))
try:
    from modelo_congestion import preparar_modelo, sugerir_ruta
    CONGESTION_DISPONIBLE = True
except Exception:
    CONGESTION_DISPONIBLE = False


# ---- Colores ----
COLOR_FONDO = "#eef2f6"
COLOR_LIENZO = "#ffffff"
COLOR_LINEA = "#b8c4d0"
COLOR_ESTACION = "#d7dee6"
COLOR_BORDE = "#8a97a4"
COLOR_EXPLORANDO = "#ffd24d"   # amarillo
COLOR_RUTA = "#2ecc71"         # verde
COLOR_ORIGEN = "#16a085"       # verde azulado (estacion de inicio)
COLOR_DESTINO = "#e67e22"      # naranja (estacion de fin)
COLOR_LINEA_RUTA = "#2d6cdf"   # azul: lineas del recorrido de la ruta
COLOR_LINEA_AJUSTE = "#e67e22"  # naranja: lineas de la ruta ajustada
COLOR_TITULO = "#1f4e79"
COLOR_TEXTO = "#333333"

# Radio de cada estacion (circulo) en el mapa.
RADIO = 16

# Tiempo entre cada paso de la animacion (milisegundos).
RETARDO_MS = 600


class MapaRutas:
    """Ventana con el mapa de estaciones y la animacion de busqueda."""

    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Mapa Inteligente de Rutas - Transporte Masivo")
        self.ventana.configure(bg=COLOR_FONDO)

        # Guarda los identificadores de los circulos dibujados,
        # para poder cambiarles el color despues.
        self.circulos = {}

        # Guarda los identificadores de las LINEAS (conexiones) dibujadas,
        # para poder resaltar el recorrido de la ruta. La clave es un
        # frozenset {origen, destino} para que sirva en ambos sentidos.
        self.lineas = {}

        self._construir_controles()
        self._construir_lienzo()
        self._dibujar_red()

    # ----------------------------------------------------------------
    # Zona superior: titulo, menus y boton.
    # ----------------------------------------------------------------
    def _construir_controles(self):
        tk.Label(
            self.ventana,
            text="Mapa Inteligente de Rutas",
            font=("Segoe UI", 16, "bold"),
            bg=COLOR_FONDO, fg=COLOR_TITULO,
        ).pack(pady=(12, 0))

        tk.Label(
            self.ventana,
            text="Elige origen y destino y observa como se arma el recorrido.",
            font=("Segoe UI", 10),
            bg=COLOR_FONDO, fg=COLOR_TEXTO,
        ).pack(pady=(0, 8))

        panel = tk.Frame(self.ventana, bg=COLOR_FONDO)
        panel.pack(pady=(0, 8))

        estaciones = listar_estaciones()

        tk.Label(panel, text="Origen:", bg=COLOR_FONDO,
                 font=("Segoe UI", 10)).grid(row=0, column=0, padx=5)
        self.combo_origen = ttk.Combobox(
            panel, values=estaciones, state="readonly", width=18)
        self.combo_origen.grid(row=0, column=1, padx=5)
        # Cuando el usuario elige un origen, se pinta en el mapa.
        self.combo_origen.bind(
            "<<ComboboxSelected>>", self._marcar_seleccion)

        tk.Label(panel, text="Destino:", bg=COLOR_FONDO,
                 font=("Segoe UI", 10)).grid(row=0, column=2, padx=5)
        self.combo_destino = ttk.Combobox(
            panel, values=estaciones, state="readonly", width=18)
        self.combo_destino.grid(row=0, column=3, padx=5)
        # Cuando el usuario elige un destino, se pinta en el mapa.
        self.combo_destino.bind(
            "<<ComboboxSelected>>", self._marcar_seleccion)

        self.boton = tk.Button(
            panel, text="Buscar ruta", font=("Segoe UI", 10, "bold"),
            bg=COLOR_TITULO, fg="white", relief="flat",
            padx=14, pady=4, cursor="hand2",
            command=self.iniciar_busqueda,
        )
        self.boton.grid(row=0, column=4, padx=10)

        # ---- Checks de condiciones (usan el modelo de congestion) ----
        # Solo se muestran si el componente de congestion esta disponible.
        self.var_hora_pico = tk.IntVar(value=0)
        self.var_lluvia = tk.IntVar(value=0)

        if CONGESTION_DISPONIBLE:
            fila_checks = tk.Frame(self.ventana, bg=COLOR_FONDO)
            fila_checks.pack(pady=(0, 6))

            tk.Label(
                fila_checks, text="Condiciones (ajustan la ruta por congestion):",
                bg=COLOR_FONDO, font=("Segoe UI", 9, "italic"),
                fg=COLOR_TEXTO,
            ).grid(row=0, column=0, padx=6)

            tk.Checkbutton(
                fila_checks, text="Hora pico", variable=self.var_hora_pico,
                bg=COLOR_FONDO, font=("Segoe UI", 10),
                command=self._marcar_seleccion,
            ).grid(row=0, column=1, padx=6)

            tk.Checkbutton(
                fila_checks, text="Lluvia", variable=self.var_lluvia,
                bg=COLOR_FONDO, font=("Segoe UI", 10),
                command=self._marcar_seleccion,
            ).grid(row=0, column=2, padx=6)

            # Entrenamos el modelo UNA vez al abrir la ventana.
            self._modelo_congestion = preparar_modelo()
        else:
            self._modelo_congestion = None

        # Etiqueta de resultado (texto).
        self.etiqueta_resultado = tk.Label(
            self.ventana,
            text="",
            font=("Segoe UI", 11, "bold"),
            bg=COLOR_FONDO, fg=COLOR_TEXTO,
        )
        self.etiqueta_resultado.pack(pady=(0, 2))

        # Segunda etiqueta: ruta ajustada por congestion (parte 2).
        self.etiqueta_congestion = tk.Label(
            self.ventana,
            text="",
            font=("Segoe UI", 10),
            bg=COLOR_FONDO, fg=COLOR_TEXTO,
            justify="left",
        )
        self.etiqueta_congestion.pack(pady=(0, 4))

    # ----------------------------------------------------------------
    # Lienzo donde se dibuja el mapa.
    # ----------------------------------------------------------------
    def _construir_lienzo(self):
        self.lienzo = tk.Canvas(
            self.ventana, width=900, height=600,
            bg=COLOR_LIENZO, highlightthickness=1,
            highlightbackground=COLOR_BORDE,
        )
        self.lienzo.pack(padx=12, pady=(0, 12))

    # ----------------------------------------------------------------
    # Dibuja las conexiones y las estaciones en su posicion.
    # ----------------------------------------------------------------
    def _dibujar_red(self):
        # 1) Dibujar primero las lineas (para que queden por debajo).
        for origen, destino, costo in obtener_conexiones_unicas():
            x1, y1 = obtener_posicion(origen)
            x2, y2 = obtener_posicion(destino)
            linea = self.lienzo.create_line(
                x1, y1, x2, y2, fill=COLOR_LINEA, width=3)
            # Guardamos el id de la linea para poder resaltarla despues.
            # La clave es un frozenset para que sirva en ambos sentidos.
            self.lineas[frozenset((origen, destino))] = linea
            # Costo en el punto medio de la linea.
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            self.lienzo.create_text(
                mx, my - 8, text=str(costo),
                font=("Segoe UI", 8), fill="#7a8794")

        # 2) Dibujar las estaciones (circulos + nombre).
        for estacion in listar_estaciones():
            x, y = obtener_posicion(estacion)
            circulo = self.lienzo.create_oval(
                x - RADIO, y - RADIO, x + RADIO, y + RADIO,
                fill=COLOR_ESTACION, outline=COLOR_BORDE, width=2)
            self.circulos[estacion] = circulo
            self.lienzo.create_text(
                x, y - RADIO - 10, text=estacion,
                font=("Segoe UI", 8, "bold"), fill=COLOR_TEXTO)

    def _pintar(self, estacion, color):
        """Cambia el color de relleno de una estacion en el mapa."""
        if estacion in self.circulos:
            self.lienzo.itemconfig(self.circulos[estacion], fill=color)

    def _reiniciar_colores(self):
        """Vuelve todas las estaciones y lineas al color normal."""
        for estacion in self.circulos:
            self._pintar(estacion, COLOR_ESTACION)
        # Tambien reiniciamos las lineas (color y grosor normales).
        for linea in self.lineas.values():
            self.lienzo.itemconfig(linea, fill=COLOR_LINEA, width=3)

    def _pintar_ruta_lineas(self, ruta, color):
        """
        Resalta las LINEAS que forman el recorrido de una ruta.
        Recorre la ruta por pares de estaciones consecutivas y pinta
        cada tramo con el color dado y un grosor mayor, para que se vea
        claramente por donde pasa.
        """
        if not ruta:
            return
        for i in range(len(ruta) - 1):
            clave = frozenset((ruta[i], ruta[i + 1]))
            if clave in self.lineas:
                self.lienzo.itemconfig(self.lineas[clave], fill=color, width=6)

    def _marcar_seleccion(self, evento=None):
        """
        Se ejecuta cada vez que el usuario elige un origen o un destino.
        Repinta el mapa: origen en verde azulado y destino en naranja,
        para que se vea claramente antes de buscar la ruta.
        """
        # Partimos de todo en gris para no dejar colores viejos.
        self._reiniciar_colores()

        origen = self.combo_origen.get()
        destino = self.combo_destino.get()

        if origen:
            self._pintar(origen, COLOR_ORIGEN)
        if destino:
            self._pintar(destino, COLOR_DESTINO)

        # Mensaje guia para el usuario.
        if origen and destino:
            self.etiqueta_resultado.config(
                text=f"Origen: {origen}  |  Destino: {destino}  "
                     f"(presiona 'Buscar ruta')",
                fg=COLOR_TEXTO)

    # ----------------------------------------------------------------
    # Ejecuta la busqueda y lanza la animacion.
    # ----------------------------------------------------------------
    def iniciar_busqueda(self):
        origen = self.combo_origen.get()
        destino = self.combo_destino.get()

        # Validaciones basicas.
        if not origen or not destino:
            self.etiqueta_resultado.config(
                text="Selecciona origen y destino.", fg=COLOR_TEXTO)
            return
        if origen == destino:
            self.etiqueta_resultado.config(
                text="El origen y el destino son la misma estacion.",
                fg=COLOR_TEXTO)
            return

        # Limpiamos el mapa y volvemos a marcar origen y destino.
        self._reiniciar_colores()
        self._pintar(origen, COLOR_ORIGEN)
        self._pintar(destino, COLOR_DESTINO)
        self.boton.config(state="disabled")

        # Llamamos al algoritmo con historial (mismo cerebro).
        ruta, costo, historial = buscar_con_historial(origen, destino)

        # Guardamos los datos para la animacion.
        self._ruta = ruta
        self._costo = costo
        self._historial = historial
        self._origen = origen
        self._destino = destino

        self.etiqueta_resultado.config(
            text="Explorando estaciones...", fg=COLOR_TEXTO)

        # Empezamos la animacion de exploracion en el paso 0.
        self._animar_exploracion(0)

    def _animar_exploracion(self, indice):
        """
        Pinta de amarillo cada estacion que el algoritmo evalua,
        una por una, usando el retardo para que se vea el proceso.
        """
        if indice < len(self._historial):
            estacion = self._historial[indice]
            # No tapamos el origen ni el destino: mantienen su color.
            if estacion not in (self._origen, self._destino):
                self._pintar(estacion, COLOR_EXPLORANDO)
            # Programa el siguiente paso.
            self.ventana.after(
                RETARDO_MS,
                lambda: self._animar_exploracion(indice + 1))
        else:
            # Termino la exploracion: mostramos el resultado final.
            self._mostrar_resultado_final()

    def _mostrar_resultado_final(self):
        if self._ruta is None:
            self.etiqueta_resultado.config(
                text="No existe una ruta que conecte esas estaciones.",
                fg=COLOR_DESTINO)
            self.boton.config(state="normal")
            return

        # Pintamos las LINEAS del recorrido de azul (para ver el camino).
        self._pintar_ruta_lineas(self._ruta, COLOR_LINEA_RUTA)

        # Pintamos la ruta final de verde.
        for estacion in self._ruta:
            self._pintar(estacion, COLOR_RUTA)

        # Origen y destino conservan sus colores propios (verde azulado
        # y naranja) para distinguirlos de las estaciones intermedias.
        self._pintar(self._origen, COLOR_ORIGEN)
        self._pintar(self._destino, COLOR_DESTINO)

        secuencia = "  ->  ".join(self._ruta)
        self.etiqueta_resultado.config(
            text=(f"Ruta base: {secuencia}    |    "
                  f"Costo base: {self._costo}    |    "
                  f"Estaciones: {len(self._ruta)}"),
            fg=COLOR_RUTA)

        # ---- Ruta ajustada por congestion (parte 2) ----
        self._mostrar_congestion()

        self.boton.config(state="normal")

    def _mostrar_congestion(self):
        """
        Si el modelo de congestion esta disponible, calcula la ruta
        teniendo en cuenta las condiciones (hora pico / lluvia) y la
        muestra. Si esa ruta es distinta a la base, la pinta en el mapa.
        """
        if not CONGESTION_DISPONIBLE or self._modelo_congestion is None:
            return

        hora_pico = self.var_hora_pico.get()
        lluvia = self.var_lluvia.get()

        # Si no hay ninguna condicion activa, no hay nada que ajustar.
        if not hora_pico and not lluvia:
            self.etiqueta_congestion.config(
                text="(Activa 'Hora pico' o 'Lluvia' para ver el ajuste "
                     "por congestion)",
                fg=COLOR_TEXTO)
            return

        # Ruta SIN condiciones (todo congestion baja = costos base).
        # La usamos como referencia para comparar: asi el cambio de ruta
        # se debe exclusivamente a las condiciones activadas.
        base = sugerir_ruta(
            self._modelo_congestion, self._origen, self._destino,
            hora_pico=0, lluvia=0)
        ruta_base = base["ruta"]

        # Ruta CON las condiciones activadas (hora pico / lluvia).
        resultado = sugerir_ruta(
            self._modelo_congestion, self._origen, self._destino,
            hora_pico, lluvia)

        ruta_ajustada = resultado["ruta"]
        costo_ajustado = resultado["costo"]

        condiciones = []
        if hora_pico:
            condiciones.append("hora pico")
        if lluvia:
            condiciones.append("lluvia")
        texto_cond = " y ".join(condiciones)

        cambio = ruta_ajustada != ruta_base
        secuencia = "  ->  ".join(ruta_ajustada)

        if cambio:
            # La ruta cambio: resaltamos sus LINEAS en naranja y sus
            # estaciones en amarillo, para distinguirla de la ruta base.
            self._pintar_ruta_lineas(ruta_ajustada, COLOR_LINEA_AJUSTE)
            for estacion in ruta_ajustada:
                self._pintar(estacion, COLOR_EXPLORANDO)
            self._pintar(self._origen, COLOR_ORIGEN)
            self._pintar(self._destino, COLOR_DESTINO)
            self.etiqueta_congestion.config(
                text=(f"Con {texto_cond}, conviene OTRA ruta: {secuencia}  "
                      f"(costo ajustado: {costo_ajustado})"),
                fg=COLOR_DESTINO)
        else:
            self.etiqueta_congestion.config(
                text=(f"Con {texto_cond}, la ruta se mantiene pero el "
                      f"costo sube a {costo_ajustado} por la congestion."),
                fg=COLOR_DESTINO)


if __name__ == "__main__":
    ventana = tk.Tk()
    app = MapaRutas(ventana)
    ventana.mainloop()
