from typing import List, Optional
from scipy import spatial
from openai import OpenAI
import pandas as pd
import os
from scipy.spatial.distance import cosine
from utils.dataframe import create_context
from tenacity import retry, wait_random_exponential, stop_after_attempt
import tiktoken
import ast

model="gpt-3.5-turbo-instruct"
GPT_MODEL = "gpt-3.5-turbo-instruct"
EMBEDDING_MODEL = "text-embedding-3-small"
FILE_PATH="processed/embeddings.csv"
MAX_TOKEN=150
NO_ANSWER = "I don't know"

client = OpenAI()
OpenAI.api_key = os.environ.get("OPENAI_API_KEY")

@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def embedding_request(text, model=EMBEDDING_MODEL, **kwargs):
    text = text.replace("\n", " ")
    response = client.embeddings.create(input=[text], model=model, **kwargs)
    return response.data[0].embedding

def strings_ranked_by_relatedness(
    query: str,
    df: pd.DataFrame,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 100,
) -> list[str]:
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    query_embedding = embedding_request(query)
    strings_and_relatednesses = [
        (row["filepath"], relatedness_fn(query_embedding, row["embedding"]))
        for i, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)
    return strings[:top_n]

# Split a text into smaller chunks of size n, preferably ending at the end of a sentence
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

def summarize_text(text, filepath=FILE_PATH):

    # If the library is empty (no searches have been performed yet), we perform one and download the results
    library_df = pd.read_csv(filepath).reset_index()
    library_df.columns = ["title","filepath", "embedding"]
    library_df["embedding"] = library_df["embedding"].apply(ast.literal_eval)
    print(library_df)
    
    strings = strings_ranked_by_relatedness(text, library_df, top_n=1)

    file = open(strings[0], "r", encoding="UTF-8")
    fileText = file.read()

    tokenizer = tiktoken.get_encoding("cl100k_base")

    chunks = create_chunks(fileText, 1500, tokenizer)
    text_chunks = [tokenizer.decode(chunk) for chunk in chunks]

    prompt=f"Answer the question based on the context below, and if the question can't be answered based on the context, say {NO_ANSWER}\n\nContext: {text_chunks}\n\n---\n\nQuestion: {text}\nAnswer:",
    try:
        response = client.completions.create(
            model=GPT_MODEL,
            prompt=prompt,
            temperature=0,
            max_tokens=MAX_TOKEN,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return e
