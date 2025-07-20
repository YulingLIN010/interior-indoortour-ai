from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from docx_generator import docx_generate
from prompts import vision_prompt, proposal_prompt
import base64
import openai
import os
from io import BytesIO

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)  # ✅ 加入 CORS 支援

@app.route("/api/parse_floorplan", methods=["POST"])
def parse_floorplan():
    image_file = request.files.get("image")
    total_area = request.form.get("total_area", "")
    if not image_file:
        return jsonify({"error": "No image provided"}), 400

    image_bytes = image_file.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    messages = [
        {"role": "system", "content": vision_prompt},
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
            {"type": "text", "text": f"請協助分析此圖面，若已知總坪數：{total_area} 可供參考"}
        ]}
    ]

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=2000
    )
    reply = response.choices[0].message.content
    return jsonify({"reply": reply})


@app.route("/api/gen_proposal", methods=["POST"])
def gen_proposal():
    data = request.get_json()
    style = data.get("style", "")
    owner_info = data.get("owner_info", "")
    total_area = data.get("total_area", "")
    furniture_list = data.get("furniture_list", "")

    content = proposal_prompt.format(
        style=style,
        owner=owner_info,
        area=total_area,
        furniture=furniture_list
    )

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": content}],
        max_tokens=3000
    )

    reply = response.choices[0].message.content
    return jsonify({"reply": reply})


@app.route("/api/export_docx", methods=["POST"])
def export_docx():
    data = request.get_json()
    text = data.get("text", "")
    image_base64 = data.get("image", "")

    image_bytes = base64.b64decode(image_base64.split(",")[-1]) if image_base64 else None
    output = BytesIO()
    docx_generate(text, image_bytes, output)
    output.seek(0)

    return send_file(output, as_attachment=True, download_name="設計提案.docx", mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

if __name__ == "__main__":
    app.run(debug=True)