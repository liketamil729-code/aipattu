# AI Learning & Study Assistant

Final-year B.E. Computer Science project foundation for a personalized AI study assistant.

This repository currently contains the project foundation plus a first working RAG/LLM path: PDF upload, PDF text extraction, chunking, OpenAI-compatible embeddings, SQLite vector storage with cosine similarity, source-aware retrieval, and chat responses from `/api/chat`.

## Phase 1 Architecture

- `frontend`: React + Vite app shell with responsive navigation and backend health check.
- `backend`: FastAPI app with CORS, typed settings, SQLAlchemy engine/session, document routes, and chat routes.
- `uploads`: reserved for study material files.
- `vector_db`: reserved for future ChromaDB persistence. The current runnable Windows build stores vectors in SQLite to avoid native build-tool issues.
- `.env.example`: required configuration without secrets.

## Folder Structure

```text
ai-study-assistant/
  backend/
    app/
      core/
      database/
      routes/
      schemas/
      services/
      main.py
    requirements.txt
  frontend/
    src/
      components/
      pages/
      services/
      App.jsx
      main.jsx
      styles.css
    index.html
    package.json
  uploads/
  vector_db/
  .env.example
  .gitignore
  README.md
```

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example .env
uvicorn app.main:app --reload
```

Backend runs at:

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/api/health`

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

- `http://localhost:5173`

## How To Test Phase 1

1. Start the backend.
2. Visit `http://localhost:8000/api/health`.
3. Start the frontend.
4. Open `http://localhost:5173`.
5. Confirm the status card shows `Backend: ok` and `Database: connected`.

## How RAG Works In This Build

1. Upload a PDF on the Study Materials page.
2. The backend extracts page text with PyMuPDF.
3. Text is split into overlapping chunks.
4. Embeddings are generated with the configured OpenAI-compatible provider.
5. Chunks and embeddings are stored in SQLite.
6. Chat questions are embedded, compared with cosine similarity, and answered using retrieved chunks.
7. The response includes document/page sources when retrieval succeeds.

To enable real AI calls, set these values in `backend/.env`:

```text
LLM_API_KEY=your_real_key
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small
```

## Next Phase

Phase 2 should add:

- User model
- Register endpoint
- Login endpoint
- JWT generation and validation
- Password hashing
- Protected backend routes
- Frontend auth context
- Protected React routes
