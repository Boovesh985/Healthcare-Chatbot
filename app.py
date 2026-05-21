import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# ==========================================================
# ✅ Load environment variables
# ==========================================================
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow Streamlit frontend to call Flask backend

# ==========================================================
# ⚙️ Configuration
# ==========================================================
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "bn32iaFT8oc9mYmWoYcYHZhKm6WOHlZf")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-medium-latest")

# ==========================================================
# 🩺 Health check endpoint
# ==========================================================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


# ==========================================================
# 💬 Chat generation endpoint
# ==========================================================
@app.route("/api/generate", methods=["POST"])
def generate():
    """
    Expected JSON body:
    {
        "prompt": "Hello, how are you?",
        "max_tokens": 256,
        "temperature": 0.7,
        "model": "mistral-medium-latest"
    }
    """
    data = request.get_json(force=True)
    prompt = data.get("prompt", "").strip()
    max_tokens = int(data.get("max_tokens", 512))
    temperature = float(data.get("temperature", 0.7))
    model = data.get("model", MISTRAL_MODEL)

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    if not MISTRAL_API_KEY:
        return jsonify({"error": "MISTRAL_API_KEY not set"}), 500

    # Prepare request for Mistral API
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(MISTRAL_API_URL, json=payload, headers=headers, timeout=60)
    except requests.exceptions.RequestException as e:
        app.logger.exception("❌ Failed to reach Mistral API")
        return jsonify({"error": "Failed to reach Mistral API", "detail": str(e)}), 502

    if resp.status_code != 200:
        app.logger.error("Mistral API error: %s %s", resp.status_code, resp.text)
        return jsonify({
            "error": "Mistral API request failed",
            "status_code": resp.status_code,
            "provider_response": resp.text
        }), 502

    # Parse response
    try:
        model_json = resp.json()
        content = (
            model_json.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
    except Exception as e:
        app.logger.exception("⚠️ Failed to parse Mistral response")
        return jsonify({"error": "Invalid JSON from Mistral", "raw": resp.text}), 502

    return jsonify({"response": content})


# ==========================================================
# 🚀 Run Flask app
# ==========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
