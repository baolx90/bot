
import ast
import pandas as pd
from promptflow import tool
import tiktoken
from scipy.spatial.distance import cosine
from scipy import spatial
import os

FILE_PATH=".runs/result.csv"

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
# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def my_python_tool(text: str) -> str:
    library_df = pd.read_csv(debug_file(FILE_PATH)).reset_index()
    library_df.columns = ["title","filepath", "embedding"]
    library_df["embedding"] = library_df["embedding"].apply(ast.literal_eval)
    
    strings = strings_ranked_by_relatedness(text, library_df, top_n=1)

    file = open(debug_file(strings[0]), "r", encoding="UTF-8")
    fileText = file.read()

    print(fileText)

    tokenizer = tiktoken.get_encoding("cl100k_base")

    chunks = create_chunks(fileText, 1500, tokenizer)
    text_chunks = [tokenizer.decode(chunk) for chunk in chunks]
    return text_chunks
