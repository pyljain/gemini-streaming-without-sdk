import subprocess
import aiohttp
import asyncio
import json
import os

def get_token():
    # Get token by running command gcloud auth print-access-token
    output = subprocess.check_output(["gcloud", "auth", "print-access-token"]).decode().strip()
    return output

async def make_api_call(token, url, payload):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }) as response:
            async for event in response.content.iter_any():
                decoded_event = event.decode('utf-8')
                yield decoded_event

async def main(token):
    project = os.get_env('GCP_PROJECT')
    url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project}/locations/us-central1/publishers/google/models/gemini-1.5-pro:streamGenerateContent"
    payload = {
        "contents": {
            "role": "user",
            "parts": [
                {
                    "text": "What's a good name for a flower shop that specializes in selling bouquets of dried flowers?"
                }
            ]
        }
    }
    async for event in make_api_call(token, url, payload):
        if event[0] == ',':
            event = event[1:]
        if event[0] == '[':
            event = event[1:]
        if event[-1] == ']':
            event = event[:-1]
        e = json.loads(event)
        print(e['candidates'][0]['content']['parts'][0]['text'], end='')

if __name__ == "__main__":
    token = get_token()
    asyncio.run(main(token))