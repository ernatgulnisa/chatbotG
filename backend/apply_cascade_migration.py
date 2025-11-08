"""
Apply CASCADE DELETE migration for WhatsApp numbers
This script directly updates the database to add CASCADE delete constraints
"""
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy import create_engine, text
from app.core.config import settings

def apply_cascade_migration():
    """Apply CASCADE DELETE constraints to WhatsApp number foreign keys"""
    engine = create_engine(settings.DATABASE_URL)
    
    print("🔄 Connecting to database...")
    
    with engine.connect() as conn:
        try:
            print("\n📝 Applying CASCADE DELETE to bots table...")
            # For PostgreSQL
            conn.execute(text("""
                ALTER TABLE bots 
                DROP CONSTRAINT IF EXISTS bots_whatsapp_number_id_fkey,
                ADD CONSTRAINT bots_whatsapp_number_id_fkey 
                FOREIGN KEY (whatsapp_number_id) 
                REFERENCES whatsapp_numbers(id) 
                ON DELETE CASCADE;
            """))
            conn.commit()
            print("✓ Bots table updated")
            
            print("\n📝 Applying CASCADE DELETE to conversations table...")
            conn.execute(text("""
                ALTER TABLE conversations 
                DROP CONSTRAINT IF EXISTS conversations_whatsapp_number_id_fkey,
                ADD CONSTRAINT conversations_whatsapp_number_id_fkey 
                FOREIGN KEY (whatsapp_number_id) 
                REFERENCES whatsapp_numbers(id) 
                ON DELETE CASCADE;
            """))
            conn.commit()
            print("✓ Conversations table updated")
            
            print("\n📝 Applying CASCADE DELETE to broadcasts table...")
            conn.execute(text("""
                ALTER TABLE broadcasts 
                DROP CONSTRAINT IF EXISTS broadcasts_whatsapp_number_id_fkey,
                ADD CONSTRAINT broadcasts_whatsapp_number_id_fkey 
                FOREIGN KEY (whatsapp_number_id) 
                REFERENCES whatsapp_numbers(id) 
                ON DELETE CASCADE;
            """))
            conn.commit()
            print("✓ Broadcasts table updated")
            
            print("\n✅ Migration completed successfully!")
            print("\n📋 Summary:")
            print("   - Bots will be deleted when WhatsApp number is deleted")
            print("   - Conversations will be deleted when WhatsApp number is deleted")
            print("   - Broadcasts will be deleted when WhatsApp number is deleted")
            
        except Exception as e:
            conn.rollback()
            print(f"\n❌ Error applying migration: {e}")
            print("\n💡 Tip: Make sure PostgreSQL is running and the database exists")
            return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("  WhatsApp Number CASCADE DELETE Migration")
    print("=" * 60)
    
    success = apply_cascade_migration()
    
    if success:
        print("\n✨ Now you can delete WhatsApp numbers without errors!")
        print("   All related data will be automatically removed.")
    else:
        print("\n⚠️  Migration failed. Please check the error messages above.")
        sys.exit(1)
