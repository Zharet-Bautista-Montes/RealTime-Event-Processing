# RealTime Event Processing Engine — USGS Earthquakes 🌋

Sistema distribuido de ingesta, procesamiento de eventos sísmicos en tiempo real y análisis batch orquestado. Consume datos de la USGS (United States Geological Survey), calcula métricas acumulativas en ventanas de tiempo y genera reportes periódicos automatizados.

---

## 🚀 Requisitos Previos

- Docker Engine (v20.10+)

- Docker Compose (v2.0+)

- Git

## ⚙️ Despliegue y Ejecución

- Clonar el repositorio:

```Bash
git clone [https://github.com/Zharet-Bautista-Montes/RealTime-Event-Processing.git](https://github.com/Zharet-Bautista-Montes/RealTime-Event-Processing.git)
cd RealTime-Event-Processing/core
```

- Configurar variables de entorno:
Crea un archivo .env en la raíz del proyecto tomando como base el siguiente formato:

```.env
MONGO_URI=mongodb://admin:admin_password123@mongodb:27017/events_db?authSource=admin
MONGO_DB_NAME=events_db
AIRFLOW_PORT=8080
AIRFLOW_SERVERS_USER=admin
AIRFLOW_SERVERS_PASSWORD=admin_secure_pass123
AIRFLOW_SERVERS_EMAIL=admin@example.com
```

- Iniciar Docker Desktop:

```Bash
C:\Program Files\Docker\Docker\Docker Desktop.exe ---Windows

systemctl --user start docker-desktop ---Linux
```

- Iniciar la infraestructura con Docker Compose:

```Bash
docker compose up -d --build
```

- Verificar estado de los contenedores:

```Bash
docker compose ps
```

## 📊 Endpoints de la API & Consultas Disponibles

1. Ingesta de Eventos

POST http://localhost:8000/api/v1/events

Recibe y persiste un nuevo sismo. Programa el cálculo inmediato de métricas en tiempo real.

Ejemplo:

```JSON
{
  "event_id": "us7000m123",
  "magnitude": 4.5,
  "place": "12 km SW of Anchor Point, Alaska",
  "event_time": "2026-07-20T23:00:00Z"
}
```

2. Consulta de Eventos

GET http://localhost:8001/earthquakes

Consulta el listado histórico de sismos registrados. 

Ejemplo:

```JSON
[
  {
    "_id": "6a5ed8a7a7c715d0d4e0a9c7",
    "event_id": "ci40658626",
    "magnitude": 1.23041752621257,
    "location": "14 km SE of Anza, CA",
    "event_time": "2026-07-21T02:22:06"
  }
]
```

3. Consulta de Métricas

GET http://localhost:8001/metrics

Retorna el acumulado de métricas calculadas por ventanas de tiempo (total de eventos, magnitud promedio, máxima y distribución por rangos).

Ejemplo:

```JSON
[
  {
    "_id": "window_20260721_0200",
    "window": "2026-07-21T02:22:06Z",
    "earthquake_count": 7,
    "avg_magnitude": 1.54,
    "max_magnitude": 2.72,
    "magnitude_distribution": {
      "2.0-2.9": 1,
      "0.0-0.9": 1,
      "1.0-1.9": 5
    }
  }
]
```

4. Reportes Consolidados (Airflow Output):

GET http://localhost:8001/reports

Devuelve los reportes consolidados generados por los DAGs de Airflow.

Ejemplo:

```JSON
[
  {
    "_id": "report_20260721_0200",
    "generated_at": "2026-07-21T02:00:00Z",
    "total_events": 41,
    "avg_magnitude": 1.84,
    "max_magnitude": 5.2,
    "top_locations": [
      "California",
      "Alaska",
      "Nevada",
      "Puerto Rico"
    ]
  }
]
```

## 🛠️ Monitoreo y UI de Airflow
Puedes acceder a la consola web de Apache Airflow para monitorear o disparar manualmente la ejecución del DAG de reportes:

URL: http://localhost:8080

Usuario: admin (o el configurado en .env)

Contraseña: admin (o el configurado en .env)

## 📄 Recursos Adicionales

En la raíz del proyecto podrán encontrar además el diagrama de su arquitectura y la colección de peticiones de Postman para validar pruebas. 