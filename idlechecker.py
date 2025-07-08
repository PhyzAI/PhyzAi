import time
import random


IDLE_THRESHOLD = 30  # seconds

# Load lines once
with open("idle_lines.txt", "r", encoding="utf-8") as f:
    idle_lines = [line.strip() for line in f if line.strip()]

def check_idle_and_prompt_chatgpt(last_interaction_time_ref):
    """Check idle time, and if idle, return a fun prompt string."""
    global IDLE_THRESHOLD
    current_time = time.time()
    if current_time - last_interaction_time_ref > IDLE_THRESHOLD:
        if idle_lines:
            response = random.choice(idle_lines)
            print(f"PHYZAI (idle): {response}")
            last_interaction_time_ref = current_time
            IDLE_THRESHOLD = random.randint(15,45)
            return response  # Return the string to optionally use elsewhere
    return None
