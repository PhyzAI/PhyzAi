import asyncio
import concurrent.futures
import os
import time
from typing import NoReturn

import openai
from rich import print as rp


def report_missing_api_key() -> NoReturn:
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
    with concurrent.futures.ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, _query, "gpt-4o", system_prompt, user_prompt)


async def query_35_turbo(system_prompt: str, user_prompt: str) -> str:
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, _query, "gpt-3.5-turbo", system_prompt, user_prompt)
