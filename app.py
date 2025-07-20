from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import openai, os, base64
from utils.docx_generator import generate_docx
from utils.pptx_generator import generate_pptx

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# 載入風格知識庫
with open('styles.txt', encoding='utf-8') as f:
    styles_text = f.read()

@app.route("/")
def index():
    return "✅ 室內設計提案生成器 API 運作中"

@app.route("/api/parse_floorplan", methods=["POST"])
def parse_floorplan():
    if 'image' not in request.files:
        return jsonify({"error": "未收到圖片"}), 400

    img_file = request.files['image']
    img_bytes = img_file.read()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    user_input_total_area = request.form.get("total_area", "").strip()

    vision_prompt = f"""
你是一位專業室內設計師與圖面分析師，請根據以下上傳的「2D 室內平面配置圖」圖片，完成以下任務，並使用繁體中文回覆：

1. 根據圖片中的區塊與標註，列出所有空間與其功能（如主臥、客廳、餐廳、浴室...）
2. 辨識圖中每個空間內出現的主要家具，請列出：「空間名稱 / 家具名稱 / 擺放位置（用自然語言描述）」
3. {"請根據圖面總面積為 " + user_input_total_area + " 坪，依照空間比例估算各空間坪數。" if user_input_total_area else "嘗試估算圖面中各空間的坪數與總坪數（如有比例尺或標註）"}
4. 請輸出格式如下：

{{
  "傢俱配置": [
    {{"空間名稱": "主臥室", "家具名稱": "雙人床", "位置": "靠窗中央"}},
    {{"空間名稱": "客廳", "家具名稱": "沙發", "位置": "正對電視牆"}}
  ],
  "總坪數估算": "約 18.5 坪",
  "各空間坪數估算": [
    {{"空間": "主臥室", "坪數": "4.8"}},
    {{"空間": "客廳", "坪數": "5.1"}}
  ]
}}

請務必以 JSON 格式回覆（可閱讀為主，不必完全符合資料格式語法）。
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": vision_prompt},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]
                }
            ]
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
你是一位專業室內設計師，請根據以下資訊，撰寫一篇完整的室內設計提案文案，風格以【{style}】為主。請依以下格式條列清楚，語氣具備專業與情感。

【屋主基本資料】：
{owner_info}

【總坪數】：
{total_area}

【傢俱配置表】：
{furniture_text}

【風格設計原則】：
{styles_text}

請產出以下格式內容：
1. 提案命名（具故事性）
2. 設計理念總述（300字）
3. 空間導覽（依照進門順序，列出空間）
4. 每個空間逐一介紹，內容包含：
    - 坪數
    - 功能定位
    - 家具配置重點
    - 色彩搭配邏輯
    - 設計亮點與細節
    - 情感敘述
5. 屋主故事（與空間的連結）
6. 結語（設計總結與情感收束）

請以繁體中文回覆，語調需專業但富含情感，並保持段落清晰易讀。
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是一位頂尖的室內設計師，擅長撰寫空間提案。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/export_docx", methods=["POST"])
def export_docx():
    try:
        data = request.get_json()
        text = data.get("text", "")
        print("📥 收到匯出 Word 請求，字數：", len(text))
        path = generate_docx(text)
        return send_file(path, as_attachment=True)
    except Exception as e:
        print("❌ 匯出 Word 發生錯誤：", e)
        return jsonify({"error": str(e)}), 500

@app.route("/api/export_pptx", methods=["POST"])
def export_pptx():
    try:
        data = request.get_json()
        text = data.get("text", "")
        print("📥 收到匯出 PPT 請求，字數：", len(text))
        path = generate_pptx(text)
        return send_file(path, as_attachment=True)
    except Exception as e:
        print("❌ 匯出 PPT 發生錯誤：", e)
        return jsonify({"error": str(e)}), 500