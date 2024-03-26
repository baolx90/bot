
import os
import pandas as pd
from promptflow import tool
from csv import writer

DATA_URL='processed'
EMBEDDING_FILE = DATA_URL+"/result.csv"

# Create a directory to store the text files
if not os.path.exists(DATA_URL+"/"):
    os.mkdir(DATA_URL+"/")

if not os.path.exists(EMBEDDING_FILE):
    # If the directory doesn't exist, create it and any necessary intermediate directories
    df = pd.DataFrame(list())
    df.to_csv(EMBEDDING_FILE)

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def my_python_tool(file_path: str, embedding: list) -> list:
    
    file_reference = [
        file_path,
        embedding,
    ]
    
    with open(EMBEDDING_FILE, "a") as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(file_reference)
        f_object.close()
        
    return file_path
