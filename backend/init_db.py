"""
Initialize Database Script
Run this to create all tables
"""
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import engine
from app.models import base

def init_db(force=False):
    """Create all database tables"""
    
    if force:
        print("⚠️  Force mode: Dropping all existing tables...")
        try:
            base.Base.metadata.drop_all(bind=engine)
            print("✓ Existing tables dropped")
        except Exception as e:
            print(f"⚠️  Warning while dropping tables: {e}")
    
    print("🔧 Creating database tables...")
    
    try:
        base.Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        print("\n📊 Tables created:")
        for table in base.Base.metadata.sorted_tables:
            print(f"  - {table.name}")
        
        # Show information about CASCADE DELETE
        print("\n✨ Важно: Таблицы созданы с каскадным удалением!")
        print("   При удалении номера WhatsApp автоматически удалятся:")
        print("   • Все боты этого номера")
        print("   • Все разговоры через этот номер")
        print("   • Все рассылки с этого номера")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Initialize database')
    parser.add_argument('--force', action='store_true', 
                       help='Drop existing tables before creating new ones')
    args = parser.parse_args()
    
    if args.force:
        confirm = input("⚠️  Это удалит ВСЕ данные! Продолжить? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Отменено.")
            sys.exit(0)
    
    success = init_db(force=args.force)
    
    if success:
        print("\n🎉 База данных готова к использованию!")
    else:
        print("\n❌ Не удалось инициализировать базу данных")
        sys.exit(1)
