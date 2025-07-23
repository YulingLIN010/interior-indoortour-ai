from docx import Document
from docx.shared import Inches
import io
import os

def generate_docx(data, image_path=None):
    doc = Document()
    doc.add_heading("空間設計導覽文案", 0)

    doc.add_heading("提案命名與設計理念總述", level=1)
    doc.add_paragraph(data.get("concept", ""))

    doc.add_heading("空間總覽與動線說明", level=1)
    doc.add_paragraph(data.get("overview", ""))
    if image_path and os.path.exists(image_path):
        doc.add_picture(image_path, width=Inches(5.5))

    doc.add_heading("逐區空間導覽", level=1)
    doc.add_paragraph(data.get("rooms", ""))

    doc.add_heading("屋主故事", level=1)
    doc.add_paragraph(data.get("owner_story", ""))

    doc.add_heading("空間結語", level=1)
    doc.add_paragraph(data.get("conclusion", ""))

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()
