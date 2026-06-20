import json
import os
import time

from flask.cli import load_dotenv
from openai import OpenAI
load_dotenv()

class MemoryDB:
    """Simple on-disk vector memory store backed by OpenAI embeddings."""

    def __init__(self, file_path="data/memory_db.json", embedding_model="openai/text-embedding-3-small"):
        self.file_path = file_path
        self.embedding_model = embedding_model

        self._client = OpenAI(
            base_url="https://models.github.ai/inference",
            api_key=os.getenv("OPENAI_API_KEY"),
        )

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
