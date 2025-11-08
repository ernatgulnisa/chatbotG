"""Broadcast endpoints"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_broadcasts():
    return {"message": "List broadcasts endpoint"}
