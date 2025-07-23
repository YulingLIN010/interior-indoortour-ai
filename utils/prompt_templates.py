import openai

def generate_narrative_prompt(data, section="concept"):
    style = data.get("style", "")
    owner_info = data.get("owner_info", "")
    total_area = data.get("total_area", "")
    furniture = data.get("furniture_layout", [])

    if section == "concept":
        prompt = f"請根據以下資訊，產生【提案命名與設計理念總述】，150字內。\n設計風格：{style}\n總坪數：{total_area}\n屋主：{owner_info}"
    elif section == "overview":
        prompt = f"請根據以下資訊，產生【空間總覽與動線說明】（依大門入口開始按照動線順序規劃及介紹)，100字內。\n總坪數：{total_area}\n空間分布：{', '.join([s.get('name','') for s in furniture])}\n"
    elif section == "rooms":
        prompt = "請依下列空間資料，每個空間100字以上，產生【逐區空間導覽】（依大門入口開始按照動線順序介紹、每區以『【空間名稱】』開頭，內容請條列式列出:坪數、功能、設計重點、色彩配置、家具重點、情感）。\n"
        for space in furniture:
            name = space.get("name", "未命名")
            area = space.get("area", "未提供")
            furn_list = space.get("furniture", [])
            furniture_text = "、".join(furn_list)
            prompt += f"空間名稱：{name}，坪數：{area}，家具：{furniture_text}\n"
    elif section == "room":
        room = data.get("room_data", {})
        name = room.get("name", "未命名")
        area = room.get("area", "未提供")
        furn_list = room.get("furniture", [])
        furniture_text = "、".join(furn_list)
        prompt = (
            f"請根據以下單一空間資料，產生100字以上的【逐區空間導覽】段落，格式須條列：\n"
            f"空間名稱：{name}\n"
            f"坪數：{area}\n"
            f"主要家具：{furniture_text}\n"
            "請條列功能、家具重點、設計重點、色彩搭配、情感描述。"
        )
    elif section == "owner_story":
        prompt = f"請根據以下屋主資料，產生100字的【屋主故事】。\n{owner_info}"
    elif section == "conclusion":
        prompt = f"請根據以上空間資料，產生50-100字的【空間結語】，以專業且感性的語氣收尾。"
    else:
        prompt = "請產生簡短摘要。"
    return prompt

def call_gpt_section(prompt):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是專業的室內設計師"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()
