from json_db import read_json, write_json
import uuid

def create_order(name, phone, cart, total):
    orders = read_json("orders.json")

    order = {
        "id": str(uuid.uuid4()),
        "order_number": "ORD" + str(len(orders)+1),
        "name": name,
        "phone": phone,
        "cart": cart,
        "total": total,
        "status": "pending"
    }

    orders.append(order)
    write_json("orders.json", orders)

    return order
