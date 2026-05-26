# services/message_service.py
from json_db import read_json, write_json, get_timestamp
from debug_logger import log

def save_message(phone, message_type, content, status="sent"):
    """Save message to history"""
    messages = read_json("messages.json")
    
    message = {
        "id": len(messages) + 1,
        "phone": phone,
        "message_type": message_type,  # text, image, template
        "content": content,
        "status": status,
        "sent_at": get_timestamp()
    }
    
    messages.append(message)
    write_json("messages.json", messages)
    log(f"Saved message history for {phone}", "DEBUG")
    
    return message

def get_message_history(phone=None, limit=100):
    """Get message history, optionally filtered by phone"""
    messages = read_json("messages.json")
    
    if phone:
        messages = [m for m in messages if m["phone"] == phone]
    
    return messages[-limit:]

def get_all_messages():
    """Get all messages"""
    return read_json("messages.json")
