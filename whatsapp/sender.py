
# whatsapp/sender.py
import requests
import json
from debug_logger import log
import re  # <-- REQUIRED


TOKEN = "EAAODBhndGMkBRaJ4194WOhPJZA4haRrv6Bb3XTOhpMfzxcZBDkYSYVG1xZBuYLDnmSkNjD1kdl42Wrz8TxtTb7lokTIQaLT54OWno3TAWkjw7evToc1G6T9nzrrx4CPXdg4Qt9cZCbVr7TVr7K8t0UJrB0Nj543wQSiL4fdL8QWJrfOrNXGXMF76KXUT3OLNaErX97JbGJE5cgBxaXUUZC5dZCqEB1AfrVDC7ZCoOaV2MgBFwUkijLedDWFJnu1igem5UfGQT5x0G4ZAONrZC5wDutZCM5qhRm1RtjhgHqvQZDZD"
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
    log(f"Sending text to {to}", "DEBUG")
    response = requests.post(url, headers=headers, json=data)
    log(f"Text response: {response.status_code}", "DEBUG")
    if response.status_code != 200:
        log(f"Text error: {response.text}", "ERROR")
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
    
    # Remove all markdown characters from body_text
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
    log(f"List payload: {json.dumps(data, indent=2)[:500]}", "DEBUG")
    
    response = requests.post(url, headers=headers, json=data)
    log(f"List message response: {response.status_code}", "DEBUG")
    
    if response.status_code != 200:
        log(f"ERROR: {response.text}", "ERROR")
        # DO NOT fallback to plain text - we want to see the error
        # Instead, send a debug message to the user
        send_message(to, "⚠️ Sorry, the menu format temporarily failed. Please try again or type 'hi' to restart.")
    else:
        log("List message sent successfully", "INFO")
    
    return response.json()

def send_reply_buttons(to, text, buttons):
    """
    Send WhatsApp Interactive Reply Buttons (max 3 buttons)
    """
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    whatsapp_buttons = []
    for b in buttons[:3]:
        whatsapp_buttons.append({
            "type": "reply",
            "reply": {
                "id": b["id"],
                "title": b["title"][:20]
            }
        })
    
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": text[:200]},
            "action": {"buttons": whatsapp_buttons}
        }
    }
    
    log(f"Sending buttons to {to}", "DEBUG")
    response = requests.post(url, headers=headers, json=data)
    log(f"Buttons response: {response.status_code}", "DEBUG")
    
    if response.status_code != 200:
        log(f"ERROR: {response.text}", "ERROR")
        send_message(to, "⚠️ Button menu failed. Please type 'hi' to restart.")
    
    return response.json()
