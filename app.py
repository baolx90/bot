from flask import Flask, render_template, request, jsonify , url_for , redirect
import pandas as pd
from werkzeug.utils import secure_filename
import os
from promptflow import load_flow

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.environ.get("UPLOAD_FOLDER")
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "csv"}
FILE_PATH="processed/result.csv"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# if not os.path.exists(BASE_DIR + "/.pdfs"):
#     os.mkdir(BASE_DIR + "/.pdfs")
# if not os.path.exists(BASE_DIR + "/.index/.pdfs"):
#     os.makedirs(BASE_DIR + "/.index/.pdfs")
chat_history = []
promptflow_history = []

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def index():
    df = pd.read_csv(FILE_PATH).reset_index()
    df = df.iloc[:, 0:1]
    df.columns = ["filepath"]
    return render_template("index.html", chat_history=chat_history, files=df)

@app.route("/chat", methods=["POST"])
def chat():
    question = request.json["message"]
    chat_history.append({"role": "user", "content": question})

    flow_result = run_flow(
        flow_path="flows/chat",
        flow_inputs=dict(question=question, chat_history=promptflow_history)
    )

    chat_history.append({"role": "assistant", "content": flow_result['answer']})
    promptflow_history.append(dict(inputs=dict(question=question), outputs=dict(answer=flow_result['answer'])))
    return jsonify(success=True, message=flow_result['answer'])

def run_flow(flow_path: str, flow_inputs: object = object) -> object:
    flow_func = load_flow(flow_path)
    return flow_func(**flow_inputs)

@app.route("/crawl", methods=["POST"])
def crawl():
    url = request.form.get('url', '')
    if url != '':
        crawl_web = run_flow(
            flow_path="flows/crawl-web", 
            flow_inputs=dict(url=url)
        )

        run_flow(
            flow_path="flows/summary-data",
            flow_inputs=dict(file_path=crawl_web['result'])
        )

    if "file-upload" in request.files:
        file = request.files["file-upload"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # run_flow(
            #     flow_path="flows/summary-data",
            #     flow_inputs=dict(file_path=app.config['UPLOAD_FOLDER'] + "/" + filename)
            # )
    
    return jsonify(
            success=True,
            message="Crawl url successfully and added to the storage"
        )

@app.route("/reset", methods=["GET"])
def reset_chat():
    global chat_history
    chat_history = []
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0')