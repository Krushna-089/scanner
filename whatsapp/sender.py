# whatsapp/sender.py
import requests
import json
import os
from debug_logger import log
import re
from dotenv import load_dotenv
from services.message_service import save_message

load_dotenv()

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_NUMBER_ID")

def send_text_message(to, text):
    """Send plain text message"""
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    
    log(f"Sending text to {to}", "DEBUG")
    response = requests.post(url, headers=headers, json=data)
    
    # Save to message history
    if response.status_code == 200:
        save_message(to, "text", text)
    else:
        log(f"Text error: {response.text}", "ERROR")
        save_message(to, "text", text, status="failed")
    
    return response.json()

def send_image_message(to, image_url, caption=""):
    """Send image message"""
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": {
            "link": image_url,
            "caption": caption[:200]  # WhatsApp caption limit
        }
    }
    
    log(f"Sending image to {to}: {image_url}", "DEBUG")
    response = requests.post(url, headers=headers, json=data)
    
    # Save to message history
    if response.status_code == 200:
        save_message(to, "image", f"Image: {image_url}\nCaption: {caption}")
    else:
        log(f"Image error: {response.text}", "ERROR")
        save_message(to, "image", f"Image: {image_url}", status="failed")
    
    return response.json()

def send_template_message(to, template_name, language="en", components=None):
    """Send template message"""
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language}
        }
    }
    
    if components:
        data["template"]["components"] = components
    
    log(f"Sending template to {to}: {template_name}", "DEBUG")
    response = requests.post(url, headers=headers, json=data)
    
    # Save to message history
    if response.status_code == 200:
        save_message(to, "template", f"Template: {template_name}")
    else:
        log(f"Template error: {response.text}", "ERROR")
        save_message(to, "template", f"Template: {template_name}", status="failed")
    
    return response.json()

# Keep existing functions for backward compatibility
def send_message(to, text):
    """Alias for send_text_message"""
    return send_text_message(to, text)

def send_list_message(to, body_text, button_text, sections):
    """Send a WhatsApp Interactive List Message"""
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
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
    
    # Save to message history
    if response.status_code == 200:
        save_message(to, "list", body_text_short)
    else:
        save_message(to, "list", body_text_short, status="failed")
    
    return response.json()

def send_reply_buttons(to, text, buttons):
    """Send WhatsApp Interactive Reply Buttons (max 3 buttons)"""
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
    
    # Save to message history
    if response.status_code == 200:
        save_message(to, "buttons", text)
    else:
        log(f"ERROR: {response.text}", "ERROR")
        save_message(to, "buttons", text, status="failed")
    
    return response.json()
