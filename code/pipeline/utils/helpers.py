'''
helpers.py contains functions that are reused across scripts

To access helper info in other files:
from utils.helpers import save_to_file

'''
import json
from pathlib import Path

# Function for saving data as json
def save_to_file(data, file_path):
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)