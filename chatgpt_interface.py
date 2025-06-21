import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "sk-your-api-key")

def ask_chatgpt(prompt, user_input):
    print(f"[DEBUG] Prompt: {prompt}\nUser input: {user_input}")
    return "This is a dummy response until your API quota is available."


# def ask_chatgpt(prompt, user_input):
#     messages = [
#         {"role": "system", "content": prompt},
#         {"role": "user", "content": user_input}
#     ]
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=messages
#     )
#     return response.choices[0].message.content.strip()
