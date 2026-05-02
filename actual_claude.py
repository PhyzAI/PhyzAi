import os
import sys
import time

from dotenv import load_dotenv

try:
    import anthropic
except ImportError:
    anthropic = None

conversation_history = []  # Global or persistent in-session
MEMORY_DURATION = 120       # Amount of time to remember

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or "your-anthropic-api-key"
client = None
if anthropic is not None:
    client = anthropic.Client(api_key=ANTHROPIC_API_KEY)


def ask_claude(system_prompt, user_prompt, memory_context=None):
    if client is None:
        print("[ERROR] anthropic package is not installed or Claude client could not be created.")
        return "This is a dummy response until the Claude client is available."

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
        system_prompt_to_use = (
            f"{system_prompt}\n\nRelevant memories for this turn:\n{memory_context}"
        )

    messages = [{"role": "system", "content": system_prompt_to_use}] + valid_messages
    messages.append({"role": "user", "content": user_prompt})

    # 4. Store this user input in memory
    conversation_history.append({
        "role": "user",
        "content": user_prompt,
        "timestamp": current_time
    })

    try:
        response = client.chat.completions.create(
            model="claude-3.0",
            messages=messages,
            temperature=0.7,
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
        print(f"[ERROR] Failed to get response from Claude: {e}")
        return "This is a dummy response until your API quota is available."


if __name__ == "__main__":
    from OPTIONS import prompt, prompt_override
    from rich.prompt import Prompt
    from rich import print as rp

    used_prompt = prompt

    if len(sys.argv) > 1 and sys.argv[1] == "override":
        rp("[yellow]override prompt[/]")
        used_prompt = prompt_override

    try:
        while True:
            query = Prompt.ask("[green]user[/] ")
            rp(f"[blue]agent[/]: ", end='', flush=True)
            resp = ask_claude(used_prompt, query)
            rp(f"{resp}")
    except KeyboardInterrupt:
        rp(f"[red] quitting[/]")
        pass
    except EOFError:
        rp(f"[red]EOF quitting[/]")
