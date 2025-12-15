from flask import Flask, request, jsonify
import json, os, time, secrets

app = Flask(__name__)

KEY_DB = "keys.json"
TOKEN_DB = "tokens.json"
TOKEN_LIFETIME = 24 * 60 * 60  # 24 tiếng

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def home():
    return jsonify({"status": "online", "message": "KEY SERVER OK"})

@app.route("/check", methods=["POST"])
def check_key():
    data = request.get_json(force=True)
    key = data.get("key", "").strip()

    if not key:
        return jsonify(success=False, message="EMPTY_KEY")

    keys = load_json(KEY_DB)

    if key not in keys:
        return jsonify(success=False, message="KEY_INVALID")

    if keys[key]["status"] != "ON":
        return jsonify(success=False, message="KEY_DISABLED")

    # Tạo token
    token = secrets.token_hex(16)
    expire = int(time.time()) + TOKEN_LIFETIME

    tokens = load_json(TOKEN_DB)
    tokens[token] = {
        "expire": expire
    }
    save_json(TOKEN_DB, tokens)

    return jsonify(
        success=True,
        token=token,
        expires_at=expire
    )

@app.route("/verify", methods=["POST"])
def verify_token():
    data = request.get_json(force=True)
    token = data.get("token", "").strip()

    tokens = load_json(TOKEN_DB)

    if token not in tokens:
        return jsonify(valid=False)

    if time.time() > tokens[token]["expire"]:
        del tokens[token]
        save_json(TOKEN_DB, tokens)
        return jsonify(valid=False)

    return jsonify(valid=True)

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
