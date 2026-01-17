"""
AI service for generating explanations using OpenAI
"""
import os
import logging
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered explanation generation"""
    
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.enabled = False
        self.client = None
        
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                self.enabled = True
                logger.info("OpenAI service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.enabled = False
        else:
            logger.info("OpenAI API Key missing. Using template explanations.")
    
    def generate_explanation(self, decision_data: Dict) -> str:
        """
        Generate farmer-friendly explanation for a decision
        
        Args:
            decision_data: Dictionary containing decision context
        
        Returns:
            Human-readable explanation string
        """
        if not self.enabled:
            logger.info("Using template explanation (AI Disabled)")
            return self._generate_template_explanation(decision_data)
        
        try:
            prompt = self._build_prompt(decision_data)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an agricultural advisor for Tunisian farmers. "
                            "Explain planting decisions in simple, clear language. "
                            "Use simple vocabulary (primary school level). "
                            "Be specific about timeframes (days). "
                            "Keep explanation to 2-3 sentences maximum. "
                            "Be practical and encouraging."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=120
            )
            
            explanation = response.choices[0].message.content.strip()
            
            if len(explanation) > 20:
                return explanation
            else:
                raise ValueError("AI response too short")
        
        except Exception as e:
            logger.warning(f"AI Service Error: {e}. Falling back to template.")
            return self._generate_template_explanation(decision_data)
    
    def _build_prompt(self, data: Dict) -> str:
        """Build prompt for AI"""
        crop = data.get('crop_name', 'the crop')
        action = data.get('action', 'WAIT')
        wait_days = data.get('wait_days', 0)
        period = data.get('period_name', 'the current period')
        risks = data.get('risks', [])
        
        prompt = f"Explain this planting decision to a Tunisian farmer:\n"
        prompt += f"Crop: {crop}\n"
        prompt += f"Current agrarian period: {period}\n"
        prompt += f"Recommendation: {action}\n"
        
        if wait_days > 0:
            prompt += f"Wait time: {wait_days} days\n"
        
        if risks:
            prompt += f"Weather risks detected: {', '.join(risks)}\n"
        
        prompt += "\nPlease generate a clear, simple explanation."
        return prompt
    
    def _generate_template_explanation(self, data: Dict) -> str:
        """Generate template-based explanation as fallback"""
        action = data.get('action', 'WAIT')
        crop = data.get('crop_name', 'this crop')
        period = data.get('period_name', '')
        
        if action == 'PLANT_NOW':
            return f"Good time to plant {crop}. The {period} period provides ideal conditions for growth and weather is favorable."
        elif action == 'WAIT':
            days = data.get('wait_days', 'a few')
            reasons = ', '.join(data.get('risks', ['unstable weather']))
            return f"Wait {days} days before planting {crop}. The {period} period has {reasons} that could harm young plants."
        else:  # NOT_RECOMMENDED
            return f"{crop} is not recommended right now. This is {period} period with high risks. Consider planting in a different season."