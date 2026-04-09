from fastapi import APIRouter

from app.api.routes.chat import router as chat_router
from app.api.routes.devotional import router as devotional_router
from app.api.routes.members import router as members_router
from app.api.routes.rag import router as rag_router

api_router = APIRouter()
api_router.include_router(members_router)
api_router.include_router(chat_router)
api_router.include_router(rag_router)
api_router.include_router(devotional_router)
