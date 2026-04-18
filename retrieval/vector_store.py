import faiss
import numpy as np
import pickle
import os
from openai import AsyncOpenAI
from utils.config import config
from typing import List, Dict

class VectorStore:
    def __init__(self, course_id: int, course_name: str, user_id: int):
        self.user_id = user_id
        self.course_name = course_name
        self.path = os.path.join(config.COURSES_DIR, str(user_id), course_name)
        os.makedirs(self.path, exist_ok=True)
        
        self.index_file = os.path.join(self.path, "index.faiss")
        self.meta_file = os.path.join(self.path, "index.pkl")
        
        self.client = AsyncOpenAI(
            api_key=config.EMBEDDING_API_KEY,
            base_url=config.EMBEDDING_BASE_URL
        )
        
        self.dimension = 1536 # Default for text-embedding-3-small
        self.index = None
        self.chunks = []
        
        self._load()

    def _load(self):
        if os.path.exists(self.index_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.meta_file, "rb") as f:
                self.chunks = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.chunks = []

    async def _get_embedding(self, text: str) -> List[float]:
        response = await self.client.embeddings.create(
            input=[text],
            model=config.EMBEDDING_MODEL
        )
        return response.data[0].embedding

    async def add_chunks(self, texts: List[str], metadata: Dict = None):
        embeddings = []
        for text in texts:
            emb = await self._get_embedding(text)
            embeddings.append(emb)
            self.chunks.append({"text": text, "metadata": metadata or {}})
            
        embeddings_np = np.array(embeddings).astype('float32')
        self.index.add(embeddings_np)
        self._save()

    def _save(self):
        faiss.write_index(self.index, self.index_file)
        with open(self.meta_file, "wb") as f:
            pickle.dump(self.chunks, f)

    async def search(self, query: str, k: int = 5) -> List[Dict]:
        if self.index.ntotal == 0:
            return []
            
        query_emb = await self._get_embedding(query)
        query_np = np.array([query_emb]).astype('float32')
        
        distances, indices = self.index.search(query_np, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.chunks):
                chunk = self.chunks[idx].copy()
                chunk["score"] = float(distances[0][i])
                results.append(chunk)
        return results
