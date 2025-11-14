"""
Quick script to check and initialize WhatsApp number on Render
Run this in Render Shell if webhook shows "WhatsApp number not found"
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.whatsapp_number import WhatsAppNumber
from app.models.business import Business
from app.models.user import User
from app.core.security import get_password_hash

def check_and_create_data():
    """Check database and create missing data"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("  Checking Database")
        print("=" * 60)
        print()
        
        # Check WhatsApp numbers
        whatsapp_count = db.query(WhatsAppNumber).count()
        print(f"📱 WhatsApp Numbers: {whatsapp_count}")
        
        if whatsapp_count > 0:
            numbers = db.query(WhatsAppNumber).all()
            for num in numbers:
                print(f"   • {num.phone_number} (ID: {num.phone_number_id})")
                print(f"     Status: {num.status}, Active: {num.is_active}")
        else:
            print("   ⚠️  No WhatsApp numbers found!")
            
        print()
        
        # Check businesses
        business_count = db.query(Business).count()
        print(f"🏢 Businesses: {business_count}")
        
        if business_count > 0:
            businesses = db.query(Business).all()
            for biz in businesses:
                print(f"   • {biz.name} (ID: {biz.id})")
        else:
            print("   ⚠️  No businesses found!")
            
        print()
        
        # Check users
        user_count = db.query(User).count()
        print(f"👤 Users: {user_count}")
        
        if user_count > 0:
            users = db.query(User).all()
            for user in users:
                print(f"   • {user.email} - {user.role}")
        else:
            print("   ⚠️  No users found!")
            
        print()
        print("=" * 60)
        
        # If no data, create it
        if whatsapp_count == 0 or business_count == 0 or user_count == 0:
            print()
            print("🔧 Creating missing data...")
            print()
            
            # Create user if needed
            if user_count == 0:
                user = User(
                    email='admin@chatbot.com',
                    full_name='Admin User',
                    hashed_password=get_password_hash('admin123'),
                    role='owner',
                    is_active=True,
                    is_verified=True
                )
                db.add(user)
                db.flush()
                print(f"✅ User created: {user.email}")
            else:
                user = db.query(User).first()
            
            # Create business if needed
            if business_count == 0:
                business = Business(
                    name='Demo Business',
                    description='Demo business for testing',
                    owner_id=user.id,
                    is_active=True
                )
                db.add(business)
                db.flush()
                
                # Update user with business_id
                user.business_id = business.id
                print(f"✅ Business created: {business.name}")
            else:
                business = db.query(Business).first()
            
            # Create WhatsApp number if needed
            if whatsapp_count == 0:
                # Get from environment or use default
                phone_number = os.getenv('WHATSAPP_PHONE_NUMBER', '+1234567890')
                phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', 'demo_phone_id')
                
                whatsapp_number = WhatsAppNumber(
                    business_id=business.id,
                    phone_number=phone_number,
                    display_name='Demo WhatsApp',
                    provider='meta',
                    phone_number_id=phone_number_id,
                    status='connected',
                    is_active=True
                )
                db.add(whatsapp_number)
                db.flush()
                print(f"✅ WhatsApp number created: {whatsapp_number.phone_number}")
                print(f"   Phone Number ID: {phone_number_id}")
            
            db.commit()
            print()
            print("=" * 60)
            print("✅ Data initialized successfully!")
            print()
            print("📋 Credentials:")
            print(f"   Email: admin@chatbot.com")
            print(f"   Password: admin123")
            print("=" * 60)
        else:
            print("✅ All data exists, nothing to create")
            print("=" * 60)
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(check_and_create_data())
