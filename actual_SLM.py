from ollama import chat
from sympy.physics.units import temperature

# print(response.message.content)
sysprompt = ""
with open("slm_prompt.txt", "r") as f:
    sysprompt += f.read()
messages = [{'role': 'system', 'content': sysprompt}]

def should_remember(prompt: str, memory_context=None) -> bool:
    # Factors to consider: is the information in the prompt something that can be searched on the internet?
    # Does the statement contain the word "I" in it (I have, I like, I want, etc.)
    # Do I know who I am currently talking to?
    # If Phyz knows who they are talking to, remember the data under that user's name, if not, remember under the "guest" username
    # Can use vision/face recognition to identify faces

    messages.append({'role': 'user', 'content': f"\"{prompt}\""})
    response = chat(
        model='smollm2',
        messages=messages,
        options={temperature: 0.5}
    )

    response2 = chat(
        model='llama3.1:8b',
        messages=messages,
        options={temperature: 0.5}
    )

    print(response.message.content)
    print(response2.message.content)
    # return (
    #     "yes" in response.message.content.lower()
    # )


if __name__ == "__main__":
    print(should_remember("I like apples"))