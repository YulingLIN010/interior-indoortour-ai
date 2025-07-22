
import openai

def generate_narrative_prompt(data):
    style = data.get("style", "北歐風")
    owner = data.get("owner_info", "")
    furniture_data = data.get("furniture_layout", [])
    total_area = data.get("total_area", "")
    layout = ""
    for space in furniture_data[:1]:  # 只取第一個空間避免超長
        layout += f"空間名稱：{space['name']}，坪數：{space['area']}，家具：{', '.join(space['furniture'])}\n"
    prompt = f"""
請根據以下資訊撰寫室內設計導覽文案（精簡版）：
1. 一段設計理念總述（不超過200字）
2. 描述以下空間（僅限1區），以段落呈現完整敘述（約200字）
空間風格：{style}
總坪數：{total_area}
屋主資料：{owner}
空間家具資料如下：
{layout}
請輸出格式如下：
【設計理念】
（內文）

【主臥室】
（空間文案）

【結語】
（一段結語）
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
            if hasattr(chunk.choices[0].delta, "content"):
            content += chunk.choices[0].delta.content

        parts = {"concept": "", "sections": [], "conclusion": ""}
        current = None
        for line in content.splitlines():
            if "【設計理念】" in line:
                current = "concept"
                continue
            elif "【結語】" in line:
                current = "conclusion"
                continue
            elif line.startswith("【") and "】" in line:
                current = "section"
                parts["sections"].append({"title": line.strip("【】"), "text": ""})
                continue

            if current == "concept":
                parts["concept"] += line + "\n"
            elif current == "conclusion":
                parts["conclusion"] += line + "\n"
            elif current == "section" and parts["sections"]:
                parts["sections"][-1]["text"] += line + "\n"

        parts["content"] = content  # ✅ fallback 加入成功
        return parts
    except Exception as e:
        return {"error": str(e)}
