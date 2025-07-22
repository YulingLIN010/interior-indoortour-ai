
import openai

def generate_narrative_prompt(data):
    style = data.get("style", "北歐風")
    owner = data.get("owner_info", "")
    furniture_data = data.get("furniture_layout", [])
    total_area = data.get("total_area", "")
    layout = ""
    for space in furniture_data[:1]:  # 只取一區空間
        layout += f"空間名稱：{space['name']}，坪數：{space['area']}，家具：{', '.join(space['furniture'])}\n"
    prompt = f"""
請根據以下資訊撰寫室內設計導覽文案（精簡版）：
1. 設計理念總述（1段）
2. 空間導覽（僅描述一個空間，包含：坪數、功能、家具、色彩、設計重點與情感）
風格：{style}
總坪數：{total_area}
屋主資料：{owner}
空間家具資料：
{layout}
請用簡潔段落撰寫。
"""
    return prompt.strip()

def call_gpt_narrative(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=800,
            stream=True
        )
        content = ""
        for chunk in response:
            content += chunk.choices[0].delta.get("content", "")
        return {"content": content}
    except Exception as e:
        return {"error": str(e)}
