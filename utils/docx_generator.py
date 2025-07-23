from docx import Document
from docx.shared import Inches
import io
import os

def generate_docx(data, image_path=None):
    doc = Document()
    doc.add_heading("空間設計導覽文案", 0)

    doc.add_heading("提案命名與設計理念總述", level=1)
    doc.add_paragraph(data.get("proposal_title_and_concept", ""))

    doc.add_heading("空間總覽與動線說明", level=1)
    doc.add_paragraph(data.get("overview_and_circulation", ""))
    if image_path and os.path.exists(image_path):
        doc.add_picture(image_path, width=Inches(5.5))

    doc.add_heading("逐區空間導覽", level=1)
    sections = data.get("sections", [])
    for section in sections:
        doc.add_heading(section.get("room", "未命名空間"), level=2)
        doc.add_paragraph(f"坪數：{section.get('area', '')}")
        doc.add_paragraph(f"空間功能說明：{section.get('function', '')}")
        doc.add_paragraph("家具重點配置：" + "、".join(section.get("furniture", [])))
        doc.add_paragraph(f"色彩搭配邏輯：{section.get('color', '')}")
        doc.add_paragraph(f"設計重點分析：{section.get('design_note', '')}")
        doc.add_paragraph(f"空間情感敘述：{section.get('emotion', '')}")

    doc.add_heading("屋主故事", level=1)
    doc.add_paragraph(data.get("owner_story", ""))

    doc.add_heading("空間結語", level=1)
    doc.add_paragraph(data.get("conclusion", ""))

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()
