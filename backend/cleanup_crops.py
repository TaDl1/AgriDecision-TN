from app import create_app
from models.base import db
from sqlalchemy import text

def cleanup_and_categorize():
    app = create_app()
    with app.app_context():
        print("🗑️ Removing unwanted crops...")
        
        # Delete unwanted crops using raw SQL
        crops_to_remove = [
            'Carrot', 'Carrots', 
            'Lentil', 
            'Chickpea', 'Chickpeas',
            'Fava Bean', 'Fava Beans', 
            'Green Pea', 'Green Peas', 
            'Spinach', 'Winter Spinach'
        ]
        
        for crop_name in crops_to_remove:
            try:
                # Delete decisions first
                db.session.execute(text("DELETE FROM decisions WHERE crop_id IN (SELECT id FROM crops WHERE name = :name)"), {"name": crop_name})
                # Delete crop
                result = db.session.execute(text("DELETE FROM crops WHERE name = :name"), {"name": crop_name})
                if result.rowcount > 0:
                    print(f"  ✓ Removed: {crop_name}")
            except Exception as e:
                print(f"  ⚠️ Error removing {crop_name}: {e}")
        
        print("\n📂 Updating categories...")
        
        # Update categories using raw SQL
        updates = [
            # VEGETABLES
            ('Tomato', 'vegetable', '🍅'),
            ('Potato', 'vegetable', '🥔'),
            ('Onion', 'vegetable', '🧅'),
            ('Pepper', 'vegetable', '🌶️'),
            ('Garlic', 'vegetable', '🧄'),
            ('Zucchini', 'vegetable', '🥒'),
            ('Okra', 'vegetable', '🥘'),
            ('Artichoke', 'vegetable', '🌻'),
            ('Olive', 'vegetable', '🫒'),
            
            # FRUITS
            ('Watermelon', 'fruit', '🍉'),
            ('Citrus', 'fruit', '🍋'),
            ('Grape', 'fruit', '🍇'),
            ('Almond', 'fruit', '🌰'),
            
            # GRAINS
            ('Wheat', 'grain', '🌾'),
        ]
        
        for name, category, icon in updates:
            try:
                result = db.session.execute(
                    text("UPDATE crops SET category = :cat, icon = :icon WHERE name = :name"),
                    {"cat": category, "icon": icon, "name": name}
                )
                if result.rowcount > 0:
                    print(f"  ✓ Updated: {name} → {category}")
            except Exception as e:
                print(f"  ⚠️ Error updating {name}: {e}")
        
        try:
            db.session.commit()
            print("\n✅ Complete!")
            print("\n📊 Categories:")
            print("   🥬 Vegetables: Tomato, Potato, Onion, Pepper, Garlic, Zucchini, Okra, Artichoke, Olive")
            print("   🍎 Fruits: Watermelon, Citrus, Grape, Almond")
            print("   🌾 Grains: Wheat")
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    cleanup_and_categorize()
