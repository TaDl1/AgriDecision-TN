import sys
import os
sys.path.append(os.path.abspath('backend'))

from app import create_app
from models.base import db
from sqlalchemy import text

app = create_app()

def migrate():
    with app.app_context():
        print("Creating Analytics Events table...")
        db.create_all() # This should catch the new model since it's imported in some places or we can import it here
        
        # Explicitly check if the table exists, if create_all doesn't do it (it should)
        try:
            from models.analytics import AnalyticsEvent
            AnalyticsEvent.__table__.create(db.engine)
            print("Table created.")
        except Exception as e:
            print(f"Notice: {e}")

if __name__ == "__main__":
    migrate()
