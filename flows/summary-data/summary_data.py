
import os
import pandas as pd
from promptflow import tool
from csv import writer

DATA_URL='processed'
EMBEDDING_FILE = DATA_URL+"/result.pkl"

# Create a directory to store the text files
if not os.path.exists(DATA_URL+"/"):
    os.mkdir(DATA_URL+"/")

if not os.path.exists(EMBEDDING_FILE):
    # If the directory doesn't exist, create it and any necessary intermediate directories
    pd.DataFrame(list()).to_pickle(EMBEDDING_FILE)

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def my_python_tool(file_path: str, embedding: list) -> list:
    
    file_reference = [
        file_path,
        str(embedding),
    ]
    
    data = pd.concat([
                pd.read_pickle(filepath_or_buffer=EMBEDDING_FILE), 
                pd.DataFrame([file_reference])]
           ).reset_index(drop=True)
    data.to_pickle(EMBEDDING_FILE)
        
    return file_path
