from docx import Document
from docx.shared import Inches
import io
import os

def generate_docx(data, image_path=None):
    doc = Document()
    doc.add_heading("空間設計導覽文案", 0)

    # 設計理念
    doc.add_heading("設計理念總述", level=1)
    doc.add_paragraph(data.get("concept", ""))

    # 動線說明＋插圖
    doc.add_heading("空間總覽與導覽動線說明", level=1)
    doc.add_paragraph("以下為本案動線說明與原始平面圖：")
    if image_path and os.path.exists(image_path):
        doc.add_picture(image_path, width=Inches(5.5))

    # 空間逐區
    doc.add_heading("空間導覽文案", level=1)
    for section in data.get("sections", []):
        doc.add_heading(section["room"], level=2)
        doc.add_paragraph(f"坪數：{section['area']}")
        doc.add_paragraph(f"功能：{section['function']}")
        doc.add_paragraph("傢俱配置：" + "、".join(section["furniture"]))
        doc.add_paragraph(f"色彩搭配：{section['color']}")
        doc.add_paragraph(f"設計重點：{section['design_note']}")
        doc.add_paragraph(f"情感描述：{section['emotion']}")

    # 結語
    doc.add_heading("結語", level=1)
    doc.add_paragraph(data.get("conclusion", ""))

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()
