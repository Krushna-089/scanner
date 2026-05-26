# whatsapp/parser.py (add/modify these parts)
# Add imports at the top:
from services.customer_service import save_customer
from services.billing_service import generate_bill
from whatsapp.sender import send_text_message
from services.message_service import save_message

# Replace the order confirmation section in handle_message function
# Find where order is created and replace with:

# In the awaiting_phone section, replace the order confirmation code:

if session["step"] == "awaiting_phone":
    session["phone"] = text
    total = calculate_total(session["cart"])
    
    # Create order
    order = create_order(session["name"], session["phone"], session["cart"], total)
    
    # Save/update customer
    save_customer(session["phone"], session["name"], total)
    
    # Generate bill
    bill = generate_bill(order["order_number"], {
        "phone": session["phone"],
        "name": session["name"],
        "total": total,
        "cart": session["cart"]
    })
    
    session["last_order_id"] = order["order_number"]
    
    # Format bill message
    bill_message = format_bill_message(order, bill, session["cart"])
    
    # Send bill message
    send_text_message(user, bill_message)
    
    # Save to message history
    save_message(user, "bill", bill_message)
    
    # Clear session
    clear_session(user)
    return

# Add helper function at the end of parser.py:
def format_bill_message(order, bill, cart):
    """Format bill message for WhatsApp"""
    items_text = ""
    for item in cart:
        items_text += f"• {item['name']} x{item['quantity']} = ₹{item['price'] * item['quantity']}\n"
        if item.get("addons"):
            addon_names = ", ".join([a["name"] for a in item["addons"]])
            items_text += f"  *Add-ons:* {addon_names}\n"
        if item.get("spice"):
            items_text += f"  *Spice:* {item['spice']}\n"
    
    message = f"""🧾 *ORDER CONFIRMED* 🧾

*Order ID:* {order['order_number']}
*Name:* {order['name']}

*Items Ordered:*
{items_text}

*Bill Details:*
Subtotal: ₹{bill['subtotal']}
GST (5%): ₹{bill['gst']}
Delivery: ₹{bill['delivery_charge']}
━━━━━━━━━━━━━━━
💰 *Total: ₹{bill['total']}*

Thank you for ordering from FoodieHub! ❤️

Your order is being prepared. We'll notify you when it's ready!"""
    
    return message
