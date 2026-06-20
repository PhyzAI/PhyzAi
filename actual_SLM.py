from ollama import chat
from sympy.physics.units import temperature

# print(response.message.content)
sysprompt = ""
with open("slm_prompt.txt", "r") as f:
    sysprompt += f.read()
messages = [{'role': 'system', 'content': sysprompt}]

remembering_keywords = ["I like", "I want", "I have", "My favorite", "I am"] #simple manual filter for basic questions

def should_remember(prompt: str, memory_context=None) -> bool:
    # Factors to consider: is the information in the prompt something that can be searched on the internet?
    # Does the statement contain the word "I" in it (I have, I like, I want, etc.)
    # Do I know who I am currently talking to?
    # If Phyz knows who they are talking to, remember the data under that user's name, if not, remember under the "guest" username
    # Can use vision/face recognition to identify faces

    if any(word in prompt for word in remembering_keywords): #if they don't pass this, then pass it to the slm
        return True


    temp = 0.7
    messages.append({'role': 'user', 'content': f"\"{prompt}\""})
    while True:
        response = chat(
            model='smollm2',
            messages=messages,
            options={temperature: temp}
        )

        response2 = chat(
            model='llama3.1:8b',
            messages=messages,
            options={temperature: temp}
        )

        print(response.message.content)
        print(response2.message.content)

        llm1 = "yes" in response.message.content.lower()
        llm2 = "yes" in response2.message.content.lower()

        if llm1 == llm2: #both yesses
           return True

        temp-=0.1
        print(f"prompting again: temperature {temp}")


if __name__ == "__main__":
    print(should_remember("Ayaan remembers that his cats name was Mira"))