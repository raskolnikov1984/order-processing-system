# order-processing-system

Sistema de e-commerce usando una arquitectura de microservicios con comunicación asíncrona mediante RabbitMQ, orquestación con Docker Compose y gestión de bases de datos PostgreSQL con Alembic. Proyecto desarrollado en Python con usando Poetry como gestor dependencias.

# Requerimientos:

- Docker version 28.4.0
- Docker Compose version 2.39.4
- rake, version 13.3.0
- ruby 3.4.5 (2025-07-16)
- Python 3.13.7

# Componentes:

| Componente               | Tecnología            | Puerto     | Descripción                                   |
| ------------------------ | --------------------- | ---------- | --------------------------------------------- |
| **Message Broker**       | RabbitMQ 3-management | 5672/15672 | Colas de mensajes para comunicación asíncrona |
| **Order Service**        | Python/FastAPI        | 8010       | Gestión de pedidos y órdenes de compra        |
| **Inventory Service**    | Python/FastAPI        | 8011       | Control de stock y gestión de productos       |
| **Payment Service**      | Python/FastAPI        | 8012       | Procesamiento de pagos y transacciones        |
| **Notification Service** | Python/FastAPI        | 8013       | Envío de Notificaciones
| **Order Database**       | PostgreSQL 18         | (interno)  | `order_data` - Volúmen persistente            |
| **Inventory Database**   | PostgreSQL 18         | (interno)  | `inventory_data` - Volúmen persistente        |
| **Payment Database**     | PostgreSQL 18         | (interno)  | `payment_data` - Volúmen persistente          |

# Arquitectura

![Arquitectura](./images/architecture.png)

## Descripción

La estructura de directorios en `src/service_name/`` sigue principios de Clean Architecture y Domain-Driven Design adaptados para microservicios con FastAPI, optimizada para mantenibilidad, escalabilidad y claridad en el desarrollo colaborativo.

## Desglose por Directorio

### api/

**Propósito:** Capa de presentación y transporte
**Contenido:** Routers, endpoints HTTP y dependencias de FastAPI (Depends())

**Justificación:** Separación de responsabilidades: Los endpoints están desacoplados de la lógica de negocio
**Reusabilidad:** Las dependencias (get_async_session, get_rabbitmq_client) son compartidas entre endpoints
**Testing:** Facilita el mocking de peticiones HTTP sin tocar la lógica interna

### core/
**Propósito:** Configuración central y utilidades.
**Contenido:** Configuración de base de datos, conexiones, constantes

**Justificación:** Single Source of Truth: Todos los componentes usan la misma configuración
**Inyección de dependencias:** Centraliza la creación de sesiones y conexiones

## events/

**Propósito:** Comunicación asíncrona y event-driven architecture
**Contenido:** Modelos de eventos, publishers y cosumers de RabbitMQ
**Justificación:** Comunicación desacoplada: El servicio publica eventos sin conocer consumidores
**Evolución independiente:** Poder cambiar componentes sin modificar lógica de negocio

## models/

**Propósito:** Capa de datos y modelos de dominio
**Contenido:** schemas.py: Pydantic models para validación de entrada/salida, database.py: SQLAlchemy ORM models y queries, events.py: Modelos de eventos (DTOs para mensajería)
**Justificación:** Validación estricta: Pydantic asegura el contrato de la API
**Separación de concerns:** Los modelos de DB y de API evolucionan independientemente
**Tipado Seguro:** Refuerza la integridad de datos en toda la aplicación
services/
Propósito: Lógica de negocio pura
Contenido: db_create_order, db_get_order_status y reglas de negocio
Justificación:
Clean Business Logic: Independiente del framework (FastAPI) y del transporte (HTTP)
Reusabilidad: Los mismos servicios pueden ser llamados desde CLI, jobs o GraphQL
Testing unitario: Puedes probar lógica sin levantar servidor HTTP
main.py
Propósito: Punto de entrada y ensamblado de la aplicación
Justificación: Orquesta todos los componentes mantiene el bootstrapping mínimo
🎯 Beneficios Clave de esta Arquitectura
Table
Copy
Beneficio	Cómo se logra
Escalabilidad	Cada capa puede escalar independientemente (más workers de API, pool de conexiones a DB)
Mantenibilidad	Cambios en un componente no afectan otros (ej: modificar schemas no rompe la DB)
Testabilidad	Mocks específicos por capa (AsyncClient para API, AsyncMock para eventos)
Observabilidad	Logging centralizado en logger.py con contexto de cada capa
Evolución	Puedes migrar a gRPC o GraphQL cambiando solo api/, no toda la app
🔧 Decisiones Técnicas
AsyncIO en toda la pila: Desde API hasta queries SQLAlchemy, maximiza throughput
Event-Driven: publish_order_created() con asyncio.create_task() para no bloquear respuestas HTTP
Dependency Injection: FastAPI's Depends() + fábricas en core/ para testability
Migraciones como código: Alembic controla tanto schema como datos semilla
Esta estructura soporta fácilmente futuras expansiones como:
workers/ (consumidores de cola)
integrations/ (clientes de otros microservicios)
strategies/ (implementaciones de algoritmos de pricing, descuentos)

# Deploy

1. Clonar el repositorio

```
git clone <repository-url>
cd nombre-del-proyecto
```

2. Configurar variables de entorno personalizadas. En el momento de clonar el repositorio ya cuenta con un archivo .env estandar

```
POSTGRES_PASSWORD="SUp3r-pass*DB"

POSTGRES_ORDER_DB="order_service"
POSTGRES_INVENTORY_DB="inventory_service"
POSTGRES_PAYMENT_DB="payment_service"

ORDER_API_PORT=8010
INVENTORY_API_PORT=8011
PAYMENT_API_PORT=8012
NOTIFICATION_API_PORT=8013

AMQP_URL=amqp://guest:guest@rabbitmq:5672/
AMQP_PORT=5672
UI_PORT=15672
```

3. Desplegar el entorno completo.

```
# Construir y levantar todos los servicios
rake up

# El comando ejecuta:
# docker compose -f docker-compose.yml up --build -d
```

> Esto iniciará en orden: RabbitMQ → Bases de datos → Microservicios (con healthchecks)

# Comando Disponibles (Rake Tasks)

## Gestión Globla del Entorno

| Comando        | Descripción                                                               |
| -------------- | ------------------------------------------------------------------------- |
| `rake up`      | Construir y levantar todos los servicios.                 |
| `rake restart` | Reiniciar todos los contenedores                                          |
| `rake del`     | Eliminar contenedores, volúmenes Y eliminar **todas** las imágenes Docker |


## Order Service

| Comando                             | Descripción                                        |
| ----------------------------------- | -------------------------------------------------- |
| `rake order:sh`                     | Acceder a la shell bash del contenedor             |
| `rake order:tdd`                    | Ejecutar tests con pytest en modo verbose (`-vvv`) |
| `rake order:migrate['descripción']` | Crear y aplicar migración de BD con Alembic        |
| `rake order:tail`                   | Monitorear logs en tiempo real (últimas 50 líneas) |

## Inventory Service

| Comando               | Descripción                               |
| --------------------- | ----------------------------------------- |
| `rake inventory:sh`   | Acceder a la shell bash del contenedor    |
| `rake inventory:tdd`  | Ejecutar tests con pytest en modo verbose |
| `rake inventory:tail` | Monitorear logs en tiempo real            |

## Payment Service

| Comando                           | Descripción                                 |
| --------------------------------- | ------------------------------------------- |
| `rake pay:sh`                     | Acceder a la shell bash del contenedor      |
| `rake pay:tdd`                    | Ejecutar tests con pytest en modo verbose   |
| `rake pay:migrate['descripción']` | Crear y aplicar migración de BD con Alembic |
| `rake pay:tail`                   | Monitorear logs en tiempo real              |

## Notification Service

| Comando          | Descripción                               |
| ---------------- | ----------------------------------------- |
| `rake noti:sh`   | Acceder a la shell bash del contenedor    |
| `rake noti:tdd`  | Ejecutar tests con pytest en modo verbose |
| `rake noti:tail` | Monitorear logs en tiempo real            |

# Test

Ejecutar tests de un servicio

# Testear order-service
rake order:tdd

# Testear inventory-service
rake inventory:tdd

# Testear todos los servicios secuencialmente
```
rake order:tdd && rake inventory:tdd && rake pay:tdd && rake noti:tdd
```

# Migraciones
```
# Sintaxis: rake {service}:migrate['descripción']
rake order:migrate['add order_status column with index']
rake pay:migrate['add payment_method enum']

# Las migraciones se crean y aplican automáticamente en dos pasos:
# 1. alembic revision --autogenerate -m 'descripción'
# 2. alembic upgrade head
```
> Nota: El notification-service no tiene base de datos PostgreSQL configurada en docker-compose.yml, por lo que no tiene tarea migrate.


# Seed

Al Construir el entorno la tabla de Inventarios sera poblada con los siguiente informacion.

| ID | product_id | forecast_quantity |
|----|------------|-------------------|
| 1  | prod-1     | 150.0             |
| 2  | prod-2     | 200.0             |
| 3  | prod-3     | 75.5              |
| 4  | prod-4     | 300.0             |

# Crear una Orden

```
# Query

curl -X 'POST' \
  'http://localhost:8010/api/v1/create_order' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "customer_id": "Empresa-1",
  "customer_email": "empresa@empresa.org",
  "items": [
    {
      "product_id": "prod-1",
      "product_name": "prod",
      "quantity": 32,
      "price": 3000
    }
  ]
}'

# Response

{"message":"successful","order_id":12,"status":"PENDING"}
```

