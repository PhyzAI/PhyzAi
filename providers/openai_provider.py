import asyncio
import os
import time
from typing import NoReturn

import openai
from rich import print as rp


def report_missing_api_key() -> NoReturn:
    rp('[red][bold]Error: [/] No OpenAI api key provided; set the OPENAI_API_KEY environment variable.')
    raise ImportError("missing API key")


openai.api_key = os.environ.get("OPENAI_API_KEY") or report_missing_api_key()


def _query_4o(system_prompt: str, user_prompt: str) -> str:
    start = time.perf_counter()
    resp = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    end = time.perf_counter()
    rp(f'[bright_blue]Total request duration: {end - start}s[/]')
    return resp['choices'][0]['message']['content']


async def query_4o(system_prompt: str, user_prompt: str) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _query_4o, system_prompt, user_prompt)
