"""Retrieval-augmented chat endpoints."""

import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.deps import get_chat_service
from app.schemas.chat import ChatRequest, ChatResponse, ChatSource
from app.services.chat import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


def _stream_response(service: ChatService, payload: ChatRequest) -> StreamingResponse:
    def event_stream():
        stream = service.stream(payload.query, payload.top_k)
        for delta in stream.deltas:
            yield f"data: {json.dumps({'type': 'delta', 'content': delta})}\n\n"
        sources = [
            ChatSource.from_retrieved(result).model_dump() for result in stream.chunks
        ]
        yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"}
    )


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    service: ChatService = Depends(get_chat_service),
):
    """Answer ``query`` grounded on retrieved chunks.

    Set ``stream: true`` for a Server-Sent-Events stream of answer deltas
    followed by a ``sources`` event.
    """
    if payload.stream:
        return _stream_response(service, payload)
    answer = service.answer(payload.query, payload.top_k)
    return ChatResponse(
        answer=answer.answer,
        sources=[ChatSource.from_retrieved(result) for result in answer.chunks],
    )