from fastapi import APIRouter, HTTPException, Header
from database import get_db
from datetime import datetime
from bson import ObjectId
from twilio.rest import Client as TwilioClient
import os

router = APIRouter()


def verificar_admin(x_admin_secret: str = Header(None)):
    segredo = os.getenv("ADMIN_SECRET", "yafah_admin_2024")
    if x_admin_secret != segredo:
        raise HTTPException(status_code=401, detail="Acesso não autorizado")


def formatar_doc(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    if "criado_em" in doc and doc["criado_em"]:
        doc["criado_em"] = doc["criado_em"].isoformat()
    if "aprovado_em" in doc and doc["aprovado_em"]:
        doc["aprovado_em"] = doc["aprovado_em"].isoformat()
    # Remove campos internos
    doc.pop("nome_lower", None)
    doc.pop("cpf_cnpj_limpo", None)
    return doc


@router.get("/pendentes")
async def listar_pendentes(x_admin_secret: str = Header(None)):
    verificar_admin(x_admin_secret)
    db = get_db()
    pendentes = await db.usuarios.find({"status": "pendente"}).to_list(length=100)
    return [formatar_doc(u) for u in pendentes]


@router.get("/todas")
async def listar_todas(x_admin_secret: str = Header(None)):
    verificar_admin(x_admin_secret)
    db = get_db()
    todas = await db.usuarios.find({}).to_list(length=200)
    return [formatar_doc(u) for u in todas]


@router.put("/aprovar/{usuario_id}")
async def aprovar_usuario(usuario_id: str, x_admin_secret: str = Header(None)):
    verificar_admin(x_admin_secret)
    db = get_db()

    try:
        obj_id = ObjectId(usuario_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")

    usuario = await db.usuarios.find_one({"_id": obj_id})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuária não encontrada")

    await db.usuarios.update_one(
        {"_id": obj_id},
        {"$set": {"status": "ativo", "aprovado_em": datetime.utcnow()}}
    )

    # Notificação WhatsApp via Twilio (opcional — ignora erro se não configurado)
    try:
        telefone = usuario.get("telefone", "").strip()
        if telefone and os.getenv("TWILIO_ACCOUNT_SID"):
            twilio = TwilioClient(
                os.getenv("TWILIO_ACCOUNT_SID"),
                os.getenv("TWILIO_AUTH_TOKEN")
            )
            # Formata número para E.164
            numero = f"+55{telefone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')}"
            if not numero.startswith("+55+"):
                twilio.messages.create(
                    from_=os.getenv("TWILIO_WHATSAPP_FROM"),
                    to=f"whatsapp:{numero}",
                    body=(
                        f"✨ Olá, {usuario['nome']}!\n\n"
                        "Seu acesso à Yafah foi aprovado! 🌹\n\n"
                        "Acesse agora e comece a transformar seu negócio com IA.\n"
                        "https://yafah.vercel.app"
                    )
                )
    except Exception as e:
        print(f"⚠️ Twilio: {e}")  # Não falha o endpoint por erro de notificação

    return {"mensagem": f"Usuária {usuario['nome']} aprovada com sucesso"}


@router.put("/bloquear/{usuario_id}")
async def bloquear_usuario(usuario_id: str, x_admin_secret: str = Header(None)):
    verificar_admin(x_admin_secret)
    db = get_db()

    try:
        obj_id = ObjectId(usuario_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")

    await db.usuarios.update_one(
        {"_id": obj_id},
        {"$set": {"status": "bloqueado"}}
    )
    return {"mensagem": "Usuária bloqueada"}
