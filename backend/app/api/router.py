from fastapi import APIRouter

from app.api import analysis, auth, chat, compare, documents

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(chat.router)
api_router.include_router(analysis.router)
api_router.include_router(compare.router)
