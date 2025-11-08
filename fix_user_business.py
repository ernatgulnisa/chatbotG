"""
Temporary script to fix existing users without business_id
"""
import sys
sys.path.append('backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.models.business import Business

# Connect to database
engine = create_engine('sqlite:///backend/app.db')
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Find users without business_id
    users_without_business = db.query(User).filter(User.business_id == None).all()
    
    print(f"Found {len(users_without_business)} users without business_id")
    
    for user in users_without_business:
        print(f"\nProcessing user: {user.email}")
        
        # Create business for user
        business = Business(
            name=f"{user.full_name or user.email.split('@')[0]}'s Business",
            owner_id=user.id,
            email=user.email
        )
        
        db.add(business)
        db.flush()
        
        # Update user
        user.business_id = business.id
        
        print(f"✓ Created business (ID: {business.id}) for user {user.email}")
    
    db.commit()
    print(f"\n✅ Successfully fixed {len(users_without_business)} users")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
