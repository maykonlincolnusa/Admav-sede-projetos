from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "yafah_premium_db")

client: AsyncIOMotorClient = None
db = None

async def connect_db():
    global client, db
    if not MONGODB_URI:
        print("⚠️ MONGODB_URI não configurada. Usando banco em memória ou indisponível.")
        return
    try:
        client = AsyncIOMotorClient(MONGODB_URI)
        db = client[MONGODB_DB]
        print(f"✅ MongoDB conectado — Banco Principal: {MONGODB_DB}")
    except Exception as e:
        print(f"❌ Erro ao conectar ao MongoDB: {e}")

async def close_db():
    global client
    if client:
        client.close()
        print("🔌 MongoDB desconectado")

def get_db():
    return db

def get_collection(name: str):
    if db is not None:
        return db[name]
    raise Exception("Banco de dados não inicializado")
