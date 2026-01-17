"""
Analytics endpoints for performance tracking
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.base import db
from models.decision import Decision, Outcome
from models.user import Farmer
from models.crop import Crop
from sqlalchemy import func, desc, case
from utils.decorators import track_performance
from utils.errors import NotFoundError
from services.regional_analytics import RegionalAnalyticsService
import logging

analytics_bp = Blueprint('analytics', __name__)
logger = logging.getLogger(__name__)

@analytics_bp.route('/regional-benchmark', methods=['GET'])
@jwt_required()
@track_performance
def get_regional_benchmark():
    """
    Enhanced Regional Performance Benchmarking
    ---
    tags:
      - Analytics
    security:
      - bearerAuth: []
    responses:
      200:
        description: Regional benchmarks vs personal performance
        schema:
          type: object
          properties:
            governorate:
              type: string
            gsi:
              type: number
              description: Governorate Success Index
            personal_benchmark:
              type: object
              description: PBD - Personal Benchmark Deviation
            top_regional_crops:
              type: array
              description: Ranked crops for region
            risk_adjusted_performance:
              type: object
              description: RRAP - Risk-Adjusted Regional Performance
      404:
        description: Farmer not found
    """
    user_id = int(get_jwt_identity())
    farmer = Farmer.query.get(user_id)
    
    if not farmer:
        return jsonify({'error': 'Farmer not found'}), 404
    
    # Calculate GSI for farmer's governorate
    gsi_data = RegionalAnalyticsService.calculate_gsi(farmer.governorate)
    
    # Calculate Personal Benchmark Deviation
    pbd_data = RegionalAnalyticsService.calculate_pbd(user_id, farmer.governorate)
    
    # Get top crops for region
    top_crops = RegionalAnalyticsService.get_top_crops_for_region(farmer.governorate, limit=5)
    
    # Calculate Risk-Adjusted Performance
    rrap_data = RegionalAnalyticsService.calculate_regional_risk_adjusted_performance(farmer.governorate)
    
    return jsonify({
        'governorate': farmer.governorate,
        'gsi': gsi_data,
        'personal_benchmark': pbd_data,
        'top_regional_crops': top_crops,
        'risk_adjusted_performance': rrap_data
    }), 200


@analytics_bp.route('/smart-summary', methods=['GET'])
@jwt_required()
def get_smart_summary():
    """
    Get a natural language interpretation of all analytics
    ---
    tags:
      - Analytics
    security:
      - bearerAuth: []
    responses:
      200:
        description: AI-generated summary
        schema:
          type: object
          properties:
            summary:
              type: string
    """
    user_id = int(get_jwt_identity())
    from services.advanced_analytics import AdvancedAnalyticsService
    summary = AdvancedAnalyticsService.generate_smart_summary(user_id)
    return jsonify({'summary': summary}), 200


@analytics_bp.route('/simulate-data', methods=['POST'])
@jwt_required()
def simulate_data():
    """
    Seeds 100 sample records for simulation mode
    ---
    tags:
      - Analytics
    security:
      - bearerAuth: []
    responses:
      201:
        description: Simulation data generated
      500:
        description: Simulation failed
    """
    user_id = int(get_jwt_identity())
    from services.advanced_analytics import AdvancedAnalyticsService
    success = AdvancedAnalyticsService.seed_user_simulation(user_id)
    
    if success:
        return jsonify({'message': 'Simulation data generated successfully'}), 201
    else:
        return jsonify({'error': 'Failed to generate simulation data'}), 500

@analytics_bp.route('/personal-insights', methods=['GET'])
@jwt_required()
@track_performance
def get_personal_insights():
    """
    Get deep insights into user's success conditions with pattern analysis
    ---
    tags:
      - Analytics
    security:
      - bearerAuth: []
    responses:
      200:
        description: Personal insights and patterns
        schema:
          type: object
          properties:
            best_crop:
              type: string
            optimal_temp:
              type: number
            patterns:
              type: array
              items:
                type: object
                properties:
                  type:
                    type: string
                  message:
                    type: string
    """
    user_id = int(get_jwt_identity())
    
    from models.crop import AgrarianPeriod
    
    # Get all successful outcomes for detailed analysis
    successful_decisions = db.session.query(Decision).join(Outcome).filter(
        Decision.farmer_id == user_id,
        Outcome.outcome == 'success'
    ).all()
    
    # Initialize insights
    insights = {
        'best_crop': None,
        'best_crop_success_rate': None,
        'best_period': None,
        'best_period_success_rate': None,
        'optimal_temp': None,
        'temp_range': None,
        'total_successes': len(successful_decisions),
        'patterns': []
    }
    
    if not successful_decisions:
        # No successes yet - provide estimated insights based on decisions
        total_decisions = Decision.query.filter_by(farmer_id=user_id).count()
        
        if total_decisions > 0:
            # Most frequent crop
            top_crop = db.session.query(
                Crop.name,
                func.count(Decision.id).label('count')
            ).join(Decision).filter(
                Decision.farmer_id == user_id
            ).group_by(Crop.name).order_by(desc('count')).first()
            
            insights['best_crop'] = top_crop[0] if top_crop else None
            insights['best_crop_success_rate'] = 'Estimated 65%'
            
        return jsonify(insights), 200
    
    # 1. Best Crop with Success Rate
    crop_analysis = db.session.query(
        Crop.name,
        func.count(Outcome.id).label('successes'),
        func.count(Decision.id).label('total')
    ).select_from(Crop).join(Decision, Crop.id == Decision.crop_id).outerjoin(Outcome, Decision.id == Outcome.decision_id).filter(
        Decision.farmer_id == user_id
    ).group_by(Crop.name).all()
    
    best_crop_data = None
    best_success_rate = 0
    
    for crop_name, successes, total in crop_analysis:
        if total > 0:
            success_rate = (successes / total) * 100
            if success_rate > best_success_rate:
                best_success_rate = success_rate
                best_crop_data = (crop_name, success_rate, successes, total)
    
    if best_crop_data:
        insights['best_crop'] = best_crop_data[0]
        insights['best_crop_success_rate'] = f"{round(best_crop_data[1], 1)}%"
        insights['patterns'].append({
            'type': 'crop_mastery',
            'message': f"🍅 {best_crop_data[2]} out of {best_crop_data[3]} {best_crop_data[0]} plantings were successful"
        })
    
    # 2. Best Period with Success Rate
    period_analysis = db.session.query(
        AgrarianPeriod.name,
        func.count(Outcome.id).label('successes')
    ).select_from(Outcome).join(Decision).join(AgrarianPeriod).filter(
        Decision.farmer_id == user_id,
        Outcome.outcome == 'success'
    ).group_by(AgrarianPeriod.name).order_by(desc('successes')).first()
    
    if period_analysis:
        insights['best_period'] = period_analysis[0]
        insights['best_period_success_rate'] = f"{period_analysis[1]} successes"
    
    # 3. Temperature Analysis
    temps = [d.weather_temp_avg for d in successful_decisions if d.weather_temp_avg]
    
    if temps:
        avg_temp = sum(temps) / len(temps)
        min_temp = min(temps)
        max_temp = max(temps)
        
        insights['optimal_temp'] = round(avg_temp, 1)
        insights['temp_range'] = {
            'min': round(min_temp, 1),
            'max': round(max_temp, 1),
            'optimal': round(avg_temp, 1)
        }
        
        insights['patterns'].append({
            'type': 'temperature_sweet_spot',
            'message': f"☀️ Your successes occur between {round(min_temp, 1)}°C and {round(max_temp, 1)}°C"
        })
    
    # 4. Identify specific winning combinations
    if len(successful_decisions) >= 3:
        # Find most common crop-period combination
        combinations = {}
        for decision in successful_decisions:
            if decision.crop and decision.period:
                key = f"{decision.crop.name}_{decision.period.name}"
                if key not in combinations:
                    combinations[key] = {
                        'crop': decision.crop.name,
                        'period': decision.period.name,
                        'count': 0,
                        'avg_temp': []
                    }
                combinations[key]['count'] += 1
                if decision.weather_temp_avg:
                    combinations[key]['avg_temp'].append(decision.weather_temp_avg)
        
        # Find best combination
        best_combo = max(combinations.values(), key=lambda x: x['count']) if combinations else None
        
        if best_combo and best_combo['count'] >= 2:
            avg_combo_temp = sum(best_combo['avg_temp']) / len(best_combo['avg_temp']) if best_combo['avg_temp'] else None
            
            message = f"🏆 Winning combo: {best_combo['crop']} during {best_combo['period']}"
            if avg_combo_temp:
                message += f" at ~{round(avg_combo_temp, 1)}°C"
            
            insights['patterns'].append({
                'type': 'winning_combination',
                'message': message,
                'count': best_combo['count']
            })
    
    from services.success_condition_analysis import SuccessConditionService
    
    # Add Success Condition Analysis to insights
    oci = SuccessConditionService.calculate_oci(user_id=user_id)
    mfsp = SuccessConditionService.find_mfsp(user_id=user_id)
    
    insights.update({
        'optimal_conditions': oci,
        'success_patterns': mfsp
    })
    
    return jsonify(insights), 200


@analytics_bp.route('/advanced', methods=['GET'])
@jwt_required()
@track_performance
def get_advanced_analytics():
    """
    Get all 6 advanced analytics metrics with statistical validation
    ---
    tags:
      - Analytics
    security:
      - bearerAuth: []
    responses:
      200:
        description: Detailed 6-point advanced analytics
        schema:
          type: object
          properties:
            advice_effectiveness_score:
              type: number
            compliance_index:
              type: number
            risk_avoidance_roi:
              type: number
            confidence_validation:
              type: number
            learning_slope:
              type: number
            crop_accuracy:
              type: number
            diversification_index:
              type: number
            opportunity_gap:
              type: number
            performance_trends:
              type: object
    """
    user_id = int(get_jwt_identity())
    farmer = Farmer.query.get(user_id)
    
    from services.advanced_analytics import AdvancedAnalyticsService
    from services.regional_analytics import RegionalAnalyticsService
    
    # Calculate all metrics
    aes = AdvancedAnalyticsService.calculate_aes(user_id)
    fci = AdvancedAnalyticsService.calculate_fci(user_id)
    rar = AdvancedAnalyticsService.calculate_rar(user_id)
    cvs = AdvancedAnalyticsService.calculate_cvs(user_id)
    tls = AdvancedAnalyticsService.calculate_tls(user_id)
    csaa = AdvancedAnalyticsService.calculate_csaa(user_id)
    
    # Add DOI and OGA to advanced response
    doi = RegionalAnalyticsService.calculate_doi(farmer.governorate, user_id) if farmer else 0
    oga = RegionalAnalyticsService.calculate_oga(farmer.governorate) if farmer else 0
    trends = AdvancedAnalyticsService.calculate_performance_trends(user_id)
    
    return jsonify({
        'advice_effectiveness_score': aes,
        'compliance_index': fci,
        'risk_avoidance_roi': rar,
        'confidence_validation': cvs,
        'learning_slope': tls,
        'crop_accuracy': csaa,
        'diversification_index': doi,
        'opportunity_gap': oga,
        'performance_trends': trends
    }), 200


@analytics_bp.route('/tier-status', methods=['GET'])
@jwt_required()
@track_performance
def get_tier_status():
    """
    Get current user's farming intelligence tier and progress
    ---
    tags:
      - Analytics
    security:
      - bearerAuth: []
    responses:
      200:
        description: Gamification tier status
    """
    user_id = int(get_jwt_identity())
    from services.truthful_engine import TruthfulAnalyticsEngine
    status = TruthfulAnalyticsEngine.get_user_tier_status(user_id)
    quality = TruthfulAnalyticsEngine.get_data_quality_score(user_id)
    return jsonify({**status, 'data_quality_score': quality}), 200


@analytics_bp.route('/milestones', methods=['GET'])
@jwt_required()
@track_performance
def get_milestones():
    """
    Get unlock status of various analytical features
    ---
    tags:
      - Analytics
    security:
      - bearerAuth: []
    responses:
      200:
        description: List of unlocked/locked milestones
    """
    user_id = int(get_jwt_identity())
    from services.truthful_engine import TruthfulAnalyticsEngine
    milestones = TruthfulAnalyticsEngine.get_milestones(user_id)
    return jsonify(milestones), 200