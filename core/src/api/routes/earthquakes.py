from typing import List
from fastapi import APIRouter, HTTPException, status
from src.models.earthquake import EarthquakeModel
from src.database.mongodb import db_manager
from src.config.logging import setup_logger

logger = setup_logger("api.earthquakes")

router = APIRouter(prefix="/earthquakes", tags=["Consulta de Sismos"])

@router.get("", response_model=List[EarthquakeModel], status_code=status.HTTP_200_OK)
async def get_all_earthquakes():
    # Retorna la totalidad de los registros de sismos almacenados en la colección Earthquakes.
    try:
        cursor = db_manager.earthquakes_collection.find()
        earthquakes_list = await cursor.to_list(length=None)
        logger.info(f"Consulta exitosa: se recuperaron {len(earthquakes_list)} sismos.")
        return earthquakes_list
    except Exception as e:
        logger.error(f"Error al consultar la colección Earthquakes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al consultar los eventos sísmicos."
        )