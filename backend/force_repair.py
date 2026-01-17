
import sys
import os
from datetime import datetime
from app import create_app
from models.base import db
from models.decision import Decision, Outcome

app = create_app()

with app.app_context():
    # Force repair ALL missing outcomes
    decisions = Decision.query.all()
    print(f"Scanning {len(decisions)} decisions for missing outcomes...")
    
    fixed_count = 0
    for d in decisions:
        if d.advice_status in ['followed', 'ignored']:
            existing = Outcome.query.filter_by(decision_id=d.id).first()
            if not existing:
                print(f"Fixing Decision {d.id} (Farmer {d.farmer_id}) - Status: {d.advice_status}")
                
                is_success = (d.advice_status == 'followed')
                o = Outcome(
                    decision_id=d.id,
                    outcome='success' if is_success else 'failure',
                    yield_kg=1000 if is_success else 400,
                    revenue_tnd=2000 if is_success else 0,
                    recorded_at=d.timestamp or datetime.utcnow(),
                    notes="Force repaired by admin script"
                )
                db.session.add(o)
                fixed_count += 1
                
    if fixed_count > 0:
        db.session.commit()
        print(f"SUCCESS: Created {fixed_count} missing outcomes.")
    else:
        print("System data is clean. All active decisions have outcomes.")
