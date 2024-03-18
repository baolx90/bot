"""
    python services/embed.py \
        --requests_url https://zopi.crisp.help/en/
"""
import argparse
import asyncio

openai_url='https://api.openai.com/v1/embeddings'
save_filepath='examples/data/example_requests_to_parallel_process_results.jsonl' 
token_encoding_name='cl100k_base'

max_requests_per_minute=1500
max_tokens_per_minute=6250000
max_attempts=5
logging_level=20

async def process_requests():
    print('here')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--requests_url")
    args = parser.parse_args()
    asyncio.run(
        process_requests(
            requests_filepath=args.requests_filepath,
            save_filepath=args.save_filepath,
            request_url=args.request_url,
            api_key=args.api_key,
            max_requests_per_minute=float(args.max_requests_per_minute),
            max_tokens_per_minute=float(args.max_tokens_per_minute),
            token_encoding_name=args.token_encoding_name,
            max_attempts=int(args.max_attempts),
            logging_level=int(args.logging_level),
        )
    )
    print(args)