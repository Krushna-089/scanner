# app.py
from flask import Flask, request, render_template_string, jsonify
from whatsapp.parser import handle_message
from debug_logger import log, get_logs, clear_logs
import json

app = Flask(__name__)

VERIFY_TOKEN = "12345"

# HTML debug page (auto-refreshes every 3 seconds)
DEBUG_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>WhatsApp Bot Debug Console</title>
    <meta http-equiv="refresh" content="3">
    <style>
        body { background: #1e1e1e; color: #d4d4d4; font-family: 'Courier New', monospace; padding: 20px; margin: 0; }
        h1 { color: #4ec9b0; font-size: 24px; }
        .toolbar { margin-bottom: 15px; }
        button { background: #0e639c; color: white; border: none; padding: 8px 16px; cursor: pointer; font-size: 14px; border-radius: 4px; }
        button:hover { background: #1177bb; }
        .log-container { border: 1px solid #333; background: #252526; padding: 10px; height: 85vh; overflow-y: auto; white-space: pre-wrap; font-size: 13px; }
        .info { color: #9cdcfe; }
        .error { color: #f48771; font-weight: bold; }
        .warn { color: #ce9178; }
        .debug { color: #6a9955; }
        hr { border-color: #333; }
    </style>
</head>
<body>
    <h1>🤖 WhatsApp Bot Debug Console</h1>
    <div class="toolbar">
        <button onclick="fetch('/clear-logs').then(() => location.reload())">🗑️ Clear Logs</button>
        <button onclick="location.reload()">🔄 Refresh</button>
    </div>
    <div class="log-container">
        {% for line in logs %}
        <div class="
            {% if 'ERROR' in line %}error
            {% elif 'WARN' in line %}warn
            {% elif 'DEBUG' in line %}debug
            {% else %}info{% endif %}
        ">{{ line }}</div>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            log(f"Webhook verified with token {VERIFY_TOKEN}", "INFO")
            return request.args.get("hub.challenge"), 200
        log("Invalid verify token received", "ERROR")
        return "Invalid", 403

    # POST: receive webhook data
    data = request.json
    log(f"📨 Webhook received: {json.dumps(data, indent=2)[:500]}", "DEBUG")
    
    try:
        handle_message(data)
        log("✅ Message handled successfully", "INFO")
    except Exception as e:
        log(f"❌ Error handling message: {str(e)}", "ERROR")
        import traceback
        tb = traceback.format_exc()
        log(tb, "ERROR")
    
    return "OK", 200

@app.route("/debug")
@app.route("/logs")
def debug_logs():
    return render_template_string(DEBUG_PAGE, logs=get_logs())

@app.route("/clear-logs")
def clear_logs_route():
    clear_logs()
    return "Logs cleared", 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
