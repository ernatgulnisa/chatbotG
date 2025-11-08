"""Business endpoints"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_businesses():
    return {"message": "List businesses endpoint"}
