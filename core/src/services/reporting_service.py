from datetime import datetime, timedelta, timezone
from collections import Counter
from pymongo import MongoClient
from src.database.mongodb import db_manager
from src.models.report import ReportModel
from src.config.logging import setup_logger
from src.config.settings import MongoSettings

logger = setup_logger("services.reporting")

# Método auxiliar para obtener concretamente el lugar sin la dirección
def extract_state_or_country(location_str: str) -> str:
    if not location_str or location_str == "Ubicación Desconocida":
        return "Desconocido"
    
    if "," in location_str:
        return location_str.split(",")[-1].strip()
    
    return location_str.strip()

async def generate_hourly_report(reference_time: datetime = None) -> ReportModel:
    """
    Función síncrona/estándar diseñada para ser ejecutada por el PythonOperator de Airflow.
    Lee los eventos sísmicos de la última hora, genera el consolidado y lo guarda en 'Reports'.
    """
    settings = MongoSettings()
    
    # Airflow ejecuta tareas de manera síncrona en sus workers, por lo que usamos PyMongo directo para la tarea Batch.
    client = MongoClient(settings.mongo_uri)
    db = client[settings.mongo_db_name]
    
    try:
        # 1. Definir referencia en UTC
        if not reference_time:
            reference_time = datetime.now(timezone.utc)
        elif reference_time.tzinfo is None:
            reference_time = reference_time.replace(tzinfo=timezone.utc)
        start_time = reference_time - timedelta(hours=24)

        # 2. Consulta robusta con $or (Soporta ISO String y Datetime de Mongo)
        query = {
            "$or": [
                {
                    "event_time": {
                        "$gte": start_time,
                        "$lte": reference_time
                    }
                },
                {
                    "event_time": {
                        "$gte": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "$lte": reference_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                    }
                }
            ]
        }
        
        logger.info(f"Generando reporte batch para la ventana: {start_time.isoformat()} a {reference_time.isoformat()}")
        
        # 3. Extraer sismos para el reporte
        cursor = db_manager.earthquakes_collection.find(query)
        events = await cursor.to_list(length=10000)
        
        total_events = len(events)
        if total_events == 0:
            logger.warning("No se encontraron sismos en las últimas 24 horas para el reporte.")
            avg_mag = 0.0
            max_mag = 0.0
        else:
            mags = [float(e.get("magnitude", 0.0)) for e in events]
            avg_mag = round(sum(mags) / total_events, 2)
            max_mag = round(max(mags), 2)

        # --- EXTRACCIÓN Y CÁLCULO DE TOP LOCATIONS ---
        location_counts = Counter()
        for event in events:
            raw_place = event.get("location") or event.get("place", "")
            state_or_country = extract_state_or_country(raw_place)
            location_counts[state_or_country] += 1
        top_locations = [loc for loc, _ in location_counts.most_common()]

        # 4. Estructurar ID y Modelo del Reporte
        report_id = f"report_{reference_time.strftime('%Y%m%d_%H00')}"
        
        report_data = {
            "_id": report_id,
            "report_date": reference_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_events": total_events,
            "average_magnitude": avg_mag,
            "max_magnitude": max_mag,
            "top_locations": top_locations
        }

        # 5. Persistir en la colección 'Reports' (Upsert: Actualiza si existe, crea si no)
        await db_manager.reports_collection.replace_one(
            {"_id": report_id},
            report_data,
            upsert=True
        )

        logger.info(f"¡ÉXITO! Reporte {report_id} generado correctamente con {total_events} eventos.")
        return report_data

    except Exception as e:
        logger.error(f"Error durante la generación del reporte batch: {str(e)}")
        raise e
    finally:
        client.close()