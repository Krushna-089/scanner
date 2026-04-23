from whatsapp.sender import send_message
from services.menu_service import get_menu, get_items

def handle_message(data):

    msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
    user = msg["from"]

    if msg["type"] == "text":
        text = msg["text"]["body"].lower()

        if text == "hi":
            send_message(user, "👋 Welcome! type 'menu'")

        elif text == "menu":
            menu = get_menu()
            msg = "\n".join([f"{c['id']}. {c['name']}" for c in menu])
            send_message(user, msg)
