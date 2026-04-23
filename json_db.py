# json_db.py
import json
import os

DATA_PATH = "data"

def read_json(file):
    """Read JSON file, return empty list if file doesn't exist"""
    path = os.path.join(DATA_PATH, file)
    
    # Create data folder if it doesn't exist
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        print(f"Created data folder at {DATA_PATH}")
    
    # Return empty list if file doesn't exist
    if not os.path.exists(path):
        print(f"File {path} not found, creating empty file")
        write_json(file, [])
        return []
    
    try:
        with open(path, "r", encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error reading {path}, returning empty list")
        return []

def write_json(file, data):
    """Write data to JSON file"""
    path = os.path.join(DATA_PATH, file)
    
    # Create data folder if it doesn't exist
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        print(f"Created data folder at {DATA_PATH}")
    
    try:
        with open(path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Successfully wrote to {path}")
        return True
    except Exception as e:
        print(f"Error writing to {path}: {e}")
        return False
