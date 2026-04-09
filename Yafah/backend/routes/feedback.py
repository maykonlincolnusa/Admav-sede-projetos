from fastapi import APIRouter, HTTPException
from database import get_db
from models import FeedbackRequest
from datetime import datetime
from bson import ObjectId

router = APIRouter()


@router.post("/feedback")
async def registrar_feedback(data: FeedbackRequest):
    db = get_db()

    # Valida usuária
    try:
        obj_id = ObjectId(data.usuario_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")

    usuario = await db.usuarios.find_one({"_id": obj_id})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuária não encontrada")

    feedback_doc = {
        "usuario_id": data.usuario_id,
        "conversa_id": data.conversa_id,
        "estrelas": data.estrelas,
        "comentario": data.comentario or "",
        "criado_em": datetime.utcnow()
    }

    # Salva feedback
    await db.feedback.insert_one(feedback_doc)

    # Atualiza perfil de aprendizado da usuária
    perfil = await db.perfis_aprendizado.find_one({"usuario_id": data.usuario_id})
    if perfil:
        total = perfil.get("metricas", {}).get("total_conversas", 0) + 1
        media_atual = perfil.get("metricas", {}).get("media_estrelas", data.estrelas)
        nova_media = round((media_atual * (total - 1) + data.estrelas) / total, 2)
        await db.perfis_aprendizado.update_one(
            {"usuario_id": data.usuario_id},
            {
                "$set": {
                    "metricas.total_conversas": total,
                    "metricas.media_estrelas": nova_media,
                    "atualizado_em": datetime.utcnow()
                }
            }
        )
    else:
        await db.perfis_aprendizado.insert_one({
            "usuario_id": data.usuario_id,
            "perguntas_frequentes": [],
            "areas_dificuldade": [],
            "nivel_atual": "iniciante",
            "metricas": {
                "total_conversas": 1,
                "media_estrelas": float(data.estrelas),
                "area_mais_consultada": "",
                "crescimento_nivel": []
            },
            "atualizado_em": datetime.utcnow()
        })

    return {"mensagem": "Feedback registrado. Obrigada! 🌹"}
