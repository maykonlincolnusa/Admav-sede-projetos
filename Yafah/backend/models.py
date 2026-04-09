from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class StatusUsuario(str, Enum):
    pendente = "pendente"
    ativo = "ativo"
    bloqueado = "bloqueado"


class NivelUsuario(str, Enum):
    iniciante = "iniciante"
    intermediaria = "intermediaria"
    avancada = "avancada"


# ── Auth ──────────────────────────────────────────────
class LoginRequest(BaseModel):
    nome: str
    cpf_cnpj: str


# ── Cadastro ──────────────────────────────────────────
class CadastroRequest(BaseModel):
    nome: str
    cpf_cnpj: str
    email: EmailStr
    telefone: str
    tipo_negocio: str
    cidade: str
    instagram: Optional[str] = None
    como_ajudar: Optional[str] = None


# ── Chat ──────────────────────────────────────────────
class MensagemChat(BaseModel):
    mensagem: str
    usuario_id: str


class MensagemHistorico(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ── Feedback ──────────────────────────────────────────
class FeedbackRequest(BaseModel):
    usuario_id: str
    conversa_id: str
    estrelas: int = Field(ge=1, le=5)
    comentario: Optional[str] = None


# ── Knowledge Base ────────────────────────────────────
class KnowledgeAddText(BaseModel):
    texto: str
    fonte: str = "maykon"
    categoria: str        # financeiro / marketing / vendas / gestao / tendencias
    subcategoria: Optional[str] = None


class KnowledgeAddUrl(BaseModel):
    url: str
    categoria: str
    subcategoria: Optional[str] = None


class KnowledgeAddSocial(BaseModel):
    handle: str
    rede: str  # "instagram" ou "tiktok"
    categoria: str = "Social Media"


# ── Admin ─────────────────────────────────────────────
class StatusUpdate(BaseModel):
    usuario_id: str


# ── Finance ───────────────────────────────────────────
class FinanceEntry(BaseModel):
    usuario_id: str
    valor: float
    tipo: str  # "receita" ou "despesa"
    categoria: str
    descricao: Optional[str] = None
    data: datetime = Field(default_factory=datetime.utcnow)


class FinanceSummary(BaseModel):
    total_receita: float
    total_despesa: float
    lucro: float
    margem_lucro: Optional[float] = 0.0
    forecast_next_month: Optional[float] = 0.0
