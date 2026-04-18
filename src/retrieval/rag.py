import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
from docx import Document
from src.config import Config

class RAGManager:
    def __init__(self):
        # We use a standard local embedding model for simplicity and speed
        self.encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.indexes = {} # course_slug -> faiss_index
        self.metadata = {} # course_slug -> list of text chunks

    def _extract_text(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        text = ""
        if ext == '.pdf':
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif ext == '.docx':
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        return text

    def _split_chunks(self, text, chunk_size=500):
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunks.append(" ".join(words[i:i + chunk_size]))
        return chunks

    def index_file(self, file_path, course_slug):
        text = self._extract_text(file_path)
        chunks = self._split_chunks(text)
        
        embeddings = self.encoder.encode(chunks)
        
        dim = embeddings.shape[1]
        if course_slug not in self.indexes:
            self.indexes[course_slug] = faiss.IndexFlatL2(dim)
            self.metadata[course_slug] = []
            
        self.indexes[course_slug].add(np.array(embeddings).astype('float32'))
        self.metadata[course_slug].extend(chunks)
        
        # Save index locally (simplified)
        index_path = os.path.join(Config.VECTOR_STORE_DIR, f"{course_slug}.index")
        faiss.write_index(self.indexes[course_slug], index_path)

    def retrieve(self, query, course_slug, k=3):
        if course_slug not in self.indexes:
            # Try to load if exists
            index_path = os.path.join(Config.VECTOR_STORE_DIR, f"{course_slug}.index")
            if os.path.exists(index_path):
                self.indexes[course_slug] = faiss.read_index(index_path)
            else:
                return ""

        query_vector = self.encoder.encode([query])
        distances, indices = self.indexes[course_slug].search(np.array(query_vector).astype('float32'), k)
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.metadata.get(course_slug, [])):
                results.append(self.metadata[course_slug][idx])
        
        return "\n---\n".join(results)
