from fastapi import APIRouter


router = APIRouter()


@router.post("/create_order")
async def create_order():
    """
    Crear una nueva orden
    """
    return {"message": "successful"}
