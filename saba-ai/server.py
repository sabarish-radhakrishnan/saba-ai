# server.py (Render + local compatible)
print("✅ server.py STARTED")

import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from ai_assistant import BrowserAI

app = Flask(__name__)
CORS(app)

# Model name: use env var on Render if you want, otherwise default
MODEL_NAME = os.environ.get("MODEL_NAME", "llama3.1")

# Initialize AI
ai = BrowserAI(model=MODEL_NAME)


@app.route("/")
def home():
    return "Saba browser backend is running (REAL mode)"


@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({"name": ai.name, "version": ai.version, "model": MODEL_NAME})


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True) or {}
        msg = (data.get("message") or "").strip()

        if not msg:
            return jsonify({"success": False, "error": "Empty message"}), 400

        # Optional context from page text/selected text
        context = (data.get("context") or "").strip()
        include_page = bool(data.get("includePage") or data.get("include_page"))

        # Build a simple prompt wrapper if context is provided
        full_prompt = msg
        if context:
            full_prompt = (
                "You are Saba, a helpful browser assistant.\n\n"
                f"User message:\n{msg}\n\n"
                f"{'Full page/selected text:' if include_page else 'Context:'}\n{context}\n"
            )

        reply = ai.process_input(full_prompt)
        return jsonify({"success": True, "response": reply})

    except Exception as e:
        # Return the error so your frontend can show it
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    # Render requires 0.0.0.0 + PORT env var
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "0").lower() in ("1", "true", "yes")

    print(f"🚀 Starting Flask server on {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)
