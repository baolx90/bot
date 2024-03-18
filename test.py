import pandas as pd
import tiktoken
from utils.crawl import summarize_url,crawl
import os
from openai import OpenAI
from ast import literal_eval
import numpy as np
from scipy.spatial.distance import cosine
from utils.dataframe import create_context
from utils.openai import summarize_text

# embedding_model = "text-embedding-3-small"
# embedding_encoding = "cl100k_base"
# max_tokens = 8000  # the maximum for text-embedding-3-small is 8191

# # load & inspect dataset
# input_datapath = "data/scraped.csv"  # to save space, we provide a pre-filtered dataset
# df = pd.read_csv(input_datapath, index_col=0)
# df = df[["fname", "text"]]
# df = df.dropna()
# df["combined"] = (
#     "Title: " + df.fname.str.strip() + "; Content: " + df.text.str.strip()
# )
# df.head()

# top_n = 1000
# encoding = tiktoken.get_encoding(embedding_encoding)

# # omit reviews that are too long to embed
# df["n_tokens"] = df.text.apply(lambda x: len(encoding.encode(x)))
# df = df[df.n_tokens <= max_tokens].tail(top_n)
# a = len(df)

# print(a)

# df["embedding"] = df.text.apply(lambda x: get_embedding(x, model=embedding_model))
# df.to_csv("data/fine_food_reviews_with_embeddings_1k.csv")

# a = get_embedding("hi", model=embedding_model)
# print(a)

max_len=1800
max_tokens=150
no_answer = "I don't know"
model="gpt-3.5-turbo-instruct"

# client = OpenAI()
# OpenAI.api_key = os.environ.get("OPENAI_API_KEY")

# def answer_question(question):
#     q_embeddings = get_embedding(question)
#     df=pd.read_csv('processed/zopi.crisp.help.csv', index_col=0)
#     df['embeddings'] = df['embeddings'].apply(literal_eval).apply(np.array)
#     df["distances"] = df["embeddings"].apply(lambda x: cosine(q_embeddings, x))

#     context = create_context(
#         question,
#         df,
#         max_len=max_len
#     )
#     try:
#         # Create a completions using the questin and context
#         response = client.completions.create(
#             model=model,
#             prompt=f"Context: {context}\n\n---\n\nQuestion: {question}\nAnswer:",
#             temperature=0,
#             max_tokens=max_tokens,
#         )
#         print(response)
#         return response.choices[0].text.strip()
#     except Exception as e:
#         print(e)
#         return ""
    # text_content = answer_question(df, question=question)
    # df.head()

from urllib.request import Request, urlopen
import pandas as pd
from pypdf import PdfReader
import re

if __name__ == "__main__":
    # url = 'https://firegroup.io/about-us/'
    # url = 'https://zopi.crisp.help/en/'
    url = 'https://zopi.crisp.help/en/article/what-is-zopi-14hq2og/'
    # url = 'https://wonderchat.io/'
    # url = 'https://zopi.crisp.help/en/article/how-to-set-pricing-rules-and-assign-cent-wregvi/'
    # summarize_url(url)

    # req = Request(
    #     url=url, 
    #     headers={'User-Agent': 'Mozilla/5.0'}
    # )
    # webpage = urlopen(req).read()
    # print(webpage)
    # crawl(url)
    question = 'what is zopi ?'
    text_content = summarize_text(text=question)
    print(text_content)

    question = 'how to install ?'
    text_content = summarize_text(text=question)
    print(text_content)
    # answer_question('what is zopi ?')
    # answer_question('who is lâm xuân bảo ?')

    # filePath = "processed/embeddings.csv"
    # df=pd.read_csv(filePath, index_col=0)
    # new_row = {'content': 'John', 'n_tokens': 35, 'embeddings': 'New York'}
    # df = df._append(new_row, ignore_index=True)
    # print(df)
    # file = 'uploads/One-Click_Import_Products_to_your_Zopi___Zopi_Help_Desk.pdf'
    # reader = PdfReader(file) 
    # text = "" 
    # for page in reader.pages: 
    #     text+=page.extract_text().strip()
    # print(text) 
    # print(reader.pages)
    # page = reader.pages[0] 
    # content = page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False) 
    # # content= re.sub("(Page) (\d{1,3}) (of) (\d{1,3})", "", content)
    # print(content)

