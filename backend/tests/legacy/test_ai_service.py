"""
AI service tests
"""
import pytest
from unittest.mock import patch, MagicMock
from services.ai_service import AIService


class TestAIService:
    """Test AI service functionality"""
    
    def test_init_without_api_key(self, monkeypatch):
        """Test initialization without API key"""
        monkeypatch.delenv('OPENAI_API_KEY', raising=False)
        service = AIService()
        assert service.enabled is False
    
    def test_init_with_api_key(self, monkeypatch):
        """Test initialization with API key"""
        monkeypatch.setenv('OPENAI_API_KEY', 'test_key')
        with patch('services.ai_service.OpenAI'):
            service = AIService()
            assert service.enabled is True
    
    @patch('services.ai_service.OpenAI')
    def test_generate_explanation_success(self, mock_openai):
        """Test successful explanation generation"""
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='This is a test explanation for farmers.'))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        service = AIService()
        service.enabled = True
        service.client = mock_client
        
        decision_data = {
            'crop_name': 'Tomato',
            'action': 'PLANT_NOW',
            'wait_days': 0,
            'period_name': 'Spring Stability',
            'risks': []
        }
        
        explanation = service.generate_explanation(decision_data)
        
        assert len(explanation) > 20
        assert 'test explanation' in explanation.lower()
    
    def test_generate_explanation_fallback(self):
        """Test fallback to template when AI fails"""
        service = AIService()
        service.enabled = False
        
        decision_data = {
            'crop_name': 'Tomato',
            'action': 'PLANT_NOW',
            'wait_days': 0,
            'period_name': 'Spring Stability',
            'risks': []
        }
        
        explanation = service.generate_explanation(decision_data)
        
        assert 'Tomato' in explanation
        assert 'Spring Stability' in explanation
    
    def test_template_explanation_plant_now(self):
        """Test template for PLANT_NOW"""
        service = AIService()
        
        decision_data = {
            'crop_name': 'Wheat',
            'action': 'PLANT_NOW',
            'period_name': 'Pre-Winter Establishment'
        }
        
        explanation = service._generate_template_explanation(decision_data)
        
        assert 'Good time' in explanation
        assert 'Wheat' in explanation
    
    def test_template_explanation_wait(self):
        """Test template for WAIT"""
        service = AIService()
        
        decision_data = {
            'crop_name': 'Tomato',
            'action': 'WAIT',
            'wait_days': 7,
            'period_name': 'Early Spring Transition',
            'risks': ['frost_risk', 'low_temperature']
        }
        
        explanation = service._generate_template_explanation(decision_data)
        
        assert 'Wait' in explanation
        assert '7' in explanation
        assert 'Tomato' in explanation
    
    def test_template_explanation_not_recommended(self):
        """Test template for NOT_RECOMMENDED"""
        service = AIService()
        
        decision_data = {
            'crop_name':' Wheat',
            'action': 'NOT_RECOMMENDED',
            'period_name': 'Peak Summer Risk'
        }
        explanation = service._generate_template_explanation(decision_data)
    
        assert 'not recommended' in explanation.lower()
        assert 'Wheat' in explanation
        