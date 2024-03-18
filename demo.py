import os
import ast
import pandas as pd
import tiktoken
from csv import writer
from IPython.display import display, Markdown, Latex
from openai import OpenAI
from PyPDF2 import PdfReader
from scipy import spatial
from tenacity import retry, wait_random_exponential, stop_after_attempt

GPT_MODEL = "gpt-3.5-turbo-instruct"
# GPT_MODEL = "gpt-3.5-turbo-0613"
EMBEDDING_MODEL = "text-embedding-ada-002"
client = OpenAI()
OpenAI.api_key = os.environ.get("OPENAI_API_KEY")

directory = './bao/papers'

# Check if the directory already exists
if not os.path.exists(directory):
    # If the directory doesn't exist, create it and any necessary intermediate directories
    os.makedirs(directory)

# Set a directory to store downloaded papers
data_dir = os.path.join(os.curdir, "bao", "papers")
paper_dir_filepath = "./bao/data.csv"

# Check if the directory already exists
if not os.path.exists(paper_dir_filepath):
    # If the directory doesn't exist, create it and any necessary intermediate directories
    df = pd.DataFrame(list())
    df.to_csv(paper_dir_filepath)

@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def embedding_request(text):
    response = client.embeddings.create(input=text, model=EMBEDDING_MODEL)
    return response

@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def get_articles(library=paper_dir_filepath):
    url = "firegroup.io"
    for file in os.listdir("url-pages/" + url + "/"):
        filePath = "url-pages/" + url + "/" + file
        # Open the file and read the text
        with open(filePath, "r", encoding="UTF-8") as f:
            title = file[11:-4].replace('-',' ').replace('_', ' ').replace('#update','')
            response = embedding_request(text=title)
            file_reference = [
                title,
                filePath,
                response.data[0].embedding,
            ]
            with open(library, "a") as f_object:
                writer_object = writer(f_object)
                writer_object.writerow(file_reference)
                f_object.close()

def strings_ranked_by_relatedness(
    query: str,
    df: pd.DataFrame,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 100,
) -> list[str]:
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    query_embedding_response = embedding_request(query)
    query_embedding = query_embedding_response.data[0].embedding
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

def summarize_text(query):

    # If the library is empty (no searches have been performed yet), we perform one and download the results
    library_df = pd.read_csv(paper_dir_filepath).reset_index()
    if len(library_df) == 0:
        print("No papers searched yet, downloading first.")
        get_articles()
        print("Papers downloaded, continuing")
        library_df = pd.read_csv(paper_dir_filepath).reset_index()
    library_df.columns = ["title","filepath", "embedding"]
    library_df["embedding"] = library_df["embedding"].apply(ast.literal_eval)
    
    strings = strings_ranked_by_relatedness(query, library_df, top_n=1)

    file = open(strings[0], "r", encoding="UTF-8")
    fileText = file.read()

    tokenizer = tiktoken.get_encoding("cl100k_base")

    chunks = create_chunks(fileText, 1500, tokenizer)
    text_chunks = [tokenizer.decode(chunk) for chunk in chunks]
    print(text_chunks)

    no_answer = "I don't know"
    max_tokens=150

    prompt=f"Answer the question based on the context below, and if the question can't be answered based on the context, say {no_answer}\n\nContext: {text_chunks}\n\n---\n\nQuestion: {query}\nAnswer:",
    # prompt = f"Context: {context}\n\n---\n\nQuestion: {question}\nAnswer:"
    try:
        # Create a completions using the questin and context
        response = client.completions.create(
            model=GPT_MODEL,
            prompt=prompt,
            temperature=0,
            max_tokens=max_tokens,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return e

chat_test_response = summarize_text("what is zopi ?")
print(chat_test_response)
a = summarize_text("what is firegroup ?")
print(a)
# get_articles()
# b = summarize_text("what is firegroup ?")
# print(b)