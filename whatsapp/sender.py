# whatsapp/sender.py
import requests
import json
from debug_logger import log

TOKEN = "EAAODBhndGMkBRYUueLebktA0kRCvCIFBEaVNhZCZAlzZBrAerBEEo3ZBwm8oT33lkLv3uB6R2y4z8YXiZBGVZCvFxvoT9gbmXhnyUsqV66YZBmBGSXYItseZAyUN8u1HCtA5LdfZBHivCCm4ioZAJw0ypllTqRcNeQDZBEae6goqm3X5a9W3oKUVtPpuue8zkYpCVvMeTZAFeGWTmD1JcNmuZBqrPP75pcMoFhT6eCIB3ZCTlSe8PkmSBZB8uADJnKpf9sfeJ0UJQIMlWCPbnyDI4rB7AL5GqupyP4xglWMESpIlwZDZD"
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
    
    log(f"Sending text message to {to}", "DEBUG")
    response = requests.post(url, headers=headers, json=data)
    log(f"Response status: {response.status_code}", "DEBUG")
    if response.status_code != 200:
        log(f"Error: {response.text}", "ERROR")
    return response.json()

def send_list_message(to, body_text, button_text, sections):
    """
    Send a WhatsApp Interactive List Message (NO markdown allowed in header/body)
    """
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Remove markdown characters (*, _, ~, etc.) from body_text
    clean_body = re.sub(r'[*_~`]', '', body_text)
    clean_body = clean_body.replace('\n', ' ').strip()
    
    button_text = button_text[:20]
    header_text = clean_body[:60]
    body_text_short = clean_body[:60]
    
    interactive_payload = {
        "type": "list",
        "header": {"type": "text", "text": header_text},
        "body": {"text": body_text_short},
        "footer": {"text": "Tap to see options"},
        "action": {"button": button_text, "sections": sections}
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": interactive_payload
    }
    
    log(f"Sending list message to {to}", "DEBUG")
    response = requests.post(url, headers=headers, json=data)
    log(f"List message response: {response.status_code}", "DEBUG")
    
    if response.status_code != 200:
        log(f"ERROR: {response.text}", "ERROR")
        # Fallback to plain text (without markdown)
        fallback = f"{clean_body}\n\n"
        for section in sections:
            fallback += f"\n{section['title']}:\n"
            for row in section['rows']:
                fallback += f"• {row['title']}\n"
        send_message(to, fallback)
    
    return response.json()

def send_reply_buttons(to, text, buttons):
    """
    Send WhatsApp Interactive Reply Buttons (max 3 buttons)
    buttons: [{"id": "payload", "title": "Button Text"}]
    """
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Format buttons for WhatsApp API
    whatsapp_buttons = []
    for b in buttons[:3]:
        whatsapp_buttons.append({
            "type": "reply",
            "reply": {
                "id": b["id"],
                "title": b["title"][:20]  # Max 20 chars
            }
        })
    
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": text[:200]  # Max 200 chars
            },
            "action": {
                "buttons": whatsapp_buttons
            }
        }
    }
    
    log(f"Sending buttons to {to}", "DEBUG")
    response = requests.post(url, headers=headers, json=data)
    log(f"Buttons response: {response.status_code}", "DEBUG")
    
    if response.status_code != 200:
        log(f"ERROR: {response.text}", "ERROR")
        # Fallback to text
        fallback = f"{text}\n\n"
        for b in buttons:
            fallback += f"• {b['title']}\n"
        send_message(to, fallback)
    
    return response.json()
