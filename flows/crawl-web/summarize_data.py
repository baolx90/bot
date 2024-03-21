
import os
from urllib.parse import urlparse
from promptflow import tool
from csv import writer

DATA_URL='.bao'
EMBEDDING_FILE = DATA_URL+"/result.csv"
HTTP_URL_PATTERN = r'^http[s]{0,1}://.+$'

def get_domain(url):
    return urlparse(url).netloc


# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def my_python_tool(url: str, content: str, embedding: str) -> str:
    local_domain = get_domain(url)

    if not os.path.exists(DATA_URL+"/"+local_domain+"/"):
            os.mkdir(DATA_URL+"/" + local_domain + "/")
    
    fileName = url[8:].replace("/", "_") + ".txt"
    filePath = DATA_URL+'/'+local_domain+'/'+fileName
    with open(filePath, "w", encoding="UTF-8") as f:
         f.write(content)
         
    file_reference = [
        fileName[11:-4].replace('-',' ').replace('_', ' ').replace('#update',''),
        filePath,
        embedding,
    ]
    
    with open(EMBEDDING_FILE, "a") as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(file_reference)
        f_object.close()
    return embedding
