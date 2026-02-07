print("✅ server.py STARTED")

import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from ai_assistant import BrowserAI

app = Flask(__name__)

# ---- CORS ----
# Allow local dev + your deployed frontend(s).
# You can add your Netlify/Vercel domain later.
ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://127.0.0.1:5000",
    "http://localhost:5500",
    "http://localhost:5000",
    "null",  # needed when opening web/index.html directly as a file:// page
]

# Optional: set FRONTEND_ORIGIN in Render/hosting, e.g. https://your-site.netlify.app
frontend_origin = os.environ.get("FRONTEND_ORIGIN")
if frontend_origin:
    ALLOWED_ORIGINS.append(frontend_origin)

CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS}})

# ---- SECURITY (API KEY) ----
# Set this in Render environment variables.
# Locally, you can set it too or leave it blank to allow local testing.
API_KEY = os.environ.get("SABA_API_KEY", "")

def require_api_key():
    """
    If SABA_API_KEY is set, requests must include:
      Header: x-api-key: <your_key>
    If SABA_API_KEY is empty, API key check is skipped (local dev mode).
    """
    if not API_KEY:
        return None  # local dev mode
    sent = request.headers.get("x-api-key", "")
    if sent != API_KEY:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    return None

# ---- AI ----
# NOTE: Whatever BrowserAI does internally (Ollama/local/etc.) must be available on the host.
# For local: fine. For Render: you may need to modify BrowserAI to use a cloud model.
MODEL_NAME = os.environ.get("SABA_MODEL", "gpt-oss:120b-cloud")
ai = BrowserAI(model=MODEL_NAME)

@app.route("/")
def home():
    return "Saba backend is running."

@app.route("/api/health")
def health():
    return jsonify({"ok": True})

@app.route("/api/status")
def status():
    return jsonify({"name": ai.name, "version": ai.version, "model": MODEL_NAME})

@app.route("/api/chat", methods=["POST"])
def chat():
    # API key gate (if enabled)
    auth_resp = require_api_key()
    if auth_resp is not None:
        return auth_resp

    try:
        data = request.get_json(force=True) or {}
        msg = (data.get("message") or "").strip()
        context = (data.get("context") or "").strip()

        if not msg:
            return jsonify({"success": False, "error": "Empty message"}), 400

        # Combine context + message
        full_prompt = msg
        if context:
            full_prompt = (
                "Context from the webpage/user:\n"
                f"{context}\n\n"
                "User message:\n"
                f"{msg}"
            )

        print(f"➡️ /api/chat | msg_len={len(msg)} context_len={len(context)}")

        # AI call
        reply = ai.process_input(full_prompt)

        return jsonify({"success": True, "response": reply})

    except Exception as e:
        print("❌ /api/chat error:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    # Render provides PORT. Locally, default to 5000.
    port = int(os.environ.get("PORT", "5000"))
    host = os.environ.get("HOST", "0.0.0.0")  # Render needs 0.0.0.0
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"

    print(f"🚀 Starting Flask server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
