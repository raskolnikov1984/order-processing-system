from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from src.payment_service.core.config import settings
from src.payment_service.events.consumers import start_consumers
from src.payment_service.api.dependencies import rabbitmq_client
from src.payment_service.logger import logger
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Iniciando Order Service...")

    # Conectar RabbitMQ
    await rabbitmq_client.connect()

    # Iniciar consumidores en background
    asyncio.create_task(start_consumers())

    yield

    # Shutdown
    logger.info("Apagando Order Service...")

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


@app.get("/")
async def root():
    return {
        "message": "Bienvenido, Microservicio Para Gestion de Pagos"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }
