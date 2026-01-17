from app import create_app
from models.base import db
from models.crop import Crop
import sys
import os

sys.path.append(os.getcwd())

def seed_v2():
    app = create_app()
    with app.app_context():
        print("🌱 Seeding Crop 2.0 Data (Refined)...")
        
        # User defined rules with EXACT specifications
        # Format: Name: [Category, InputType, YieldMin, YieldMax, YieldUnit]
        
        updates = {
            # GRAINS & LEGUMES (All seeds_kg)
            'Chickpea': {'cat': 'field', 'in': 'seeds_kg', 'min': 8.0, 'max': 15.0, 'unit': 'kg'},
            'Lentil': {'cat': 'field', 'in': 'seeds_kg', 'min': 10.0, 'max': 18.0, 'unit': 'kg'},
            'Wheat': {'cat': 'field', 'in': 'seeds_kg', 'min': 20.0, 'max': 40.0, 'unit': 'kg'},
            'Fava Bean': {'cat': 'field', 'in': 'seeds_kg', 'min': 10.0, 'max': 20.0, 'unit': 'kg'},
            'Green Pea': {'cat': 'field', 'in': 'seeds_kg', 'min': 15.0, 'max': 25.0, 'unit': 'kg'},
            
            # VEGETABLES - Seeds
            'Potato': {'cat': 'vegetable', 'in': 'seeds_kg', 'min': 8.0, 'max': 15.0, 'unit': 'kg'},
            'Onion': {'cat': 'vegetable', 'in': 'seeds_kg', 'min': 300.0, 'max': 500.0, 'unit': 'kg'},
            'Garlic': {'cat': 'vegetable', 'in': 'seeds_kg', 'min': 6.0, 'max': 10.0, 'unit': 'kg'},
            'Carrot': {'cat': 'vegetable', 'in': 'seeds_kg', 'min': 200.0, 'max': 300.0, 'unit': 'kg'},
            'Spinach': {'cat': 'vegetable', 'in': 'seeds_kg', 'min': 45.0, 'max': 65.0, 'unit': 'kg', 'icon': '🥬'},
            'Zucchini': {'cat': 'vegetable', 'in': 'seeds_packet', 'min': 20.0, 'max': 50.0, 'unit': 'kg'},
            'Okra': {'cat': 'vegetable', 'in': 'seeds_kg', 'min': 30.0, 'max': 50.0, 'unit': 'kg'},
            'Pepper': {'cat': 'vegetable', 'in': 'seedlings', 'min': 1.0, 'max': 3.0, 'unit': 'kg'},
            'Artichoke': {'cat': 'vegetable', 'in': 'sapling', 'min': 50.0, 'max': 150.0, 'unit': 'buds'},
            
            # FRUITS (sapling/seedlings - unified for Fruit tab visibility)
            'Tomato': {'cat': 'fruit', 'in': 'seedlings', 'min': 3.0, 'max': 8.0, 'unit': 'kg'},
            'Watermelon': {'cat': 'fruit', 'in': 'seeds_kg', 'min': 200.0, 'max': 400.0, 'unit': 'kg'},
            'Olive': {'cat': 'fruit', 'in': 'sapling', 'min': 20.0, 'max': 40.0, 'unit': 'kg_per_year'},
            'Almond': {'cat': 'fruit', 'in': 'sapling', 'min': 3.0, 'max': 8.0, 'unit': 'kg_per_year'},
            'Citrus': {'cat': 'fruit', 'in': 'sapling', 'min': 50.0, 'max': 150.0, 'unit': 'kg_per_year'},
            'Grape': {'cat': 'fruit', 'in': 'sapling', 'min': 5.0, 'max': 15.0, 'unit': 'kg_per_year'},
        }
        
        for name, rules in updates.items():
            crop = Crop.query.filter_by(name=name).first()
            if crop:
                print(f"✓ Updating {name}...")
                crop.category = rules['cat']
                crop.input_type = rules['in']
                crop.yield_min = rules['min']
                crop.yield_max = rules['max']
                crop.yield_unit = rules['unit']
            else:
                print(f"⚠️ {name} not found in DB, creating...")
                crop = Crop(
                    name=name,
                    category=rules['cat'],
                    input_type=rules['in'],
                    yield_min=rules['min'],
                    yield_max=rules['max'],
                    yield_unit=rules['unit'],
                    min_temp=10, max_temp=30,  # Defaults
                    icon='🌱'  # Default icon
                )
                db.session.add(crop)

        try:
            db.session.commit()
            print("\n✅ Crop 2.0 Data Seeded Successfully!")
            print("\n📊 Summary:")
            print("   - Fruits (Unified): Tomato, Watermelon, Olive, Almond, Citrus, Grape")
            print("   - Vegetables: Potato, Onion, Pepper, Garlic, Carrot, Spinach, Okra, Zucchini, Artichoke")
            print("   - Legumes: Chickpea, Lentil, Fava Bean, Green Pea")
        except Exception as e:
            print(f"❌ Failed: {e}")
            db.session.rollback()

if __name__ == "__main__":
    seed_v2()
