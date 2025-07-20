
from docx import Document
from docx.shared import Inches
from io import BytesIO

def docx_generate(text: str, image_bytes: bytes = None) -> str:
    doc = Document()
    doc.add_heading('室內設計導覽文案', 0)

    lines = text.split("\n")
    insert_image_after_heading = "3. 空間導覽"
    image_inserted = False

    for line in lines:
        line = line.strip()
        if not line:
            doc.add_paragraph("")
            continue

        # Heading 判斷
        if line.startswith("【") and line.endswith("】"):
            doc.add_heading(line.strip("【】"), level=1)
        elif line.startswith("1.") or line.startswith("2.") or line.startswith("3."):
            doc.add_heading(line, level=2)
            if insert_image_after_heading in line and image_bytes and not image_inserted:
                doc.add_picture(BytesIO(image_bytes), width=Inches(5.5))
                image_inserted = True
        elif any(line.startswith(f"{i}.") for i in range(4, 20)):
            doc.add_heading(line, level=3)
        else:
            doc.add_paragraph(line)

    path = "室內設計導覽文案.docx"
    doc.save(path)
    return path
