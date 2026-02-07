import os
import re
from openai import OpenAI
import chromadb
from chromadb.config import Settings

# -------------------------------
# 1) Initialize OpenAI + Chroma
# -------------------------------
client = OpenAI()

CHROMA_DIR = "./chroma_storage"
os.makedirs(CHROMA_DIR, exist_ok=True)

chroma_client = chromadb.Client(
    Settings(
        persist_directory=CHROMA_DIR,
        anonymized_telemetry=False
    )
)

collection = chroma_client.get_or_create_collection(
    name="knowledge_base",
    metadata={"hnsw:space": "cosine"}  # cosine similarity
)


def _maybe_persist(client):
    """Call client.persist() if the installed chromadb exposes it.

    Newer chromadb versions don't provide a public persist() method on the
    Client object (persistence is handled automatically when a
    persist_directory is configured). This helper keeps the code compatible
    with older and newer chromadb releases.
    """
    try:
        persist_fn = getattr(client, "persist", None)
        if callable(persist_fn):
            persist_fn()
    except Exception:
        # If anything goes wrong, don't crash the application for this
        # non-critical operation.
        pass


# -------------------------------
# 2) Detect memory requests
# -------------------------------
memory_patterns = [
    r"remember that (.*)",
    r"remember this[: ](.*)",
    r"save this[: ](.*)",
    r"store this[: ](.*)",
    r"add this[: ](.*)",
    r"please remember (.*)",
    r"put this in memory[: ](.*)",
    r"add to knowledge base[: ](.*)",
]

def is_memory_request(text: str) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in memory_patterns)

def extract_memory_content(text: str) -> str:
    for p in memory_patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


# -------------------------------
# 3) Add item to persistent RAG
# -------------------------------
def add_memory_item(text: str):
    print(f"\n📥 Storing to memory: “{text}”")

    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    ).data[0].embedding

    item_id = f"mem_{collection.count() + 1}"

    collection.add(
        ids=[item_id],
        documents=[text],
        embeddings=[embedding]
    )

    # Persist if the client has that method (older chromadb versions).
    _maybe_persist(chroma_client)

    print("✅ Memory saved!\n")


# -------------------------------
# 4) RAG Query
# -------------------------------
def rag_query(question: str, top_k: int = 3) -> str:

    # 1. Embed question
    q_embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    ).data[0].embedding

    # 2. Retrieve nearest docs
    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=top_k
    )

    retrieved_docs = results["documents"][0]
    context = "\n\n".join(retrieved_docs)

    # 3. LLM answer using the retrieved RAG context
    prompt = f"""
You are Mira, a helpful assistant.
Use the provided context to answer the question accurately.

Context:
{context}

Question:
{question}

Answer:
    """

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# -------------------------------
# 5) Interactive Loop
# -------------------------------
if __name__ == "__main__":
    print("\n✨ Mira RAG Memory System Ready")
    print("• Ask anything normally = RAG query")
    print("• Say 'remember that ...' to store new memory\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            _maybe_persist(chroma_client)
            print("\n🧠 Database persisted. Goodbye!")
            break

        # --- Memory handling ---
        if is_memory_request(user_input):
            content = extract_memory_content(user_input)
            if content:
                add_memory_item(content)
                print("Mira: Got it — I’ll remember that.\n")
            else:
                print("Mira: I think you meant to store something, but I couldn’t parse it.\n")
            continue

        # --- Normal RAG query ---
        answer = rag_query(user_input)
        print(f"Mira: {answer}\n")
