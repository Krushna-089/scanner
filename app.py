from flask import Flask, render_template, request, jsonify, send_file
import json, os, zipfile
from barcode import Code128
from barcode.writer import ImageWriter

app = Flask(__name__)

# Load items data
with open("data.json") as f:
    items = json.load(f)

# Ensure folders exist
os.makedirs("barcodes", exist_ok=True)
os.makedirs("zip_files", exist_ok=True)


def generate_barcode(code):
    """Generate a barcode image and save it inside /barcodes"""
    file_path = f"barcodes/{code}.png"
    barcode = Code128(code, writer=ImageWriter())
    barcode.save(file_path.replace(".png", ""))
    return file_path


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/fetch", methods=["POST"])
def fetch():
    entered_code = request.form.get("code")
    
    for item in items:
        if item["Code"] == entered_code:
            return jsonify({"status": "success", "data": item})
    
    return jsonify({"status": "error", "message": "Code not found"})


@app.route("/download_single/<code>")
def download_single(code):
    # Generate barcode
    barcode_path = generate_barcode(code)
    
    # Create zip file
    zip_path = f"zip_files/{code}.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        zipf.write(barcode_path, os.path.basename(barcode_path))
    
    return send_file(zip_path, as_attachment=True)


@app.route("/download_all")
def download_all():
    zip_path = "zip_files/all_barcodes.zip"
    
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for item in items:
            path = generate_barcode(item["Code"])
            zipf.write(path, os.path.basename(path))
    
    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

