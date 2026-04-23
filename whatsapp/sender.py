# whatsapp/sender.py
import requests

TOKEN = "EAAODBhndGMkBRYLNk2dZCBKHZAiYWTybqiTeGUBdeyBCdzpuS6x5DwYqzIMbg8XjewGUMiH2FylO2d2ZBnZCLrOjPz5laG16ZBAaLxjJIZAaAU0H9ABiFmgZAzCR7mAIqBptElVPQuMYiom3UX7saCLIHIGlO1ij4zzRabrQYVXwgWcoKksn2SV4gklnTqnXZAm2KK1gAxxv936pYboc6oNxVZB4G1MvMqfDhLlK9wzcjZB8RIBcXEiR4fSsvSN2iDcGFktXOAxr6DvNcKDjkGlEY2m89nlLATDRC0kJldHwZDZD"
PHONE_ID = "1087735387757925"

def send_message(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": to, "text": {"body": text}}
    requests.post(url, headers=headers, json=data)

def send_reply_buttons(to, text, buttons):
    """buttons: list of {'id': 'value', 'title': 'Button text'} (max 3)"""
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
                "buttons": [
                    {"type": "reply", "reply": {"id": b["id"], "title": b["title"][:20]}}
                    for b in buttons[:3]
                ]
            }
        }
    }
    requests.post(url, headers=headers, json=data)

def send_list_message(to, body_text, button_text, sections):
    """sections = [{'title': 'Section', 'rows': [{'id': 'id', 'title': 'Option', 'description': 'desc'}]}]"""
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
