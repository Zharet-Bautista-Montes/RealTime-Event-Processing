import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class MongoSettings(BaseSettings):
    """Configuración de conexión a MongoDB mediante Pydantic V2 BaseSettings."""

    load_dotenv()
    mongo_uri: str = Field(
        default=os.getenv("MONGO_URI", "mongodb://172.20.0.10:27017/events_db"),
        validation_alias="MONGO_URI"
    )
    mongo_db_name: str = Field(
        default=os.getenv("MONGO_DB_NAME", "events_db"),
        validation_alias="MONGO_DB_NAME"
    )
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

class Settings(BaseSettings):
    """Configuración general de la aplicación."""
    
    app_name: str = Field(default="USGS Sismic Ingestion Engine")
    debug: bool = Field(default=False, validation_alias="DEBUG")
    
    # Instancia anidada para configuraciones de MongoDB
    mongo: MongoSettings = Field(default_factory=MongoSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instancia global accesible para importar en el proyecto
settings = Settings()
mongo_settings = MongoSettings()