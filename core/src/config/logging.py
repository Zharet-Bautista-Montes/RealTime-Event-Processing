import logging
import sys
from pydantic_settings import BaseSettings

class LoggingSettings(BaseSettings):
    """Permite cambiar el nivel de log dinámicamente según el entorno."""
    LOG_LEVEL: str = "INFO"

def setup_logger(module_name: str) -> logging.Logger:
    """
    Configura y retorna un logger estandarizado con salida estructurada hacia stdout.
    """
    settings = LoggingSettings()
    logger = logging.getLogger(module_name)
    
    # Evitamos duplicación de logs si el logger ya fue configurado
    if not logger.handlers:
        logger.setLevel(settings.LOG_LEVEL.upper())
        
        # Formato limpio y profesional para producción (Fecha [Nivel] Módulo: Mensaje)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Redirección obligatoria a stdout para que Docker capture los flujos de logs
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Previene que los mensajes se propaguen al logger raíz duplicándose
        logger.propagate = False
        
    return logger