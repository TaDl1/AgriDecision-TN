"""
Add financial settings columns to decisions table
"""
from models.base import db
from models.decision import Decision
from sqlalchemy import text

def migrate():
    """Add seedling_cost_tnd and market_price_tnd columns to decisions table"""
    try:
        with db.engine.connect() as connection:
            # Check if columns already exist
            result = connection.execute(text("PRAGMA table_info(decisions)"))
            columns = [row[1] for row in result]
            
            if 'seedling_cost_tnd' not in columns:
                print("Adding seedling_cost_tnd column...")
                connection.execute(text("ALTER TABLE decisions ADD COLUMN seedling_cost_tnd FLOAT"))
                connection.commit()
                print("✅ Added seedling_cost_tnd column")
            else:
                print("⏭️ seedling_cost_tnd column already exists")
            
            if 'market_price_tnd' not in columns:
                print("Adding market_price_tnd column...")
                connection.execute(text("ALTER TABLE decisions ADD COLUMN market_price_tnd FLOAT"))
                connection.commit()
                print("✅ Added market_price_tnd column")
            else:
                print("⏭️ market_price_tnd column already exists")
        
        print("\n✅ Migration completed successfully!")
        return True
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    from app import app
    with app.app_context():
        migrate()
