'''
helpers.py contains functions that are reused across scripts

To access helper info in other files:
from utils.helpers import save_to_file

'''
import json
from pathlib import Path

from config import SILVER_DIR, GOLD_DIR

# Function for saving data as json
def save_to_file(data, file_path):
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# Importing raw files from silver
def import_silver(file_name):
    with open(SILVER_DIR / file_name, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    return raw_data

# Exporting clean files to gold
def export_gold(file_name, clean_data, indent_num):
    with open(GOLD_DIR / file_name, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, indent=indent_num, ensure_ascii=False)
    print(f"Output saved to data/gold/{file_name}")

# Set the type of each variable
def cast_record(record, type_map):
    for field, field_type in type_map.items():
        value = record.get(field)

        if value in (None, ""):
            record[field] = None
        else:
            try:
                record[field] = field_type(value)
            except (ValueError, TypeError):
                record[field] = None

    return record