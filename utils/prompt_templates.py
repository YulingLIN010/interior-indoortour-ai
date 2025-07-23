import openai
import json

def generate_narrative_prompt(data):
    style = data.get("style", "")
    owner_info = data.get("owner_info", "")
    total_area = data.get("total_area", "")
    furniture = data.get("furniture_layout", [])

    prompt = f"""你是一位專業室內設計師，請根據下列資訊撰寫空間設計導覽文案：
1. 先寫一段設計理念總述（約100-200字）。
2. 針對每一個空間，請依下列欄位產生完整條列（必填所有欄位）：
- 空間名稱（room）
- 坪數（area）
- 功能說明（function）
- 家具配置（furniture，以頓號或逗號分隔）
- 色彩搭配（color）
- 設計重點（design_note）
- 空間情感描述（emotion）
請用 JSON 陣列格式輸出所有空間，key 必須與上述相同（如 room, area, ...）。

3. 最後寫一段結語（50-100字）。

設計風格：{style}
總坪數：{total_area}
屋主資料：{owner_info}
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
    prompt += "\n請務必照上述格式與 key 回答。"
    return prompt

def call_gpt_narrative(prompt, data):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是專業的室內設計師，擅長撰寫空間導覽文案"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2048,
    )

    # 嘗試從回應解析 JSON
    text = response.choices[0].message.content
    parts = {"content": text}
    # 理念
    concept = ""
    conclusion = ""
    sections = []
    # 自動抽理念
    concept_match = None
    conclusion_match = None
    import re
    concept_match = re.search(r"(?:【?設計理念(?:總述)?】?\n?)([\s\S]+?)(?:\n|【)", text)
    if concept_match:
        concept = concept_match.group(1).strip()
    # sections: 嘗試抓出json
    json_match = re.search(r"\[(\s*{[\s\S]+?}\s*)\]", text)
    if json_match:
        json_str = "[" + json_match.group(1).strip() + "]"
        try:
            sections = json.loads(json_str)
        except Exception:
            sections = []
    # 結語
    conclusion_match = re.search(r"(?:【?結語】?\n?)([\s\S]+)$", text)
    if conclusion_match:
        conclusion = conclusion_match.group(1).strip()
    if not concept:
        concept = text.split("\n")[0]
    if not sections:
        # fallback: 只抽主要段落
        sections = []
        for line in text.split("\n"):
            if any(k in line for k in ["空間名稱", "room"]):
                sections.append({"function": line})
    if not conclusion:
        conclusion = text.split("\n")[-1]
    # 自動補全欄位
    sections = normalize_sections(sections)
    return {
        "concept": concept,
        "sections": sections,
        "conclusion": conclusion,
        "content": text
    }

def normalize_sections(sections):
    keys = ["room", "area", "function", "furniture", "color", "design_note", "emotion"]
    normed = []
    for s in sections:
        norm = {}
        for k in keys:
            if k not in s:
                norm[k] = [] if k == "furniture" else ""
            else:
                norm[k] = s[k]
        # 家具欄位統一成字串陣列
        if not isinstance(norm["furniture"], list):
            norm["furniture"] = [str(norm["furniture"])]
        normed.append(norm)
    return normed
