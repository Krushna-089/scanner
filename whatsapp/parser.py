# whatsapp/parser.py
from whatsapp.sender import send_message, send_reply_buttons, send_list_message
from services.menu_service import get_menu, get_items
from services.order_service import create_order, get_order_by_id
from session import get_session, clear_session
from json_db import read_json
import json
from debug_logger import log

def handle_message(data):
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        
        if "messages" not in value:
            log("No messages field (status update)", "DEBUG")
            return
        
        msg = value["messages"][0]
        user = msg["from"]
        session = get_session(user)
    except Exception as e:
        log(f"Error parsing webhook: {e}", "ERROR")
        return

    if msg["type"] == "interactive":
        interactive = msg["interactive"]
        if interactive["type"] == "list_reply":
            payload = interactive["list_reply"]["id"]
            handle_interactive(user, session, payload)
        elif interactive["type"] == "button_reply":
            payload = interactive["button_reply"]["id"]
            handle_interactive(user, session, payload)
        return

    if msg["type"] == "text":
        text = msg["text"]["body"].strip().lower()

        if text in ["hi", "hello"]:
            send_reply_buttons(user, 
                "🍽️ *Welcome to FoodieHub!*\n\nChoose an option below:",
                [
                    {"id": "see_menu", "title": "📋 See Menu"},
                    {"id": "order_status", "title": "📦 Order Status"},
                    {"id": "help", "title": "🆘 Help & Support"}
                ]
            )
            session["step"] = "start"
            return

        if session["step"] == "awaiting_quantity_text":
            try:
                qty = int(text)
                if 6 <= qty <= 10:
                    session["current_quantity"] = qty
                    addons = read_json("addons.json")
                    if addons:
                        buttons = [{"id": f"addon_{a['id']}", "title": a['name']} for a in addons[:2]]
                        buttons.append({"id": "no_addon", "title": "Skip"})
                        send_reply_buttons(user, "🧀 *Add extras?*", buttons)
                        session["step"] = "asking_addons"
                    else:
                        ask_spice(user, session, session["current_item"], qty)
                else:
                    send_message(user, "Please enter a number between 6 and 10.")
                return
            except ValueError:
                send_message(user, "Invalid number. Please enter a number between 6 and 10.")
                return

        if session["step"] == "awaiting_name":
            session["name"] = text
            session["step"] = "awaiting_phone"
            send_message(user, "📞 *Great!* Now please send your phone number (e.g., +919876543210):")
            return

        if session["step"] == "awaiting_phone":
            session["phone"] = text
            total = calculate_total(session["cart"])
            order = create_order(session["name"], session["phone"], session["cart"], total)
            session["last_order_id"] = order["order_number"]
            confirm_msg = f"""✅ *Order Placed Successfully!*

*Order ID:* {order['order_number']}
*Name:* {order['name']}
*Total:* ${order['total']}

📦 *Status:* {order['status'].upper()}

We will notify you when your order is ready.

Thank you for ordering from FoodieHub! 🍕"""
            send_message(user, confirm_msg)
            clear_session(user)
            return

        if session["step"] == "awaiting_order_id":
            order_id = text.strip().upper()
            order = get_order_by_id(order_id)
            if order:
                status_emoji = {
                    "pending": "⏳", "received": "✅", "rejected": "❌",
                    "preparing": "👨‍🍳", "cooked": "🍳", "served": "🍽️", "completed": "🏁"
                }.get(order["status"], "📌")
                
                cart_text = ""
                for item in order["cart"]:
                    cart_text += f"• {item['name']} x{item['quantity']} - ${item['price']*item['quantity']}\n"
                    if item.get("addons"):
                        addon_names = ", ".join([a["name"] for a in item["addons"]])
                        cart_text += f"  *Add-ons:* {addon_names}\n"
                    if item.get("spice"):
                        cart_text += f"  *Spice:* {item['spice']}\n"
                
                status_msg = f"""📦 *Order Status* {status_emoji}

*Order ID:* {order['order_number']}
*Status:* {order['status'].upper()}
*Name:* {order['name']}
*Phone:* {order['phone']}

*Items:*
{cart_text}
*Total:* ${order['total']}

Thank you for choosing FoodieHub!"""
            else:
                status_msg = f"❌ *Order ID {order_id} not found.*\nPlease check and try again, or type 'hi' to start a new order."
            send_message(user, status_msg)
            session["step"] = "start"
            return

        send_reply_buttons(user, 
            "I didn't understand that. Please choose an option:",
            [
                {"id": "see_menu", "title": "📋 See Menu"},
                {"id": "order_status", "title": "📦 Order Status"},
                {"id": "help", "title": "🆘 Help & Support"}
            ]
        )
        return

def handle_interactive(user, session, payload):
    if payload == "see_menu":
        log("User clicked See Menu", "INFO")
        categories = get_menu()
        if not categories:
            send_message(user, "Menu is currently empty. Please try again later.")
            return
        
        rows = []
        for c in categories:
            rows.append({
                "id": f"cat_{c['id']}",
                "title": c["name"][:24],  # ensure max 24 chars
                "description": f"View {c['name']} items"
            })
        
        sections = [{"title": "📋 MENU CATEGORIES", "rows": rows}]
        send_list_message(user, "Welcome to FoodieHub! Please select a category:", "View Menu", sections)
        session["step"] = "selecting_category"
        return

    if payload == "order_status":
        send_message(user, "🔍 Please enter your *Order ID* (e.g., ORD5):")
        session["step"] = "awaiting_order_id"
        return

    if payload == "help":
        help_msg = """🆘 *Help & Support*

📖 *How to order:*
1. Tap 'See Menu' and select a category
2. Choose an item
3. Select quantity (1-10)
4. Add extras if you like
5. Choose spice level
6. Proceed to checkout
7. Enter name & phone number

📞 *Contact us:* +1 (555) 630-1363

⏰ *Delivery time:* 30-45 min

Type 'hi' anytime to restart."""
        send_message(user, help_msg)
        return

    if payload.startswith("cat_"):
        cat_id = int(payload.split("_")[1])
        session["current_category_id"] = cat_id
        items = get_items(cat_id)
        if not items:
            send_message(user, "No items in this category. Please go back.")
            return
        
        rows = []
        for i in items:
            # Create a short title (max 24 chars)
            title = f"{i['name']} ${i['price']}"
            if len(title) > 24:
                # Truncate name part
                name_part = i['name'][:21]  # leave room for " $xx"
                title = f"{name_part} ${i['price']}"
            rows.append({
                "id": f"item_{i['id']}",
                "title": title[:24],
                "description": "Tap to order"
            })
        
        sections = [{"title": "🍽️ CHOOSE AN ITEM", "rows": rows}]
        send_list_message(user, "Select an item to add to your cart:", "View Items", sections)
        session["step"] = "selecting_item"
        return

    if payload.startswith("item_"):
        item_id = int(payload.split("_")[1])
        items = get_items(session["current_category_id"])
        item = next((i for i in items if i["id"] == item_id), None)
        if item:
            session["current_item"] = item
            quantity_buttons = [
                {"id": f"qty_{i}", "title": str(i)} for i in [1,2,3,4,5]
            ] + [{"id": "qty_more", "title": "6-10"}]
            send_reply_buttons(user, f"🔢 *How many {item['name']}?* (1-10)", quantity_buttons)
            session["step"] = "asking_quantity"
        return

    if payload.startswith("qty_"):
        if payload == "qty_more":
            send_message(user, "Please type a number between 6 and 10:")
            session["step"] = "awaiting_quantity_text"
            return
        else:
            qty = int(payload.split("_")[1])
            session["current_quantity"] = qty
            addons = read_json("addons.json")
            if addons:
                buttons = [{"id": f"addon_{a['id']}", "title": a['name']} for a in addons[:2]]
                buttons.append({"id": "no_addon", "title": "Skip"})
                send_reply_buttons(user, "🧀 *Add extras?*", buttons)
                session["step"] = "asking_addons"
            else:
                ask_spice(user, session, session["current_item"], session["current_quantity"])
        return

    if payload.startswith("addon_"):
        addon_id = int(payload.split("_")[1])
        addons = read_json("addons.json")
        selected = next((a for a in addons if a["id"] == addon_id), None)
        if selected:
            session["current_addons"].append(selected)
        ask_spice(user, session, session["current_item"], session["current_quantity"])
        return

    if payload == "no_addon":
        ask_spice(user, session, session["current_item"], session["current_quantity"])
        return

    if payload.startswith("spice_"):
        spice_id = int(payload.split("_")[1])
        spices = read_json("spice_levels.json")
        spice = next((s for s in spices if s["id"] == spice_id), None)
        if spice:
            session["current_spice"] = spice
            cart_item = {
                "item_id": session["current_item"]["id"],
                "name": session["current_item"]["name"],
                "price": session["current_item"]["price"],
                "quantity": session["current_quantity"],
                "addons": session["current_addons"],
                "spice": spice["name"]
            }
            session["cart"].append(cart_item)
            session["current_addons"] = []
            session["current_spice"] = None
            session["current_item"] = None
            session["current_quantity"] = 1
            cart_summary = format_cart_summary(session["cart"])
            send_reply_buttons(user, 
                f"✅ *Item added to cart!*\n\n{cart_summary}\n\nWhat would you like to do?",
                [
                    {"id": "more_items", "title": "➕ Add More"},
                    {"id": "view_cart", "title": "🛒 View Cart"},
                    {"id": "checkout", "title": "💳 Checkout"}
                ]
            )
            session["step"] = "post_add"
        return

    if payload == "more_items":
        categories = get_menu()
        rows = [{"id": f"cat_{c['id']}", "title": c["name"][:24], "description": ""} for c in categories]
        sections = [{"title": "📂 CATEGORIES", "rows": rows}]
        send_list_message(user, "Select a category:", "Menu", sections)
        session["step"] = "selecting_category"
        return

    if payload == "view_cart":
        if not session["cart"]:
            send_message(user, "🛒 Your cart is empty.")
            return
        cart_summary = format_cart_summary(session["cart"])
        total = calculate_total(session["cart"])
        send_reply_buttons(user, 
            f"🛒 *Your Cart*\n\n{cart_summary}\n\n*Total:* ${total}\n\nWhat next?",
            [{"id": "more_items", "title": "➕ Add More"}, {"id": "checkout", "title": "💳 Checkout"}]
        )
        return

    if payload == "checkout":
        if not session["cart"]:
            send_message(user, "Your cart is empty. Add items first.")
            return
        total = calculate_total(session["cart"])
        send_message(user, f"📝 *Checkout*\n\nTotal amount: ${total}\n\nPlease send your *full name*:")
        session["step"] = "awaiting_name"
        return

    send_reply_buttons(user, "Please use the buttons below:", [
        {"id": "see_menu", "title": "📋 See Menu"},
        {"id": "order_status", "title": "📦 Order Status"},
        {"id": "help", "title": "🆘 Help"}
    ])

def ask_spice(user, session, item, quantity):
    spices = read_json("spice_levels.json")
    if spices:
        buttons = [{"id": f"spice_{s['id']}", "title": s["name"]} for s in spices]
        send_reply_buttons(user, f"🌶️ *Spice level for {item['name']}*", buttons)
        session["step"] = "asking_spice"
    else:
        cart_item = {
            "item_id": item["id"],
            "name": item["name"],
            "price": item["price"],
            "quantity": quantity,
            "addons": [],
            "spice": None
        }
        session["cart"].append(cart_item)
        cart_summary = format_cart_summary(session["cart"])
        send_reply_buttons(user, 
            f"✅ *Item added!*\n\n{cart_summary}\n\nWhat next?",
            [{"id": "more_items", "title": "➕ Add More"}, {"id": "view_cart", "title": "🛒 View Cart"}, {"id": "checkout", "title": "💳 Checkout"}]
        )
        session["step"] = "post_add"

def format_cart_summary(cart):
    lines = []
    for item in cart:
        lines.append(f"• {item['name']} x{item['quantity']} = ${item['price']*item['quantity']}")
        if item.get("addons") and len(item["addons"]) > 0:
            addon_str = ", ".join([a["name"] for a in item["addons"]])
            lines.append(f"  *Add-ons:* {addon_str}")
        if item.get("spice"):
            lines.append(f"  *Spice:* {item['spice']}")
    return "\n".join(lines)

def calculate_total(cart):
    total = 0
    for item in cart:
        total += item["price"] * item["quantity"]
        for addon in item.get("addons", []):
            total += addon["price"] * item["quantity"]
    return round(total, 2)
