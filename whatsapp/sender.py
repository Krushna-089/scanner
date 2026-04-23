# whatsapp/sender.py
import requests
import json
from debug_logger import log

TOKEN = "EAAODBhndGMkBRbMaYFlK3LAIWExIZCdkAiIZC2zcVhFHDAhgH7AZCYS8zLkSiIQjcQipPkAyZA12XXJAX5ATs18Kka3uxdY7Y9imPlPPNDJGFRmZCK0HqS9rm26QoN2JvhVZCiUn84WhCDuaVeIbIPXhD2AZC8ZB4ZCaJfYLrjpEzheANaL3kVwmOhwsd52lH8A1Ha9pg0XuJAet5ZB6y3SY7VUvihra77pRl6QvBoLXO2DKuZBuDqAVCM70H6joPcWk9s4r6e9PwXSUkGFfaYiPlz9zauThC7DeXEvkChimgZDZD"
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
    return response.json()

def send_list_message(to, body_text, button_text, sections):
    """
    Send a WhatsApp Interactive List Message
    sections: [{"title": "Section Title", "rows": [{"id": "id", "title": "Option", "description": "desc"}]}]
    """
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Ensure button_text is not too long (max 20 chars)
    button_text = button_text[:20]
    
    # Ensure body_text is not too long (max 60 chars for header, 60 for body)
    header_text = body_text[:60]
    body_text_short = body_text[:60]
    
    # Build the interactive list payload
    interactive_payload = {
        "type": "list",
        "header": {
            "type": "text",
            "text": header_text
        },
        "body": {
            "text": body_text_short
        },
        "footer": {
            "text": "Tap to see options"
        },
        "action": {
            "button": button_text,
            "sections": sections
        }
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": interactive_payload
    }
    
    log(f"Sending list message to {to}", "DEBUG")
    log(f"List payload: {json.dumps(data, indent=2)[:500]}", "DEBUG")
    
    response = requests.post(url, headers=headers, json=data)
    log(f"List message response: {response.status_code}", "DEBUG")
    
    if response.status_code != 200:
        log(f"ERROR: {response.text}", "ERROR")
        # Fallback to text message
        fallback = f"{body_text}\n\n"
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
