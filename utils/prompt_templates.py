
import openai

def generate_narrative_prompt(data):
    style = data.get("style", "")
    owner_info = data.get("owner_info", "")
    total_area = data.get("total_area", "")
    furniture = data.get("furniture_layout", [])

    prompt = f"請根據以下資訊撰寫室內設計導覽文案（精簡版）：\n"
    prompt += "1. 一段設計理念總述（不超過200字）\n"
    prompt += "2. 描述以下空間（僅限1區），以段落呈現完整敘述（約200字）\n"
    prompt += "3. 一段結語收尾（約100字）\n\n"
    prompt += f"空間風格：{style}\n總坪數：{total_area}\n屋主資料：{owner_info}\n空間家具資料如下：\n"

    for space in furniture:
        prompt += f"空間名稱：{space.get('name')}，坪數：{space.get('area')}，家具：{', '.join(space.get('furniture', []))}\n"

    prompt += "\n請用以下格式回覆：\n【設計理念】\n（內文）\n\n【空間名稱】\n（空間文案）\n\n【結語】\n（一段結語）"
    return prompt

def call_gpt_narrative(prompt):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是專業的室內設計師，擅長撰寫空間導覽文案"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1024,
        stream=True
    )

    content = ""
    for chunk in response:
        if hasattr(chunk.choices[0].delta, "content"):
            content += chunk.choices[0].delta.content

    parts = {"content": content}

    lines = content.splitlines()
    current_key = None
    buffer = []
    for line in lines:
        if "設計理念" in line:
            if current_key:
                parts[current_key] = "\n".join(buffer).strip()
                buffer = []
            current_key = "concept"
        elif "結語" in line:
            if current_key:
                parts[current_key] = "\n".join(buffer).strip()
                buffer = []
            current_key = "conclusion"
        elif "】" in line:
            if current_key:
                parts[current_key] = "\n".join(buffer).strip()
                buffer = []
            current_key = "sections"
        else:
            buffer.append(line)

    if current_key and buffer:
        if current_key == "sections":
            parts["sections"] = [{"title": "空間文案", "text": "\n".join(buffer).strip()}]
        else:
            parts[current_key] = "\n".join(buffer).strip()

    return parts
