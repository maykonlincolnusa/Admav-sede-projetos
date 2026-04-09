from fastapi import APIRouter, HTTPException, Header
from database import get_collection
from models import FinanceEntry, FinanceSummary
from datetime import datetime, timedelta
from bson import ObjectId
import math

router = APIRouter()

@router.post("/finance/add")
async def add_record(data: FinanceEntry, x_user_id: str = Header(None)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Usuária não identificada")
    
    finances_col = get_collection("finances")
    doc = data.dict()
    doc["usuario_id"] = x_user_id
    doc["criado_em"] = datetime.utcnow()
    
    result = await finances_col.insert_one(doc)
    return {"mensagem": "Registro financeiro salvo", "id": str(result.inserted_id)}

@router.get("/finance/summary", response_model=FinanceSummary)
async def get_summary(x_user_id: str = Header(None)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Usuária não identificada")
    
    finances_col = get_collection("finances")
    
    pipeline = [
        {"$match": {"usuario_id": x_user_id}},
        {"$group": {
            "_id": "$tipo",
            "total": {"$sum": "$valor"}
        }}
    ]
    
    results = await finances_col.aggregate(pipeline).to_list(length=100)
    
    summary = {"total_receita": 0.0, "total_despesa": 0.0, "lucro": 0.0, "margem_lucro": 0.0, "forecast_next_month": 0.0}
    
    for res in results:
        if res["_id"] == "receita":
            summary["total_receita"] = res["total"]
        elif res["_id"] == "despesa":
            summary["total_despesa"] = res["total"]
            
    summary["lucro"] = summary["total_receita"] - summary["total_despesa"]
    if summary["total_receita"] > 0:
        summary["margem_lucro"] = round((summary["lucro"] / summary["total_receita"]) * 100, 2)
        
    # --- Basic ML Forecasting via Time Series Mock / Trend Analysis ---
    # Para Prophet precisaríamos de N dados diários. Vamos simular uma Regressão Linear sobre os dados dos últimos 3 meses
    # Pega os últimos 90 dias de receita
    ninety_days_ago = datetime.utcnow() - timedelta(days=90)
    recent_pipeline = [
        {"$match": {"usuario_id": x_user_id, "tipo": "receita", "data": {"$gte": ninety_days_ago}}},
        {"$group": {"_id": None, "total": {"$sum": "$valor"}, "count": {"$sum": 1}}}
    ]
    recent_results = await finances_col.aggregate(recent_pipeline).to_list(length=1)
    
    if recent_results and recent_results[0]["total"] > 0:
        # Crescimento orgânico heurístico básico (Isolation Forest/Prophet serveriam aqui com sklearn local)
        # Aqui injetamos uma previsão 8% superior baseada na média diária gerada
        media_dia = recent_results[0]["total"] / 90
        summary["forecast_next_month"] = round(media_dia * 30 * 1.08, 2)
    else:
        # Sem dados recentes, forecast baseia-se na receita global atual dividida proativamente
        summary["forecast_next_month"] = round((summary["total_receita"] * 1.05) if summary["total_receita"] > 0 else 0, 2)

    return summary

@router.get("/finance/history")
async def get_history(x_user_id: str = Header(None)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Usuária não identificada")
    
    finances_col = get_collection("finances")
    
    docs = await finances_col.find(
        {"usuario_id": x_user_id}
    ).sort("data", -1).to_list(length=100)
    
    return [{
        "id": str(d["_id"]),
        "valor": d["valor"],
        "tipo": d["tipo"],
        "categoria": d["categoria"],
        "descricao": d.get("descricao", ""),
        "data": d["data"].isoformat() if isinstance(d["data"], datetime) else d["data"]
    } for d in docs]

@router.delete("/finance/{record_id}")
async def delete_record(record_id: str, x_user_id: str = Header(None)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Usuária não identificada")
    
    finances_col = get_collection("finances")
    try:
        obj_id = ObjectId(record_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de registro inválido")
        
    result = await finances_col.delete_one({"_id": obj_id, "usuario_id": x_user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
        
    return {"mensagem": "Registro removido"}

