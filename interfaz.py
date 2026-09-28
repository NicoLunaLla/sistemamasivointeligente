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

        self._construir_controles()
        self._construir_lienzo()
        self._dibujar_red()

    # ----------------------------------------------------------------
# Zona superior: titulo, menus y boton.abs    # ----------------------------------------------------------------
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

        # Etiqueta de resultado (texto).
        self.etiqueta_resultado = tk.Label(
            self.ventana,
            text="",
            font=("Segoe UI", 11, "bold"),
            bg=COLOR_FONDO, fg=COLOR_TEXTO,
        )
        self.etiqueta_resultado.pack(pady=(0, 4))

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
            self.lienzo.create_line(
                x1, y1, x2, y2, fill=COLOR_LINEA, width=3)
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
        """Vuelve todas las estaciones al color normal."""
        for estacion in self.circulos:
            self._pintar(estacion, COLOR_ESTACION)

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

        # Pintamos la ruta final de verde.
        for estacion in self._ruta:
            self._pintar(estacion, COLOR_RUTA)

        # Origen y destino conservan sus colores propios (verde azulado
        # y naranja) para distinguirlos de las estaciones intermedias.
        self._pintar(self._origen, COLOR_ORIGEN)
        self._pintar(self._destino, COLOR_DESTINO)

        secuencia = "  ->  ".join(self._ruta)
        self.etiqueta_resultado.config(
            text=(f"Ruta: {secuencia}    |    "
                  f"Costo total: {self._costo}    |    "
                  f"Estaciones: {len(self._ruta)}"),
            fg=COLOR_RUTA)

        self.boton.config(state="normal")


if __name__ == "__main__":
    ventana = tk.Tk()
    app = MapaRutas(ventana)
    ventana.mainloop()
