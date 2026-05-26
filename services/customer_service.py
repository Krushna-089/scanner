# services/customer_service.py
from json_db import read_json, write_json, get_timestamp
from debug_logger import log

def save_customer(phone, name, order_total=0):
    """Save or update customer information"""
    customers = read_json("customers.json")
    
    if phone in customers:
        # Update existing customer
        customer = customers[phone]
        customer["name"] = name
        customer["total_orders"] = customer.get("total_orders", 0) + 1
        customer["total_spent"] = customer.get("total_spent", 0) + order_total
        customer["last_order_date"] = get_timestamp()
        log(f"Updated customer {phone}", "INFO")
    else:
        # Create new customer
        customers[phone] = {
            "phone": phone,
            "name": name,
            "total_orders": 1,
            "total_spent": order_total,
            "last_order_date": get_timestamp(),
            "joined_date": get_timestamp()
        }
        log(f"Created new customer {phone}", "INFO")
    
    write_json("customers.json", customers)
    return customers[phone]

def get_customer(phone):
    """Get customer by phone number"""
    customers = read_json("customers.json")
    return customers.get(phone)

def get_all_customers():
    """Get all customers as list"""
    customers = read_json("customers.json")
    return list(customers.values())

def update_customer_stats(phone, order_total):
    """Update customer statistics after order"""
    customers = read_json("customers.json")
    
    if phone in customers:
        customers[phone]["total_orders"] += 1
        customers[phone]["total_spent"] += order_total
        customers[phone]["last_order_date"] = get_timestamp()
        write_json("customers.json", customers)
        return True
    return False
