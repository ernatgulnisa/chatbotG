"""
Create test user and business for testing WhatsApp deletion
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.business import Business
from app.core.security import get_password_hash

def create_test_data():
    """Create test user and business"""
    db = SessionLocal()
    
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        
        if existing_user:
            print("✓ Тестовый пользователь уже существует")
            print(f"  Email: test@example.com")
            print(f"  Password: test123")
            return
        
        # Create business
        business = Business(
            name="Test Business",
            description="Тестовый бизнес для проверки функций",
            email="business@test.com",
            phone="+79001234567",
            is_active=True
        )
        db.add(business)
        db.flush()
        
        # Create user
        user = User(
            email="test@example.com",
            full_name="Test User",
            hashed_password=get_password_hash("test123"),
            role="owner",
            is_active=True,
            is_verified=True,
            business_id=business.id
        )
        
        # Update business owner
        business.owner_id = user.id
        
        db.add(user)
        db.commit()
        
        print("✅ Тестовые данные успешно созданы!")
        print("\n📋 Данные для входа:")
        print(f"  Email: test@example.com")
        print(f"  Password: test123")
        print(f"\n🏢 Бизнес: {business.name} (ID: {business.id})")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка создания тестовых данных: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  Creating Test Data")
    print("=" * 60)
    print()
    create_test_data()
