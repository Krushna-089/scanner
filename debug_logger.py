# debug_logger.py
from datetime import datetime
import json

# In-memory log storage (last 1000 lines)
logs = []
MAX_LOGS = 1000

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    logs.append(log_entry)
    if len(logs) > MAX_LOGS:
        logs.pop(0)
    # Also print to console for Render logs
    print(log_entry)

def get_logs():
    return logs

def clear_logs():
    global logs
    logs = []
    log("Logs cleared", "WARN")
