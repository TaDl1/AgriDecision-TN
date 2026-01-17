from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.voice_service import DerjaVoiceParser

voice_bp = Blueprint('voice', __name__)
parser = DerjaVoiceParser()

@voice_bp.route('/parse', methods=['POST'])
@jwt_required()
def parse_voice():
    """
    Parse Tunisian Derja voice transcript to structured data
    ---
    tags:
      - Tools
    security:
      - bearerAuth: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - text
          properties:
            text:
              type: string
              example: "nheb nezra3 tomat fi tunis"
    responses:
      200:
        description: Extracted entities
        schema:
          type: object
          properties:
            status:
              type: string
            data:
              type: object
    """
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        result = parser.parse(data['text'])
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
