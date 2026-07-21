from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, HTTPException, status, BackgroundTasks
from pymongo.errors import DuplicateKeyError
from src.models.earthquake import EarthquakeModel
from src.services.metrics_service import process_event_metrics
from src.database.mongodb import db_manager
from src.config.logging import setup_logger

logger = setup_logger("ingestion_service")

# Creamos el router para modularizar los endpoints de ingesta
router = APIRouter(prefix="/api/v1/events", tags=["Ingestión de Eventos"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def ingest_earthquake_event(event: EarthquakeModel, background_tasks: BackgroundTasks):
    """
    Endpoint de alta velocidad para la ingesta de sismos en tiempo real.
    Valida el payload entrante con Pydantic y lo persiste asíncronamente en MongoDB.
    """
    try:
        # Convertimos el modelo de Pydantic a un diccionario de Python compatible con MongoDB
        # Usamos 'by_alias=True' para guardar el campo 'id' como '_id' en Mongo
        event_dict = event.model_dump(by_alias=True, exclude_none=True)
        
        # Inserción asíncrona no bloqueante en la colección Earthquakes
        await db_manager.earthquakes_collection.insert_one(event_dict)
        logger.debug(f"Evento {event.event_id} insertado exitosamente en Earthquakes.")
        # Programamos el cálculo de métricas en segundo plano
        background_tasks.add_task(process_event_metrics, event)
        return {"status": "success", "message": "Event ingested successfully", "event_id": event.event_id}
        
    except DuplicateKeyError:
        # El índice único de MongoDB atajó un evento repetido. Respondemos con 409 Conflict.
        logger.warning(f"Intento de duplicación detectado para el event_id: {event.event_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El evento con ID {event.event_id} ya existe en el sistema."
        )
    except Exception as e:
        logger.error(f"Error interno al procesar la ingesta del evento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al persistir el evento."
        )
    
@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación.
    Garantiza que el pool de conexiones de red se abra al encender la API 
    y se cierre de forma limpia al apagar el contenedor.
    """
    # Fase de Inicialización (Startup)
    await db_manager.connect_to_mongo()
    logger.info("Servicio de Ingestión inicializado y escuchando en el puerto 8000...")
    yield
    
    # Fase de Apagado (Shutdown)
    await db_manager.close_mongo_connection()
    logger.info("Servicio de Ingestión apagado correctamente.")

# Instanciamos FastAPI inyectando el ciclo de vida y metadatos de documentación
app = FastAPI(
    title="Procesador de Eventos Sísmicos - API Ingestión",
    version="1.0.0",
    lifespan=app_lifespan
)

# Incluimos las rutas de ingesta de datos
app.include_router(router)

@app.get("/health", tags=["Monitoreo"])
async def health_check():
    """Endpoint utilitario para los Healthchecks de Docker."""
    return {"status": "healthy", "service": "ingestion-service"}