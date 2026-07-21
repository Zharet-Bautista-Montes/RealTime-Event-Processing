from motor.motor_asyncio import AsyncIOMotorClient
from src.config.logging import setup_logger
from src.config.settings import mongo_settings

logger = setup_logger("database.mongodb")

class MongoDBManager:

    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db = None

    async def connect_to_mongo(self):
        """Inicializa la conexión asíncrona a MongoDB usando Motor."""
        if self.client is None:
            logger.info(f"Conectando a MongoDB en: {mongo_settings.mongo_uri}")
            self.client = AsyncIOMotorClient(mongo_settings.mongo_uri)
            self.db = self.client[mongo_settings.mongo_db_name]
            logger.info(
                f"Conexión exitosa a la base de datos: '{mongo_settings.mongo_db_name}'"
            )

    async def close_mongo_connection(self):
        """Cierra la conexión con la base de datos."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("Conexión a MongoDB cerrada.")

    # Acceso directo a las colecciones principales
    @property
    def earthquakes_collection(self):
        if self.db is None:
            # Fallback de inicialización perezosa si se accede sin llamar explicitamente a connect_to_database
            self.client = AsyncIOMotorClient(mongo_settings.mongo_uri)
            self.db = self.client[mongo_settings.mongo_db_name]
        return self.db["Earthquakes"]

    @property
    def metrics_collection(self):
        if self.db is None:
            self.client = AsyncIOMotorClient(mongo_settings.mongo_uri)
            self.db = self.client[mongo_settings.mongo_db_name]
        return self.db["Metrics"]

    @property
    def reports_collection(self):
        if self.db is None:
            self.client = AsyncIOMotorClient(mongo_settings.mongo_uri)
            self.db = self.client[mongo_settings.mongo_db_name]
        return self.db["Reports"]


# Instancia única reutilizable en todo el proyecto (Ingesta, Métricas, Reportes y DAGs)
db_manager = MongoDBManager()