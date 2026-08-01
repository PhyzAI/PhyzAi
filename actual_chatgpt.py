import os
import sys
import time

from dotenv import load_dotenv
from openai import OpenAI
import actual_SLM
conversation_history = []  # Global or persistent in-session
MEMORY_DURATION = 120       # Amount of time to remember


load_dotenv()

# Load OpenAI client (replace with your actual key or use .env file)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "sk-your-api-key")



def ask_chatgpt(system_prompt, user_prompt, memory_context=None):
    current_time = time.time()

    # 1. Filter for only recent messages
    valid_messages = [
        {"role": entry["role"], "content": entry["content"]}
        for entry in conversation_history
        if current_time - entry["timestamp"] <= MEMORY_DURATION
    ]

    # 2. Prune old entries from history
    conversation_history[:] = [
        entry for entry in conversation_history
        if current_time - entry["timestamp"] <= MEMORY_DURATION
    ]

    # 3. Add system and current user prompt
    system_prompt_to_use = system_prompt
    if memory_context:
        # Add the most relevant stored memories to the system prompt.
        system_prompt_to_use = (
            f"{system_prompt}\n\nRelevant memories for this turn:\n{memory_context}"
        )

    messages = [{"role": "system", "content": system_prompt_to_use}] + valid_messages
    messages.append({"role": "user", "content": user_prompt})
    
    #print(messages) # DEBUG

    # 4. Store this user input in memory
    conversation_history.append({
        "role": "user",
        "content": user_prompt,
        "timestamp": current_time
    })

    try:
        response = client.chat.completions.create(
            messages=messages,
            model="gpt-4o",
            temperature=0.7,
            # stream=True,
        )

        reply = response.choices[0].message.content.strip()

        # 5. Store assistant response in memory
        conversation_history.append({
            "role": "assistant",
            "content": reply,
            "timestamp": current_time
        })

        return reply

    except Exception as e:
        print(f"[ERROR] Failed to get response from ChatGPT: {e}")
        return "This is a dummy response until your API quota is available." #TODO: Respond with an apology prefab



if __name__ == "__main__":
    # Testing chat client
    from OPTIONS import prompt, prompt_override
    from rich.prompt import Prompt
    from rich import print as rp

    used_prompt = prompt

    if len(sys.argv) > 1 and sys.argv[1] == "override":
        rp("[yellow]override prompt[/]")
        used_prompt = prompt_override

    try:
        while 1:
            query = Prompt.ask("[green]user[/] ")
            rp(f"[blue]agent[/]: ", end='', flush=True)
            resp = ask_chatgpt(used_prompt, query)
            rp(f"{resp}")
    except KeyboardInterrupt:
        rp(f"[red] quitting[/]")
        pass
    except EOFError:
        rp(f"[red]EOF quitting[/]")
