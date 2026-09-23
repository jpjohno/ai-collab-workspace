from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "status": "online"})

@app.route("/ask", methods=["POST", "OPTIONS"])
def ask():
    data = request.get_json(force=True, silent=True) or {}
    text = (data.get("text") or data.get("q") or data.get("prompt") or "").strip()
    reply = f"I heard: {text}" if text else "I heard nothing."

    return jsonify({
        "ok": True,
        "reply": reply,
        "answer": reply,
        "response": reply,
        "text": reply,
        "message": reply
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
