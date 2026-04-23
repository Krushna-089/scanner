from flask import Flask, request
from whatsapp.parser import handle_message

app = Flask(__name__)

VERIFY_TOKEN = "12345"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge"), 200
        return "Invalid", 403

    data = request.json

    try:
        handle_message(data)   # 👈 ALL LOGIC GOES OUTSIDE
    except Exception as e:
        print(e)

    return "OK", 200


if __name__ == "__main__":
    app.run(port=5000)
