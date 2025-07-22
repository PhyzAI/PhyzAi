import time
import random
from actual_chatgpt import ask_chatgpt


IDLE_THRESHOLD = random.randint(60, 120)

BEHAVIOR_MODES = {
    "joke": 0.2,
    "quiz": 0.1,
    "moderator_poke": 0.3,
    "curious_question": 0.4
    #Science News
}

BEHAVIOR_PROMPTS = {
    "joke": "You are addressing a small crowd. What you say needs to break the ice and get people to engage with you. Say something that breaks the silence that leads into telling a short, funny sometimes science-related joke to get a kid's attention. Keep it quick and silly. try not to end in an odd question.",
    "quiz": "You are addressing a small crowd. What you say needs to break the ice and get people to engage with you. Ask a fun, easy STEM trivia question to engage nearby kids. Only ask one question.",
    "moderator_poke": "You are addressing a small crowd. What you say needs to break the ice and get people to engage with you. Say something playful to poke fun at one of the moderators. Be very light-hearted and funny.",
    "curious_question": "You are addressing a small crowd. What you say needs to break the ice and get people to engage with you. Ask the room a curious STEM-related question to spark conversation. Keep it friendly and thought-provoking."
}

SYSTEM_PROMPT = (
    "You are PhyzAI, an educational robot. You're witty, engaging, and love talking with kids and moderators. "
    "Make your responses fun, smart, and short. try to sound as human like as possible."
    "Make sure to not include any emoji's"
)

#reads out the possibilities of phyz saying different idle actions
def weighted_choice(weight_dict):
    """
    Randomly selects a key from the dictionary based on weights.
    Example input: {"joke": 0.5, "quiz": 0.2, "poke": 0.3}
    """
    total = sum(weight_dict.values())
    r = random.uniform(0, total)
    upto = 0
    for key, weight in weight_dict.items():
        if upto + weight >= r:
            return key
        upto += weight

#gets who has been seen from file to feed idle propmts
def get_seen_mentors(filepath="seen_mentors.txt"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            mentors = [line.strip() for line in f if line.strip()]
        return mentors
    except FileNotFoundError:
        return []


def check_idle_and_prompt_chatgpt(last_interaction_time, last_idle_response_time):
    global IDLE_THRESHOLD
    current_time = time.time()

    if (current_time - last_interaction_time > IDLE_THRESHOLD and
        current_time - last_idle_response_time > IDLE_THRESHOLD):

        behavior = weighted_choice(BEHAVIOR_MODES)
        prompt = BEHAVIOR_PROMPTS[behavior]

        # Inject mentor if needed
        if behavior == "moderator_poke":
            seen = get_seen_mentors()
            if seen:
                chosen_mentor = random.choice(seen)
                prompt = f"Say something playful to poke fun at {chosen_mentor}, one of the moderators. Be very light-hearted and funny."

        response = ask_chatgpt(SYSTEM_PROMPT, prompt)

        if response:
            print(f"PHYZAI (idle-{behavior}): {response}")
            last_idle_response_time = current_time
            IDLE_THRESHOLD = random.randint(15, 45)
            return response, last_idle_response_time

    return None, last_idle_response_time

