# whatsapp/sender.py
import requests

TOKEN = "EAAODBhndGMkBRShdoFTJsYjrjLtfhfnfvMS8SuYLN8eKzTAp9GMH9JEKSZC6sstwbVEHiEPouO6puocD7JltRTDiOkZCtT0lTaoQusIdGacm3tYWNsjyMLtfeCEXW3rcTf57fKMJ5oRgHlPa4Lq5VDG3OE6e71FZA4Ogpp1pCJolfIyk0OIzAAgYQ8vAI8WhdSJYfM5RrugVkBf8bOW6v5hVzOFw0n86HG7FxoWBKsrhDZBMVFcfxWRPPLgfxZBdg9S2JUOGKgZAIP7eaymFRrLECrVsD0QeYRBWkcQQZDZD"
PHONE_ID = "1087735387757925"

def send_message(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": to, "text": {"body": text}}
    requests.post(url, headers=headers, json=data)

def send_list_message(to, body_text, button_text, sections):
    """
    sections = [{"title": "Section title", "rows": [{"id": "unique_id", "title": "Option", "description": "extra"}]}]
    """
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": body_text[:60]},
            "body": {"text": body_text[:60]},
            "footer": {"text": "Tap to see options"},
            "action": {
                "button": button_text[:20],
                "sections": sections
            }
        }
    }
    requests.post(url, headers=headers, json=data)

def send_reply_buttons(to, text, buttons):
    """
    buttons = [{"id": "payload_1", "title": "Button 1"}, ...]  max 3 buttons
    """
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": text[:200]},
            "action": {
                "buttons": [{"type": "reply", "reply": {"id": b["id"], "title": b["title"][:20]}} for b in buttons[:3]]
            }
        }
    }
    requests.post(url, headers=headers, json=data)
