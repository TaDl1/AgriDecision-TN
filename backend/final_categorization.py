from app import create_app
from models.base import db
from sqlalchemy import text

def final_categorization():
    app = create_app()
    with app.app_context():
        print("🔄 Implementing user's exact categorization...")
        
        # User's exact specification:
        # VEGETABLES: Tomato, Potato, Onion, Pepper, Garlic, Carrots, Winter Spinach, Zucchini, Okra, Artichoke
        # FRUITS: Watermelon, Citrus, Grape, Olive, Almond
        # LEGUMES: Chickpeas, Lentils, Fava Beans, Green Peas
        
        updates = [
            # VEGETABLES (🥦)
            ('Potato', 'vegetable', '🥔'),
            ('Onion', 'vegetable', '🧅'),
            ('Pepper', 'vegetable', '🌶️'),
            ('Garlic', 'vegetable', '🧄'),
            ('Carrot', 'vegetable', '🥕'),
            ('Carrots', 'vegetable', '🥕'),
            ('Spinach', 'vegetable', '🥬'),
            ('Zucchini', 'vegetable', '🥒'),
            ('Okra', 'vegetable', '🥘'),
            ('Artichoke', 'vegetable', '🌻'),
            
            # FRUITS (🍉)
            ('Tomato', 'fruit', '🍅'),
            ('Watermelon', 'fruit', '🍉'),
            ('Citrus', 'fruit', '🍋'),
            ('Grape', 'fruit', '🍇'),
            ('Olive', 'fruit', '🫒'),
            ('Almond', 'fruit', '🌰'),
            
            # LEGUMES (🫘)
            ('Chickpea', 'legume', '🫘'),
            ('Chickpeas', 'legume', '🫘'),
            ('Lentil', 'legume', '🥣'),
            ('Lentils', 'legume', '🥣'),
            ('Fava Bean', 'legume', '🫘'),
            ('Fava Beans', 'legume', '🫘'),
            ('Green Pea', 'legume', '🫛'),
            ('Green Peas', 'legume', '🫛'),
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
        
        # Also update Wheat if it exists
        try:
            result = db.session.execute(
                text("UPDATE crops SET category = :cat, icon = :icon WHERE name = :name"),
                {"cat": "grain", "icon": "🌾", "name": "Wheat"}
            )
            if result.rowcount > 0:
                print(f"  ✓ Updated: Wheat → grain")
        except Exception as e:
            print(f"  ⚠️ Error updating Wheat: {e}")
        
        try:
            db.session.commit()
            print("\n✅ Categorization complete!")
            print("\n📊 Final Categories:")
            print("   🥦 Vegetables: Tomato, Potato, Onion, Pepper, Garlic, Carrots, Winter Spinach, Zucchini, Okra, Artichoke")
            print("   🍉 Fruits: Watermelon, Citrus, Grape, Olive, Almond")
            print("   🫘 Legumes: Chickpeas, Lentils, Fava Beans, Green Peas")
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    final_categorization()
