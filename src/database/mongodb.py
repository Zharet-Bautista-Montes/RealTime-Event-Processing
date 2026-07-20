from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
from src.config.logging import setup_logger

# Obtenemos nuestro logger estructurado usando el módulo centralizado
logger = setup_logger("database.mongodb")

class MongoSettings(BaseSettings):
    MONGO_URI: str = "mongodb://172.20.0.10:27017/events_db"
    DB_NAME: str = "events_db"

class MongoDBManager:
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db = None
        self.earthquakes_collection = None
        self.metrics_collection = None
        self.reports_collection = None

    async def connect_to_mongo(self):
        """Inicializa el pool de conexiones asíncronas con MongoDB."""
        settings = MongoSettings()
        try:
            logger.info(f"Abriendo pool de conexiones asíncronas hacia {settings.MONGO_URI}")
            
            self.client = AsyncIOMotorClient(
                settings.MONGO_URI,
                maxPoolSize=50,
                minPoolSize=10
            )
            self.db = self.client[settings.DB_NAME]
            
            # Mapeo oficial de colecciones
            self.earthquakes_collection = self.db["Earthquakes"]
            self.metrics_collection = self.db["Metrics"]
            self.reports_collection = self.db["Reports"]
            
            logger.info("¡Pool de conexiones con MongoDB establecido de forma segura!")
        except Exception as e:
            logger.critical(f"Fallo catastrófico al conectar a la base de datos: {str(e)}")
            raise e

    async def close_mongo_connection(self):
        """Cierra de forma limpia el pool de conexiones."""
        if self.client:
            self.client.close()
            logger.info("Pool de conexiones con MongoDB liberado correctamente.")

# Instancia Singleton compartida
db_manager = MongoDBManager()