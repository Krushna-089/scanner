import requests

TOKEN = "EAAODBhndGMkBRShdoFTJsYjrjLtfhfnfvMS8SuYLN8eKzTAp9GMH9JEKSZC6sstwbVEHiEPouO6puocD7JltRTDiOkZCtT0lTaoQusIdGacm3tYWNsjyMLtfeCEXW3rcTf57fKMJ5oRgHlPa4Lq5VDG3OE6e71FZA4Ogpp1pCJolfIyk0OIzAAgYQ8vAI8WhdSJYfM5RrugVkBf8bOW6v5hVzOFw0n86HG7FxoWBKsrhDZBMVFcfxWRPPLgfxZBdg9S2JUOGKgZAIP7eaymFRrLECrVsD0QeYRBWkcQQZDZD"
PHONE_ID = "1087735387757925"

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
