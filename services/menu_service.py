from json_db import read_json

def get_menu():
    return read_json("categories.json")

def get_items(category_id):
    items = read_json("items.json")
    return [i for i in items if i["category_id"] == category_id]
