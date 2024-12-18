import requests
import random

def obtener_pokemon_aleatorio():
    id_aleatorio = random.randint(1, 1010)  # Actualizado según la PokéAPI

    url = f"https://pokeapi.co/api/v2/pokemon/{id_aleatorio}"
    response = requests.get(url)
    
    if response.status_code == 200:
        datos = response.json()
        # Extraer información relevante
        return {
            "ID": datos["id"],
            "Nombre": datos["name"],
            "Sprite": datos["sprites"]["front_default"]
        }
    else:
        return f"Error al obtener Pokémon: {response.status_code}"