# Architecture Overview

The EE Tutor Bot follows a modular service-oriented architecture.

## 1. Interaction Layer (Telegram)
Uses `python-telegram-bot` with `ApplicationBuilder`. It routes messages based on their type (text, photo, document, voice).

## 2. Intelligence Layer (LLM)
- **Engine**: OpenAI-compatible client connecting to LLM7.io.
- **Prompts**: Context-aware system messages defined in `Prompts` class.
- **Vision**: Uses GPT-4o style vision API for image analysis.

## 3. Knowledge Layer (RAG)
- **Embeddings**: `sentence-transformers` (paraphrase-multilingual-MiniLM-L12-v2) for local, fast high-quality vectorization of Persian and English text.
- **Vector DB**: `FAISS` for efficient similarity search. Chunks are stored per course.

## 4. Persistence Layer (Database)
- **Engine**: `SQLAlchemy` with `SQLite`.
- **Data Models**: Users, Flashcards, QuizAttempts.

## 5. Workflow
1. User sends a message.
2. Bot detects user's active course and mode (Solver/Bridge/QA).
3. Bot retrieves relevant document chunks from FAISS.
4. Prompt is constructed with User Question + Retrieved Context + Mode Instructions.
5. Answer is generated and delivered via Telegram.
