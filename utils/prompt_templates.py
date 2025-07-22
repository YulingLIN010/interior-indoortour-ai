
import openai

def generate_narrative_prompt(data):
    style = data.get("style", "北歐風")
    owner = data.get("owner_info", "")
    furniture_data = data.get("furniture_layout", [])
    total_area = data.get("total_area", "")
    layout = ""
    for space in furniture_data:
        layout += f"空間名稱：{space['name']}，坪數：{space['area']}，家具：{', '.join(space['furniture'])}\n"
    prompt = f"""
請根據以下提供的空間家具資料、坪數、風格與屋主背景故事，撰寫一份具故事性的室內設計導覽文案，內容需包含：
1. 提案命名與設計理念總述
2. 空間總覽與動線說明
3. 逐區空間導覽（依照從玄關起動線排序），每區包含：
  - 坪數
  - 空間功能說明
  - 家具重點配置
  - 色彩搭配邏輯
  - 設計重點分析
  - 空間情感敘述
4. 根據使用需求設定屋主故事
5. 空間結語，具備情感性與專業觀點

空間風格：{style}
總坪數：{total_area}
屋主資料：{owner}
空間家具資料如下：
{layout}
請以條列式＋段落結構撰寫。
"""
    return prompt.strip()

def call_gpt_narrative(prompt):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=2048,
        stream=True
    )
    content = ""
    for chunk in response:
        content += chunk.choices[0].delta.get("content", "")
    return {"content": content}
