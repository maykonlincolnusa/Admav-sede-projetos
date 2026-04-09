from fastapi import APIRouter, HTTPException, BackgroundTasks
from database import get_db
from models import MensagemChat
from datetime import datetime
from bson import ObjectId
import os

# LangChain OpenRouter
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# FAISS RAG Engine Import (Now using MongoDB)
from rag_engine import search_db, ingest_to_db
from database import get_collection

router = APIRouter()

SYSTEM_PROMPT_TEMPLATE = """Você é Yafah, consultora de negócios de altíssimo nível para empreendedoras do setor da beleza brasileiro.

PERFIL DA USUÁRIA:
Nome: {nome}
Tipo de negócio: {tipo_negocio}
Cidade: {cidade}
Nível: {nivel}

🧠 MEMÓRIA DE LONGO PRAZO E CONTEXTOS ANTERIORES DO NEGÓCIO DELA (USE PARA PERSONALIZAR A RESPOSTA):
{contexto_rag}

💬 HISTÓRICO RECENTE DA CONVERSA:
{historico}

COMO RESPONDER:
- Leve ESTRITAMENTE em consideração as memórias de longo prazo fornecidas se elas forem relevantes para o momento. Como uma consultora, você não pode esquecer das metas e números que ela já passou no passado.
- Seja direta e prática. Entregue valor real, não teoria vazia.
- Adapte ao nível da usuária:
  * Iniciante: exemplos simples, passo a passo, sem jargão
  * Intermediária: conceitos aplicados, cases reais, métricas
  * Avançada: estratégia, análise, benchmarks, visão de escala
- Use números reais do mercado brasileiro quando relevante
- Quando der conselho financeiro, calcule junto com ela
- Tom: sofisticado, acolhedor, direto. Como uma sócia que quer ver você crescer.
- Use emojis com moderação e elegância 🌹
- Responda sempre em português brasileiro.
- Mostre que você lembra dela usando peças do contexto para não parecer uma assistente genérica.

PERGUNTA DA USUÁRIA: {pergunta}

YAFAH:"""

def get_llm():
    return ChatOpenAI(
        model="google/gemini-2.0-flash-lite-preview-02-05:free",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.7,
        default_headers={
            "HTTP-Referer": "https://yafah.vercel.app", 
            "X-Title": "Yafa AI"
        }
    )

def formatar_historico(mensagens: list) -> str:
    if not mensagens:
        return "Nenhuma conversa anterior."
    historico = []
    for msg in mensagens[-8:]:
        papel = "Empreendedora" if msg["role"] == "user" else "Yafah"
        historico.append(f"{papel}: {msg['content']}")
    return "\n".join(historico)

def formatar_documentos(docs) -> str:
    if not docs:
        return "Sem registros extras na memória."
    return "\n---\n".join([doc.page_content for doc in docs])
    
async def processar_aprendizado_rag(pergunta: str, resposta: str, usuario_id: str, obj_id: ObjectId):
    """Background task para injetar dados no RAG sem travar a resposta da IA"""
    try:
        # Metadados ajudam a identificar de quem/o que é esse conteúdo depois no banco e RAG se quisermos filtrar.
        meta = {"usuario_id": usuario_id, "tipo": "interacao_chat", "timestamp": str(datetime.utcnow())}
        
        # 1. Aprende no Motor Vetorial Rápido (MongoDB Vector Search)
        texto_ingestao = f"Consulta: {pergunta}\nResolução Yafah: {resposta}\n"
        ingest_to_db(texto_ingestao, metadados=meta)
        
        # O Ingest já cuidou de salvar em knowledge_base com os metadados
        print(f"[Banco de Dados] Conhecimento salvo com sucesso e embutido vetorialmente para o usuário {usuario_id}.")
        
    except Exception as e:
        print(f"Erro ao processar aprendizado RAG: {e}")

@router.post("/chat")
async def chat(data: MensagemChat, background_tasks: BackgroundTasks):
    usuarios_col = get_collection("usuarios")
    finance_col = get_collection("finances")
    conversas_col = get_collection("conversas")

    # Valida usuária
    try:
        obj_id = ObjectId(data.usuario_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de usuária inválido")

    usuario = await usuarios_col.find_one({"_id": obj_id})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuária não encontrada")
    if usuario.get("status") != "ativo":
        raise HTTPException(status_code=403, detail="Acesso não autorizado")

    # 💰 Busca Contexto Financeiro Atual
    contexto_financeiro = "Nenhum dado financeiro registrado ainda."
    try:
        pipeline = [
            {"$match": {"usuario_id": data.usuario_id}},
            {"$group": {"_id": "$tipo", "total": {"$sum": "$valor"}}}
        ]
        fin_results = await finance_col.aggregate(pipeline).to_list(length=100)
        rec = 0.0; desp = 0.0
        for f in fin_results:
            if f["_id"] == "receita": rec = f["total"]
            elif f["_id"] == "despesa": desp = f["total"]
        
        if rec > 0 or desp > 0:
            lucro = rec - desp
            contexto_financeiro = (
                f"- Receita Total: R$ {rec:,.2f}\n"
                f"- Despesas Totais: R$ {desp:,.2f}\n"
                f"- Lucro Líquido Atual: R$ {lucro:,.2f}\n"
                f"- Saúde: {'Positiva' if lucro > 0 else 'Atenção/Negativa'}"
            )
    except Exception as e:
        print(f"Erro ao buscar finanças: {e}")

    # Histórico de Conversa (Curto Prazo - MongoDB)
    conversa = await conversas_col.find_one({"usuario_id": data.usuario_id})
    mensagens_historico = conversa.get("mensagens", []) if conversa else []
    conversa_id = str(conversa["_id"]) if conversa else None
    historico_fmt = formatar_historico(mensagens_historico)

    # RAG de Longo Prazo (Buscando semântica via FAISS para Lembrar de coisas passadas)
    contexto_rag = ""
    docs_usados = []
    try:
        # Trazendo o knowledge vetorial da base MongoDB filtrado por Tenant Isolation
        docs = search_db(query=f"Usuária {usuario.get('nome')} pergunta: {data.mensagem}", k=4, usuario_id=data.usuario_id)
        contexto_rag = formatar_documentos(docs)
    except Exception as e:
        print(f"⚠️ RAG não disponível neste momento: {e}")
        contexto_rag = "(Ainda aprendendo sobre a usuária)"

    # Monta prompt e chama Gemini via LangChain
    try:
        prompt = PromptTemplate(
            input_variables=["nome", "tipo_negocio", "cidade", "nivel", "contexto_financeiro",
                             "contexto_rag", "historico", "pergunta"],
            template=SYSTEM_PROMPT_TEMPLATE
        )
        llm = get_llm()
        chain = prompt | llm | StrOutputParser()

        resposta_ia = chain.invoke({
            "nome": usuario.get("nome", ""),
            "tipo_negocio": usuario.get("tipo_negocio", ""),
            "cidade": usuario.get("cidade", ""),
            "nivel": usuario.get("nivel", "iniciante"),
            "contexto_financeiro": contexto_financeiro,
            "contexto_rag": contexto_rag,
            "historico": historico_fmt,
            "pergunta": data.mensagem,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao contactar IA: {str(e)}")

    # Salva "Dumb Raw Messages" no MongoDB Conversas
    nova_user = {"role": "user", "content": data.mensagem, "timestamp": datetime.utcnow()}
    nova_ia = {"role": "model", "content": resposta_ia, "timestamp": datetime.utcnow()}

    if conversa:
        result = await conversas_col.update_one(
            {"usuario_id": data.usuario_id},
            {"$push": {"mensagens": {"$each": [nova_user, nova_ia]}}}
        )
    else:
        result = await conversas_col.insert_one({
            "usuario_id": data.usuario_id,
            "mensagens": [nova_user, nova_ia],
            "documentos_usados": docs_usados,
            "busca_web_feita": False,
            "criado_em": datetime.utcnow()
        })
        conversa_id = str(result.inserted_id)

    # Dispara a Extração de Sabedoria de Forma Assíncrona para não atrasar a TELA da usuária
    background_tasks.add_task(processar_aprendizado_rag, data.mensagem, resposta_ia, data.usuario_id, obj_id)

    # Atualiza último acesso da usuária
    await usuarios_col.update_one(
        {"_id": obj_id},
        {"$set": {"ultimo_acesso": datetime.utcnow()}}
    )

    return {
        "resposta": resposta_ia,
        "conversa_id": conversa_id,
        "usuario": usuario.get("nome")
    }
