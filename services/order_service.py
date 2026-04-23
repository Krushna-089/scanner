# services/order_service.py
from json_db import read_json, write_json
import uuid
from datetime import datetime

def create_order(name, phone, cart, total):
    orders = read_json("orders.json")
    
    order_number = f"ORD{len(orders)+1:04d}"  # ORD0001, ORD0002, etc.
    
    order = {
        "id": str(uuid.uuid4()),
        "order_number": order_number,
        "name": name,
        "phone": phone,
        "cart": cart,           # full cart with addons, spice, quantity
        "total": total,
        "status": "received",    # initial status: received
        "created_at": datetime.now().isoformat()
    }
    
    orders.append(order)
    write_json("orders.json", orders)
    
    return order

def get_order_by_id(order_number):
    """Search order by order_number (e.g., ORD0001)"""
    orders = read_json("orders.json")
    for order in orders:
        if order["order_number"] == order_number:
            return order
    return None

def update_order_status(order_number, new_status):
    orders = read_json("orders.json")
    for order in orders:
        if order["order_number"] == order_number:
            order["status"] = new_status
            write_json("orders.json", orders)
            return True
    return False
