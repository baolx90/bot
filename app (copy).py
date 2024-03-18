from flask import Flask, render_template, request, jsonify , url_for , redirect
from werkzeug.utils import secure_filename
import os
from ast import literal_eval
import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine

from openai import OpenAI

client = OpenAI()
OpenAI.api_key = os.environ.get("OPENAI_API_KEY")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.environ.get("UPLOAD_FOLDER")

message_wellcome = "Bao test ok, You are a helpful assistant."
chat_history = [
    {"role": "system", "content": message_wellcome},
]

def get_embedding(text, model="text-embedding-ada-002"):
    return client.embeddings.create(input = [text], model=model).data[0].embedding

def create_context(
    question, df, max_len=1800, size="ada"
):
    """
    Create a context for a question by finding the most similar context from the dataframe
    """

    # Get the embeddings for the question
    # q_embeddings = openai.embeddings.create(input=question, model='text-embedding-ada-002')['data'][0]['embedding']
    q_embeddings = get_embedding(question)

    # Get the distances from the embeddings
    df["distances"] = df["embeddings"].apply(lambda x: cosine(q_embeddings, x))

    returns = []
    cur_len = 0

    # Sort by distance and add the text to the context until the context is too long
    for i, row in df.sort_values('distances', ascending=True).iterrows():
        
        # Add the length of the text to the current length
        cur_len += row['n_tokens'] + 4
        
        # If the context is too long, break
        if cur_len > max_len:
            break
        
        # Else add it to the text that is being returned
        returns.append(row["text"])

    # Return the context
    return "\n\n###\n\n".join(returns)


def answer_question(
    df,
    model="gpt-3.5-turbo-instruct",
    question="Am I allowed to publish model outputs to Twitter, without a human review?",
    max_len=1800,
    size="ada",
    debug=False,
    max_tokens=150,
    stop_sequence=None,
    user="1"
):
    """
    Answer a question based on the most similar context from the dataframe texts
    """
    context = create_context(
        question,
        df,
        max_len=max_len,
        size=size,
    )
    no_answer = "I don't know"
    try:
        # Create a completions using the questin and context
        response = client.completions.create(
            prompt=f"Answer the question based on the context below, and if the question can't be answered based on the context, say {no_answer}\n\nContext: {context}\n\n---\n\nQuestion: {question}\nAnswer:",
            temperature=0,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=stop_sequence,
            model=model,
            user=user
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(e)
        return ""


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", chat_history=chat_history)

@app.route("/chat", methods=["POST"])
def chat():
    content = request.json["message"]
    chat_history.append({"role": "user", "content": content})
    
    df=pd.read_csv('processed1/embeddings.csv', index_col=0)
    df['embeddings'] = df['embeddings'].apply(literal_eval).apply(np.array)

    df.head()
    print(df)
    text_content = answer_question(df, question=content)
    chat_history.append({"role": "assistant", "content": text_content})
    return jsonify(success=True, message=text_content)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
