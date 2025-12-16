from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from src.inventory_service.api.v1.endpoints import inventory
from src.inventory_service.core.config import settings
from src.inventory_service.events.consumers import start_consumers
from src.inventory_service.api.dependencies import rabbitmq_client
from src.inventory_service.logger import logger
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Iniciando Inventory Service...")

    # Conectar RabbitMQ
    await rabbitmq_client.connect()

    # Iniciar consumidores en background
    asyncio.create_task(start_consumers())

    yield

    # Shutdown
    logger.info("Apagando Inventory Service...")

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
    inventory.router, prefix=f"{settings.API_V1_STR}", tags=["inventory"]
)


@app.get("/api/v1/")
async def root():
    return {
        "message": "Bienvenido, Microservicio Para Gestion Inventarios"
    }


@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy"
    }
