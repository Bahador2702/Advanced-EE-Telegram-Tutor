# Developer Workflow & Debugging

## Running the Bot Locally
1. Ensure your `.env` file contains valid tokens.
2. Run with verbose logging for debugging:
   ```bash
   export LOG_LEVEL=DEBUG
   python main.py
   ```

## Testing Features
- **RAG**: Upload a small PDF and ask a question about its specific content.
- **Vision**: Send a screenshot of a basic RC circuit or an op-amp circuit.
- **Voice**: Send a voice message asking "قانون اهم را توضیح بده".

## Handling LLM7.io Errors
If you see `APIError`, check:
- Is your API Key valid?
- Does the model name match (e.g., `gpt-4o`)?
- Is the `LLM_BASE_URL` accessible from your network?

## Database Maintenance
The database is a simple SQLite file at `./data/tutor_bot.db`. You can browse it using "DB Browser for SQLite" to check user stats and flashcards.
