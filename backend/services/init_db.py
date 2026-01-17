"""
Database initialization and seeding
"""
from models.base import db
from models.crop import Crop, AgrarianPeriod, CropPeriodRule
import logging

logger = logging.getLogger(__name__)


def init_database():
    """Initialize database with seed data"""
    
    # ========== AGRARIAN PERIODS ==========
    periods_data = [
        ('P1', 'Deep Winter Dormancy', 1, 1, 1, 20, 'high', 
         'Coldest period, inactive soil, high frost risk.'),
        ('P2', 'Late Winter Instability', 1, 21, 2, 15, 'medium',
         'Temperature fluctuations, unstable conditions.'),
        ('P3', 'Early Spring Transition', 2, 16, 3, 14, 'medium',
         'Gradual warming, late frost risk remains.'),
        ('P4', 'Spring Stability', 3, 15, 4, 30, 'low',
         'Optimal planting conditions, stable temperatures.'),
        ('P5', 'Early Summer Stress', 5, 1, 6, 15, 'medium',
         'Increasing heat, water stress begins.'),
        ('P6', 'Peak Summer Risk', 6, 16, 8, 31, 'high',
         'Extreme heat, drought conditions, minimal planting.'),
        ('P7', 'Autumn Recovery', 9, 1, 10, 15, 'medium',
         'Cooling temperatures, potential rainfall.'),
        ('P8', 'Pre-Winter Establishment', 10, 16, 11, 30, 'low',
         'Root establishment period, ideal for winter crops.'),
        ('P9', 'Early Cold Season', 12, 1, 12, 31, 'medium',
         'Cold temperatures, slow growth, dormancy onset.')
    ]
    
    for p_data in periods_data:
        if not AgrarianPeriod.query.get(p_data[0]):
            period = AgrarianPeriod(
                id=p_data[0],
                name=p_data[1],
                start_month=p_data[2],
                start_day=p_data[3],
                end_month=p_data[4],
                end_day=p_data[5],
                risk_level=p_data[6],
                description=p_data[7]
            )
            db.session.add(period)
            logger.info(f"Added period: {p_data[0]}")
    
    # ========== CROPS ==========
    crops_data = [
        ('Wheat', 'Triticum', 'field', 5, 28, 15, 25, 'medium', 120, '🌾',
         'Winter cereal, staple grain crop'),
        ('Tomato', 'Solanum lycopersicum', 'vegetable', 10, 35, 18, 28, 'high', 70, '🍅',
         'Heat-loving vegetable, frost sensitive'),
        ('Potato', 'Solanum tuberosum', 'vegetable', 7, 25, 15, 22, 'medium', 90, '🥔',
         'Cool season vegetable, moderate climate preference'),
        ('Onion', 'Allium cepa', 'vegetable', 5, 30, 13, 24, 'medium', 100, '🧅',
         'Versatile vegetable, multiple planting seasons'),
        ('Pepper', 'Capsicum', 'vegetable', 12, 33, 20, 30, 'medium', 75, '🌶️',
         'Warm season vegetable, similar to tomato'),
        ('Chickpeas', 'Cicer arietinum', 'field', 8, 32, 15, 28, 'low', 100, '🫘',
         'Legume crop, moderate cold tolerance'),
        ('Lentils', 'Lens culinaris', 'field', 6, 30, 15, 27, 'low', 110, '🥣',
         'Legume crop, cool season preference'),
        ('Olive', 'Olea europaea', 'perennial', -3, 40, 15, 35, 'low', 365, '🫒',
         'Tunisia\'s primary export crop, highly adaptable'),
        ('Citrus', 'Citrus x sinensis', 'perennial', 0, 38, 20, 35, 'medium', 365, '🍋',
         'Oranges and lemons, frost sensitive'),
        ('Almond', 'Prunus dulcis', 'perennial', -5, 35, 15, 30, 'low', 365, '🌰',
         'Early blooming tree, frost sensitive flowers'),
        ('Grape', 'Vitis vinifera', 'perennial', -2, 35, 15, 32, 'low', 365, '🍇',
         'Vine crop, drought tolerant once established')
    ]
    
    # Initialize crop_objects as an empty dictionary
    crop_objects = {}
    
    for c_data in crops_data:
        existing = Crop.query.filter_by(name=c_data[0]).first()
        if existing:
            crop_objects[c_data[0]] = existing
        else:
            crop = Crop(
                name=c_data[0],
                scientific_name=c_data[1],
                category=c_data[2],
                min_temp=c_data[3],
                max_temp=c_data[4],
                optimal_temp_min=c_data[5],
                optimal_temp_max=c_data[6],
                water_needs=c_data[7],
                growth_days=c_data[8],
                icon=c_data[9],
                description=c_data[10]
            )
            db.session.add(crop)
            db.session.flush()
            crop_objects[c_data[0]] = crop
            logger.info(f"Added crop: {c_data[0]}")
    
    # ========== CROP-PERIOD RULES ==========
    # Define rules_data as a constant
    RULES_DATA = [
        # Wheat
        ('Wheat', 'P8', 'optimal', 'Ideal pre-winter planting for wheat.'),
        ('Wheat', 'P9', 'optimal', 'Early season planting for winter wheat.'),
        ('Wheat', 'P4', 'risky', 'Late for wheat planting, spring varieties only.'),
        ('Wheat', 'P6', 'forbidden', 'Too hot for wheat growth.'),
        
        # Tomato
        ('Tomato', 'P4', 'optimal', 'Best spring planting period for tomatoes.'),
        ('Tomato', 'P3', 'risky', 'Early spring, frost risk remains.'),
        ('Tomato', 'P5', 'risky', 'Late planting, heat stress likely.'),
        ('Tomato', 'P6', 'forbidden', 'Extreme heat will damage plants.'),
        ('Tomato', 'P1', 'forbidden', 'Too cold for tomato.'),
        ('Tomato', 'P2', 'forbidden', 'Still too cold.'),
        ('Tomato', 'P9', 'forbidden', 'Winter approaching.'),
        
        # Potato
        ('Potato', 'P3', 'optimal', 'Early spring planting for potatoes.'),
        ('Potato', 'P4', 'optimal', 'Spring planting season.'),
        ('Potato', 'P7', 'acceptable', 'Autumn planting possible.'),
        ('Potato', 'P6', 'forbidden', 'Too hot for potato tubers.'),
        
        # Onion
        ('Onion', 'P3', 'optimal', 'Early spring onion planting.'),
        ('Onion', 'P4', 'optimal', 'Spring planting period.'),
        ('Onion', 'P7', 'optimal', 'Autumn planting for winter harvest.'),
        ('Onion', 'P8', 'acceptable', 'Late autumn planting.'),
        ('Onion', 'P6', 'risky', 'Heat stress on developing bulbs.'),
        
        # Pepper
        ('Pepper', 'P4', 'optimal', 'Best time for pepper transplanting.'),
        ('Pepper', 'P5', 'acceptable', 'Early summer planting.'),
        ('Pepper', 'P3', 'risky', 'Still risk of cold nights.'),
        ('Pepper', 'P6', 'risky', 'High heat stress.'),
        ('Pepper', 'P1', 'forbidden', 'Too cold.'),
        ('Pepper', 'P2', 'forbidden', 'Still too cold.'),
        
        # Chickpeas
        ('Chickpeas', 'P3', 'optimal', 'Early spring planting.'),
        ('Chickpeas', 'P4', 'optimal', 'Spring planting season.'),
        ('Chickpeas', 'P8', 'acceptable', 'Autumn planting possible.'),
        ('Chickpeas', 'P6', 'forbidden', 'Too hot and dry.'),
        
        # Lentils
        ('Lentils', 'P3', 'optimal', 'Early spring planting for lentils.'),
        ('Lentils', 'P4', 'optimal', 'Spring planting period.'),
        ('Lentils', 'P8', 'acceptable', 'Autumn planting.'),
        ('Lentils', 'P6', 'forbidden', 'Heat and drought stress.'),
        
        # Olive
        ('Olive', 'P7', 'optimal', 'Autumn planting for olives.'),
        ('Olive', 'P8', 'optimal', 'Pre-winter establishment period.'),
        ('Olive', 'P4', 'acceptable', 'Spring planting possible.'),
        ('Olive', 'P2', 'risky', 'Late winter instability.'),
        ('Olive', 'P6', 'risky', 'High water stress on young trees.'),
        
        # Citrus
        ('Citrus', 'P4', 'optimal', 'Spring planting for citrus.'),
        ('Citrus', 'P7', 'optimal', 'Autumn planting.'),
        ('Citrus', 'P8', 'acceptable', 'Late autumn planting.'),
        ('Citrus', 'P1', 'risky', 'Frost risk for young trees.'),
        ('Citrus', 'P6', 'risky', 'High heat stress.'),
        
        # Almond
        ('Almond', 'P8', 'optimal', 'Pre-winter planting.'),
        ('Almond', 'P7', 'optimal', 'Autumn planting period.'),
        ('Almond', 'P4', 'risky', 'Late frost can damage flowers.'),
        ('Almond', 'P6', 'risky', 'High heat stress.'),
        
        # Grape
        ('Grape', 'P8', 'optimal', 'Pre-winter planting for vines.'),
        ('Grape', 'P7', 'optimal', 'Autumn planting.'),
        ('Grape', 'P4', 'acceptable', 'Spring planting possible.'),
        ('Grape', 'P2', 'risky', 'Late winter instability.'),
        ('Grape', 'P6', 'risky', 'High heat stress on young vines.')
    ]
    
    # Process rules
    for rule_data in RULES_DATA:
        crop_name, period_id, suitability, reason = rule_data
        if crop_name in crop_objects:
            existing_rule = CropPeriodRule.query.filter_by(
                crop_id=crop_objects[crop_name].id,
                period_id=period_id
            ).first()
            
            if not existing_rule:
                rule = CropPeriodRule(
                    crop_id=crop_objects[crop_name].id,
                    period_id=period_id,
                    suitability=suitability,
                    reason=reason
                )
                db.session.add(rule)
    
    try:
        db.session.commit()
        logger.info("Database initialized successfully!")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        db.session.rollback()
        raise