
from app import create_app
from models.base import db
from sqlalchemy import text
import sys
import os

# Ensure we can import app
sys.path.append(os.getcwd())

app = create_app()

def migrate():
    with app.app_context():
        print("Migrating database using SQLAlchemy...")
        
        # 1. Update Crops Table
        try:
            print("Adding input_type to crops...")
            db.session.execute(text("ALTER TABLE crops ADD COLUMN input_type TEXT DEFAULT 'seeds_kg'"))
        except Exception as e:
            print(f"Skipped (extant?): {e}")

        try:
            print("Adding yield_min to crops...")
            db.session.execute(text("ALTER TABLE crops ADD COLUMN yield_min REAL DEFAULT 1.0"))
        except Exception as e:
            print(f"Skipped (extant?): {e}")
            
        try:
            print("Adding yield_max to crops...")
            db.session.execute(text("ALTER TABLE crops ADD COLUMN yield_max REAL DEFAULT 1.0"))
        except Exception as e:
            print(f"Skipped (extant?): {e}")
            
        try:
            print("Adding yield_unit to crops...")
            db.session.execute(text("ALTER TABLE crops ADD COLUMN yield_unit TEXT DEFAULT 'kg'"))
        except Exception as e:
            print(f"Skipped (extant?): {e}")

        # 2. Update Decisions Table
        try:
            print("Adding input_quantity to decisions...")
            db.session.execute(text("ALTER TABLE decisions ADD COLUMN input_quantity REAL DEFAULT 1.0"))
        except Exception as e:
            print(f"Skipped (extant?): {e}")

        try:
            db.session.commit()
            print("Committed changes.")
        except Exception as e:
            print(f"Commit failed: {e}")
            db.session.rollback()

if __name__ == "__main__":
    migrate()
