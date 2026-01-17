from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        print("Migrating database - Adding preferences column...")
        try:
            # Check if column exists first
            with db.engine.connect() as conn:
                try:
                    conn.execute(text("SELECT preferences FROM farmers LIMIT 1"))
                    print("Column 'preferences' already exists.")
                except Exception:
                    print("Column not found. Adding it now...")
                    # SQLite specific alter table
                    conn.execute(text("ALTER TABLE farmers ADD COLUMN preferences JSON DEFAULT '{}'"))
                    conn.commit()
                    print("Successfully added 'preferences' column.")
        except Exception as e:
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
