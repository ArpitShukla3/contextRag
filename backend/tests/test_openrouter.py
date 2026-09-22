"""Tests for the OpenRouter LLM provider."""

import json

import httpx
import pytest

from app.exceptions import LLMError
from app.services.llm import OpenRouterProvider


def _transport_for(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_complete_parses_message_content():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer test-key"
        body = json.loads(request.content)
        assert body["model"] == "fake-model"
        assert body["stream"] is False
        assert body["messages"][0]["role"] == "user"
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"role": "assistant", "content": "Hello!"}}
                ]
            },
        )

    provider = OpenRouterProvider(
        api_key="test-key",
        model="fake-model",
        client=_transport_for(handler),
    )

    assert provider.complete([{"role": "user", "content": "hi"}]) == "Hello!"


def test_stream_yields_deltas_until_done():
    chunks = ['{"choices":[{"delta":{"content":"Hel"}}]}', '{"choices":[{"delta":{"content":"lo"}}]}', "[DONE]"]
    record = []
    provider = OpenRouterProvider(
        api_key="test-key",
        model="fake-model",
        client=_transport_for(
            lambda request: (
                record.append(json.loads(request.content)),
                httpx.Response(200, text="\n".join(f"data: {c}" for c in chunks)),
            )[1]
        ),
    )

    deltas = list(provider.stream([{"role": "user", "content": "hi"}]))

    assert deltas == ["Hel", "lo"]
    assert record[0]["stream"] is True


def test_error_status_raises_lm_error():
    provider = OpenRouterProvider(
        api_key="test-key",
        model="fake-model",
        client=_transport_for(
            lambda request: httpx.Response(
                429, json={"error": {"message": "Rate limited"}}
            )
        ),
    )

    with pytest.raises(LLMError) as exc:
        provider.complete([{"role": "user", "content": "hi"}])
    assert "Rate limited" in str(exc.value)


def test_missing_api_key_raises_without_network():
    provider = OpenRouterProvider(api_key="", model="fake-model")

    with pytest.raises(LLMError):
        provider.complete([{"role": "user", "content": "hi"}])
    with pytest.raises(LLMError):
        for _ in provider.stream([{"role": "user", "content": "hi"}]):
            pass


def test_malformed_success_raises_lm_error():
    provider = OpenRouterProvider(
        api_key="test-key",
        model="fake-model",
        client=_transport_for(lambda request: httpx.Response(200, json={})),
    )

    with pytest.raises(LLMError):
        provider.complete([{"role": "user", "content": "hi"}])