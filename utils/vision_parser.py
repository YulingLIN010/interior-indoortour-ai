import openai

def parse_floorplan_image(image_bytes):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是專業的室內設計師，擅長從2D平面圖辨識出空間用途與家具配置。"},
            {"role": "user", "content": [
                {"type": "text", "text": "請從這張圖判斷所有空間的名稱（如：主臥、客廳、廚房、浴室等），並列出每個空間的坪數（估算），以及包含哪些家具（名稱＋數量）。請以 JSON 格式回傳：{空間: [...], 總坪數}"},
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + image_bytes.decode("latin1")}}
            ]}
        ],
        temperature=0.2,
        max_tokens=1024
    )
    return response.choices[0].message.content
