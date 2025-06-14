import asyncio
import os
import time
from typing import Never

import openai
from rich import print as rp


def report_missing_api_key() -> Never:
    rp('[red][bold]Error: [/] No OpenAI api key provided; set the OPENAI_API_KEY environment variable.')
    raise ImportError("missing API key")


openai.api_key = os.environ.get("OPENAI_API_KEY") or report_missing_api_key()


def _query(model: str, system_prompt: str, user_prompt: str) -> str:
    rp(f'[bright_blue]Asking ChatGPT model: {model}[/]')
    start = time.perf_counter()
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    end = time.perf_counter()
    rp(f'[bright_blue]Total request duration: {end - start:.3f}s[/]')
    return resp['choices'][0]['message']['content']


async def query_4o(system_prompt: str, user_prompt: str) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _query, "gpt-4o", system_prompt, user_prompt)

query_4o.name_spoken = "ChatGPT 4 o"
query_4o.name = "ChatGPT 4o"


async def query_35_turbo(system_prompt: str, user_prompt: str) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _query, "gpt-3.5-turbo", system_prompt, user_prompt)

query_35_turbo.name_spoken = "ChatGPT 3.5 turbo"
query_35_turbo.name = "ChatGPT 3.5 turbo"
