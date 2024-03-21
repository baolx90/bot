# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import bs4
from promptflow import tool
import requests
import pandas as pd

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
DATA_URL='.runs'
EMBEDDING_FILE = DATA_URL+"/result.csv"

# Create a directory to store the text files
if not os.path.exists(DATA_URL+"/"):
    os.mkdir(DATA_URL+"/")

if not os.path.exists(EMBEDDING_FILE):
    # If the directory doesn't exist, create it and any necessary intermediate directories
    df = pd.DataFrame(list())
    df.to_csv(EMBEDDING_FILE)

@tool
def my_python_tool(url: str) -> str:
    # Send a request to the URL
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 Edg/113.0.1774.35',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive',
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = bs4.BeautifulSoup(response.text, "html.parser")
            soup.prettify()
            return soup.get_text()
        else:
            msg = (
                f"Get url failed with status code {response.status_code}.\nURL: {url}\nResponse: "
                f"{response.text[:100]}"
            )
            print(msg)
            return "No available content"
    except Exception as e:
        print("Get url failed with error: {}".format(e))
        return "No available content"