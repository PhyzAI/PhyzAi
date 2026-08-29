import json
import os
import time

from flask.cli import load_dotenv
from openai import OpenAI
from torch.distributed._shard.sharding_spec.chunk_sharding_spec_ops import embedding

load_dotenv()

class MemoryDB:
    """Simple on-disk vector memory store backed by OpenAI embeddings."""

    def __init__(self, file_path="data/memory_db.json", embedding_model="text-embedding-3-small"):
        self.file_path = file_path
        self.embedding_model = embedding_model

        self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "sk-your-api-key")

        self.memories = []
        self._load()

    def _load(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.memories = json.load(f)
        except FileNotFoundError:
            self.memories = []
        except Exception:
            # If file is corrupt, start fresh to avoid crashes.
            self.memories = []

    def _save(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _cosine_similarity(vec_a, vec_b):
        # Using pure python to avoid extra dependencies
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = sum(a * a for a in vec_a) ** 0.5
        norm_b = sum(b * b for b in vec_b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def add_memory(self, text: str, metadata: dict | None = None) -> str:
        """Store a new memory item (text + embedding) and persist to disk."""
        print("Adding data to memory")
        # Ensure we only store non-empty strings
        if not text or not text.strip():
            raise ValueError("Memory text must be a non-empty string")

        # Embed the text
        embedding = self._client.embeddings.create(
            model=self.embedding_model,
            input=text,
        ).data[0].embedding

        item_id = f"mem_{len(self.memories) + 1}"
        entry = {
            "id": item_id,
            "text": text,
            "embedding": embedding,
            "timestamp": int(time.time()),
        }
        if metadata:
            entry["metadata"] = metadata

        self.memories.append(entry)
        self._save()
        return item_id

    def filter_by_metadata(self, key: str, value: str): #metadata filter
        """Filter memories based on the provided criteria."""
        filtered_memories = []
        for entry in self.memories:
            try: #try to filter by the selected key, just ignore if it doesn't exist
                if entry["metadata"][key] == value:
                    filtered_memories.append(entry)
            except KeyError:
                pass
        return filtered_memories


    def query(self, query_text: str, top_k: int = 5):
        """Return the top-K most relevant memory texts for the query."""
        if not self.memories:
            return []

        embedding = self._client.embeddings.create(
            model=self.embedding_model,
            input=query_text,
        ).data[0].embedding

        scored = []
        for entry in self.memories:
            score = self._cosine_similarity(embedding, entry.get("embedding", []))
            scored.append((score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = []
        for score, entry in scored[:top_k]:
            top.append({
                "id": entry.get("id"),
                "text": entry.get("text"),
                "score": score,
                "timestamp": entry.get("timestamp"),
                "metadata": entry.get("metadata"),
            })
        return top

    def does_memory_exist(self, query_text: str, accepted_similarity: float = 0.95) -> bool:
        """
        Try to find if a similar memory is already existing in the database
        Comparing the embeddings of the query with that of the memories to match a similarity
        """

        if not self.memories:
            return False

        embedding = self._client.embeddings.create(
            model=self.embedding_model,
            input=query_text,
        ).data[0].embedding


        for entry in self.memories:
            score = self._cosine_similarity(embedding, entry.get("embedding", []))
            # print(f"{entry['text']}\n{score}\n\n")

            if score >= accepted_similarity:
                return True

        return False

    def list_memories(self):
        """just print out the memory text"""
        for entry in self.memories:
            print(entry["text"])


if __name__ == "__main__":
    db = MemoryDB()
    print(db.does_memory_exist("Hi Fizz, do you know that I really like robots? Fizz, can you identify who's speaking right now?", accepted_similarity=0.6))
    # db.list_memories()
    # print(db.does_memory_exist("What is LeAnn's dog's name?", accepted_similarity=0.6))
    # print(db.does_memory_exist("Does Bahadir enjoy math?"))
    # print(db.query("Does Bahadir enjoy math?"))
    # print(db.query("Does Bahadir like math?"))
    # print(db.query("Is Bahadir good at math?"))
    # print(db.query("Is Bahadir a math person?"))
    # print(db.query("Who likes math?"))
    # print(db.query("I really love math, its my favorite subject!"))
    # print(db.does_memory_exist("In his free time, Bahadir enjoys puzzles and physics"))

    # print(db.does_memory_exist("Ayaan said: I like the color green", accepted_similarity=0.6))
    # print(db.query("How did Keith contribute to Phyz?", top_k=3))
    # Structured testing


    #misc tests
    # memories = db.query("Hi Fizz. Fizz, what's my favorite color?", top_k=5)
    # print(memories[0]["metadata"]["speaker"])
    # print(memories)
    # if memories:
    #     memory_context = ""
    #     for m in memories:
    #         try:
    #             # print(m)
    #             speaker = m["metadata"]["speaker"]
    #             memory_context += (f"- {speaker} said {m['text']}")
    #         except (KeyError, TypeError) as e: #excepting in case the metadata doesn't exist or is None
    #             memory_context += (f"- {m['text']}")
    #         memory_context += "\n"

        # try:
        #     memory_context = "\n".join(f"- {m['metadata']['speaker']} said:  {m['text']}" for m in memories)
        # except KeyError:
        #     memory_context = "\n".join(f"- {m['text']}" for m in memories)
        # print(memory_context)