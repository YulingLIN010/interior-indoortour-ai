import openai
import re

def generate_narrative_prompt(data):
    style = data.get("style", "")
    owner_info = data.get("owner_info", "")
    total_area = data.get("total_area", "")
    furniture = data.get("furniture_layout", [])

    prompt = f"""請根據提供的空間家具資料、坪數、風格與屋主背景及主要需求，撰寫一份具故事性的室內設計導覽文案，內容需包含：
1. 【提案命名與設計理念總述】— 取一個具創意的提案名稱，並以約150字說明本案設計理念與風格核心價值。
2. 【空間總覽與動線說明】— 描述總坪數、空間分布及從玄關出發的動線邏輯，約100字。
3. 【逐區空間導覽】— 依玄關起的動線順序，針對每個空間依下列格式詳述（每區100字以上）：
   - 坪數
   - 空間功能說明
   - 家具重點配置
   - 色彩搭配邏輯
   - 設計重點分析
   - 空間情感敘述
4. 【屋主故事】— 依據屋主職業、成員、興趣與主要需求，描寫一段有故事感的背景敘述（約100字）。
5. 【空間結語】— 以專業且富含情感的語句做總結，強調設計特色與空間價值（約50-100字）。

設計風格：{style}
總坪數：{total_area}
屋主背景與需求：{owner_info}
空間家具資料如下：
"""
    for space in furniture:
        name = space.get("name", "未命名")
        area = space.get("area", "未提供")
        furn_list = space.get("furniture", [])
        if not isinstance(furn_list, list):
            furn_list = [str(furn_list)]
        furniture_text = "、".join(furn_list)
        prompt += f"空間名稱：{name}，坪數：{area}，家具：{furniture_text}\n"
    prompt += "\n請務必逐一分段、以下述格式完整回覆：\n" + \
        "【提案命名與設計理念總述】\n...\n\n" + \
        "【空間總覽與動線說明】\n...\n\n" + \
        "【逐區空間導覽】\n【空間名稱】\n坪數：\n空間功能說明：\n家具重點配置：\n色彩搭配邏輯：\n設計重點分析：\n空間情感敘述：\n（請依動線順序寫出所有空間）\n\n" + \
        "【屋主故事】\n...\n\n" + \
        "【空間結語】\n..."
    return prompt

def call_gpt_narrative(prompt, data):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是專業的室內設計師，擅長撰寫室內設計導覽文案"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=4096,
    )
    text = response.choices[0].message.content
    # 分章節正規化
    def extract_block(label, t):
        m = re.search(rf"【{label}】\n?([\s\S]+?)(?=\n?【|\Z)", t)
        return m.group(1).strip() if m else ""
    result = {
        "proposal_title_and_concept": extract_block("提案命名與設計理念總述", text),
        "overview_and_circulation": extract_block("空間總覽與動線說明", text),
        "room_sections_raw": extract_block("逐區空間導覽", text),
        "owner_story": extract_block("屋主故事", text),
        "conclusion": extract_block("空間結語", text),
        "content": text,
    }
    # 解析所有空間區段
    room_sections = []
    for match in re.finditer(r"【(.+?)】\n坪數：(.+)\n空間功能說明：(.+)\n家具重點配置：(.+)\n色彩搭配邏輯：(.+)\n設計重點分析：(.+)\n空間情感敘述：(.+?)(?=\n【|\Z)", result["room_sections_raw"], re.DOTALL):
        room_sections.append({
            "room": match.group(1).strip(),
            "area": match.group(2).strip(),
            "function": match.group(3).strip(),
            "furniture": [f.strip() for f in match.group(4).strip().replace("、",",").replace("，",",").split(",") if f.strip()],
            "color": match.group(5).strip(),
            "design_note": match.group(6).strip(),
            "emotion": match.group(7).strip(),
        })
    result["sections"] = room_sections
    return result
