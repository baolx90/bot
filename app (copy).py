from promptflow import load_flow
import json
import pandas as pd

def flow_chat():
    text = "what is zopi?"
    flow_path = "flows/chat"
    flow_inputs = {
        "question": text
    }

    flow_func = load_flow(flow_path)
    flow_result = flow_func(**flow_inputs)
    print(f"Flow function result: {flow_result}")

def flow_crawl():
    flow_path = "flows/crawl-web"
    flow_inputs = {
        "url": "https://zopi.crisp.help/en/article/what-is-zopi-14hq2og/"
    }
    flow_func = load_flow(flow_path)
    flow_result = flow_func(**flow_inputs)

# Please protect the entry point by using `if __name__ == '__main__':`,
# otherwise it would cause unintended side effect when promptflow spawn worker processes.
# Ref: https://docs.python.org/3/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    flow_crawl()
    # filepath="flows/crawl-web/.bao/result.csv"
    # library_df = pd.read_csv(filepath).reset_index()    
    # library_df.columns = ["url","content", "embedding"]
    # print(library_df)