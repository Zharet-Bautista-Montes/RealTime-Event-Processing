from typing import List
from fastapi import APIRouter, HTTPException, status
from src.models.report import ReportModel
from src.database.mongodb import db_manager
from src.config.logging import setup_logger

logger = setup_logger("api.reports_router")

router = APIRouter(prefix="/reports", tags=["Consulta de Reportes"])

@router.get("", response_model=List[ReportModel], status_code=status.HTTP_200_OK)
async def get_all_reports():
    # Retorna la totalidad de los reportes históricos consolidados almacenados en la colección Reports.
    try:
        cursor = db_manager.reports_collection.find()
        reports_list = await cursor.to_list(length=None)
        logger.info(f"Consulta exitosa: se recuperaron {len(reports_list)} reportes.")
        return reports_list
    except Exception as e:
        logger.error(f"Error al consultar la colección Reports: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al consultar los reportes."
        )