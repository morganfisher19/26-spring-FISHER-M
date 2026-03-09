# Code from video: https://www.youtube.com/watch?v=JVQNywo4AbU

import requests
import json
from pathlib import Path

# Base url for extraction
base_url = "https://pokeapi.co/api/v2/"

def get_api_info(name):
    url = f"{base_url}/pokemon/{name}"
    response = requests.get(url)

    # Checking for status error
    if response.status_code == 200:
        # Storing response as json
        api_data = response.json()
        return api_data
    else:
        print(f"Failed to retrieve data {response.status_code}")

def save_to_file(data, file_path):
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

pokemon_name = "pikachu"
api_info = get_api_info(pokemon_name)

output_path = "./code/data/json_files/pikachu.json"
save_to_file(api_info, output_path)