# services/promotion_service.py
from json_db import read_json, write_json, get_next_id, get_timestamp
from whatsapp.sender import send_text_message, send_image_message
from services.customer_service import get_all_customers
from services.message_service import save_message
from debug_logger import log

def save_promotion(promotion_data):
    """Save promotion to history"""
    promotions = read_json("promotions.json")
    
    promotion = {
        "id": get_next_id("promotions.json"),
        **promotion_data,
        "created_at": get_timestamp()
    }
    
    promotions.append(promotion)
    write_json("promotions.json", promotions)
    return promotion

def get_all_promotions():
    """Get all promotions"""
    return read_json("promotions.json")

def send_promotion_to_all(message_type, content, image_url=None):
    """Send promotion to all customers"""
    customers = get_all_customers()
    results = []
    
    log(f"Sending {message_type} promotion to {len(customers)} customers", "INFO")
    
    for customer in customers:
        phone = customer["phone"]
        
        try:
            if message_type == "text":
                result = send_text_message(phone, content)
            elif message_type == "image" and image_url:
                result = send_image_message(phone, image_url, content)
            else:
                continue
            
            # Save message to history
            save_message(phone, f"promotion_{message_type}", content)
            results.append({"phone": phone, "success": True, "result": result})
            log(f"Promotion sent to {phone}", "DEBUG")
            
        except Exception as e:
            log(f"Failed to send promotion to {phone}: {e}", "ERROR")
            results.append({"phone": phone, "success": False, "error": str(e)})
    
    # Save promotion record
    promotion_data = {
        "type": message_type,
        "content": content,
        "image_url": image_url,
        "recipients_count": len(customers),
        "successful_count": len([r for r in results if r["success"]]),
        "results": results
    }
    save_promotion(promotion_data)
    
    return results
