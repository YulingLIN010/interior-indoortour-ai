import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from utils.vision_parser import parse_floorplan_image
from utils.prompt_templates import generate_narrative_prompt, call_gpt_narrative
from utils.docx_generator import generate_docx
import io
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
UPLOAD_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/api/parse_floorplan", methods=["POST"])
def parse_floorplan():
    try:
        if "file" not in request.files:
            return jsonify({"error": "未收到圖面"}), 400
        image_file = request.files["file"]
        filename = image_file.filename
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(save_path)  # ⬅️ 實體檔案儲存於 static/
        result = parse_floorplan_image(image_file)
        result["image_filename"] = filename  # 回傳給前端後續產 Word 用
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/generate_design_narrative", methods=["POST"])
def generate_narrative():
    try:
        data = request.get_json()
        prompt = generate_narrative_prompt(data)
        content = call_gpt_narrative(prompt, data)
        return jsonify(content)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/download_word_docx", methods=["POST"])
def download_docx():
    data = request.get_json()
    image_filename = data.get("image_filename", None)
    image_path = os.path.join(UPLOAD_FOLDER, image_filename) if image_filename else None
    docx_bytes = generate_docx(data, image_path=image_path)
    return send_file(io.BytesIO(docx_bytes), as_attachment=True,
                     download_name="空間設計導覽文案.docx",
                     mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

if __name__ == "__main__":
    app.run(debug=True)
