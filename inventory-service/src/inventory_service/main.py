from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.inventory_service.api.v1.endpoints import inventory
from src.inventory_service.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
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
