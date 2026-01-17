"""
Input validation schemas using Marshmallow
"""
from marshmallow import Schema, fields, validate, validates, ValidationError as MarshmallowValidationError
import re


class FarmerRegistrationSchema(Schema):
    """Validation schema for farmer registration"""
    phone_number = fields.Str(
        required=True,
        validate=validate.Regexp(
            r'^216\d{8}$',
            error='Phone number must be Tunisian format (216XXXXXXXX)'
        )
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8, error='Password must be at least 8 characters')
    )
    first_name = fields.Str(
        required=True,
        validate=validate.Length(min=2, error='First name must be at least 2 characters')
    )
    last_name = fields.Str(
        required=True,
        validate=validate.Length(min=2, error='Last name must be at least 2 characters')
    )
    governorate = fields.Str(
        required=True,
        validate=validate.OneOf([
            'Tunis', 'Ariana', 'Ben Arous', 'Manouba', 'Nabeul', 'Zaghouan',
            'Bizerte', 'Beja', 'Jendouba', 'Kef', 'Siliana', 'Kairouan',
            'Kasserine', 'Sidi Bouzid', 'Sousse', 'Monastir', 'Mahdia',
            'Sfax', 'Gabes', 'Medenine', 'Tataouine', 'Gafsa', 'Tozeur', 'Kebili'
        ])
    )
    farm_type = fields.Str(
        required=True,
        validate=validate.OneOf(['rain_fed', 'irrigated'])
    )
    farm_size_ha = fields.Float(
        required=False,
        validate=validate.Range(min=0, error='Farm size must be positive')
    )
    soil_type = fields.Str(
        required=False,
        validate=validate.Length(min=2, max=50, error='Soil type must be between 2 and 50 characters')
    )
    
    @validates('password')
    def validate_password_strength(self, value, **kwargs):
        """Ensure password has minimum complexity"""
        if not re.search(r'[A-Za-z]', value):
            raise MarshmallowValidationError('Password must contain at least one letter')
        if not re.search(r'\d', value):
            raise MarshmallowValidationError('Password must contain at least one number')


class LoginSchema(Schema):
    """Validation schema for login"""
    phone = fields.Str(required=True)
    password = fields.Str(required=True)


class GetAdviceSchema(Schema):
    """Validation schema for get-advice endpoint"""
    crop_id = fields.Int(
        required=True,
        validate=validate.Range(min=1, error='Invalid crop ID')
    )
    governorate = fields.Str(
        required=False,
        validate=validate.OneOf([
            'Tunis', 'Ariana', 'Ben Arous', 'Manouba', 'Nabeul', 'Zaghouan',
            'Bizerte', 'Beja', 'Jendouba', 'Kef', 'Siliana', 'Kairouan',
            'Kasserine', 'Sidi Bouzid', 'Sousse', 'Monastir', 'Mahdia',
            'Sfax', 'Gabes', 'Medenine', 'Tataouine', 'Gafsa', 'Tozeur', 'Kebili'
        ])
    )
    seedling_cost = fields.Float(
        required=False, 
        validate=validate.Range(min=0, error='Seedling cost must be positive')
    )
    market_price = fields.Float(
        required=False, 
        validate=validate.Range(min=0, error='Market price must be positive')
    )
    input_quantity = fields.Float(
        required=False, 
        validate=validate.Range(min=0, error='Input quantity must be positive')
    )


class OutcomeSchema(Schema):
    """Validation schema for recording outcome"""
    decision_id = fields.Int(required=True)
    outcome = fields.Str(
        required=True,
        validate=validate.OneOf(['success', 'failure', 'unknown'])
    )
    yield_kg = fields.Float(required=False, validate=validate.Range(min=0))
    revenue_tnd = fields.Float(required=False, validate=validate.Range(min=0))
    notes = fields.Str(required=False, validate=validate.Length(max=500))


def validate_request(schema_class):
    """Decorator to validate request data against schema"""
    def decorator(f):
        from functools import wraps
        from flask import request
        from utils.errors import ValidationError as APIValidationError
        import logging
        
        logger = logging.getLogger(__name__)
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            schema = schema_class()
            try:
                data = request.get_json()
                
                # Log incoming data for debugging
                logger.info(f"Received {schema_class.__name__} - Raw data: {data}")
                logger.info(f"Data types: {[(k, type(v).__name__) for k, v in (data or {}).items()]}")
                
                if not data:
                    raise APIValidationError('Request body cannot be empty')
                
                validated_data = schema.load(data)
                logger.info(f"Validation successful - Validated data: {validated_data}")
                logger.info(f"Validated types: {[(k, type(v).__name__) for k, v in validated_data.items()]}")
                
                request.validated_data = validated_data
                return f(*args, **kwargs)
            except MarshmallowValidationError as err:
                logger.error(f"❌ Validation error in {schema_class.__name__}: {err.messages}")
                logger.error(f"❌ Original data was: {data}")
                raise APIValidationError(
                    message='Validation failed',
                    payload={'errors': err.messages}
                )
        return decorated_function
    return decorator