
import os
import PyPDF2
from promptflow import tool


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

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def my_python_tool(file_path: str) -> str:
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
          
          return split_text(text, chunk_size, chunk_overlap)
