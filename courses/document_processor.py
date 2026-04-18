import os
from pypdf import PdfReader
from docx import Document as DocxDocument
from utils.config import config
import re

class DocumentProcessor:
    @staticmethod
    def extract_text(file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return DocumentProcessor._parse_pdf(file_path)
        elif ext == '.docx':
            return DocumentProcessor._parse_docx(file_path)
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    @staticmethod
    def _parse_pdf(file_path: str) -> str:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n---\n"
        return text

    @staticmethod
    def _parse_docx(file_path: str) -> str:
        doc = DocxDocument(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text

    @staticmethod
    def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list[str]:
        chunk_size = chunk_size or config.MAX_CHUNK_SIZE
        overlap = overlap or config.CHUNK_OVERLAP
        
        # Simple paragraph and length based chunking
        # In production, use semantic chunking
        paragraphs = text.split("\n")
        chunks = []
        current_chunk = ""
        
        for p in paragraphs:
            if len(current_chunk) + len(p) < chunk_size:
                current_chunk += p + "\n"
            else:
                chunks.append(current_chunk.strip())
                # Start next chunk with overlap
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + p + "\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks
