from openai import OpenAI
import os

client = OpenAI()
OpenAI.api_key = os.environ.get("OPENAI_API_KEY")

client.fine_tuning.jobs.create(
  training_file="file-abc123",
  model="gpt-3.5-turbo"
)