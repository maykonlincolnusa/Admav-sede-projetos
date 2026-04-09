from fastapi import APIRouter, HTTPException, Header, UploadFile, File
from database import get_db
from models import KnowledgeAddText, KnowledgeAddUrl, KnowledgeAddSocial
from datetime import datetime
from bson import ObjectId
import os

# ... (Previous routes)

@router.post("/knowledge/add-social")
async def add_social(data: KnowledgeAddSocial, x_user_id: str = Header(None)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Logue para usar os conectores.")
    
    db = get_db()
    
    # Mock de Indexação de Perfil
    # Na vida real, aqui chamaríamos uma API da Apify ou similar para pegar Bio e Posts.
    texto_simulado = f"Perfil {data.rede.upper()} (@{data.handle}) indexado. Foco em: Estilo de postagem, Bio estratégica e Engajamento com a audiência de beleza."
    
    doc = {
        "usuario_id": x_user_id,
        "texto_preview": texto_simulado,
        "fonte": f"{data.rede.capitalize()}: @{data.handle}",
        "categoria": data.categoria,
        "tipo": data.rede,
        "qualidade_score": 0.95,
        "inserido_em": datetime.utcnow()
    }
    
    result = await db.knowledge_base.insert_one(doc)
    return {"mensagem": f"Inteligência do {data.rede} conectada!", "id": str(result.inserted_id)}

@router.get("/knowledge/list")
# ...
import httpx
from bs4 import BeautifulSoup

router = APIRouter()


def verificar_admin(x_admin_secret: str = Header(None)):
    segredo = os.getenv("ADMIN_SECRET", "yafah_admin_2024")
    if x_admin_secret != segredo:
        raise HTTPException(status_code=401, detail="Acesso não autorizado")


def get_embeddings():
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    return GoogleGenerativeAIEmbeddings(
        model=os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )


async def vetorizar_e_salvar(db, texto: str, fonte: str, categoria: str, user_id: str = None, subcategoria: str = ""):
    """Gera embedding e salva na coleção knowledge_base com isolamento de usuário"""
    try:
        embeddings = get_embeddings()
        vetor = embeddings.embed_query(texto)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar embedding: {str(e)}")

    doc = {
        "texto": texto,
        "embedding": vetor,
        "fonte": fonte,
        "categoria": categoria,
        "subcategoria": subcategoria,
        "user_id": user_id,  # None means global/admin knowledge
        "qualidade_score": 0.8,
        "vezes_usado": 0,
        "criado_em": datetime.utcnow(),
        "atualizado_em": datetime.utcnow()
    }
    result = await db.knowledge_base.insert_one(doc)
    return str(result.inserted_id)


@router.post("/knowledge/add-text")
async def adicionar_texto(
    data: KnowledgeAddText, 
    x_admin_secret: str = Header(None), 
    x_user_id: str = Header(None)
):
    # Se não for admin, deve ser um usuário enviando sua própria base
    if not x_admin_secret and not x_user_id:
        raise HTTPException(status_code=401, detail="Identificação necessária")
    
    db = get_db()
    # Se for admin, user_id é None (Global). Se for usuário, salva com id dele.
    u_id = None if x_admin_secret == os.getenv("ADMIN_SECRET", "yafah_admin_2024") else x_user_id
    
    doc_id = await vetorizar_e_salvar(db, data.texto, data.fonte, data.categoria, u_id, data.subcategoria or "")
    return {"mensagem": "Documento adicionado à base de conhecimento", "id": doc_id}


@router.post("/knowledge/add-url")
async def adicionar_url(
    data: KnowledgeAddUrl, 
    x_admin_secret: str = Header(None), 
    x_user_id: str = Header(None)
):
    if not x_admin_secret and not x_user_id:
        raise HTTPException(status_code=401, detail="Identificação necessária")
        
    db = get_db()
    u_id = None if x_admin_secret == os.getenv("ADMIN_SECRET", "yafah_admin_2024") else x_user_id

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(data.url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        texto = soup.get_text(separator="\n", strip=True)
        texto = texto[:8000]

        if len(texto) < 100:
            raise HTTPException(status_code=422, detail="Conteúdo extraído muito curto. Verifique a URL.")
    except httpx.RequestError as e:
        raise HTTPException(status_code=400, detail=f"Erro ao acessar URL: {str(e)}")

    doc_id = await vetorizar_e_salvar(db, texto, data.url, data.categoria, u_id, data.subcategoria or "")
    return {"mensagem": "URL indexada com sucesso", "id": doc_id, "chars_extraidos": len(texto)}


@router.post("/knowledge/add-pdf")
async def adicionar_pdf(
    categoria: str,
    x_admin_secret: str = Header(None),
    x_user_id: str = Header(None),
    arquivo: UploadFile = File(...)
):
    if not x_admin_secret and not x_user_id:
        raise HTTPException(status_code=401, detail="Identificação necessária")
        
    db = get_db()
    u_id = None if x_admin_secret == os.getenv("ADMIN_SECRET", "yafah_admin_2024") else x_user_id

    if not arquivo.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos")

    try:
        from pypdf import PdfReader
        import io
        conteudo = await arquivo.read()
        reader = PdfReader(io.BytesIO(conteudo))
        texto = "\n".join([page.extract_text() or "" for page in reader.pages])
        texto = texto[:8000]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar PDF: {str(e)}")

    doc_id = await vetorizar_e_salvar(db, texto, arquivo.filename, categoria, u_id)
    return {"mensagem": "PDF indexado com sucesso", "id": doc_id, "paginas": len(reader.pages)}


@router.get("/knowledge/list")
async def listar_documentos(
    x_admin_secret: str = Header(None), 
    x_user_id: str = Header(None)
):
    if not x_admin_secret and not x_user_id:
        raise HTTPException(status_code=401, detail="Identificação necessária")
        
    db = get_db()
    
    # Busca apenas documentos do usuário OU globais se for admin
    if x_admin_secret == os.getenv("ADMIN_SECRET", "yafah_admin_2024"):
        query = {"user_id": None} # Admin visualiza apenas base global
    else:
        query = {"user_id": x_user_id} # Usuário visualiza apenas sua base privada
        
    docs = await db.knowledge_base.find(
        query, {"embedding": 0}
    ).sort("criado_em", -1).to_list(length=100)

    return [{
        "id": str(d["_id"]),
        "texto_preview": d["texto"][:150] + "...",
        "fonte": d.get("fonte"),
        "categoria": d.get("categoria"),
        "qualidade_score": d.get("qualidade_score"),
        "vezes_usado": d.get("vezes_usado", 0),
        "criado_em": d["criado_em"].isoformat()
    } for d in docs]


@router.delete("/knowledge/{doc_id}")
async def remover_documento(
    doc_id: str, 
    x_admin_secret: str = Header(None), 
    x_user_id: str = Header(None)
):
    if not x_admin_secret and not x_user_id:
        raise HTTPException(status_code=401, detail="Identificação necessária")
        
    db = get_db()
    try:
        obj_id = ObjectId(doc_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")

    # Verifica permissão para deletar
    filtro = {"_id": obj_id}
    if x_admin_secret != os.getenv("ADMIN_SECRET", "yafah_admin_2024"):
        filtro["user_id"] = x_user_id # Usuário comum só deleta o dele
    else:
        filtro["user_id"] = None # Admin só deleta o Global

    result = await db.knowledge_base.delete_one(filtro)
    if result.deleted_count == 0:
        raise HTTPException(status_code=403, detail="Permissão negada ou documento não localizado")
    return {"mensagem": "Documento removido"}
