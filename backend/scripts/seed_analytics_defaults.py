
from app import create_app
from models.base import db
from models.analytics import CropSpecificDefaults, RegionalBenchmarks
from models.crop import Crop
import sys
import os

sys.path.append(os.getcwd())
app = create_app()

def seed():
    with app.app_context():
        print("Seeding CropSpecificDefaults...")
        
        # Default data for Tunisian crops
        defaults = [
            {'crop_id': 1, 'name': 'Wheat', 'fail_rate': 0.12, 'loss': 250, 'temp': '15-25'},
            {'crop_id': 2, 'name': 'Barley', 'fail_rate': 0.15, 'loss': 200, 'temp': '10-22'},
            {'crop_id': 3, 'name': 'Tomato', 'fail_rate': 0.20, 'loss': 400, 'temp': '18-30'},
            {'crop_id': 4, 'name': 'Pepper', 'fail_rate': 0.18, 'loss': 350, 'temp': '20-32'},
            {'crop_id': 5, 'name': 'Olive', 'fail_rate': 0.08, 'loss': 600, 'temp': '12-35'},
            {'crop_id': 6, 'name': 'Dates', 'fail_rate': 0.10, 'loss': 800, 'temp': '25-45'},
            {'crop_id': 7, 'name': 'Potato', 'fail_rate': 0.15, 'loss': 300, 'temp': '15-20'},
            {'crop_id': 8, 'name': 'Onion', 'fail_rate': 0.12, 'loss': 200, 'temp': '13-25'},
            {'crop_id': 9, 'name': 'Grape', 'fail_rate': 0.15, 'loss': 500, 'temp': '15-30'},
        ]
        
        for d in defaults:
            crop = Crop.query.get(d['crop_id'])
            if not crop: continue
            
            existing = CropSpecificDefaults.query.get(d['crop_id'])
            if not existing:
                existing = CropSpecificDefaults(crop_id=d['crop_id'])
                db.session.add(existing)
            
            existing.conservative_failure_rate = d['fail_rate']
            existing.avg_loss_tnd = d['loss']
            existing.optimal_temp_range = d['temp']
            
        db.session.commit()
        print("Seeding complete.")
        
        # Trigger benchmark refresh from existing data
        from services.regional_analytics import RegionalAnalyticsService
        print("Refreshing Regional Benchmarks from existing outcomes...")
        RegionalAnalyticsService.refresh_benchmarks()
        print("Regional benchmarks refreshed.")

if __name__ == "__main__":
    seed()
