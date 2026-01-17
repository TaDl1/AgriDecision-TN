
from app import app
from models.base import db
from models.user import Farmer
from models.decision import Decision, Outcome
from sqlalchemy import func

def check_data():
    with app.app_context():
        results = db.session.query(
            Farmer.id,
            Farmer.phone_number,
            Farmer.governorate,
            func.count(Decision.id).label('decisions'),
            func.count(Outcome.id).label('outcomes')
        ).outerjoin(Decision, Decision.farmer_id == Farmer.id)\
         .outerjoin(Outcome, Outcome.decision_id == Decision.id)\
         .group_by(Farmer.id).all()
        
        print(f"{'ID':<5} | {'Phone':<15} | {'Gov':<12} | {'Decisions':<10} | {'Outcomes':<10}")
        print("-" * 60)
        for r in results:
            print(f"{r[0]:<5} | {r[1]:<15} | {r[2]:<12} | {r[3]:<10} | {r[4]:<10}")

if __name__ == "__main__":
    check_data()
