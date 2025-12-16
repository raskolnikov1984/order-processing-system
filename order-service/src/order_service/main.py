from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from src.order_service.api.v1.endpoints import orders
from src.order_service.core.config import settings
from src.order_service.events.consumers import start_consumers
from src.order_service.api.dependencies import rabbitmq_client
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Iniciando Order Service...")

    # Conectar RabbitMQ
    await rabbitmq_client.connect()

    # Iniciar consumidores en background
    asyncio.create_task(start_consumers())

    yield

    # Shutdown
    print("🔻 Apagando Order Service...")

    await rabbitmq_client.disconnect()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    orders.router, prefix=f"{settings.API_V1_STR}", tags=["create_order"])


@app.get("/api/v1/")
async def root():
    return {
        "message": "Bienvenido, Este es un Microservicio Para Crear Ordenes"
    }


@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy"
    }
