import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Load OpenAI client (replace with your actual key or use .env file)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "sk-your-api-key")



def ask_chatgpt(system_prompt, user_prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[ERROR] Failed to get response from ChatGPT: {e}")
        return "This is a dummy response until your API quota is available."


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
