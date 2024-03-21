import os
from typing import Union

from promptflow import tool
from promptflow.connections import AzureOpenAIConnection, OpenAIConnection


@tool
def setup_env(connection: Union[AzureOpenAIConnection, OpenAIConnection]):
    config = {
        "EMBEDDING_MODEL_DEPLOYMENT_NAME":"text-embedding-ada-002",
        "CHAT_MODEL_DEPLOYMENT_NAME":"gpt-3.5-turbo",
        "PROMPT_TOKEN_LIMIT":3000,
        "MAX_COMPLETION_TOKENS":1024,
        "VERBOSE":1,
        "CHUNK_SIZE":1024,
        "CHUNK_OVERLAP":64
    }
    if not connection:
        return

    if isinstance(connection, AzureOpenAIConnection):
        os.environ["OPENAI_API_TYPE"] = "azure"
        os.environ["OPENAI_API_BASE"] = connection.api_base
        os.environ["OPENAI_API_KEY"] = connection.api_key
        os.environ["OPENAI_API_VERSION"] = connection.api_version

    if isinstance(connection, OpenAIConnection):
        os.environ["OPENAI_API_KEY"] = connection.api_key
        if connection.organization is not None:
            os.environ["OPENAI_ORG_ID"] = connection.organization

    for key in config:
        os.environ[key] = str(config[key])

    return "Ready"
