import requests

TOKEN = "YOUR_TOKEN"
PHONE_ID = "YOUR_PHONE_ID"

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
