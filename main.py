import flet as ft
import random
from Funtions.pokefuns import obtener_pokemon_aleatorio
import requests
import json
import os
import sys

# Función para obtener rutas absolutas para recursos empaquetados
def resource_path(relative_path):
    """Obtiene la ruta absoluta del recurso, considerando el entorno empaquetado."""
    try:
        # Si está empaquetado con PyInstaller
        base_path = sys._MEIPASS
    except AttributeError:
        # Si se ejecuta desde el código fuente
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Función para obtener un nombre de Pokémon al azar
def obtener_nombre_pokemon_aleatorio():
    id_aleatorio = random.randint(1, 1010)  # Genera un ID aleatorio
    url = f"https://pokeapi.co/api/v2/pokemon/{id_aleatorio}"
    response = requests.get(url)
    if response.status_code == 200:
        datos = response.json()
        return datos["name"].capitalize()
    else:
        return None

def main(page: ft.Page):
    # Configuración inicial
    page.title = "Adivina el Pokémon"
    page.scroll = "adaptive"
    page.window_width = 360  # Ancho de la ventana
    page.window_height = 640  # Alto de la ventana

    # Variables globales
    pokemon_actual = {"Nombre": "", "Sprite": ""}
    opciones = []
    racha_actual = 0

    # Ruta del archivo JSON
    ruta_racha_user = resource_path('data/racha_user.json')

    # Cargar la racha más alta
    try:
        with open(ruta_racha_user, 'r') as archivo:
            dato = json.load(archivo)
        mayor_racha = dato.get('racha', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        mayor_racha = 0

    # Generar un nuevo desafío
    def nuevo_desafio():
        nonlocal pokemon_actual, opciones

        # Obtener un nuevo Pokémon
        pokemon_actual = obtener_pokemon_aleatorio()
        if not pokemon_actual:
            nombre_text.value = "Error al obtener Pokémon. Intenta de nuevo."
            sprite_image.src = None
            opciones_container.controls.clear()
            page.update()
            return

        # Generar las opciones (1 correcta + 2 aleatorias)
        opciones = [pokemon_actual["Nombre"].capitalize()]
        while len(opciones) < 3:
            nombre_aleatorio = obtener_nombre_pokemon_aleatorio()
            if nombre_aleatorio and nombre_aleatorio not in opciones:
                opciones.append(nombre_aleatorio)

        random.shuffle(opciones)  # Mezclar las opciones

        # Actualizar UI
        sprite_image.src = pokemon_actual["Sprite"]
        nombre_text.value = "¿Cuál es el nombre de este Pokémon?"
        opciones_container.controls = [
            ft.ElevatedButton(
                text=opcion,
                on_click=lambda e, opcion=opcion: verificar_respuesta(opcion)
            )
            for opcion in opciones
        ]
        page.update()

    # Verificar la respuesta del usuario
    def verificar_respuesta(opcion):
        nonlocal racha_actual, mayor_racha

        if opcion == pokemon_actual["Nombre"].capitalize():
            racha_actual += 1
            racha_text.value = f"Racha actual: {racha_actual}"  # Actualizar racha
            nombre_text.value = "¡Correcto! "
            if racha_actual > mayor_racha:
                mayor_racha = racha_actual
                with open(ruta_racha_user, 'w') as archivo:
                    json.dump({'racha': mayor_racha}, archivo)
            page.update()
            nuevo_desafio()  # Llamar directamente a la generación del nuevo desafío
        else:
            if racha_actual > mayor_racha:
                mayor_racha = racha_actual
                with open(ruta_racha_user, 'w') as archivo:
                    json.dump({'racha': mayor_racha}, archivo)
            racha_actual = 0
            racha_text.value = f"Racha actual: {racha_actual}"  # Reiniciar racha
            nombre_text.value = "¡Incorrecto! Intenta de nuevo."
            page.update()
            nuevo_desafio()

    # Elementos iniciales de la UI
    sprite_image = ft.Image(height=150, width=150)
    nombre_text = ft.Text(size=20, weight="bold", text_align="center")
    racha_text = ft.Text("Racha actual: 0", size=16, text_align="center")
    better_racha_text = ft.Text(f"Racha más larga: {mayor_racha}", size=16, text_align="center")
    opciones_container = ft.Column()

    # Contenedor principal con centrado
    layout = ft.Column(
        controls=[
            ft.Text("Adivina el Pokémon", size=30, weight="bold", text_align="center"),
            sprite_image,
            nombre_text,
            racha_text,
            better_racha_text,
            opciones_container,
        ],
        alignment="center",  # Centrar los elementos verticalmente
        horizontal_alignment="center",  # Centrar los elementos horizontalmente
    )

    # Agregar el layout a la página
    page.add(layout)

    # Iniciar el primer desafío
    nuevo_desafio()

# Ejecutar la aplicación
ft.app(target=main)
