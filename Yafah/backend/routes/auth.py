from fastapi import APIRouter, HTTPException
from database import get_db
from models import LoginRequest
import re

router = APIRouter()


def normalizar_cpf_cnpj(valor: str) -> str:
    """Remove pontos, traços e barras para comparação"""
    return re.sub(r"[.\-/]", "", valor).strip()


@router.post("/login")
async def login(data: LoginRequest):
    db = get_db()
    
    nome_normalizado = data.nome.strip().lower()
    cpf_normalizado = normalizar_cpf_cnpj(data.cpf_cnpj)

    # Busca por nome (case-insensitive) e CPF/CNPJ
    usuario = await db.usuarios.find_one({
        "nome_lower": nome_normalizado,
        "cpf_cnpj_limpo": cpf_normalizado
    })

    # Fallback: busca por cpf_cnpj bruto no campo original
    if not usuario:
        todos = await db.usuarios.find({}).to_list(length=None)
        for u in todos:
            cpf_db = normalizar_cpf_cnpj(u.get("cpf_cnpj", ""))
            nome_db = u.get("nome", "").strip().lower()
            if cpf_db == cpf_normalizado and nome_db == nome_normalizado:
                usuario = u
                break

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuária não encontrada")

    if usuario.get("status") == "pendente":
        raise HTTPException(status_code=403, detail="Cadastro aguardando aprovação")

    if usuario.get("status") == "bloqueado":
        raise HTTPException(status_code=403, detail="Acesso bloqueado")

    return {
        "id": str(usuario["_id"]),
        "nome": usuario["nome"],
        "tipo_negocio": usuario.get("tipo_negocio"),
        "cidade": usuario.get("cidade"),
        "status": usuario["status"]
    }
