from ollama import chat

# print(response.message.content)
sysprompt = ""
with open("slm_prompt.txt", "r") as f: #tips for prompt: give examples, keep it simple, and only yes/no answers
    sysprompt += f.read()

remembering_keywords = ["I like", "I want", "I have", "My favorite", "I am"] #simple manual filter for basic questions

def should_remember(prompt: str, memory_context=None) -> bool:
    # Factors to consider: is the information in the prompt something that can be searched on the internet?
    # Does the statement contain the word "I" in it (I have, I like, I want, etc.)
    # Do I know who I am currently talking to?
    # If Phyz knows who they are talking to, remember the data under that user's name, if not, remember under the "guest" username
    # Can use vision/face recognition to identify faces

    if any(word in prompt for word in remembering_keywords): #if they don't pass this, then pass it to the slm
        return True

    prompts = [
        "Ayaan remembers that his cat's name was Mira",
        "His cat's name was Mira",
        "The cat's name was Mira",
        "Ayaan likes robotics",
        "Robotics is cool",
        "What is robotics?"
    ]

    aprompts = [
        "Bahadir used to play soccer on the street with his friends",
        "The world cup is on",
        "The world cup is fun",
        "Ayaan wants Scotland to win the world cup",
        "I like sports"
    ]

    # for prompt in prompts:
    temp = 0.7
    print("\n\n\n\n")
    messages = [{'role': 'system', 'content': sysprompt}, {'role': 'user', 'content': f"\"{prompt}\""}]
    while temp>=0.1:
        response = chat(
            model='smollm2',
            messages=messages,
            options={"temperature": temp}
        )
        response2 = chat(
            model='llama3.1:8b',
            messages=messages,
            options={"temperature": temp}
        )

        print(f"smollm2: {prompt} @ {temp}: {response.message.content}")
        print(f"llama3.1: {prompt} @ {temp}: {response2.message.content}")
        print("\n")
        llm1 = "yes" in response.message.content.lower()
        llm2 = "yes" in response2.message.content.lower()

        if llm1 == llm2 == True: #both yesses
           return True
        elif llm1 == llm2 == False: #both noos or unsure verdict
           return False

        temp-=0.1
        # print(f"prompting again: temperature {temp}")
    return False #unsure verdict

if __name__ == "__main__":
    print(should_remember("Ayaan remembers that his cats name was Mira"))