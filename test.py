
import re
import PyPDF2
import pandas as pd
from werkzeug.utils import secure_filename
import os
from promptflow import load_flow

ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "csv"}

message_wellcome = "Bao test ok, You are a helpful assistant."
chat_history = [
    {"role": "system", "content": message_wellcome},
]
FILE_PATH="processed/result.csv"

def chat():
    question = 'what is zopi ?'
    chat_history.append({"role": "user", "content": question})

    flow_path = "flows/chat"
    flow_inputs = {
        "question": question
    }

    flow_func = load_flow(flow_path)
    flow_result = flow_func(**flow_inputs)
    print(flow_result)


def split_text(text, chunk_size, chunk_overlap):
    # Calculate the number of chunks
    num_chunks = (len(text) - chunk_overlap) // (chunk_size - chunk_overlap)

    # Split the text into chunks
    chunks = []
    for i in range(num_chunks):
        start = i * (chunk_size - chunk_overlap)
        end = start + chunk_size
        chunks.append(text[start:end])

    # Add the last chunk
    chunks.append(text[num_chunks * (chunk_size - chunk_overlap):])

    return chunks

def test():
    file_path = 'processed/uploads/test.pdf'

    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".txt":
        f = open(file_path, "r")
        return f.read()
    elif ext == ".pdf":

        chunk_size = int(os.environ.get("CHUNK_SIZE"))
        chunk_overlap = int(os.environ.get("CHUNK_OVERLAP"))
        reader = PyPDF2.PdfReader(file_path)
        text = "" 
        for page in reader.pages: 
            text+=page.extract_text().strip()
        
        segments = split_text(text, chunk_size, chunk_overlap)
        # print(segments)
        # print(text)
        # print(reader.pages)
        # page = reader.pages[0] 
        # content = page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False) 
        text= re.sub("(Page) (\d{1,3}) (of) (\d{1,3})", "", text)
        print(text)
    else:
        print (file_path,"is an unknown file format.")
    

if __name__ == "__main__":
    # chat()
    # library_df = pd.read_csv(FILE_PATH).reset_index()
    # library_df = library_df.iloc[:, 1:2]
    # library_df.columns = ["filepath"]
    # print(library_df)
    test()