import os

from openai import OpenAI

# Load OpenAI client (replace with your actual key or use .env file)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "sk-your-api-key")


def ask_chatgpt(prompt, user_input):
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_input}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # or "gpt-4"
        messages=messages
    )
    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    # Testing chat client
    from OPTIONS import prompt
    from rich.prompt import Prompt
    from rich import print as rp
    try:
        while 1:
            query = Prompt.ask("[green]user[/] ")
            rp(f"[blue]agent[/]: ", end='', flush=True)
            resp = ask_chatgpt(prompt, query)
            rp(f"{resp}")
    except KeyboardInterrupt:
        rp(f"[red] quitting[/]")
        pass
    except EOFError:
        rp(f"[red]EOF quitting[/]")
