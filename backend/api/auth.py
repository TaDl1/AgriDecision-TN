"""
Authentication endpoints
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import Farmer
from models.base import db
from middleware.validators import validate_request, FarmerRegistrationSchema, LoginSchema
from utils.errors import ValidationError, AuthenticationError, ConflictError
from utils.decorators import track_performance
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@track_performance
@validate_request(FarmerRegistrationSchema)
def register():
    """
    Register a new farmer
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - phone_number
            - password
            - governorate
            - farm_type
          properties:
            phone_number:
              type: string
              example: "21612345678"
            password:
              type: string
              example: "SecurePass123"
            governorate:
              type: string
              example: "Tunis"
            farm_type:
              type: string
              enum: [rain_fed, irrigated]
            first_name:
              type: string
            last_name:
              type: string
            soil_type:
              type: string
            farm_size_ha:
              type: number
    responses:
      201:
        description: User created successfully
      400:
        description: Validation error
      409:
        description: User already exists
    """
    data = request.validated_data
    
    # Check if user already exists
    existing_farmer = Farmer.query.filter_by(phone_number=data['phone_number']).first()
    if existing_farmer:
        raise ConflictError('User with this phone number already exists')
    
    # Create new farmer
    farmer = Farmer(
        phone_number=data['phone_number'],
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        governorate=data['governorate'],
        farm_type=data['farm_type'],
        soil_type=data.get('soil_type'),
        farm_size_ha=data.get('farm_size_ha')
    )
    farmer.set_password(data['password'])
    
    try:
        db.session.add(farmer)
        db.session.commit()
        logger.info(f"New farmer registered: {farmer.phone_number}")
        
        return jsonify({
            'message': 'User created successfully',
            'farmer_id': farmer.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {e}")
        raise ValidationError('Failed to create user')


@auth_bp.route('/login', methods=['POST'])
@track_performance
@validate_request(LoginSchema)
def login():
    """
    Login farmer and return JWT token
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - phone
            - password
          properties:
            phone:
              type: string
              example: "21612345678"
            password:
              type: string
              example: "SecurePass123"
    responses:
      200:
        description: Login successful with token
      401:
        description: Invalid credentials
    """
    data = request.validated_data
    
    # Find farmer
    farmer = Farmer.query.filter_by(phone_number=data['phone']).first()
    
    if not farmer or not farmer.check_password(data['password']):
        raise AuthenticationError('Invalid credentials')
    
    if not farmer.is_active:
        raise AuthenticationError('Account is deactivated')
    
    # Create JWT token with additional claims
    additional_claims = {
        'role': farmer.role,
        'governorate': farmer.governorate
    }
    access_token = create_access_token(
        identity=str(farmer.id),
        additional_claims=additional_claims
    )
    
    # Update last login
    farmer.update_last_login()
    
    logger.info(f"Farmer logged in: {farmer.phone_number}")
    
    return jsonify({
        'token': access_token,
        'user': farmer.to_dict()
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
@track_performance
def get_current_user():
    """
    Get current authenticated user information
    ---
    tags:
      - Authentication
    security:
      - bearerAuth: []
    responses:
      200:
        description: User information
      401:
        description: Unauthorized
    """
    current_user_id = get_jwt_identity()
    farmer = Farmer.query.get(current_user_id)
    
    if not farmer:
        raise AuthenticationError('User not found')
    
    return jsonify(farmer.to_dict()), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required()
@track_performance
def refresh_token():
    """
    Refresh JWT token
    ---
    tags:
      - Authentication
    security:
      - bearerAuth: []
    responses:
      200:
        description: New token received
      401:
        description: Unauthorized
    """
    current_user_id = get_jwt_identity()
    farmer = Farmer.query.get(current_user_id)
    
    if not farmer:
        raise AuthenticationError('User not found')
    
    additional_claims = {
        'role': farmer.role,
        'governorate': farmer.governorate
    }
    new_token = create_access_token(
        identity=str(farmer.id),
        additional_claims=additional_claims
    )
    
    return jsonify({'token': new_token}), 200


@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
@track_performance
def update_profile():
    """
    Update farmer profile
    ---
    tags:
      - Authentication
    security:
      - bearerAuth: []
    parameters:
      - name: body
        in: body
        schema:
          type: object
          properties:
            first_name:
              type: string
            last_name:
              type: string
            governorate:
              type: string
            farm_type:
              type: string
            soil_type:
              type: string
            farm_size_ha:
              type: number
            phone_number:
              type: string
    responses:
      200:
        description: Profile updated successfully
      409:
        description: Phone number already in use
    """
    current_user_id = get_jwt_identity()
    farmer = Farmer.query.get(current_user_id)
    
    if not farmer:
        raise AuthenticationError('User not found')
        
    data = request.get_json()
    
    # Update allowed fields
    if 'first_name' in data:
        farmer.first_name = data['first_name']
    if 'last_name' in data:
        farmer.last_name = data['last_name']
    if 'governorate' in data:
        farmer.governorate = data['governorate']
    if 'farm_type' in data:
        farmer.farm_type = data['farm_type']
    if 'soil_type' in data:
        farmer.soil_type = data['soil_type']
    if 'farm_size_ha' in data:
        farmer.farm_size_ha = data['farm_size_ha']
        
    # Handle phone number update
    if 'phone_number' in data and data['phone_number'] != farmer.phone_number:
        new_phone = data['phone_number']
        # Check if phone is already taken
        existing_farmer = Farmer.query.filter_by(phone_number=new_phone).first()
        if existing_farmer:
            return jsonify({'error': 'Phone number already in use'}), 409
        farmer.phone_number = new_phone
        
    try:
        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully',
            'user': farmer.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Profile update failed: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500


@auth_bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_preferences():
    """
    Update user preferences
    ---
    tags:
      - Authentication
    security:
      - bearerAuth: []
    parameters:
      - name: body
        in: body
        schema:
          type: object
          properties:
            language:
              type: string
              enum: [en, fr, ar, tn]
            notifications:
              type: boolean
            units:
              type: string
              enum: [metric, imperial]
    responses:
      200:
        description: Preferences updated
    """
    current_user_id = get_jwt_identity()
    farmer = Farmer.query.get(current_user_id)
    
    if not farmer:
        return jsonify({'error': 'User not found'}), 404
        
    data = request.get_json()
    
    # Merge existing preferences with new ones
    current_prefs = farmer.preferences or {}
    updated_prefs = {**current_prefs, **data}
    
    farmer.preferences = updated_prefs
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Preferences updated',
            'preferences': farmer.preferences
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update preferences'}), 500


@auth_bp.route('/account', methods=['DELETE'])
@jwt_required()
def delete_account():
    """
    Delete farmer account and all associated data
    ---
    tags:
      - Authentication
    security:
      - bearerAuth: []
    responses:
      200:
        description: Account deleted successfully
      404:
        description: User not found
    """
    current_user_id = get_jwt_identity()
    farmer = Farmer.query.get(current_user_id)
    
    if not farmer:
        return jsonify({'error': 'User not found'}), 404
        
    try:
        # Cascade delete is configured in models, but we can be explicit if needed
        db.session.delete(farmer)
        db.session.commit()
        
        logger.info(f"Account deleted for user {current_user_id}")
        return jsonify({'message': 'Account deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Account deletion failed: {e}")
        return jsonify({'error': 'Failed to delete account'}), 500