from pptx import Presentation

def generate_pptx(gpt_text: str):
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[1])  # Title & Content

    slide.shapes.title.text = "設計提案簡報"
    content_box = slide.placeholders[1]
    tf = content_box.text_frame
    tf.clear()  # 清空原本 placeholder 預設內容

    for para in gpt_text.split("\n"):
        if para.strip():
            tf.add_paragraph().text = para.strip()

    path = "/mnt/data/proposal.pptx"
    prs.save(path)
    return path
