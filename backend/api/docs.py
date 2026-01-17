from flask import Blueprint, jsonify

docs_bp = Blueprint('docs', __name__)


@docs_bp.route('/swagger.json')
def swagger_spec():
    """
    OpenAPI/Swagger specification
    
    Returns:
        200: OpenAPI spec
    """
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "AgriDecision-TN API",
            "description": "Agricultural Decision Support System for Tunisian Farmers",
            "version": "1.0.0",
            "contact": {
                "name": "AgriDecision-TN",
                "email": "support@agridecision.tn"
            }
        },
        "servers": [
            {
                "url": "http://localhost:5000",
                "description": "Development server"
            },
            {
                "url": "https://api.agridecision.tn",
                "description": "Production server"
            }
        ],
        "tags": [
            {"name": "Authentication", "description": "User authentication endpoints"},
            {"name": "Crops", "description": "Crop information endpoints"},
            {"name": "Decisions", "description": "Planting decision endpoints"},
            {"name": "Analytics", "description": "Analytics and statistics endpoints"},
            {"name": "Health", "description": "Health check endpoints"}
        ],
        "paths": {
            "/api/auth/register": {
                "post": {
                    "tags": ["Authentication"],
                    "summary": "Register new farmer",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["phone_number", "password", "governorate", "farm_type"],
                                    "properties": {
                                        "phone_number": {"type": "string", "example": "21612345678"},
                                        "password": {"type": "string", "example": "SecurePass123"},
                                        "governorate": {"type": "string", "example": "Tunis"},
                                        "farm_type": {"type": "string", "enum": ["rain_fed", "irrigated"]}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "User created successfully"},
                        "400": {"description": "Validation error"},
                        "409": {"description": "User already exists"}
                    }
                }
            },
            "/api/auth/login": {
                "post": {
                    "tags": ["Authentication"],
                    "summary": "Login farmer",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["phone", "password"],
                                    "properties": {
                                        "phone": {"type": "string"},
                                        "password": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Login successful"},
                        "401": {"description": "Invalid credentials"}
                    }
                }
            },
            "/api/crops/": {
                "get": {
                    "tags": ["Crops"],
                    "summary": "Get all crops",
                    "responses": {
                        "200": {"description": "List of crops"}
                    }
                }
            },
            "/api/decisions/get-advice": {
                "post": {
                    "tags": ["Decisions"],
                    "summary": "Get planting advice",
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["crop_id"],
                                    "properties": {
                                        "crop_id": {"type": "integer"},
                                        "governorate": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Advice generated successfully"},
                        "401": {"description": "Unauthorized"},
                        "404": {"description": "Crop not found"}
                    }
                }
            }
        },
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        }
    }
    
    return jsonify(spec), 200