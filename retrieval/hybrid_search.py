import logging
import numpy as np
from typing import List, Dict, Optional
from rank_bm25 import BM25Okapi
import json
import os

from retrieval.vector_store import VectorStoreManager
from utils.config import config

logger = logging.getLogger(__name__)


class HybridSearch:
    """Hybrid search combining semantic (FAISS) + keyword (BM25)"""
    
    def __init__(self, vector_manager: VectorStoreManager):
        self.vector_manager = vector_manager
        self.bm25_indices: Dict[str, BM25Okapi] = {}
        self.corpus: Dict[str, List[str]] = {}
    
    def build_bm25_index(self, course_name: str, chunks: List[Dict]):
        """Build BM25 index for a course"""
        
        texts = [chunk["text"] for chunk in chunks]
        tokenized_corpus = [self._tokenize(text) for text in texts]
        
        self.bm25_indices[course_name] = BM25Okapi(tokenized_corpus)
        self.corpus[course_name] = texts
        
        logger.info(f"Built BM25 index for course '{course_name}' with {len(texts)} chunks")
        self._save_index(course_name, texts)
    
    async def search(
        self,
        query: str,
        course_name: str,
        top_k: int = 5,
        alpha: float = 0.5,
    ) -> List[Dict]:
        """Hybrid search: combine semantic and keyword scores"""
        
        # 1. Semantic search (FAISS)
        semantic_results = self.vector_manager.search(
            query=query,
            course_name=course_name,
            top_k=top_k * 2,
        )
        
        # 2. Keyword search (BM25)
        keyword_results = await self._keyword_search(query, course_name, top_k * 2)
        
        # 3. Combine scores
        combined = self._reciprocal_rank_fusion(
            semantic_results, keyword_results, k=60, alpha=alpha
        )
        
        return combined[:top_k]
    
    async def _keyword_search(self, query: str, course_name: str, top_k: int) -> List[Dict]:
        """BM25 keyword search"""
        
        if course_name not in self.bm25_indices:
            logger.warning(f"No BM25 index for course '{course_name}'")
            return []
        
        bm25 = self.bm25_indices[course_name]
        tokenized_query = self._tokenize(query)
        scores = bm25.get_scores(tokenized_query)
        
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append({
                    "text": self.corpus[course_name][idx],
                    "score": float(scores[idx]),
                    "source": "bm25",
                })
        
        return results
    
    def _reciprocal_rank_fusion(
        self,
        semantic_results: List[Dict],
        keyword_results: List[Dict],
        k: int = 60,
        alpha: float = 0.5,
    ) -> List[Dict]:
        """RRF with weighted combination"""
        
        combined_scores = {}
        text_to_item = {}
        
        for rank, item in enumerate(semantic_results):
            text = item["text"]
            score = alpha * (1.0 / (k + rank + 1))
            combined_scores[text] = combined_scores.get(text, 0) + score
            text_to_item[text] = item
        
        for rank, item in enumerate(keyword_results):
            text = item["text"]
            score = (1 - alpha) * (1.0 / (k + rank + 1))
            combined_scores[text] = combined_scores.get(text, 0) + score
            if text not in text_to_item:
                text_to_item[text] = item
        
        sorted_texts = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for text, score in sorted_texts:
            item = text_to_item[text].copy()
            item["hybrid_score"] = score
            results.append(item)
        
        return results
    
    def _tokenize(self, text: str) -> List[str]:
        import re
        text = re.sub(r'[،\.\!\؟\;\:\"\']', ' ', text)
        return text.lower().split()
    
    def _save_index(self, course_name: str, texts: List[str]):
        course_dir = os.path.join(config.COURSES_DIR, course_name)
        os.makedirs(course_dir, exist_ok=True)
        
        bm25_path = os.path.join(course_dir, "bm25_corpus.json")
        with open(bm25_path, "w", encoding="utf-8") as f:
            json.dump(texts, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved BM25 corpus to {bm25_path}")
    
    def load_index(self, course_name: str):
        bm25_path = os.path.join(config.COURSES_DIR, course_name, "bm25_corpus.json")
        
        if os.path.exists(bm25_path):
            with open(bm25_path, "r", encoding="utf-8") as f:
                texts = json.load(f)
            
            tokenized_corpus = [self._tokenize(t) for t in texts]
            self.bm25_indices[course_name] = BM25Okapi(tokenized_corpus)
            self.corpus[course_name] = texts
            logger.info(f"Loaded BM25 index for '{course_name}' with {len(texts)} chunks")