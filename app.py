import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

def get_openai_client():
    # Import here so the home page can still load if the AI package/key is not configured.
    from openai import OpenAI
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("OPENAI_API_KEY Render Environment bo'limida sozlanmagan.")
    return OpenAI(api_key=key)

@app.get("/")
def home():
    try:
        return render_template("index.html")
    except Exception:
        app.logger.exception("Bosh sahifani ochishda template xatosi")
        return """
        <!doctype html><html lang="uz"><meta charset="utf-8">
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <title>KENJATOY AI</title>
        <body style="margin:0;background:#0b0911;color:#eee;font:16px Arial;padding:28px">
        <h1 style="color:#b79aff">KENJATOY AI</h1>
        <p>Sayt serveri ishlayapti, lekin <b>templates/index.html</b> faylini topa olmadi.</p>
        <p>GitHub repository ichida <code>templates</code> papkasi va uning ichida <code>index.html</code> borligini tekshiring.</p>
        </body></html>
        """, 200

@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify(error="Xabar yozing."), 400
    try:
        client = get_openai_client()
        response = client.responses.create(
            model=os.getenv("CHAT_MODEL", "gpt-4.1-mini"),
            instructions="Sen KENJATOY AI nomli yordamchisan. O'zbek tilida aniq, do'stona va foydali javob ber.",
            input=message,
        )
        return jsonify(reply=response.output_text)
    except Exception:
        app.logger.exception("Chat API xatosi")
        return jsonify(error="AI ishlamadi. Render Environment'dagi OPENAI_API_KEY, API billing va model ruxsatini tekshiring."), 500

@app.post("/api/image")
def image():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify(error="Rasm uchun tavsif yozing."), 400
    try:
        client = get_openai_client()
        result = client.images.generate(
            model=os.getenv("IMAGE_MODEL", "gpt-image-1"),
            prompt=prompt,
            size="1024x1024",
        )
        item = result.data[0]
        if getattr(item, "url", None):
            return jsonify(image_url=item.url)
        import base64
        return jsonify(image_url="data:image/png;base64," + item.b64_json)
    except Exception:
        app.logger.exception("Image API xatosi")
        return jsonify(error="Rasm yaratilmadi. API kaliti, model ruxsati va API hisobidagi billingni tekshiring."), 500

@app.get("/health")
def health():
    return jsonify(status="ok"), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
