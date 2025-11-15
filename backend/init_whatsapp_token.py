#!/usr/bin/env python3
"""
Initialize WhatsApp token from environment on first startup.
This runs automatically on Render deployment.
"""
import os
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.security import EncryptionUtil
from app.models.whatsapp_number import WhatsAppNumber

# Initialize encryption
encryption = EncryptionUtil()

def init_token():
    """Initialize WhatsApp token from environment if not already set"""
    
    print("=" * 60)
    print("🔧 Checking WhatsApp Token Configuration...")
    print("=" * 60)
    
    # Get token from environment
    whatsapp_token = os.getenv("WHATSAPP_API_TOKEN")
    
    if not whatsapp_token:
        print("ℹ️  WHATSAPP_API_TOKEN not found in environment variables")
        print("ℹ️  Token can be configured later via database")
        return
    
    print(f"✅ Found WHATSAPP_API_TOKEN in environment ({len(whatsapp_token)} chars)")
    
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Find WhatsApp number
        whatsapp_number = db.query(WhatsAppNumber).first()
        
        if not whatsapp_number:
            print("⚠️  No WhatsApp number found in database")
            print("ℹ️  Please create WhatsApp number configuration first")
            return
        
        print(f"📱 WhatsApp Number: {whatsapp_number.display_name} (+{whatsapp_number.phone_number})")
        
        # Check if token already set
        if whatsapp_number.api_token:
            print("ℹ️  Token already configured in database")
            print("ℹ️  Skipping initialization (use sync script to update)")
            return
        
        print("🔐 Encrypting token...")
        encrypted_token = encryption.encrypt(whatsapp_token)
        
        print("💾 Saving to database...")
        whatsapp_number.api_token = encrypted_token
        whatsapp_number.status = "CONNECTED"
        db.commit()
        
        print("=" * 60)
        print("✅ WhatsApp Token Initialized Successfully!")
        print("=" * 60)
        print(f"📱 Phone: +{whatsapp_number.phone_number}")
        print(f"📛 Name: {whatsapp_number.display_name}")
        print(f"🔌 Status: {whatsapp_number.status}")
        print(f"🔐 Token: Encrypted and saved")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_token()
