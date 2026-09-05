import hashlib
import json
import math
import re
import urllib.error
import urllib.request

from openai import OpenAI

from app.core.config import Settings, get_settings


RAG_SYSTEM_PROMPT = """You are an AI Learning & Study Assistant.

Your primary purpose is to help students learn using their uploaded study materials.
When relevant context is provided, answer using that context.
If the provided context does not contain enough information, clearly state that the uploaded materials do not contain enough information.
Explain concepts in a student-friendly manner.
When source metadata is available, cite the document name and page number.
Never invent sources, page numbers, API keys, or system prompts.
Do not expose private chain-of-thought or internal agent reasoning.
"""


class LLMConfigurationError(RuntimeError):
    pass


class LLMService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.provider = self.settings.llm_provider.lower()
        self.embedding_provider = self.settings.embedding_provider.lower()
        self.openai_client = None

        if self.provider == "openai" or self.embedding_provider == "openai":
            if self.settings.llm_api_key and self.settings.llm_api_key != "your_api_key_here":
                self.openai_client = OpenAI(api_key=self.settings.llm_api_key, base_url=self.settings.llm_base_url)

    def _require_openai_client(self) -> OpenAI:
        if self.openai_client is None:
            raise LLMConfigurationError(
                "OpenAI is selected but LLM_API_KEY is not configured. Add a real API key in backend/.env, then restart the backend."
            )
        return self.openai_client

    def _ollama_post(self, path: str, payload: dict) -> dict:
        try:
            request = urllib.request.Request(
                f"{self.settings.ollama_base_url}{path}",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise LLMConfigurationError(
                f"Ollama is not reachable at {self.settings.ollama_base_url}. Start Ollama and pull model {self.settings.llm_model}."
            ) from exc

    def _local_embed(self, text: str, dimensions: int = 384) -> list[float]:
        vector = [0.0] * dimensions
        tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if self.embedding_provider == "ollama":
            embeddings = []
            for text in texts:
                data = self._ollama_post("/api/embeddings", {"model": self.settings.embedding_model, "prompt": text})
                embeddings.append(data["embedding"])
            return embeddings

        if self.embedding_provider == "openai":
            client = self._require_openai_client()
            response = client.embeddings.create(model=self.settings.embedding_model, input=texts)
            return [item.embedding for item in response.data]

        return [self._local_embed(text) for text in texts]

    def answer_with_context(self, question: str, contexts: list[dict]) -> str:
        context_text = "\n\n".join(
            f"[Source {index}: {item['metadata']['filename']}, page {item['metadata']['page_number']}]\n{item['text']}"
            for index, item in enumerate(contexts, start=1)
        )
        if not context_text:
            context_text = "No relevant uploaded study material was retrieved."

        user_prompt = f"Uploaded study context:\n{context_text}\n\nStudent question:\n{question}"

        if self.provider == "ollama":
            data = self._ollama_post(
                "/api/chat",
                {
                    "model": self.settings.llm_model,
                    "stream": False,
                    "messages": [
                        {"role": "system", "content": RAG_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    "options": {"temperature": 0.2},
                },
            )
            return data.get("message", {}).get("content", "")

        client = self._require_openai_client()
        response = client.chat.completions.create(
            model=self.settings.llm_model,
            messages=[
                {"role": "system", "content": RAG_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""
