from fastapi import APIRouter, HTTPException
from database import get_db
from models import CadastroRequest
from datetime import datetime
import re

router = APIRouter()


def normalizar(valor: str) -> str:
    return re.sub(r"[.\-/]", "", valor).strip()


@router.post("/cadastro")
async def cadastro(data: CadastroRequest):
    db = get_db()

    cpf_limpo = normalizar(data.cpf_cnpj)

    # Verifica duplicata
    existente = await db.usuarios.find_one({"cpf_cnpj_limpo": cpf_limpo})
    if existente:
        raise HTTPException(
            status_code=409,
            detail="Já existe um cadastro com esse CPF/CNPJ"
        )

    novo_usuario = {
        "nome": data.nome.strip(),
        "nome_lower": data.nome.strip().lower(),
        "cpf_cnpj": data.cpf_cnpj,
        "cpf_cnpj_limpo": cpf_limpo,
        "email": data.email,
        "telefone": data.telefone,
        "tipo_negocio": data.tipo_negocio,
        "cidade": data.cidade,
        "instagram": data.instagram or "",
        "como_ajudar": data.como_ajudar or "",
        "status": "pendente",
        "criado_em": datetime.utcnow(),
        "aprovado_em": None
    }

    resultado = await db.usuarios.insert_one(novo_usuario)

    return {
        "mensagem": "Cadastro enviado com sucesso! Aguarde aprovação.",
        "id": str(resultado.inserted_id)
    }
