from app import app, db
from models.crop import Crop
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_crops():
    """Seed the database with additional crops"""
    
    new_crops = [
        {
            'name': 'Fava Beans',
            'scientific_name': 'Vicia faba',
            'category': 'legume',
            'min_temp': 5.0,
            'max_temp': 25.0,
            'optimal_temp_min': 15.0,
            'optimal_temp_max': 22.0,
            'water_needs': 'medium',
            'growth_days': 120,
            'icon': '🫘',
            'description': 'Typical Tunisian winter crop, nitrogen fixer. Commonly known as Foul.'
        },
        {
            'name': 'Garlic',
            'scientific_name': 'Allium sativum',
            'category': 'bulb',
            'min_temp': 0.0,
            'max_temp': 30.0,
            'optimal_temp_min': 12.0,
            'optimal_temp_max': 24.0,
            'water_needs': 'low',
            'growth_days': 210,
            'icon': '🧄',
            'description': 'Winter crop, essential for Tunisian cuisine. Needs cold period for bulbing.'
        },
        {
            'name': 'Winter Spinach',
            'scientific_name': 'Spinacia oleracea',
            'category': 'leafy green',
            'min_temp': 2.0,
            'max_temp': 24.0,
            'optimal_temp_min': 10.0,
            'optimal_temp_max': 18.0,
            'water_needs': 'medium',
            'growth_days': 50,
            'icon': '🥬',
            'description': 'Rapid growing leafy green, very cold hardy.'
        },
        {
            'name': 'Artichoke',
            'scientific_name': 'Cynara cardunculus',
            'category': 'perennial',
            'min_temp': 7.0,
            'max_temp': 29.0,
            'optimal_temp_min': 13.0,
            'optimal_temp_max': 24.0,
            'water_needs': 'high',
            'growth_days': 150,
            'icon': '🌻',
            'description': 'Thistle-like perennial cultivated for its edible flower buds.'
        },
        {
            'name': 'Green Peas',
            'scientific_name': 'Pisum sativum',
            'category': 'legume',
            'min_temp': 5.0,
            'max_temp': 24.0,
            'optimal_temp_min': 13.0,
            'optimal_temp_max': 18.0,
            'water_needs': 'medium',
            'growth_days': 70,
            'icon': '🫛',
            'description': 'Cool-season crop known as Jelbana.'
        },
        {
            'name': 'Okra',
            'scientific_name': 'Abelmoschus esculentus',
            'category': 'vegetable',
            'min_temp': 15.0,
            'max_temp': 35.0,
            'optimal_temp_min': 20.0,
            'optimal_temp_max': 30.0,
            'water_needs': 'medium',
            'growth_days': 60,
            'icon': '🥘',
            'description': 'Heat-loving vegetable known as Gnawia.'
        },
        {
            'name': 'Watermelon',
            'scientific_name': 'Citrullus lanatus',
            'category': 'fruit',
            'min_temp': 15.0,
            'max_temp': 35.0,
            'optimal_temp_min': 25.0,
            'optimal_temp_max': 32.0,
            'water_needs': 'high',
            'growth_days': 90,
            'icon': '🍉',
            'description': 'Summer staple crop known as Dellek.'
        },
        {
            'name': 'Carrots',
            'scientific_name': 'Daucus carota',
            'category': 'root',
            'min_temp': 4.0,
            'max_temp': 29.0,
            'optimal_temp_min': 15.0,
            'optimal_temp_max': 22.0,
            'water_needs': 'medium',
            'growth_days': 75,
            'icon': '🥕',
            'description': 'Versatile root crop known as Sfenaria.'
        },
        {
            'name': 'Zucchini',
            'scientific_name': 'Cucurbita pepo',
            'category': 'vegetable',
            'min_temp': 10.0,
            'max_temp': 32.0,
            'optimal_temp_min': 18.0,
            'optimal_temp_max': 27.0,
            'water_needs': 'high',
            'growth_days': 55,
            'icon': '🥒',
            'description': 'Productive summer squash.'
        },
        {
            'name': 'Melon',
            'scientific_name': 'Cucumis melo',
            'category': 'fruit',
            'min_temp': 18.0,
            'max_temp': 35.0,
            'optimal_temp_min': 24.0,
            'optimal_temp_max': 30.0,
            'water_needs': 'high',
            'growth_days': 85,
            'icon': '🍈',
            'description': 'Sweet summer fruit, needs heat and sun.'
        }
    ]
    
    with app.app_context():
        added_count = 0
        for crop_data in new_crops:
            # Check if exists
            existing = Crop.query.filter_by(name=crop_data['name']).first()
            if not existing:
                new_crop = Crop(**crop_data)
                db.session.add(new_crop)
                added_count += 1
                logger.info(f"Adding new crop: {crop_data['name']}")
            else:
                logger.info(f"Crop already exists: {crop_data['name']}")
        
        try:
            db.session.commit()
            print(f"Successfully added {added_count} new crops to the database.")
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding crops: {e}")

if __name__ == '__main__':
    seed_crops()
