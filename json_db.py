# json_db.py
import json
import os

DATA_PATH = "data"

def read_json(file):
    path = os.path.join(DATA_PATH, file)
    if not os.path.exists(path):
        # Create empty file if doesn't exist
        with open(path, "w") as f:
            json.dump([], f)
    with open(path, "r") as f:
        return json.load(f)

def write_json(file, data):
    path = os.path.join(DATA_PATH, file)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
