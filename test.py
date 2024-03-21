
import pandas as pd
from werkzeug.utils import secure_filename
import os
from promptflow import load_flow

ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "csv"}

message_wellcome = "Bao test ok, You are a helpful assistant."
chat_history = [
    {"role": "system", "content": message_wellcome},
]

def chat():
    question = 'hello'
    chat_history.append({"role": "user", "content": question})

    flow_path = "flows/chat"
    flow_inputs = {
        "question": question
    }

    flow_func = load_flow(flow_path)
    flow_result = flow_func(**flow_inputs)
    print(flow_result)

if __name__ == "__main__":
    chat()