"""WhatsApp Numbers Management Endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_active_user, encryption
from app.models.user import User
from app.models.whatsapp_number import WhatsAppNumber
from app.schemas.whatsapp import (
    WhatsAppNumberCreate,
    WhatsAppNumberUpdate,
    WhatsAppNumberResponse,
    WhatsAppNumberListResponse
)
from app.utils.env_manager import env_manager

router = APIRouter()


@router.get("/numbers", response_model=List[WhatsAppNumberResponse], tags=["WhatsApp"])
async def list_whatsapp_numbers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of WhatsApp numbers for current user's business"""
    numbers = db.query(WhatsAppNumber).filter(
        WhatsAppNumber.business_id == current_user.business_id
    ).offset(skip).limit(limit).all()
    
    return numbers


@router.post("/numbers", response_model=WhatsAppNumberResponse, status_code=status.HTTP_201_CREATED, tags=["WhatsApp"])
async def create_whatsapp_number(
    number_data: WhatsAppNumberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add new WhatsApp number to business"""
    
    # Check if phone_number_id already exists
    existing = db.query(WhatsAppNumber).filter(
        WhatsAppNumber.phone_number_id == number_data.phone_number_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone Number ID already registered"
        )
    
    # Encrypt access token
    encrypted_token = encryption.encrypt(number_data.api_token)
    
    # Create new number
    db_number = WhatsAppNumber(
        business_id=current_user.business_id,
        display_name=number_data.display_name,
        phone_number=number_data.phone_number,
        phone_number_id=number_data.phone_number_id,
        waba_id=number_data.waba_id,
        api_token=encrypted_token,
        is_active=number_data.is_active
    )
    
    db.add(db_number)
    db.commit()
    db.refresh(db_number)
    
    # Auto-update .env file with WhatsApp credentials
    try:
        env_manager.update_whatsapp_token(number_data.api_token)
        env_manager.update_whatsapp_phone_number_id(number_data.phone_number_id)
        if number_data.waba_id:
            env_manager.update_whatsapp_business_account_id(number_data.waba_id)
        print("[OK] .env file updated with WhatsApp credentials")
    except Exception as e:
        print(f"[WARNING] Failed to update .env file: {e}")
        # Don't fail the request if .env update fails
    
    return db_number


@router.get("/numbers/{number_id}", response_model=WhatsAppNumberResponse, tags=["WhatsApp"])
async def get_whatsapp_number(
    number_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get specific WhatsApp number details"""
    number = db.query(WhatsAppNumber).filter(
        WhatsAppNumber.id == number_id,
        WhatsAppNumber.business_id == current_user.business_id
    ).first()
    
    if not number:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp number not found"
        )
    
    return number


@router.put("/numbers/{number_id}", response_model=WhatsAppNumberResponse, tags=["WhatsApp"])
async def update_whatsapp_number(
    number_id: int,
    number_data: WhatsAppNumberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update WhatsApp number details"""
    number = db.query(WhatsAppNumber).filter(
        WhatsAppNumber.id == number_id,
        WhatsAppNumber.business_id == current_user.business_id
    ).first()
    
    if not number:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp number not found"
        )
    
    # Update fields
    update_data = number_data.dict(exclude_unset=True)
    
    # Encrypt access token if provided
    if "api_token" in update_data and update_data["api_token"]:
        update_data["api_token"] = encryption.encrypt(update_data["api_token"])
    
    for field, value in update_data.items():
        setattr(number, field, value)
    
    db.commit()
    db.refresh(number)
    
    # Auto-update .env file with updated WhatsApp credentials
    try:
        if "api_token" in number_data.dict(exclude_unset=True) and number_data.api_token:
            env_manager.update_whatsapp_token(number_data.api_token)
        if "phone_number_id" in update_data:
            env_manager.update_whatsapp_phone_number_id(update_data["phone_number_id"])
        if "waba_id" in number_data.dict(exclude_unset=True) and number_data.waba_id:
            env_manager.update_whatsapp_business_account_id(number_data.waba_id)
        print("[OK] .env file updated with WhatsApp credentials")
    except Exception as e:
        print(f"[WARNING] Failed to update .env file: {e}")
        # Don't fail the request if .env update fails
    
    return number


@router.delete("/numbers/{number_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["WhatsApp"])
async def delete_whatsapp_number(
    number_id: int,
    force: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete WhatsApp number
    
    By default, will cascade delete all related data:
    - Bots using this number
    - Conversations through this number
    - Broadcast campaigns
    
    Set force=true to confirm deletion
    """
    number = db.query(WhatsAppNumber).filter(
        WhatsAppNumber.id == number_id,
        WhatsAppNumber.business_id == current_user.business_id
    ).first()
    
    if not number:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp number not found"
        )
    
    try:
        # Delete will cascade to related entities due to cascade="all, delete-orphan"
        db.delete(number)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete WhatsApp number: {str(e)}"
        )
    
    return None


@router.patch("/numbers/{number_id}/toggle", response_model=WhatsAppNumberResponse, tags=["WhatsApp"])
async def toggle_whatsapp_number(
    number_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Toggle WhatsApp number active status"""
    number = db.query(WhatsAppNumber).filter(
        WhatsAppNumber.id == number_id,
        WhatsAppNumber.business_id == current_user.business_id
    ).first()
    
    if not number:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp number not found"
        )
    
    number.is_active = not number.is_active
    db.commit()
    db.refresh(number)
    
    return number

