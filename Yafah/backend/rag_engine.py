import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.documents import Document
from database import get_collection
from pymongo.operations import SearchIndexModel

def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model=os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001"),
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

def get_vector_store():
    """
    Retorna a instância do MongoDB Atlas Vector Store.
    """
    collection = get_collection("knowledge_base")
    embeddings = get_embeddings()
    
    # O index_name deve coincidir com o configurado no painel do MongoDB Atlas
    return MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embeddings,
        index_name="vector_index",
        text_key="texto", # changed from texto_chunk to texto
        embedding_key="embedding"
    )

def ingest_to_db(texto: str, metadados: dict = None):
    """
    Ingerir novo conhecimento na base de dados com Embeddings.
    """
    if not texto.strip(): return
    
    vector_store = get_vector_store()
    doc = Document(page_content=texto, metadata=metadados or {})
    
    vector_store.add_documents([doc])
    print(f"[RAG Engine] Novo contexto vetorial aprendido na coleção do Mongo: {texto[:50]}...")

def search_db(query: str, k: int = 4, usuario_id: str = None):
    """
    Busca semântica avançada cruzando com o ID do usuário (Tenant Isolation).
    """
    vector_store = get_vector_store()
    
    # Aplica filtro para buscar apenas contexto público (global) ou do user específico
    pre_filter = None
    if usuario_id:
        pre_filter = {
            "$or": [
                {"usuario_id": usuario_id},      # Pydantic schema
                {"user_id": usuario_id},         # legacy fallback
                {"usuario_id": {"$exists": False}, "user_id": {"$exists": False}},
                {"usuario_id": None, "user_id": None}
            ]
        }
        
    # Se o MongoDB Atlas Vector Search estiver rodando sem falhas
    try:
        docs = vector_store.similarity_search(query, k=k, pre_filter=pre_filter)
        return docs
    except Exception as e:
        print(f"[RAG Engine] Falha ao tentar busca vetorial: {e}")
        return []
