from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from src.payment_service.core.config import settings
from src.payment_service.events.consumers import start_consumers
from src.payment_service.events import handlers
from src.payment_service.api.dependencies import rabbitmq_client
from src.payment_service.logger import logger
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("💳 Iniciando Payment Service...")

    await rabbitmq_client.connect()

    logger.info(
        f"Handlers registrados: {list(handlers.event_router.handlers.keys())}")

    consumer_task = asyncio.create_task(start_consumers())

    yield

    logger.info("Apagando Payment Service...")
    consumer_task.cancel()
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
