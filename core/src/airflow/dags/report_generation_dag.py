import asyncio
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

def execute_report_task():
    """
    Wrapper síncrono que crea un Event Loop aislado y re-conecta 
    el cliente asíncrono de MongoDB dentro de ese mismo loop.
    """
    async def _async_runner():
        # Importamos e inicializamos la base de datos dentro del loop activo
        from src.database.mongodb import db_manager
        from src.services.reporting_service import generate_hourly_report
        
        if hasattr(db_manager, 'connect_to_database'):
            await db_manager.connect_to_database()
        try:
            await generate_hourly_report()
        finally:
            if hasattr(db_manager, 'close_database_connection'):
                await db_manager.close_database_connection()

    asyncio.run(_async_runner())

# Configuración por defecto para las tareas del DAG
default_args = {
    'owner': 'sismic_team',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),  
    'retries': 1,                        
    'retry_delay': timedelta(minutes=1)  
}

# Declaración del DAG
with DAG(
    dag_id='hourly_earthquake_report_dag', 
    default_args=default_args,
    description='DAG programado cada hora para consolidar sismos y generar reportes analíticos',
    schedule_interval='@hourly',           
    catchup=False,                         
    tags=['sismologia', 'reports', 'batch']
) as dag:

    generate_report_task = PythonOperator(
        task_id='generate_earthquake_report',
        python_callable=execute_report_task  
    )