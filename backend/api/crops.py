"""
Crop information endpoints
"""
from flask import Blueprint, jsonify
from models.crop import Crop, AgrarianPeriod
from models.base import db  # Added import for db
from utils.errors import NotFoundError
from utils.decorators import track_performance, cache_response
import logging

logger = logging.getLogger(__name__)

crops_bp = Blueprint('crops', __name__)


@crops_bp.route('/', methods=['GET'])
@track_performance
@cache_response(timeout=3600)  # Cache for 1 hour
def get_all_crops():
    """
    Get all available crops
    ---
    tags:
      - Crops
    responses:
      200:
        description: A list of all crops registered in the system
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              category:
                type: string
              icon:
                type: string
    """
    crops = Crop.query.order_by(Crop.category, Crop.name).all()
    
    return jsonify([{
        'id': crop.id,
        'name': crop.name,
        'category': crop.category,
        'icon': crop.icon
    } for crop in crops]), 200


@crops_bp.route('/<int:crop_id>', methods=['GET'])
@track_performance
@cache_response(timeout=3600)
def get_crop_details(crop_id):
    """
    Get detailed information about a specific crop
    ---
    tags:
      - Crops
    parameters:
      - name: crop_id
        in: path
        type: integer
        required: true
        description: ID of the crop to filter by
    responses:
      200:
        description: Detailed crop information including planting guide
      404:
        description: Crop not found
    """
    crop = Crop.query.get(crop_id)
    
    if not crop:
        raise NotFoundError(f'Crop with ID {crop_id} not found')
    
    # Get period rules for this crop
    rules = crop.period_rules.all()
    period_info = {}
    
    for rule in rules:
        if rule.suitability not in period_info:
            period_info[rule.suitability] = []
        period_info[rule.suitability].append(rule.period_id)
    
    return jsonify({
        'id': crop.id,
        'name': crop.name,
        'scientific_name': crop.scientific_name,
        'category': crop.category,
        'min_temp': crop.min_temp,
        'max_temp': crop.max_temp,
        'optimal_temp_range': f"{crop.optimal_temp_min}-{crop.optimal_temp_max}°C" if crop.optimal_temp_min else None,
        'water_needs': crop.water_needs,
        'growth_days': crop.growth_days,
        'icon': crop.icon,
        'description': crop.description,
        'planting_guide': {
            'optimal_periods': period_info.get('optimal', []),
            'acceptable_periods': period_info.get('acceptable', []),
            'risky_periods': period_info.get('risky', []),
            'forbidden_periods': period_info.get('forbidden', [])
        }
    }), 200


@crops_bp.route('/categories', methods=['GET'])
@track_performance
@cache_response(timeout=3600)
def get_crop_categories():
    """
    Get all crop categories with counts
    ---
    tags:
      - Crops
    responses:
      200:
        description: List of crop categories and their counts
        schema:
          type: array
          items:
            type: object
            properties:
              category:
                type: string
              count:
                type: integer
    """
    from sqlalchemy import func
    
    categories = db.session.query(
        Crop.category,
        func.count(Crop.id).label('count')
    ).group_by(Crop.category).all()
    
    return jsonify([{
        'category': cat,
        'count': count
    } for cat, count in categories]), 200


@crops_bp.route('/periods', methods=['GET'])
@track_performance
@cache_response(timeout=3600)
def get_agrarian_periods():
    """
    Get all agrarian periods
    ---
    tags:
      - Crops
    responses:
      200:
        description: List of all Tunisian Agrarian Calendar periods
    """
    periods = AgrarianPeriod.query.order_by(
        AgrarianPeriod.start_month,
        AgrarianPeriod.start_day
    ).all()
    
    return jsonify([period.to_dict() for period in periods]), 200


@crops_bp.route('/periods/<period_id>', methods=['GET'])
@track_performance
@cache_response(timeout=3600)
def get_period_details(period_id):
    """
    Get detailed information about a specific period
    ---
    tags:
      - Crops
    parameters:
      - name: period_id
        in: path
        type: string
        required: true
        description: Period ID (e.g., P1, P2) or name component
    responses:
      200:
        description: Period details including suitable crops
      404:
        description: Period not found
    """
    period = AgrarianPeriod.query.get(period_id)
    
    if not period:
        raise NotFoundError(f'Period {period_id} not found')
    
    # Get crops suitable for this period
    rules = period.crop_rules.all()
    crops_by_suitability = {
        'optimal': [],
        'acceptable': [],
        'risky': [],
        'forbidden': []
    }
    
    for rule in rules:
        if rule.suitability in crops_by_suitability:
            crops_by_suitability[rule.suitability].append({
                'id': rule.crop.id,
                'name': rule.crop.name,
                'icon': rule.crop.icon,
                'reason': rule.reason
            })
    
    return jsonify({
        **period.to_dict(),
        'suitable_crops': crops_by_suitability
    }), 200