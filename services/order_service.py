# services/order_service.py (only the create_order function - rest unchanged)
from json_db import read_json, write_json
import uuid
from datetime import datetime
from debug_logger import log  # Add this import

def create_order(name, phone, cart, total):
    log(f"Creating order for {name}, phone: {phone}, total: {total}", "INFO")
    
    orders = read_json("orders.json")
    log(f"Current orders count: {len(orders)}", "DEBUG")
    
    order_number = f"ORD{len(orders)+1:04d}"
    calculated_total = calculate_order_total(cart)
    
    order = {
        "id": str(uuid.uuid4()),
        "order_number": order_number,
        "name": name,
        "phone": phone,
        "cart": cart,
        "total": calculated_total,
        "status": "received",
        "created_at": datetime.now().isoformat()
    }
    
    orders.append(order)
    log(f"Appending order: {order_number}", "DEBUG")
    
    success = write_json("orders.json", orders)
    
    if success:
        log(f"✅ Order saved successfully: {order_number}", "INFO")
    else:
        log(f"❌ Failed to save order: {order_number}", "ERROR")
    
    # Also print to console for Render logs
    print(f"Order saved: {order_number} - Total: ${calculated_total}")
    print(f"Total orders now: {len(orders)}")
    
    return order
    
def get_order_by_id(order_number):
    """Search order by order_number (e.g., ORD0001)"""
    orders = read_json("orders.json")
    for order in orders:
        if order["order_number"] == order_number:
            return order
    return None

def get_order_by_order_number(order_number):
    """Alias for get_order_by_id"""
    return get_order_by_id(order_number)

def update_order_status(order_number, new_status):
    orders = read_json("orders.json")
    for order in orders:
        if order["order_number"] == order_number:
            order["status"] = new_status
            write_json("orders.json", orders)
            return True
    return False

def calculate_order_total(cart):
    total = 0
    for item in cart:
        total += item["price"] * item["quantity"]
        for addon in item.get("addons", []):
            total += addon["price"] * item["quantity"]
    return round(total, 2)
