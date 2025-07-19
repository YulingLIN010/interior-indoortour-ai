from docx import Document

def generate_docx(text: str):
    doc = Document()
    doc.add_heading("設計提案報告", 0)

    if not text.strip():
        doc.add_paragraph("⚠️ 系統未接收到有效內容。")
    else:
        paragraphs = text.split("\n")
        for para in paragraphs:
            if para.strip():
                # 若段落太長，自動分段處理，避免 Word 寫入損毀
                if len(para) > 120:
                    parts = [para[i:i+120] for i in range(0, len(para), 120)]
                    for part in parts:
                        doc.add_paragraph(part.strip())
                else:
                    doc.add_paragraph(para.strip())

    path = "/mnt/data/proposal.docx"
    doc.save(path)
    return path