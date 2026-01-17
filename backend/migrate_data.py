from app import app, db
from models.user import Farmer
import sqlite3

def migrate_db():
    with app.app_context():
        # Using raw SQL for SQLite since Alembic is not set up
        # This is safe for adding nullable columns
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        print(f"Connecting to database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Check if columns exist
            cursor.execute("PRAGMA table_info(farmers)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if 'first_name' not in columns:
                print("Adding first_name column...")
                cursor.execute("ALTER TABLE farmers ADD COLUMN first_name VARCHAR(50)")
            else:
                print("first_name already exists.")
                
            if 'last_name' not in columns:
                print("Adding last_name column...")
                cursor.execute("ALTER TABLE farmers ADD COLUMN last_name VARCHAR(50)")
            else:
                print("last_name already exists.")
                
            conn.commit()
            print("Migration successful!")
            
        except Exception as e:
            print(f"Migration failed: {e}")
            conn.rollback()
        finally:
            conn.close()

if __name__ == '__main__':
    migrate_db()
