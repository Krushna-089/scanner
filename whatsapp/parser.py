# whatsapp/parser.py
from whatsapp.sender import send_message, send_list_message, send_reply_buttons
from services.menu_service import get_menu, get_items
from services.order_service import create_order
from session import get_session, clear_session
import json

def handle_message(data):
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        msg = value["messages"][0]
        user = msg["from"]
        session = get_session(user)
    except Exception as e:
        print("Error parsing incoming message:", e)
        return

    # ---- interactive button / list reply ----
    if msg["type"] == "interactive":
        interactive = msg["interactive"]
        if interactive["type"] == "list_reply":
            payload = interactive["list_reply"]["id"]
            handle_interactive_selection(user, session, payload)
        elif interactive["type"] == "button_reply":
            payload = interactive["button_reply"]["id"]
            handle_interactive_selection(user, session, payload)
        return

    # ---- plain text (only for start, name, phone) ----
    if msg["type"] == "text":
        text = msg["text"]["body"].strip().lower()

        # Start
        if text == "hi" or text == "hello":
            session["step"] = "menu"
            send_list_message(
                to=user,
                body_text="🍽️ Welcome! Choose a category:",
                button_text="See menu",
                sections=[{
                    "title": "Categories",
                    "rows": [
                        {"id": f"cat_{c['id']}", "title": c["name"], "description": f"View {c['name']} items"}
                        for c in get_menu()
                    ]
                }]
            )
            return

        # Name collection during checkout
        if session["step"] == "awaiting_name":
            session["name"] = text
            session["step"] = "awaiting_phone"
            send_message(user, "📞 Great! Now send your phone number (e.g., +1234567890)")
            return

        if session["step"] == "awaiting_phone":
            session["phone"] = text
            # Create order
            order = create_order(session["name"], session["phone"], session["cart"], calculate_total(session["cart"]))
            clear_session(user)
            send_message(user, f"✅ Order placed!\nOrder ID: {order['order_number']}\nTotal: ${order['total']}\nWe'll contact you soon.")
            return

        # If user types anything else and not in expected text state, show help
        send_reply_buttons(user, "Please tap on the buttons to order. Type 'hi' to restart.", [
            {"id": "restart", "title": "🔄 Restart"}
        ])
        return

def handle_interactive_selection(user, session, payload):
    # --- Category selection (list) ---
    if payload.startswith("cat_"):
        cat_id = int(payload.split("_")[1])
        session["current_category_id"] = cat_id
        items = get_items(cat_id)
        if not items:
            send_message(user, "No items in this category. Go back to main menu.")
            send_reply_buttons(user, "Go back?", [{"id": "back_to_menu", "title": "🔙 Main Menu"}])
            return
        sections = [{
            "title": "Items",
            "rows": [
                {"id": f"item_{i['id']}", "title": f"{i['name']} - ${i['price']}", "description": "Tap to add"}
                for i in items
            ]
        }]
        send_list_message(user, f"📋 Choose an item:", "Select item", sections)
        session["step"] = "adding_item"
        return

    # --- Item selection ---
    if payload.startswith("item_"):
        item_id = int(payload.split("_")[1])
        items = get_items(session["current_category_id"])
        item = next((i for i in items if i["id"] == item_id), None)
        if item:
            session["current_item"] = item
            # Ask for add‑ons with reply buttons (optional)
            addons = read_json("addons.json")  # you need to import read_json or pass it
            if addons:
                buttons = [{"id": f"addon_{a['id']}", "title": f"{a['name']} +${a['price']}"} for a in addons[:2]]
                buttons.append({"id": "no_addon", "title": "No, thanks"})
                send_reply_buttons(user, f"🧀 Add extra for {item['name']}?", buttons)
                session["step"] = "adding_addons"
            else:
                # skip addons, ask spice
                ask_spice(user, session, item)
        return

    # --- Add‑on selection ---
    if payload.startswith("addon_"):
        addon_id = int(payload.split("_")[1])
        addons = read_json("addons.json")
        selected = next((a for a in addons if a["id"] == addon_id), None)
        if selected:
            session["current_addons"].append(selected)
        # after addon, ask spice
        ask_spice(user, session, session["current_item"])
        return

    if payload == "no_addon":
        ask_spice(user, session, session["current_item"])
        return

    # --- Spice level selection ---
    if payload.startswith("spice_"):
        spice_id = int(payload.split("_")[1])
        spices = read_json("spice_levels.json")
        spice = next((s for s in spices if s["id"] == spice_id), None)
        if spice:
            session["current_spice"] = spice
            # Add item to cart with addons and spice
            item = session["current_item"]
            cart_item = {
                "item_id": item["id"],
                "name": item["name"],
                "price": item["price"],
                "addons": session["current_addons"],
                "spice": spice["name"],
                "quantity": 1
            }
            session["cart"].append(cart_item)
            # Reset temp fields
            session["current_addons"] = []
            session["current_spice"] = None
            session["current_item"] = None
            send_reply_buttons(user, f"✅ {item['name']} added to cart!\nWhat next?", [
                {"id": "more_items", "title": "➕ More Items"},
                {"id": "view_cart", "title": "🛒 View Cart"},
                {"id": "checkout", "title": "💳 Checkout"}
            ])
            session["step"] = "post_add"
        return

    # --- Cart / Checkout flow ---
    if payload == "more_items":
        # show categories again
        send_list_message(
            to=user,
            body_text="🍽️ Choose a category:",
            button_text="Menu",
            sections=[{
                "title": "Categories",
                "rows": [{"id": f"cat_{c['id']}", "title": c["name"], "description": ""} for c in get_menu()]
            }]
        )
        session["step"] = "adding_item"
        return

    if payload == "view_cart":
        if not session["cart"]:
            send_message(user, "🛒 Your cart is empty.")
            return
        cart_text = "Your cart:\n" + "\n".join([f"- {i['name']} x{i['quantity']} = ${i['price']*i['quantity']}" for i in session["cart"]])
        total = calculate_total(session["cart"])
        send_reply_buttons(user, f"{cart_text}\n\nTotal: ${total}", [
            {"id": "more_items", "title": "➕ Add more"},
            {"id": "checkout", "title": "💳 Checkout"}
        ])
        return

    if payload == "checkout":
        if not session["cart"]:
            send_message(user, "Cart is empty. Add items first.")
            return
        send_message(user, "📝 Please send your full name (we'll use it for the order)")
        session["step"] = "awaiting_name"
        return

    if payload == "restart":
        clear_session(user)
        send_message(user, "Restarted. Type 'hi' to begin.")
        return

    if payload == "back_to_menu":
        send_list_message(
            to=user,
            body_text="🍽️ Main menu:",
            button_text="Categories",
            sections=[{
                "title": "Categories",
                "rows": [{"id": f"cat_{c['id']}", "title": c["name"], "description": ""} for c in get_menu()]
            }]
        )
        session["step"] = "adding_item"
        return

def ask_spice(user, session, item):
    spices = read_json("spice_levels.json")
    if spices:
        buttons = [{"id": f"spice_{s['id']}", "title": s["name"]} for s in spices]
        send_reply_buttons(user, f"🌶️ Choose spice level for {item['name']}:", buttons)
        session["step"] = "selecting_spice"
    else:
        # no spice levels, add directly
        cart_item = {
            "item_id": item["id"],
            "name": item["name"],
            "price": item["price"],
            "addons": [],
            "spice": None,
            "quantity": 1
        }
        session["cart"].append(cart_item)
        send_reply_buttons(user, f"✅ {item['name']} added!\nWhat next?", [
            {"id": "more_items", "title": "➕ More Items"},
            {"id": "view_cart", "title": "🛒 View Cart"},
            {"id": "checkout", "title": "💳 Checkout"}
        ])

def calculate_total(cart):
    total = 0
    for item in cart:
        total += item["price"] * item["quantity"]
        for addon in item.get("addons", []):
            total += addon["price"]
    return round(total, 2)

def read_json(file):
    import json, os
    path = os.path.join("data", file)
    with open(path, "r") as f:
        return json.load(f)
