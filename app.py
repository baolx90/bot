from flask import Flask, render_template, request, jsonify , url_for , redirect
from werkzeug.utils import secure_filename
import os
from utils.openai import summarize_text
from utils.crawl import summarize_url

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.environ.get("UPLOAD_FOLDER")
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "csv"}

message_wellcome = "Bao test ok, You are a helpful assistant."
chat_history = [
    {"role": "system", "content": message_wellcome},
]

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", chat_history=chat_history)

@app.route("/chat", methods=["POST"])
def chat():
    question = request.json["message"]
    chat_history.append({"role": "user", "content": question})
    text_content = summarize_text(text=question)
    chat_history.append({"role": "assistant", "content": text_content})
    return jsonify(success=True, message=text_content)

@app.route("/crawl", methods=["GET"])
def crawl():
    return summarize_url(request.args.get('url'))

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify(success=False, message="No file part")
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify(success=False, message="No selected file")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    return jsonify(
            success=True,
            message="File uploaded successfully and added to the storage"
        )

if __name__ == "__main__":
    app.run(host='0.0.0.0')
