from app import create_app
from models.base import db
from sqlalchemy import text

def move_to_fruits():
    app = create_app()
    with app.app_context():
        print("🔄 Moving Olive and Tomato to Fruits...")
        
        # Move Olive and Tomato to fruits
        updates = [
            ('Olive', 'fruit', '🫒'),
            ('Tomato', 'fruit', '🍅'),
        ]
        
        for name, category, icon in updates:
            try:
                result = db.session.execute(
                    text("UPDATE crops SET category = :cat WHERE name = :name"),
                    {"cat": category, "name": name}
                )
                if result.rowcount > 0:
                    print(f"  ✓ Moved: {name} → {category}")
            except Exception as e:
                print(f"  ⚠️ Error: {e}")
        
        try:
            db.session.commit()
            print("\n✅ Complete!")
            print("\n📊 Updated Categories:")
            print("   🥦 Vegetables: Potato, Onion, Pepper, Garlic, Carrots, Winter Spinach, Zucchini, Okra, Artichoke")
            print("   🍉 Fruits: Watermelon, Citrus, Grape, Olive, Almond, Tomato")
            print("   🫘 Legumes: Chickpeas, Lentils, Fava Beans, Green Peas")
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    move_to_fruits()
