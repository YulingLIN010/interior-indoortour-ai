import base64
import io
import json
from PIL import Image
from openai import OpenAI
import re

client = OpenAI()

def parse_floorplan_image(image_file):
    image = Image.open(image_file.stream).convert("RGB")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    prompt = """
你是一位專業的室內設計師，請根據以下2D室內空間平面配置圖進行詳細分析，務必依照圖中結構與常見配置準確判斷每個空間的功能與配置。請辨識以下項目：

1. 明確列出每個空間的名稱（例如：主臥室、客廳、廚房、衛浴、陽台、多功能房等）。
2. 根據圖面比例估算每個空間的坪數。
3. 分析每個空間內的主要家具與配置，標示家具名稱及數量（例如：「雙人床」、「床頭櫃2個」、「L型沙發」、「書桌1張」、「衣櫃」）。
4. 僅列出有實際牆面／空間分隔的實際空間（不要列走道或空白處）。

⚠️ 請務必依照圖面比例、常見空間邏輯（臥室有床、浴室有馬桶與淋浴區、餐廳有餐桌）進行專業判斷。
⚠️ 若無法清楚辨識，請以最可能的空間功能進行推測，但避免過度解釋。

請將結果以標準 JSON 格式回傳如下：

{
  "total_area": 18.5,
  "spaces": [
    {
      "name": "主臥室",
      "area": 5.0,
      "furniture": ["雙人床", "床頭櫃2個", "衣櫃"]
    },
    {
      "name": "客廳",
      "area": 4.0,
      "furniture": ["L型沙發", "電視櫃", "茶几"]
    }
  ]
}

請直接回傳純 JSON 格式，不要加上 ```json 標記。
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]
            }
        ]
    )

    result = response.choices[0].message.content.strip()

    # 嘗試從 ```json 區塊中抓出純 JSON 字串
    match = re.search(r"```json\s*({.*?})\s*```", result, re.DOTALL)
    if match:
        cleaned_result = match.group(1)
    else:
        cleaned_result = result  # 若沒有包 markdown，直接使用原始內容

    try:
        return json.loads(cleaned_result)
    except json.JSONDecodeError as e:
        return {"error": f"GPT 回傳內容解析失敗: {str(e)}", "raw": result}