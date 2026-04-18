import json
import os
import pickle
from typing import List, Dict, Optional, Any
from pathlib import Path

import numpy as np
import faiss
from openai import AsyncOpenAI

from utils.config import config


class VectorStoreManager:
    """Manage FAISS vector stores per course"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.EMBEDDING_API_KEY,
            base_url=config.EMBEDDING_BASE_URL,
        )
        self.indices: Dict[str, faiss.IndexFlatL2] = {}  # course_name -> FAISS index
        self.chunk_metadata: Dict[str, List[Dict]] = {}  # course_name -> list of chunk metadata
        self.dimension = 1536  # OpenAI embedding dimension (text-embedding-3-small)
    
    def get_course_path(self, course_name: str, user_id: int = 0) -> Path:
        """Get path for course vector store"""
        if user_id:
            return Path(config.COURSES_DIR) / str(user_id) / course_name
        return Path(config.COURSES_DIR) / course_name
    
    async def add_document(
        self,
        course_name: str,
        chunks: List[Dict],
        user_id: int = 0,
    ) -> bool:
        """
        Add document chunks to vector store
        
        Args:
            course_name: Name of the course
            chunks: List of dicts with 'text' and 'metadata' keys
            user_id: User ID (for multi-user support)
        """
        if not chunks:
            return False
        
        course_path = self.get_course_path(course_name, user_id)
        course_path.mkdir(parents=True, exist_ok=True)
        
        # Get embeddings for all chunks
        texts = [chunk["text"] for chunk in chunks]
        embeddings = await self._get_embeddings(texts)
        
        # Load or create FAISS index
        index_path = course_path / "index.faiss"
        metadata_path = course_path / "metadata.pkl"
        
        if index_path.exists():
            # Load existing index
            index = faiss.read_index(str(index_path))
            existing_metadata = self._load_metadata(metadata_path)
        else:
            # Create new index
            index = faiss.IndexFlatL2(self.dimension)
            existing_metadata = []
        
        # Add new vectors
        vectors = np.array(embeddings).astype('float32')
        index.add(vectors)
        
        # Add metadata
        for chunk in chunks:
            existing_metadata.append({
                "text": chunk["text"],
                "metadata": chunk.get("metadata", {}),
            })
        
        # Save to disk
        faiss.write_index(index, str(index_path))
        self._save_metadata(metadata_path, existing_metadata)
        
        # Update in-memory cache
        cache_key = f"{user_id}_{course_name}" if user_id else course_name
        self.indices[cache_key] = index
        self.chunk_metadata[cache_key] = existing_metadata
        
        return True
    
    def search(
        self,
        query: str,
        course_name: str,
        top_k: int = 5,
        user_id: int = 0,
    ) -> List[Dict]:
        """
        Search for similar chunks in course
        
        Returns:
            List of dicts with 'text', 'metadata', and 'score'
        """
        cache_key = f"{user_id}_{course_name}" if user_id else course_name
        
        # Load index if not in cache
        if cache_key not in self.indices:
            self._load_course(course_name, user_id)
        
        if cache_key not in self.indices:
            return []
        
        index = self.indices[cache_key]
        metadata_list = self.chunk_metadata.get(cache_key, [])
        
        if len(metadata_list) == 0:
            return []
        
        # Get query embedding (sync version for simplicity)
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        query_embedding = loop.run_until_complete(
            self._get_embeddings([query])
        )
        
        vectors = np.array(query_embedding).astype('float32')
        
        # Search
        distances, indices = index.search(vectors, min(top_k, len(metadata_list)))
        
        # Build results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0 and idx < len(metadata_list):
                results.append({
                    "text": metadata_list[idx]["text"],
                    "metadata": metadata_list[idx]["metadata"],
                    "score": float(1.0 / (1.0 + distances[0][i])),  # Convert distance to similarity
                })
        
        return results
    
    async def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings from API"""
        try:
            response = await self.client.embeddings.create(
                model=config.EMBEDDING_MODEL,
                input=texts,
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"Embedding error: {e}")
            # Return random embeddings as fallback
            return [[0.0] * self.dimension for _ in texts]
    
    def _load_course(self, course_name: str, user_id: int = 0):
        """Load course index and metadata from disk"""
        course_path = self.get_course_path(course_name, user_id)
        index_path = course_path / "index.faiss"
        metadata_path = course_path / "metadata.pkl"
        
        cache_key = f"{user_id}_{course_name}" if user_id else course_name
        
        if index_path.exists():
            self.indices[cache_key] = faiss.read_index(str(index_path))
            self.chunk_metadata[cache_key] = self._load_metadata(metadata_path)
            return True
        return False
    
    def _load_metadata(self, path: Path) -> List[Dict]:
        """Load metadata from pickle file"""
        if path.exists():
            with open(path, 'rb') as f:
                return pickle.load(f)
        return []
    
    def _save_metadata(self, path: Path, metadata: List[Dict]):
        """Save metadata to pickle file"""
        with open(path, 'wb') as f:
            pickle.dump(metadata, f)
    
    def delete_course(self, course_name: str, user_id: int = 0):
        """Delete all vectors for a course"""
        cache_key = f"{user_id}_{course_name}" if user_id else course_name
        
        if cache_key in self.indices:
            del self.indices[cache_key]
        if cache_key in self.chunk_metadata:
            del self.chunk_metadata[cache_key]
        
        course_path = self.get_course_path(course_name, user_id)
        if course_path.exists():
            import shutil
            shutil.rmtree(course_path)
    
    def course_exists(self, course_name: str, user_id: int = 0) -> bool:
        """Check if course vector store exists"""
        course_path = self.get_course_path(course_name, user_id)
        return (course_path / "index.faiss").exists()