import sys
import os
sys.path.append(os.path.abspath('backend'))

from app import create_app
from models.base import db
from sqlalchemy import text

app = create_app()

def migrate():
    with app.app_context():
        print("Starting Truthful Farming Migration...")
        
        # SQL for SQLite (common in dev) or Postgres
        try:
            # 1. Farmer table
            db.session.execute(text("ALTER TABLE farmers ADD COLUMN soil_type VARCHAR(20)"))
            db.session.execute(text("ALTER TABLE farmers ADD COLUMN farm_size_ha FLOAT"))
            print("Updated farmers table.")
        except Exception as e:
            print(f"Farmers table notice: {e}")

        try:
            # 2. Decisions table
            db.session.execute(text("ALTER TABLE decisions ADD COLUMN cost_basis_tnd FLOAT"))
            print("Updated decisions table.")
        except Exception as e:
            print(f"Decisions table notice: {e}")

        try:
            # 3. Outcomes table
            db.session.execute(text("ALTER TABLE outcomes ADD COLUMN net_profit_loss FLOAT"))
            print("Updated outcomes table.")
        except Exception as e:
            print(f"Outcomes table notice: {e}")

        db.session.commit()
        print("Migration complete.")

if __name__ == "__main__":
    migrate()
