from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from src.services.reporting_service import generate_hourly_report

# Configuración por defecto para las tareas del DAG
default_args = {
    'owner': 'technical_leader',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),  
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,                        
    'retry_delay': timedelta(minutes=5)  
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
        task_id='generate_hourly_report_task',
        python_callable=generate_hourly_report  
    )

    generate_report_task