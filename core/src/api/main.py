from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.routes.earthquakes import router as earthquakes_router
from src.api.routes.metrics import router as metrics_router
from src.api.routes.reports import router as reports_router
from src.database.mongodb import db_manager
from src.config.logging import setup_logger

logger = setup_logger("query_main")

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """Gestión del ciclo de vida de conexión a la base de datos para la Query API."""
    await db_manager.connect_to_mongo()
    logger.info("Query API REST lista y escuchando en el puerto 8001...")
    yield
    await db_manager.close_mongo_connection()
    logger.info("Query API REST apagada correctamente.")

app = FastAPI(
    title="Procesador de Eventos Sísmicos - API de Consulta",
    version="1.0.0",
    description="API REST orientada exclusivamente a la lectura y consulta de colecciones en MongoDB.",
    lifespan=app_lifespan
)

# Inclusión independiente de los routers
app.include_router(earthquakes_router)
app.include_router(metrics_router)
app.include_router(reports_router)

@app.get("/health", tags=["Monitoreo"])
async def health_check():
    return {"status": "healthy", "service": "query-api"}