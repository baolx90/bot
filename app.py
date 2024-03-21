from promptflow import load_flow
import json

# Please protect the entry point by using `if __name__ == '__main__':`,
# otherwise it would cause unintended side effect when promptflow spawn worker processes.
# Ref: https://docs.python.org/3/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":

    text = "what is zopi?"
    flow_path = "flows/chat"
    flow_inputs = {
        "question": text
    }

    flow_func = load_flow(flow_path)
    flow_result = flow_func(**flow_inputs)
    print(f"Flow function result: {flow_result}")