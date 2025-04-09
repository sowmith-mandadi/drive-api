"""
API endpoints for RAG (Retrieval-Augmented Generation) capabilities.
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.content_service import ContentService
from app.services.rag_service import RAGService


# Pydantic models for request/response
class QuestionRequest(BaseModel):
    """Model for question request."""

    question: str
    content_ids: Optional[List[str]] = None


router = APIRouter(prefix="/rag", tags=["RAG"])

# Service instances
rag_service = RAGService()
content_service = ContentService()


@router.post("/ask", response_model=Dict[str, Any])
async def ask_question(request: QuestionRequest):
    """Ask a question about content."""
    try:
        # Get content items if content_ids provided
        content_items = None
        if request.content_ids is not None:
            content_items = []
            for content_id in request.content_ids:
                content = content_service.get_content_by_id(content_id)
                if content:
                    content_items.append(content)

        # Get answer from RAG service
        answer = rag_service.ask_question(
            question=request.question, content_ids=request.content_ids, content_items=content_items
        )

        return answer
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process question: {str(e)}",
        )


@router.post("/{content_id}/summarize", response_model=Dict[str, str])
async def summarize_content(content_id: str):
    """Generate a summary of the specified content."""
    try:
        # Get content
        content = content_service.get_content_by_id(content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Content with ID {content_id} not found",
            )

        # Generate summary
        summary = rag_service.summarize_content(content)

        return {"content_id": content_id, "summary": summary}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}",
        )


@router.post("/{content_id}/tags", response_model=Dict[str, Any])
async def generate_tags(content_id: str):
    """Generate tags for the specified content."""
    try:
        # Get content
        content = content_service.get_content_by_id(content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Content with ID {content_id} not found",
            )

        # Generate tags
        tags = rag_service.generate_tags(content)

        return {"content_id": content_id, "tags": tags}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate tags: {str(e)}",
        )


@router.get("/{content_id}/similar", response_model=List[Dict[str, Any]])
async def find_similar_content(content_id: str, limit: int = 5):
    """Find content similar to the specified content."""
    try:
        # Check if content exists
        content = content_service.get_content_by_id(content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Content with ID {content_id} not found",
            )

        # Find similar content
        similar = rag_service.find_similar_content(content_id, limit=limit)

        return similar
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find similar content: {str(e)}",
        )
