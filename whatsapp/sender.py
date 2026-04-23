# whatsapp/sender.py
import requests

TOKEN = "EAAODBhndGMkBRYLNk2dZCBKHZAiYWTybqiTeGUBdeyBCdzpuS6x5DwYqzIMbg8XjewGUMiH2FylO2d2ZBnZCLrOjPz5laG16ZBAaLxjJIZAaAU0H9ABiFmgZAzCR7mAIqBptElVPQuMYiom3UX7saCLIHIGlO1ij4zzRabrQYVXwgWcoKksn2SV4gklnTqnXZAm2KK1gAxxv936pYboc6oNxVZB4G1MvMqfDhLlK9wzcjZB8RIBcXEiR4fSsvSN2iDcGFktXOAxr6DvNcKDjkGlEY2m89nlLATDRC0kJldHwZDZD"
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
    
    log(f"Sending text message to {to}: {text[:50]}...", "DEBUG")
    response = requests.post(url, headers=headers, json=data)
    log(f"Response status: {response.status_code}, body: {response.text[:200]}", "DEBUG")
    return response.json()

def send_list_message(to, body_text, button_text, sections):
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Validate sections format
    if not sections or not sections[0].get("rows"):
        log(f"Invalid sections format: {sections}", "ERROR")
        send_message(to, "📋 Menu is currently unavailable. Please try again later.")
        return
    
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": body_text[:60]
            },
            "body": {
                "text": body_text[:60]
            },
            "footer": {
                "text": "Tap to see options"
            },
            "action": {
                "button": button_text[:20],
                "sections": sections
            }
        }
    }
    
    log(f"Sending list message to {to}: {body_text}", "DEBUG")
    log(f"List data: {json.dumps(data, indent=2)[:500]}", "DEBUG")
    
    response = requests.post(url, headers=headers, json=data)
    log(f"List message response: {response.status_code} - {response.text[:200]}", "DEBUG")
    
    if response.status_code != 200:
        log(f"ERROR sending list message: {response.text}", "ERROR")
        # Fallback to text message
        fallback_text = f"📋 *{body_text}*\n\n"
        for section in sections:
            for row in section.get("rows", []):
                fallback_text += f"• {row['title']}\n"
        send_message(to, fallback_text)
    
    return response.json()

def send_reply_buttons(to, text, buttons):
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
            "body": {"text": text[:200]},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": b["id"],
                            "title": b["title"][:20]
                        }
                    } for b in buttons[:3]
                ]
            }
        }
    }
    
    log(f"Sending buttons to {to}: {text[:50]}...", "DEBUG")
    response = requests.post(url, headers=headers, json=data)
    log(f"Buttons response: {response.status_code} - {response.text[:200]}", "DEBUG")
    
    if response.status_code != 200:
        log(f"ERROR sending buttons: {response.text}", "ERROR")
        # Fallback to text
        fallback_text = f"{text}\n\n" + "\n".join([f"• {b['title']}" for b in buttons])
        send_message(to, fallback_text)
    
    return response.json()
    
