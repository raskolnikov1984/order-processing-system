from fastapi import FastAPI
from order_service.api.v1.endpoints import orders

app = FastAPI()


app.include_router(orders.router, prefix="", tags=["create_order"])


@app.get("/")
async def root():
    return {
        "message": "Bienvenido, Este es un Microservicio Para Crear Ordenes"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }
