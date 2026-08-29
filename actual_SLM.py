from flask.cli import load_dotenv
from ollama import chat
import os

from openai import OpenAI

load_dotenv()
from memory_db import MemoryDB

# print(response.message.content)
sysprompt = ""
with open("slm_prompt.txt", "r") as f: #tips for prompt: give examples, keep it simple, and only yes/no answers
    sysprompt += f.read()
remembering_keywords = ["I like", "I want", "I have", "My favorite", "I am"] #simple manual filter for basic questions

def should_remember(prompt: str, memory: MemoryDB) -> bool:
    print("Evaluating if Phyz should remember")
    """"
    We did some work with the SLMs and found them to not be too reliable, so the code is commented below.
    The functioning code here works like this. Everytime Phyz is asked a question, this runs in a new thread, querrying should it remember?
    1st, Phyz checks does a related memory already exist? Generating embeddings and checking the cosine similarity of the text against phyz's database (will be hard to traverse as phyz gains more memories)
    2nd, We manually check if there are any immediate keywords used that could indicate to phyz its worth remembering
    3rd, The llm takes a system prompt and the user prompt to evaluate whether it should remember

    returns true or false for if it should remember
    """

    # Factors to consider: is the information in the prompt something that can be searched on the internet?, also, do I already know this?
    # Does the statement contain the word "I" in it (I have, I like, I want, etc.)
    # Do I know who I am currently talking to?
    # If Phyz knows who they are talking to, remember the data under that user's name, if not, remember under the "guest" username
    # Can use vision/face recognition to identify faces

    exists = memory.does_memory_exist(prompt, accepted_similarity=0.6)
    if exists: return False

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "sk-your-api-key")

    if any(word in prompt for word in remembering_keywords): #if they don't pass this, then pass it to the slm
        return True

    messages = [{'role': 'system', 'content': sysprompt}, {'role': 'user', 'content': f"\"{prompt}\""}]

    response3 = client.chat.completions.create(
        messages=messages,
        model="gpt-4o",
        temperature=0.7,
    )

    print(f"gpt-4o: {prompt} @ {0.7}: {response3.choices[0].message.content}")
    llm3 = "yes" in response3.choices[0].message.content.lower()
    return llm3


# def should_remember_tests(prompt: str) -> bool:
#
#     client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "sk-your-api-key")
#
#     # prompts = [ #just for testing
#     #     "Sam remembers that his dog name was Bob",
#     #     "LeAnn remembers that her dog's name was John",
#     #     "His dog's name was Bob",
#     #     "The dog's name was Bob",
#     #     "George likes robotics",
#     #     "Robotics is cool",
#     #     "What is robotics?"
#     # ]
#     #
#     # aprompts = [
#     #     "Bahadir used to play soccer on the street with his friends",
#     #     "The world cup is on",
#     #     "The world cup is fun",
#     #     "Ayaan wants Scotland to win the world cup",
#     #     "I like sports"
#     # ]
#
#     # for prompt in prompts:
#     temp = 0.7
#     print("\n\n\n\n")
#     messages = [{'role': 'system', 'content': sysprompt}, {'role': 'user', 'content': f"\"{prompt}\""}]
#     while temp>=0.1:
#         response = chat(
#             model='smollm2',
#             messages=messages,
#             options={"temperature": temp}
#         )
#         response2 = chat(
#             model='llama3.1:8b',
#             messages=messages,
#             options={"temperature": temp}
#         )
#         response3 = client.chat.completions.create(
#             messages=messages,
#             model="gpt-4o",
#             temperature=temp,
#         )
#
#         print(f"smollm2: {prompt} @ {temp}: {response.message.content}")
#         print(f"llama3.1: {prompt} @ {temp}: {response2.message.content}")
#         print(f"gpt-4o: {prompt} @ {temp}: {response3.choices[0].message.content}")
#
#         print("\n")
#         slm1 = "yes" in response.message.content.lower()
#         slm2 = "yes" in response2.message.content.lower()
#         llm3 = "yes" in response3.choices[0].message.content.lower()
#
#         if slm1 == slm2 == llm3 == True: #both yesses
#            # return True
#             break
#         elif slm1 == slm2 == llm3 == False: #both noos or unsure verdict
#             # return False
#            break
#
#         temp-=0.1
#         # print(f"prompting again: temperature {temp}")
#     # return False #unsure verdict

if __name__ == "__main__":
    print(should_remember("Ayaan remembers that his cats name was Mira"))