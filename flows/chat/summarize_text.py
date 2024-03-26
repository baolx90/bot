
import ast
import re
import PyPDF2
import pandas as pd
from promptflow import tool
import tiktoken
from scipy.spatial.distance import cosine
from scipy import spatial
import os

FILE_PATH="processed/result.csv"

def debug_file(file_path):
    if not os.path.exists(file_path):
        return "../../"+file_path
    return file_path

def strings_ranked_by_relatedness(
    text: str,
    df: pd.DataFrame,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 100,
):  
    strings_and_relatednesses = [
        (row["filepath"], relatedness_fn(text, row["embedding"]))
        for i, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)
    return strings[:top_n]

def create_chunks(text, n, tokenizer):
    """Returns successive n-sized chunks from provided text."""
    tokens = tokenizer.encode(text)
    i = 0
    while i < len(tokens):
        # Find the nearest end of sentence within a range of 0.5 * n and 1.5 * n tokens
        j = min(i + int(1.5 * n), len(tokens))
        while j > i + int(0.5 * n):
            # Decode the tokens and check for full stop or newline
            chunk = tokenizer.decode(tokens[i:j])
            if chunk.endswith(".") or chunk.endswith("\n"):
                break
            j -= 1
        # If no end of sentence found, use n tokens as the chunk size
        if j == i + int(0.5 * n):
            j = min(i + n, len(tokens))
        yield tokens[i:j]
        i = j

def read_file(file_path:str):
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
        
        # segments = split_text(text, chunk_size, chunk_overlap)
        # print(segments)
        # print(text)
        # print(reader.pages)
        # page = reader.pages[0] 
        # content = page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False) 
        text = re.sub("(Page) (\d{1,3}) (of) (\d{1,3})", "", text)
        return text
    else:
        return ''

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def my_python_tool(text: str, file_path: str) -> str:
    try:
        library_df = pd.read_csv(file_path).reset_index()
        library_df.columns = ["filepath", "embedding"]
        library_df["embedding"] = library_df["embedding"].apply(ast.literal_eval)
        
        strings = strings_ranked_by_relatedness(text, library_df, top_n=1)

        fileText = read_file(file_path=strings[0])

        tokenizer = tiktoken.get_encoding("cl100k_base")

        chunks = create_chunks(fileText, 1500, tokenizer)
        text_chunks = [tokenizer.decode(chunk) for chunk in chunks]
    except Exception as e:
        text_chunks = ''
    
    return text_chunks
