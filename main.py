from flask import Flask, request, jsonify
import json, os, time, secrets

app = Flask(__name__)

KEY_DB = "keys.json"
TOKEN_DB = "tokens.json"
KEY_LIFETIME = 24 * 60 * 60  # 24h
TOKEN_LIFETIME = 24 * 60 * 60

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
        return jsonify(success=False, message="Key Không Hợp Lệ!")

    key_info = keys[key]

    if key_info["status"] != "ON":
        return jsonify(success=False, message="Key Đã Hết Hạn!")

    now = int(time.time())

    # 👉 LẦN ĐẦU KÍCH HOẠT
    if key_info["activated_at"] is None:
        key_info["activated_at"] = now
        save_json(KEY_DB, keys)

    # 👉 HẾT HẠN KEY
    if now - key_info["activated_at"] > KEY_LIFETIME:
        key_info["status"] = "OFF"
        save_json(KEY_DB, keys)
        return jsonify(success=False, message="Key Đã Hết Hạn")

    # 👉 TẠO TOKEN
    token = secrets.token_hex(16)
    expire = now + TOKEN_LIFETIME

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
