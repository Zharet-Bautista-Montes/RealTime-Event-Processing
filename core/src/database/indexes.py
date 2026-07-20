import asyncio
import sys
from pymongo import ASCENDING, DESCENDING
from src.database.mongodb import db_manager
from src.config.logging import setup_logger

# Instanciamos el logger dedicado para la tarea de indexación
logger = setup_logger("database.indexes")

async def ensure_database_indexes():
    """Script encargado de sincronizar y validar los índices requeridos."""
    try:
        logger.info("Iniciando la rutina de verificación de índices en MongoDB...")
        
        # Reutilizamos la conexión limpia del mánager
        await db_manager.connect_to_mongo()
        
        # 1. Colección Earthquakes
        logger.info("Verificando índices de 'Earthquakes'...")
        await db_manager.earthquakes_collection.create_index(
            "event_id", unique=True, name="idx_unique_event_id"
        )
        await db_manager.earthquakes_collection.create_index(
            [("location", ASCENDING), ("event_time", DESCENDING)],
            name="idx_location_time_search"
        )
        
        # 2. Colección Metrics
        logger.info("Verificando índices de 'Metrics'...")
        await db_manager.metrics_collection.create_index(
            [("window", DESCENDING)], name="idx_metrics_window_timeline"
        )

        # 3. Colección Reports
        logger.info("Verificando índices de 'Reports'...")
        await db_manager.reports_collection.create_index(
            [("report_date", DESCENDING)], unique=True, name="idx_unique_report_date"
        )

        logger.info("¡Todos los índices operativos y optimizados!")

    except Exception as e:
        logger.error(f"Error crítico abortando la creación de índices: {str(e)}")
        sys.exit(1)
    finally:
        # Garantizamos el cierre de sockets pase lo que pase
        await db_manager.close_mongo_connection()

if __name__ == "__main__":
    # Comando de ejecución: python -m src.database.indexes
    asyncio.run(ensure_database_indexes())