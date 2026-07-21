from pydantic import BeforeValidator, Field
from typing_extensions import Annotated

# 1. Validador Reutilizable para el ID de MongoDB
# Convierte objetos ObjectId de Mongo a strings legibles por las APIs
PyObjectId = Annotated[str, BeforeValidator(lambda v: str(v) if v is not None else v)]

# 2. Validador Reutilizable para Magnitudes Sísmicas
# Forzamos a que cualquier campo que use este tipo sea un flotante >= 0
SismicMagnitude = Annotated[
    float, 
    Field(..., description="Magnitud sísmica validada (debe ser >= 0.0)", ge=0.0)
]

# 3. Validador Reutilizable para Contadores de Eventos
# Asegura que los contadores sean siempre enteros no negativos
EventCounter = Annotated[
    int,
    Field(..., description="Contador total de eventos (debe ser >= 0)", ge=0)
]