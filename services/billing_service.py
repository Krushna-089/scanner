# services/billing_service.py
from json_db import read_json, write_json, get_next_id, get_timestamp
from debug_logger import log

# Tax rates
GST_RATE = 0.05  # 5% GST
DELIVERY_CHARGE = 40  # Fixed delivery charge

def calculate_bill_details(subtotal):
    """Calculate GST and total"""
    gst = round(subtotal * GST_RATE, 2)
    total = round(subtotal + gst + DELIVERY_CHARGE, 2)
    return {
        "subtotal": subtotal,
        "gst": gst,
        "delivery_charge": DELIVERY_CHARGE,
        "total": total
    }

def generate_bill(order_id, order_data):
    """Generate bill from order data"""
    bills = read_json("bills.json")
    
    # Calculate bill details
    bill_details = calculate_bill_details(order_data.get("total", 0))
    
    bill = {
        "bill_id": f"BILL{get_next_id('bills.json'):04d}",
        "order_id": order_id,
        "customer_phone": order_data.get("phone"),
        "customer_name": order_data.get("name"),
        "subtotal": bill_details["subtotal"],
        "gst": bill_details["gst"],
        "delivery_charge": bill_details["delivery_charge"],
        "total": bill_details["total"],
        "items": order_data.get("cart", []),
        "generated_at": get_timestamp(),
        "status": "paid"
    }
    
    bills.append(bill)
    write_json("bills.json", bills)
    log(f"Generated bill {bill['bill_id']} for order {order_id}", "INFO")
    
    return bill

def get_bill_by_order_id(order_id):
    """Get bill by order ID"""
    bills = read_json("bills.json")
    for bill in bills:
        if bill["order_id"] == order_id:
            return bill
    return None

def get_all_bills():
    """Get all bills"""
    return read_json("bills.json")
