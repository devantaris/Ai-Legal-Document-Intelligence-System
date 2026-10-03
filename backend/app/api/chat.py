import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, owned_document
from app.models import Conversation, Message, User
from app.schemas import AskIn, MessageOut
from app.services import chat as chat_service

router = APIRouter(tags=["chat"])


@router.post("/documents/{doc_id}/chat")
def chat(
    doc_id: uuid.UUID,
    payload: AskIn,
    stream: bool = Query(default=True),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = owned_document(doc_id, user, db)
    if doc.status != "ready":
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Document is not ready (status: {doc.status}). Wait for ingestion to finish.",
        )
    if not stream:
        return chat_service.answer(db, doc, payload.question)
    return StreamingResponse(
        chat_service.stream_answer(db, doc, payload.question),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/documents/{doc_id}/messages", response_model=list[MessageOut])
def list_messages(
    doc_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MessageOut]:
    doc = owned_document(doc_id, user, db)
    conv = (
        db.query(Conversation).filter(Conversation.document_id == doc.id).first()
    )
    if conv is None:
        return []
    rows = (
        db.query(Message)
        .filter(Message.conversation_id == conv.id)
        .order_by(Message.created_at)
        .all()
    )
    return [MessageOut.model_validate(m) for m in rows]
