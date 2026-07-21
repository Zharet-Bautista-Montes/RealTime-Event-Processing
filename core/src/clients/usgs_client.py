import asyncio
import httpx
from datetime import datetime, timezone
from src.config.logging import setup_logger
from src.models.earthquake import EarthquakeModel  

logger = setup_logger("usgs_client")

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
INGESTION_API_URL = "http://172.20.0.20:8000/api/v1/events"  

async def fetch_and_ingest_earthquakes():
    """
    Consume el feed de la USGS, extrae los sismos, los transforma 
    al formato del EventModel y los envía hacia la API de Ingesta.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            logger.info(f"Consultando sismos recientes desde el servicio USGS...")
            response = await client.get(USGS_URL)
            response.raise_for_status()
            
            geojson_data = response.json()
            features = geojson_data.get("features", [])
            logger.info(f"Se detectaron {len(features)} sismos en la última hora de la USGS.")
            
            success_count = 0
            
            for feature in features:
                properties = feature.get("properties", {})
                
                # --- TRANSFORMACIÓN DE DATOS AL ESQUEMA DE NUESTRO EVENTMODEL ---
                # La USGS entrega el tiempo en milisegundos Unix epoch, lo pasamos a datetime UTC
                raw_time_ms = properties.get("time")
                if raw_time_ms:
                    dt_utc = datetime.fromtimestamp(raw_time_ms / 1000.0, tz=timezone.utc)
                    event_time_iso = dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
                else:
                    event_time_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                
                payload = {
                    "event_id": feature.get("id"),  # Ej: "us6000m1ax"
                    "magnitude": float(properties.get("mag") or 0.0),
                    "location": properties.get("place", "Ubicación Desconocida"),
                    "event_time": event_time_iso
                }
                
                try:
                    # Validamos localmente en el cliente antes de enviar para ahorrar ancho de banda
                    validated_event = EarthquakeModel(**payload)
                    
                    # Enviamos el JSON validado mediante POST asíncrono a nuestro componente de Ingesta
                    api_response = await client.post(
                        INGESTION_API_URL, 
                        json=validated_event.model_dump(by_alias=True, mode="json")
                    )
                    
                    if api_response.status_code == 201:
                        success_count += 1
                    elif api_response.status_code == 409:
                        # Si devuelve 409 es porque nuestro índice único de MongoDB atajó un ID duplicado
                        logger.debug(f"Sismo {payload['event_id']} ya procesado previamente.")
                        
                except Exception as val_error:
                    # Si el sismo tiene magnitud negativa o datos corruptos, nuestro validador lo filtra aquí
                    logger.warning(f"Sismo omitido por reglas de validación: {str(val_error)}")
                    continue
            
            logger.info(f"Proceso completado. Enviados con éxito {success_count} sismos nuevos a la API.")
            
        except httpx.HTTPError as http_err:
            logger.error(f"Error de red al conectar con servicios externos: {str(http_err)}")
        except Exception as e:
            logger.error(f"Error inesperado en el cliente de ingesta: {str(e)}")

async def main_loop():
    """Loop infinito para ejecutar el cliente como un Daemon cada 5 minutos"""
    logger.info("Iniciando Demonio de Ingesta de Sismos (USGS Client)...")
    while True:
        await fetch_and_ingest_earthquakes()
        logger.info("Esperando 3 minutos para la siguiente ráfaga de datos...")
        await asyncio.sleep(180)  # Pausa no bloqueante de 3 minutos

if __name__ == "__main__":
    asyncio.run(main_loop())