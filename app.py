
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import openai, os, base64
from docx_generator import docx_generate
from io import BytesIO

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def index():
    return "✅ AI 室內設計導覽小幫手後端運作中"

@app.route("/api/gen_proposal", methods=["POST"])
def gen_proposal():
    data = request.get_json()
    style = data.get("style", "")
    owner_info = data.get("owner_info", "")
    furniture_list = data.get("furniture_list", [])
    total_area = data.get("total_area", "")

    furniture_text = "\n".join([
        f"- 空間名稱：{item['空間名稱']}｜家具名稱：{item['家具名稱']}｜位置：{item['位置']}"
        for item in furniture_list
    ])

    prompt = f"""
你是一位專業室內設計師，請根據以下資訊，撰寫一篇完整的室內設計提案文案，風格以【{style}】為主。

【屋主基本資料】：
{owner_info}

【總坪數】：
{total_area}

【傢俱配置表】：
{furniture_text}

請依下列格式撰寫：
1. 提案命名
2. 設計理念總述
3. 空間導覽
4. 每個空間逐一介紹（坪數、功能、家具、色彩、亮點、情感）
5. 屋主故事
6. 結語
請用繁體中文回答。
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是一位頂尖的室內設計師"},
                {"role": "user", "content": prompt}
            ]
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/export_docx", methods=["POST"])
def export_docx():
    data = request.get_json()
    text = data.get("text", "")
    image_base64 = data.get("image_base64", "")
    image_bytes = None

    if image_base64:
        try:
            image_bytes = base64.b64decode(image_base64.split(",")[-1])
        except Exception as e:
            print("⚠️ 無法解碼圖片")

    try:
        path = docx_generate(text, image_bytes)
        return send_file(path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
