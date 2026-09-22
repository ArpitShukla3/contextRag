"""Vector search endpoint."""

from fastapi import APIRouter, Depends

from app.deps import get_search_service
from app.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.services.search import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=SearchResponse)
def search(
    payload: SearchRequest,
    service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    """Return the chunks most semantically similar to ``query``."""
    results = service.search(payload.query, payload.top_k)
    return SearchResponse(
        query=payload.query,
        results=[SearchResult.from_retrieved(result) for result in results],
    )