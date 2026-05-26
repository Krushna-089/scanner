# json_db.py
import json
import os
from datetime import datetime
from debug_logger import log

DATA_PATH = "data"

def ensure_data_dir():
    """Ensure data directory exists"""
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        log(f"Created data folder at {DATA_PATH}", "INFO")

def read_json(file):
    """Read JSON file, return empty list/dict if file doesn't exist"""
    ensure_data_dir()
    path = os.path.join(DATA_PATH, file)
    
    if not os.path.exists(path):
        log(f"File {path} not found, creating empty file", "DEBUG")
        # Determine default structure based on filename
        if "customers" in file:
            default_data = {}
        elif "promotions" in file:
            default_data = []
        else:
            default_data = []
        write_json(file, default_data)
        return default_data
    
    try:
        with open(path, "r", encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        log(f"Error reading {path}, returning empty structure", "ERROR")
        return {} if "customers" in file else []

def write_json(file, data):
    """Write data to JSON file"""
    ensure_data_dir()
    path = os.path.join(DATA_PATH, file)
    
    try:
        with open(path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        log(f"Successfully wrote to {path}", "DEBUG")
        return True
    except Exception as e:
        log(f"Error writing to {path}: {e}", "ERROR")
        return False

def append_json(file, new_item):
    """Append item to JSON array file"""
    data = read_json(file)
    if isinstance(data, list):
        data.append(new_item)
        return write_json(file, data)
    else:
        log(f"Cannot append to {file} - not a list", "ERROR")
        return False

def update_json(file, key_field, key_value, update_data):
    """Update item in JSON file by key"""
    data = read_json(file)
    
    if isinstance(data, list):
        for i, item in enumerate(data):
            if item.get(key_field) == key_value:
                data[i].update(update_data)
                return write_json(file, data)
    elif isinstance(data, dict):
        if key_value in data:
            data[key_value].update(update_data)
            return write_json(file, data)
    
    return False

def get_next_id(file, id_field="id"):
    """Get next available ID for list-type JSON file"""
    data = read_json(file)
    if isinstance(data, list) and data:
        return max(item.get(id_field, 0) for item in data) + 1
    return 1

def get_timestamp():
    """Return current timestamp in ISO format"""
    return datetime.now().isoformat()
