"""End-to-end tests for the search and chat endpoints."""

import json


def _upload_document(client) -> None:
    response = client.post(
        "/api/documents",
        files={
            "file": (
                "climate.txt",
                "Global warming raises average temperatures. Ice melts faster.",
                "text/plain",
            )
        },
    )
    assert response.status_code == 201, response.text


def test_search_returns_retrieved_chunks(chat_client):
    client, _ = chat_client
    _upload_document(client)

    response = client.post(
        "/api/search",
        json={
            "query": "Global warming raises average temperatures. Ice melts faster.",
            "top_k": 5,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["query"].startswith("Global warming")
    assert body["results"]
    result = body["results"][0]
    assert result["original_filename"] == "climate.txt"
    assert result["similarity"] == 1.0
    assert "Ice" in result["content"]


def test_search_returns_low_similarity_for_unrelated_query(chat_client):
    client, _ = chat_client
    _upload_document(client)

    response = client.post(
        "/api/search", json={"query": "completely unrelated topic", "top_k": 5}
    )

    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) <= 1
    if results:
        assert results[0]["similarity"] < 0.9


def test_search_rejects_empty_query(chat_client):
    client, _ = chat_client

    response = client.post("/api/search", json={"query": "", "top_k": 5})

    assert response.status_code == 422


def test_chat_returns_answer_with_sources(chat_client):
    client, fake_llm = chat_client
    _upload_document(client)

    response = client.post(
        "/api/chat", json={"query": "What does global warming do?", "top_k": 3}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "I found the answer in the context."
    assert body["sources"]
    assert body["sources"][0]["original_filename"] == "climate.txt"
    assert fake_llm.requests
    messages = fake_llm.requests[0]
    assert messages[0]["role"] == "system"
    assert "Question: What does global warming do?" in messages[1]["content"]


def test_chat_streams_answer_then_sources(chat_client):
    client, _ = chat_client
    _upload_document(client)

    with client.stream(
        "POST",
        "/api/chat",
        json={"query": "What does global warming do?", "top_k": 3, "stream": True},
    ) as response:
        assert response.headers["content-type"].startswith("text/event-stream")
        events = [
            line[len("data: ") :]
            for line in response.iter_lines()
            if line.startswith("data: ")
        ]

    deltas = [json.loads(e) for e in events if e != "[DONE]"]
    assert any(event["type"] == "delta" for event in deltas)
    sources_event = next(event for event in deltas if event["type"] == "sources")
    assert sources_event["sources"]
    assert events[-1] == "[DONE]"