from fastapi import FastAPI


app = FastAPI()


@app.get("/")
async def root():
    return {
        "message": "Bienvenido, Microservicio Para Gestion de Notificaciones"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }
