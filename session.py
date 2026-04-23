# session.py
from collections import defaultdict

user_sessions = defaultdict(lambda: {
    "step": "start",           # start, menu, category_selected, adding_item, addons, spice, checkout
    "cart": [],
    "current_category_id": None,
    "current_item": None,
    "current_addons": [],
    "current_spice": None,
    "name": None,
    "phone": None
})

def get_session(user_id):
    return user_sessions[user_id]

def clear_session(user_id):
    user_sessions[user_id] = {
        "step": "start",
        "cart": [],
        "current_category_id": None,
        "current_item": None,
        "current_addons": [],
        "current_spice": None,
        "name": None,
        "phone": None
    }
