import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

def client():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("Serverda OPENAI_API_KEY sozlanmagan.")
    return OpenAI(api_key=key)

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify(error="Xabar yozing."), 400
    try:
        response = client().responses.create(
            model=os.getenv("CHAT_MODEL", "gpt-4.1-mini"),
            instructions="Sen KENJATOY AI nomli yordamchisan. O'zbek tilida aniq, do'stona va foydali javob ber.",
            input=message
        )
        return jsonify(reply=response.output_text)
    except Exception as e:
        app.logger.exception("Chat error")
        return jsonify(error="AI javob bera olmadi. Renderdagi OPENAI_API_KEY sozlamasini tekshiring."), 500

@app.post("/api/image")
def image():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify(error="Rasm uchun tavsif yozing."), 400
    try:
        result = client().images.generate(
            model=os.getenv("IMAGE_MODEL", "gpt-image-1"),
            prompt=prompt,
            size="1024x1024"
        )
        item = result.data[0]
        if getattr(item, "url", None):
            return jsonify(image_url=item.url)
        import base64
        return jsonify(image_url="data:image/png;base64," + item.b64_json)
    except Exception:
        app.logger.exception("Image error")
        return jsonify(error="Rasm yaratilmadi. API kaliti, model ruxsati va hisob balansini tekshiring."), 500

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
