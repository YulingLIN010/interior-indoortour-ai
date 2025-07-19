from flask import Flask, request, jsonify
from flask_cors import CORS
import openai, os, base64, json

app = Flask(__name__)
CORS(app)

# 初始化 GPT 客戶端（環境變數綁定金鑰）
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 讀入設計風格資料庫
with open('styles.txt', encoding='utf-8') as f:
    styles_text = f.read()

def auto_estimate_space_ratio(total_size):
    ratio = {
        "客廳": 0.25,
        "主臥": 0.2,
        "次臥": 0.15,
        "廚餐空間": 0.15,
        "浴廁": 0.1,
        "書房／多功能區": 0.1,
        "陽台／玄關等": 0.05
    }
    return {k: round(total_size * v, 2) for k, v in ratio.items()}

@app.route("/api/design_proposal", methods=["POST"])
def design_proposal():
    # 基本欄位接收
    if 'image' not in request.files:
        return jsonify({"reply": "❌ 未收到圖片，請重新上傳！"}), 400

    img_file = request.files['image']
    img_bytes = img_file.read()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    style = request.form.get("style", "")
    residents = request.form.get("residents", "")
    total_size = request.form.get("total_size", "")
    size_mode = request.form.get("size_mode", "auto")  # auto / semi / manual
    space_sizes = request.form.get("space_sizes", "{}")

    try:
        space_sizes_dict = json.loads(space_sizes)
    except:
        space_sizes_dict = {}

    # 判斷輸入模式
    if size_mode == "manual" and space_sizes_dict:
        mode = "手動輸入"
        size_text = "\n".join([f"{k}：{v}坪" for k, v in space_sizes_dict.items()])
    elif size_mode == "semi" and total_size:
        mode = "總坪數自動估算"
        est_sizes = auto_estimate_space_ratio(float(total_size))
        space_sizes_dict = est_sizes
        size_text = "\n".join([f"{k}：{v}坪" for k, v in est_sizes.items()])
    else:
        mode = "AI自動判斷"
        size_text = "請根據圖面自動判斷各空間與坪數"

    # 準備 prompt
    prompt = f"""
你是一位專業的室內設計師，請根據以下條件撰寫完整提案文案。

使用者選擇的風格為：「{style}」
居住者資訊為：「{residents}」
空間面積輸入模式：「{mode}」
空間坪數如下：
{size_text}

請分析上傳的2D圖面，依據動線順序進行以下撰寫：
1. 命名與設計理念
2. 空間配置導覽與動線簡述
3. 每個空間逐一撰寫介紹（包含坪數、功能、傢俱重點、色彩、設計語彙與情感）
4. 整體故事背景（針對屋主生活型態補述）
5. 結語收尾

請使用繁體中文回覆，文筆具有設計美感與空間邏輯感，內容可直接展示給客戶使用。

設計風格資料如下：
{styles_text}
    """

    # 發送至 GPT-4o（含圖片）
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
    )

    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

@app.route("/")
def index():
    return "✅ 室內設計提案生成運作中...請稍等"
