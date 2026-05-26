# app.py
from flask import Flask, request, render_template_string, jsonify, render_template, session as flask_session
from whatsapp.parser import handle_message
from debug_logger import log, get_logs, clear_logs
from services.admin_service import get_admin_stats
from services.customer_service import get_all_customers
from services.order_service import read_json as read_orders
from services.promotion_service import send_promotion_to_all, get_all_promotions
from services.billing_service import get_all_bills
import json
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# Admin credentials (in production, use proper authentication)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# File upload configuration
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# HTML debug page (keep as is from original)
DEBUG_PAGE = """<!DOCTYPE html>
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

# Admin Routes
@app.route("/admin")
def admin_dashboard():
    # Simple auth (in production, use proper authentication)
    auth = request.authorization
    if not auth or auth.username != ADMIN_USERNAME or auth.password != ADMIN_PASSWORD:
        return "Authentication required", 401, {"WWW-Authenticate": 'Basic realm="Admin Login"'}
    
    stats = get_admin_stats()
    return render_template("admin_dashboard.html", stats=stats)

@app.route("/admin/orders")
def admin_orders():
    auth = request.authorization
    if not auth or auth.username != ADMIN_USERNAME or auth.password != ADMIN_PASSWORD:
        return "Authentication required", 401, {"WWW-Authenticate": 'Basic realm="Admin Login"'}
    
    orders = read_orders("orders.json")
    bills = get_all_bills()
    
    # Create bill lookup
    bill_lookup = {bill["order_id"]: bill for bill in bills}
    
    return render_template("admin_orders.html", orders=orders, bill_lookup=bill_lookup)

@app.route("/admin/customers")
def admin_customers():
    auth = request.authorization
    if not auth or auth.username != ADMIN_USERNAME or auth.password != ADMIN_PASSWORD:
        return "Authentication required", 401, {"WWW-Authenticate": 'Basic realm="Admin Login"'}
    
    customers = get_all_customers()
    return render_template("admin_customers.html", customers=customers)

@app.route("/admin/promotions", methods=["GET", "POST"])
def admin_promotions():
    auth = request.authorization
    if not auth or auth.username != ADMIN_USERNAME or auth.password != ADMIN_PASSWORD:
        return "Authentication required", 401, {"WWW-Authenticate": 'Basic realm="Admin Login"'}
    
    if request.method == "POST":
        promotion_type = request.form.get("type", "text")
        message = request.form.get("message")
        image_url = None
        
        # Handle image upload
        if promotion_type == "image" and "image" in request.files:
            file = request.files["image"]
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_url = request.url_root.rstrip('/') + '/' + filepath.replace('\\', '/')
        
        # Send promotion
        results = send_promotion_to_all(promotion_type, message, image_url)
        
        return render_template("admin_promotions.html", 
                             promotions=get_all_promotions(),
                             success=True, 
                             results=results)
    
    return render_template("admin_promotions.html", 
                         promotions=get_all_promotions())

if __name__ == "__main__":
    app.run(port=5000, debug=True)
