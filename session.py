# session.py
from collections import defaultdict

user_sessions = defaultdict(lambda: {
    "step": "start",          # start, menu, selecting_category, selecting_item, asking_quantity, asking_addons, asking_spice, checkout, awaiting_name, awaiting_phone, order_status
    "cart": [],
    "current_category_id": None,
    "current_item": None,
    "current_quantity": 1,
    "current_addons": [],
    "current_spice": None,
    "name": None,
    "phone": None,
    "last_order_id": None      # store last order ID for quick status
})

def get_session(user_id):
    return user_sessions[user_id]

def clear_session(user_id):
    user_sessions[user_id] = {
        "step": "start",
        "cart": [],
        "current_category_id": None,
        "current_item": None,
        "current_quantity": 1,
        "current_addons": [],
        "current_spice": None,
        "name": None,
        "phone": None,
        "last_order_id": None
    }
