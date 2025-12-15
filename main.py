from flask import Flask, request, jsonify
import json, os

app = Flask(__name__)
KEY_DB = "keys.json"

def load_keys():
    if not os.path.exists(KEY_DB):
        return {}
    with open(KEY_DB, "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def home():
    return jsonify({"status": "online", "message": "KEY SERVER OK"})

@app.route("/check", methods=["POST"])
def check_key():
    data = request.get_json(force=True)
    key = data.get("key", "").strip()

    if not key:
        return jsonify(success=False, message="EMPTY_KEY")

    keys = load_keys()

    if key not in keys:
        return jsonify(success=False, message="KEY_NOT_FOUND")

    if keys[key]["status"] != "ON":
        return jsonify(success=False, message="KEY_DISABLED")

    return jsonify(success=True, message="KEY_VALID")

# ⚠️ Render dùng PORT môi trường
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
