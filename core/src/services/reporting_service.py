import asyncio
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from src.config.logging import setup_logger
from src.config.settings import MongoSettings

logger = setup_logger("services.reporting")

def generate_hourly_report():
    """
    Función síncrona/estándar diseñada para ser ejecutada por el PythonOperator de Airflow.
    Lee los eventos sísmicos de la última hora, genera el consolidado y lo guarda en 'Reports'.
    """
    settings = MongoSettings()
    
    # Airflow ejecuta tareas de manera síncrona en sus workers, 
    # por lo que usamos PyMongo directo para la tarea Batch.
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.DB_NAME]
    
    try:
        # Definimos la ventana de la última hora
        now = datetime.now(timezone.utc)
        one_hour_ago = now - timedelta(hours=1)
        
        logger.info(f"Generando reporte batch para la ventana: {one_hour_ago.isoformat()} a {now.isoformat()}")
        
        # 1. Leer los sismos de la última hora desde la colección 'Earthquakes'
        query = {
            "event_time": {
                "$gte": one_hour_ago,
                "$lte": now
            }
        }
        earthquakes = list(db["Earthquakes"].find(query))
        
        total_events = len(earthquakes)
        logger.info(f"Se encontraron {total_events} eventos en el periodo.")
        
        if total_events == 0:
            # Si no hubo sismos, creamos un reporte neutral
            report_doc = {
                "report_date": now,
                "total_events": 0,
                "average_magnitude": 0.0,
                "max_magnitude": 0.0,
                "top_locations": []
            }
        else:
            # 2. Calcular agregados
            sum_mag = sum(float(eq.get("magnitude", 0.0)) for eq in earthquakes)
            max_mag = max(float(eq.get("magnitude", 0.0)) for eq in earthquakes)
            avg_mag = round(sum_mag / total_events, 2)
            
            # 3. Calcular las ubicaciones más frecuentes (Top Locations)
            location_counts = {}
            for eq in earthquakes:
                loc = eq.get("location", "Desconocida")
                location_counts[loc] = location_counts.get(loc, 0) + 1
            
            # Ordenamos por cantidad de apariciones y tomamos las 3 principales
            top_locs = sorted(location_counts, key=location_counts.get, reverse=True)[:3]
            
            report_doc = {
                "report_date": now,
                "total_events": total_events,
                "average_magnitude": avg_mag,
                "max_magnitude": round(max_mag, 2),
                "top_locations": top_locs
            }
        
        # 4. Guardar en la colección 'Reports'
        result = db["Reports"].insert_one(report_doc)
        logger.info(f"¡Reporte guardado exitosamente con _id: {result.inserted_id}!")
        return str(result.inserted_id)

    except Exception as e:
        logger.error(f"Error durante la generación del reporte batch: {str(e)}")
        raise e
    finally:
        client.close()