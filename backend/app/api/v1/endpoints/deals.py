"""Deal endpoints"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_deals():
    return {"message": "List deals endpoint"}
