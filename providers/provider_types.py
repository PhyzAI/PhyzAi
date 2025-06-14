from typing import Protocol


class ResponseProvider(Protocol):
    async def __call__(self, system_prompt: str, user_prompt: str) -> str:
        ...
