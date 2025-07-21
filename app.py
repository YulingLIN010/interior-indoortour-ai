import os
import openai
from flask import Flask, request, jsonify, send_file
from utils.vision_parser import parse_floorplan_image
from utils.prompt_templates import generate_narrative_prompt, call_gpt_narrative
from utils.docx_generator import generate_docx
import io
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
UPLOAD_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/api/parse_floorplan", methods=["POST"])
def parse_floorplan():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400
    image_bytes = file.read()
    result = parse_floorplan_image(image_bytes)
    return jsonify(result)

@app.route("/api/generate_design_narrative", methods=["POST"])
def generate_narrative():
    data = request.get_json()
    prompt = generate_narrative_prompt(data)
    content = call_gpt_narrative(prompt)
    return jsonify(content)

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
