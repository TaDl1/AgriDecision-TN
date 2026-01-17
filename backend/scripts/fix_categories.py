from app import app, db
from models.crop import Crop

def fix_categories():
    with app.app_context():
        crops = Crop.query.all()
        count = 0
        for crop in crops:
            if crop.category and any(c.isupper() for c in crop.category):
                old_cat = crop.category
                crop.category = crop.category.lower()
                print(f"Updating {crop.name}: {old_cat} -> {crop.category}")
                count += 1
        
        if count > 0:
            try:
                db.session.commit()
                print(f"Successfully updated {count} crop categories to lowercase.")
            except Exception as e:
                db.session.rollback()
                print(f"Error updating categories: {e}")
        else:
            print("No categories needed updating.")

if __name__ == '__main__':
    fix_categories()
