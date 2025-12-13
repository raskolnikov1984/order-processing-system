#!/usr/bin/env python3
from fastapi import FastAPI

app = FastAPI()


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
