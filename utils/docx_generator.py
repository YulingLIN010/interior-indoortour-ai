from docx import Document

def generate_docx(gpt_text: str):
    doc = Document()
    doc.add_heading("設計提案報告", 0)

    if not gpt_text.strip():
        doc.add_paragraph("⚠️ 系統未接收到有效內容。")
    else:
        for para in gpt_text.split("\n"):
            if para.strip():
                doc.add_paragraph(para.strip())

    path = "/mnt/data/proposal.docx"
    doc.save(path)
    return path

