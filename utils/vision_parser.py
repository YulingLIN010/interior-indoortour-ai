
import base64
import io
from PIL import Image
from openai import OpenAI

client = OpenAI()  # 預設從環境變數 OPENAI_API_KEY 讀取

def parse_floorplan_image(image_file):
    # ✅ 將圖檔轉為合格 PNG 格式並編碼為 base64
    image = Image.open(image_file.stream).convert("RGB")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # ✅ 強化 GPT-4o 圖像辨識 Prompt（v1.7）
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
    return eval(result)
