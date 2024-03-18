from utils.embeddings import get_embedding
from scipy.spatial.distance import cosine

"""
    Create a context for a question by finding the most similar context from the dataframe
"""
def create_context(
    question, df, max_len=1800, size="ada"
):

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
        returns.append(row["content"])

    # Return the context
    return "\n\n###\n\n".join(returns)