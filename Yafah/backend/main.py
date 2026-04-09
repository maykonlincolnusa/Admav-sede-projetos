from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import connect_db, close_db
from routes import auth, cadastro, chat, admin, feedback, knowledge, finance, metrics
from dotenv import load_dotenv
import os

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="Yafah API",
    description="Consultora de negócios com IA para empreendedoras do setor da beleza — LangChain + RAG + Gemini",
    version="2.0.0",
    lifespan=lifespan
)

# CORS — permite frontend Vercel e localhost
frontend_url = os.getenv("FRONTEND_URL", "https://yafah.vercel.app")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        frontend_url,
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────
app.include_router(auth.router,      prefix="/auth",   tags=["Auth"])
app.include_router(cadastro.router,  prefix="/api",    tags=["Cadastro"])
app.include_router(chat.router,      prefix="/api",    tags=["Chat"])
app.include_router(feedback.router,  prefix="/api",    tags=["Feedback"])
app.include_router(finance.router,   prefix="/api",    tags=["Finance"])
app.include_router(admin.router,     prefix="/admin",  tags=["Admin"])
app.include_router(metrics.router,   prefix="/api",    tags=["Metrics"])
app.include_router(knowledge.router, prefix="/admin",  tags=["Knowledge Base (Global)"])
app.include_router(knowledge.router, prefix="/api",    tags=["Knowledge Base (User)"])


@app.get("/")
async def root():
    return {
        "app": "Yafah API",
        "versao": "2.0.0",
        "status": "online",
        "engine": "LangChain + RAG + Gemini"
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
