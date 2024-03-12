from flask import Flask, render_template, request, jsonify , url_for , redirect
from werkzeug.utils import secure_filename
import os

from openai import OpenAI

client = OpenAI()
OpenAI.api_key = os.environ.get("OPENAI_API_KEY")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.environ.get("UPLOAD_FOLDER")
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "csv"}

# Initialize the Assistant and Thread globally
assistant_id = ""
thread_id = ""

message_wellcome = "Bao test, You are a helpful assistant."
chat_history = [
    {"role": "system", "content": message_wellcome},
]

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["POST"])
def upload_file():

    if "file" not in request.files:
        return jsonify(success=False, message="No file part")

    file = request.files["file"]

    global assistant_id

    if file.filename == "":
        return jsonify(success=False, message="No selected file")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # # Upload the file and add it to the Assistant (you could also add it to the message)
        uploaded_file = client.files.create(file=open(app.config['UPLOAD_FOLDER']+"/"+filename, "rb"), purpose="assistants")
        os.remove(app.config['UPLOAD_FOLDER']+"/"+filename)
        # uploaded_file = client.files.create(file=file.read(), purpose="assistants")
        assistant_files = client.beta.assistants.files.list(assistant_id=assistant_id)

        file_ids = [file.id for file in assistant_files.data]
        file_ids.append(uploaded_file.id)

        client.beta.assistants.update(
            assistant_id,
            file_ids=file_ids,
        )

        return jsonify(
            success=True,
            message="File uploaded successfully and added to the Assistant",
            filename=filename,
        )
    return jsonify(success=False, message="File type not allowed")


@app.route("/get_ids", methods=["GET"])
def get_ids():
    return jsonify(assistant_id=assistant_id, thread_id=thread_id)


@app.route("/get_messages", methods=["GET"])
def get_messages():
    if thread_id != "":
        thread_messages = client.beta.threads.messages.list(thread_id, order="asc")
        messages = [
            {
                "role": msg.role,
                "content": msg.content[0].text.value,
            }
            for msg in thread_messages.data
        ]
        return jsonify(success=True, messages=messages)
    else:
        return jsonify(success=False, message="No thread ID")


@app.route("/delete_files", methods=["POST"])
def delete_files():
    file_id = request.json.get("fileId")
    deleted_assistant_file = client.beta.assistants.files.delete(
        assistant_id=assistant_id, file_id=file_id
    )
    if deleted_assistant_file.deleted == True:
        return jsonify(success=True, messages="File deleted!")
    else:
        return jsonify(success=False, messages="File failed to be deleted.")


@app.route("/get_files", methods=["GET"])
def get_files():
    global assistant_id
    assistant_files = client.beta.assistants.files.list(assistant_id=assistant_id)

    files_list = []
    for file in assistant_files.data:
        files_list.append(
            {
                "id": file.id,
                "object": file.object,
                "created_at": file.created_at,
            }
        )
    return jsonify(assistant_files=files_list)


def create_assistant():
    global assistant_id
    if assistant_id == "":
        my_assistant = client.beta.assistants.create(
            instructions="This is a test assistant.",
            name="This is a test assistant.",
            tools=[{"type": "retrieval"}],
            model=os.environ.get("OPENAI_API_MODEL")
        )

        assistant_id = my_assistant.id
    else:
        my_assistant = client.beta.assistants.retrieve(assistant_id)
        assistant_id = my_assistant.id

    return my_assistant


def create_thread():
    global thread_id
    if thread_id == "":
        thread = client.beta.threads.create()
        thread_id = thread.id
    else:
        thread = client.beta.threads.retrieve(thread_id)
        thread_id = thread.id

    return thread


@app.route("/", methods=["GET"])
def index():
    return render_template("assistants.html", chat_history=chat_history)


@app.route("/chat", methods=["POST"])
def chat():
    content = request.json["message"]
    chat_history.append({"role": "user", "content": content})

    # Send the message to the assistant
    message_params = {"thread_id": thread_id, "role": "user", "content": content}

    thread_message = client.beta.threads.messages.create(**message_params)

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread_id, assistant_id=assistant_id
    )
    # Wait for the run to complete and get the response
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    response = client.beta.threads.messages.list(thread_id).data[0]

    text_content = None

    # Iterate through the content objects to find the first text content
    for content in response.content:
        if content.type == "text":
            text_content = content.text.value
            break  # Exit the loop once the first text content is found

    # Check if text content was found
    if text_content:
        chat_history.append({"role": "assistant", "content": text_content})
        return jsonify(success=True, message=text_content)
    else:
        # Handle the case where no text content is found
        return jsonify(success=False, message="No text content found")


@app.route("/reset", methods=["GET"])
def reset_chat():
    global chat_history
    chat_history = [{"role": "system", "content": message_wellcome}]

    global assistant_id
    assistant_id = ""
    create_assistant()

    global thread_id
    thread_id = ""
    create_thread()
    return redirect(url_for('index'))


# Create the assistants and thread when we first load the flask server
@app.before_request
def initialize():
    app.before_request_funcs[None].remove(initialize)
    create_assistant()
    create_thread()


if __name__ == "__main__":
    app.run(host='0.0.0.0')
