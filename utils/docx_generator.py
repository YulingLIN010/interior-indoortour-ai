from docx import Document
import os

def generate_docx(text: str):
    print("📄 開始產生 Word 檔，字數：", len(text))

    doc = Document()
    doc.add_heading("設計提案報告", 0)

    if not text.strip():
        doc.add_paragraph("⚠️ 系統未接收到有效內容。")
    else:
        paragraphs = text.split("\n")
        for para in paragraphs:
            if para.strip():
                if len(para) > 120:
                    for chunk in [para[i:i+120] for i in range(0, len(para), 120)]:
                        doc.add_paragraph(chunk.strip())
                else:
                    doc.add_paragraph(para.strip())

    path = "proposal.docx"  # ✅ 儲存在當前目錄
    try:
        doc.save(path)
        print("✅ Word 檔已成功儲存：", path)
    except Exception as e:
        print("❌ 儲存 Word 檔失敗：", str(e))
        raise e

    if not os.path.exists(path):
        raise FileNotFoundError("❌ Word 檔儲存失敗，檔案不存在")

    return path