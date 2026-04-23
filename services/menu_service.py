# services/menu_service.py
from json_db import read_json

def get_menu():
    categories = read_json("categories.json")
    # Ensure each category has an 'id' field
    for cat in categories:
        if "category_id" in cat and "id" not in cat:
            cat["id"] = cat["category_id"]
    return categories

def get_items(category_id):
    items = read_json("items.json")
    return [i for i in items if i["category_id"] == category_id]
