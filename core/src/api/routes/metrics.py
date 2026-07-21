from typing import List
from fastapi import APIRouter, HTTPException, status
from src.models.metric import MetricModel
from src.database.mongodb import db_manager
from src.config.logging import setup_logger

logger = setup_logger("api.metrics_router")

router = APIRouter(prefix="/metrics", tags=["Consulta de Métricas"])

@router.get("", response_model=List[MetricModel], status_code=status.HTTP_200_OK)
async def get_all_metrics():
    # Retorna la totalidad de las métricas y agregados en tiempo real almacenados en la colección Metrics.
    try:
        cursor = db_manager.metrics_collection.find()
        metrics_list = await cursor.to_list(length=None)
        logger.info(f"Consulta exitosa: se recuperaron {len(metrics_list)} registros de métricas.")
        return metrics_list
    except Exception as e:
        logger.error(f"Error al consultar la colección Metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al consultar las métricas."
        )