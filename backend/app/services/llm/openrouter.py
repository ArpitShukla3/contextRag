"""OpenRouter LLM provider (OpenAI-compatible API)."""

from __future__ import annotations

import json
from collections.abc import Iterator

import httpx

from app.exceptions import LLMError
from app.services.llm.base import LLMProvider


class OpenRouterProvider(LLMProvider):
    """Chat completions via the OpenRouter OpenAI-compatible API."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str = "https://openrouter.ai/api/v1",
        client: httpx.Client | None = None,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._client = client or httpx.Client(timeout=httpx.Timeout(60.0))

    def _endpoint(self) -> str:
        return f"{self._base_url}/chat/completions"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _payload(
        self,
        messages: list[dict],
        *,
        stream: bool,
        temperature: float,
        max_tokens: int,
    ) -> dict:
        return {
            "model": self._model,
            "messages": messages,
            "stream": stream,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

    def _ensure_configured(self) -> None:
        if not self._api_key:
            raise LLMError("OpenRouter API key is not configured.")

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.is_success:
            return
        detail = ""
        try:
            body = response.json()
            detail = body.get("error", {}).get("message", "")
        except json.JSONDecodeError:
            detail = response.text[:300]
        raise LLMError(
            f"OpenRouter request failed with status {response.status_code}: "
            f"{detail}"
        )

    def complete(
        self,
        messages: list[dict],
        *,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> str:
        self._ensure_configured()
        response = self._client.post(
            self._endpoint(),
            headers=self._headers(),
            json=self._payload(
                messages,
                stream=False,
                temperature=temperature,
                max_tokens=max_tokens,
            ),
        )
        self._raise_for_status(response)
        try:
            return response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise LLMError("OpenRouter response did not contain a completion.") from exc

    def stream(
        self,
        messages: list[dict],
        *,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> Iterator[str]:
        self._ensure_configured()
        with self._client.stream(
            "POST",
            self._endpoint(),
            headers=self._headers(),
            json=self._payload(
                messages,
                stream=True,
                temperature=temperature,
                max_tokens=max_tokens,
            ),
        ) as response:
            self._raise_for_status(response)
            for line in response.iter_lines():
                if not line or not line.startswith("data:"):
                    continue
                data = line[len("data:") :].strip()
                if data == "[DONE]":
                    break
                try:
                    payload = json.loads(data)
                except json.JSONDecodeError:
                    continue
                choices = payload.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta") or {}
                content = delta.get("content")
                if content:
                    yield content