
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
        print("Migrating database for Small Sample Analytics...")
        
        # 1. Create new tables
        try:
            print("Creating new tables (if not exist)...")
            db.create_all()
        except Exception as e:
            print(f"Table creation failed: {e}")

        # 2. Add columns to farmer_analytics
        columns = [
            ("data_sufficiency_score", "REAL DEFAULT 0.0"),
            ("reliability_tier", "INTEGER DEFAULT 3"),
            ("confidence_interval_width", "REAL DEFAULT 0.0"),
            ("calculation_method", "TEXT DEFAULT 'regional_estimate'"),
            ("last_calculated", "DATETIME")
        ]
        
        for col_name, col_type in columns:
            try:
                print(f"Adding {col_name} to farmer_analytics...")
                db.session.execute(text(f"ALTER TABLE farmer_analytics ADD COLUMN {col_name} {col_type}"))
                db.session.commit()
            except Exception as e:
                print(f"Skipped {col_name}: {e}")
                db.session.rollback()

        print("Migration complete.")

if __name__ == "__main__":
    migrate()
