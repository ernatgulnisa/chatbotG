"""Customer endpoints"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_customers():
    return {"message": "List customers endpoint"}
