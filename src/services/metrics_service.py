from datetime import timedelta
import math
from src.models.metric import EarthquakeModel, MetricModel
from src.database.mongodb import db_manager
from src.config.logging import setup_logger

logger = setup_logger("services.metrics")

def calculate_magnitude_range_bucket(magnitude: float) -> str:
    """
    Calcula el rango de 1.0 unidad correspondiente para una magnitud dada.
    Ejemplo: 3.4 -> "3.0-3.9"
    """
    floor_val = math.floor(magnitude)
    return f"{floor_val}.0-{floor_val}.9"

async def process_event_metrics(event: EarthquakeModel) -> MetricModel:
    """
    Recibe un evento recién ingresado, calcula las métricas de la última hora
    y las persiste en la colección 'Metrics'.
    """
    try:
        event_time = event.event_time
        one_hour_ago = event_time - timedelta(hours=1)

        # 1. Pipeline de agregación en MongoDB para consultar la ventana de la última hora
        # Usamos el índice de 'event_time' para que sea instantáneo
        cursor = db_manager.earthquakes_collection.find({
            "event_time": {
                "$gte": one_hour_ago,
                "$lte": event_time
            }
        })
        
        recent_events = await cursor.to_list(length=10000)

        if not recent_events:
            logger.warning(f"No se encontraron eventos en la ventana para {event.event_id}")
            return None

        # 2. Cómputo de Métricas en memoria
        total_count = len(recent_events)
        sum_magnitude = 0.0
        max_mag = 0.0
        distribution = {}

        for eq in recent_events:
            mag = float(eq.get("magnitude", 0.0))
            sum_magnitude += mag
            if mag > max_mag:
                max_mag = mag
            
            # Clasificación en el cubo de distribución ("0.0-0.9", "1.0-1.9", etc.)
            bucket = calculate_magnitude_range_bucket(mag)
            distribution[bucket] = distribution.get(bucket, 0) + 1

        avg_mag = round(sum_magnitude / total_count, 2) if total_count > 0 else 0.0

        # 3. Construcción e Identificación de la Métrica
        # Creamos un ID basado en el timestamp truncado por hora para evitar duplicación
        metric_id = f"window_{event_time.strftime('%Y%m%d_%H00')}"

        metric_data = MetricModel(
            _id=metric_id,
            window=event_time,
            earthquake_count=total_count,
            avg_magnitude=avg_mag,
            max_magnitude=round(max_mag, 2),
            magnitude_distribution=distribution
        )

        # 4. Persistencia en la colección 'Metrics' (Upsert: Actualiza si existe, crea si no)
        metric_dict = metric_data.model_dump(by_alias=True)
        await db_manager.metrics_collection.replace_one(
            {"_id": metric_id},
            metric_dict,
            upsert=True
        )

        logger.info(f"Métrica recalculada para ventana {metric_id}: {total_count} sismos en la última hora.")
        return metric_data

    except Exception as e:
        logger.error(f"Error procesando métricas para el evento {event.event_id}: {str(e)}")
        raise e