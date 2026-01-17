
from app import app
from models.base import db
from models.user import Farmer
from models.decision import Decision, Outcome
from sqlalchemy import func

def check():
    with app.app_context():
        print("--- Farmer Analysis ---")
        farmers = Farmer.query.all()
        for f in farmers:
            d_count = Decision.query.filter_by(farmer_id=f.id).count()
            o_count = db.session.query(func.count(Outcome.id)).join(Decision).filter(Decision.farmer_id == f.id).scalar()
            print(f"Farmer ID: {f.id}, Name: {f.first_name}, Governorate: {f.governorate}, Decisions: {d_count}, Outcomes: {o_count}")
        
        print("\n--- Decision Details (Sample) ---")
        d = Decision.query.first()
        if d:
            print(f"First Decision: ID={d.id}, Status={d.advice_status}, Action={d.actual_action}, Recommendation={d.recommendation}")
        else:
            print("No decisions found!")

if __name__ == "__main__":
    check()
