import os
import openai

# ChatGPT parameters
SYSTEM_ROLE = "You are a commedian that respond to the conversation with humor to teenagers. \
    Try to keep the response to 2 to 3 sentenses"

class Chat:
    def __init__(self, model="gpt-3.5-turbo") -> None:
        openai.api_key = os.getenv("OPENAI_API_KEY")

        self._model = model

    def respond(self, prompt: str):
        completion = openai.ChatCompletion.create(
            model=self._model,
            messages=[
            {"role": "system", "content": SYSTEM_ROLE},
            {"role": "user", "content": prompt}
            ]
        )

        return completion["choices"][0]["message"]["content"]