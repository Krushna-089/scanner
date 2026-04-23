from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = "EAAODBhndGMkBRShdoFTJsYjrjLtfhfnfvMS8SuYLN8eKzTAp9GMH9JEKSZC6sstwbVEHiEPouO6puocD7JltRTDiOkZCtT0lTaoQusIdGacm3tYWNsjyMLtfeCEXW3rcTf57fKMJ5oRgHlPa4Lq5VDG3OE6e71FZA4Ogpp1pCJolfIyk0OIzAAgYQ8vAI8WhdSJYfM5RrugVkBf8bOW6v5hVzOFw0n86HG7FxoWBKsrhDZBMVFcfxWRPPLgfxZBdg9S2JUOGKgZAIP7eaymFRrLECrVsD0QeYRBWkcQQZDZD"
PHONE_ID = "1087735387757925"


# send message
def send_message(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    }

    requests.post(url, headers=headers, json=data)


# send buttons
def send_buttons(to):
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "Welcome! Choose option:"
            },
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "menu", "title": "Menu"}},
                    {"type": "reply", "reply": {"id": "help", "title": "Help"}}
                ]
            }
        }
    }

    requests.post(url, headers=headers, json=data)


VERIFY_TOKEN = "12345"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200

        return "Error", 403

    if request.method == "POST":
        data = request.json

        try:
            entry = data["entry"][0]["changes"][0]["value"]

            if "messages" in entry:
                msg = entry["messages"][0]
                user = msg["from"]

                # TEXT MESSAGE
                if msg["type"] == "text":
                    text = msg["text"]["body"].lower()

                    if text == "hi":
                        send_buttons(user)
                    else:
                        send_message(user, "Type 'hi' to start 😊")

                # BUTTON CLICK
                elif msg["type"] == "interactive":
                    btn = msg["interactive"]["button_reply"]["id"]

                    if btn == "menu":
                        send_message(user, "🍽️ Menu:\n1. Pizza\n2. Burger\n3. Drinks")
                    elif btn == "help":
                        send_message(user, "📞 Support: Call +91 XXXXX XXXXX")

        except Exception as e:
            print("Error:", e)

        return "OK", 200
if __name__ == "__main__":
    app.run(port=5000)
