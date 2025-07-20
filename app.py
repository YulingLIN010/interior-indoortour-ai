import os
import base64
from flask import Flask, request, jsonify, send_file
from docx_generator import docx_generate
from prompts import vision_prompt, proposal_prompt
import openai
from io import BytesIO

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/api/parse_floorplan", methods=["POST"])
def parse_floorplan():
    image = request.files.get("image")
    total_area = request.form.get("total_area", "").strip()

    if not image:
        return jsonify({"error": "未提供圖面"}), 400

    image_bytes = image.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    messages = [
        {"role": "system", "content": vision_prompt},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "請解析此平面圖的坪數與傢俱配置"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }
    ]

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.4
    )

    reply = response.choices[0].message.content
    return jsonify({"reply": reply})


@app.route("/api/gen_proposal", methods=["POST"])
def gen_proposal():
    data = request.get_json()
    style = data.get("style")
    owner_info = data.get("owner_info")
    total_area = data.get("total_area")
    furniture_list = data.get("furniture_list")

    content = proposal_prompt.format(style=style, owner=owner_info, area=total_area, furniture=furniture_list)

    messages = [
        {"role": "system", "content": "你是專業的室內設計師助手，擅長撰寫具故事性的空間導覽與設計提案文案。"},
        {"role": "user", "content": content}
    ]

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7
    )

    reply = response.choices[0].message.content
    return jsonify({"reply": reply})


@app.route("/api/export_docx", methods=["POST"])
def export_docx():
    data = request.get_json()
    text = data.get("text", "")
    image_base64 = data.get("image_base64", "")

    if "," in image_base64:
        image_base64 = image_base64.split(",")[1]
    image_bytes = base64.b64decode(image_base64)

    path = docx_generate(text, image_bytes)

    return send_file(path, as_attachment=True, download_name="室內設計導覽文案.docx")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)