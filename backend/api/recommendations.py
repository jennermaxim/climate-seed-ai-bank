from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from models import get_db
from models.database_models import Farm, Seed, SeedRecommendation, User
from models.pydantic_models import (
    RecommendationRequest, SeedRecommendationResponse, 
    Season, CropType, AdaptationGuidance
)
from services.recommendation_engine import SeedRecommendationEngine
from services.climate_service import WeatherDataService, ClimateProjectionService
from services.soil_service import SoilAnalysisService
from .auth import get_current_active_user

router = APIRouter()

# Initialize services
recommendation_engine = SeedRecommendationEngine()
weather_service = WeatherDataService()
climate_service = ClimateProjectionService()
soil_service = SoilAnalysisService()

@router.get("/my-recommendations")
async def get_my_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get personalized seed recommendations for current user's farms"""
    try:
        # Get user's farms
        user_farms = db.query(Farm).filter(Farm.owner_id == current_user.id).all()
        farm_ids = [farm.id for farm in user_farms]
        
        if not farm_ids:
            return []
        
        # Get recommendations with seed details
        recommendations = db.query(SeedRecommendation).filter(
            SeedRecommendation.farm_id.in_(farm_ids)
        ).all()
        
        # Convert to response format with farm names
        response_recs = []
        for rec in recommendations:
            try:
                farm = next((f for f in user_farms if f.id == rec.farm_id), None)
                farm_name = farm.farm_name if farm else f"Farm {rec.farm_id}"
                
                # Get the seed details
                seed = db.query(Seed).filter(Seed.id == rec.seed_id).first()
                seed_name = seed.variety_name if seed else "Unknown Variety"
                crop_type = seed.crop_type if seed else "Unknown"
                
                # Handle JSON fields safely
                reasoning = rec.reasoning if rec.reasoning else {"main": "AI recommendation based on farm conditions"}
                risk_factors = rec.risk_factors if rec.risk_factors else []
                planting_window = rec.planting_window if rec.planting_window else {"start": "March", "end": "April"}
                
                response_recs.append(SeedRecommendationResponse(
                    id=rec.id,
                    seed_id=rec.seed_id,
                    seed_name=seed_name,
                    crop_type=crop_type,
                    suitability_score=rec.suitability_score or 0.75,
                    climate_match_score=rec.climate_match_score or 0.85,
                    soil_match_score=rec.soil_match_score or 0.80,
                    market_potential_score=rec.market_potential_score or 0.75,
                    risk_score=rec.risk_score or 0.3,
                    confidence_level=rec.confidence_level or 0.7,
                    expected_yield=rec.expected_yield,
                    expected_profit=rec.expected_profit,
                    reasoning=reasoning,
                    risk_factors=risk_factors if isinstance(risk_factors, list) else [str(risk_factors)] if risk_factors else [],
                    planting_window=planting_window if isinstance(planting_window, dict) else {"start": "March", "end": "April"},
                    seed_rate=rec.seed_rate,
                    fertilizer_recommendation=rec.fertilizer_recommendation,
                    irrigation_schedule=rec.irrigation_schedule,
                    pest_management=rec.pest_management
                ))
            except Exception as e:
                print(f"Error processing recommendation {rec.id}: {e}")
                continue
        
        return response_recs
        
    except Exception as e:
        print(f"Error in get_my_recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching recommendations: {str(e)}")@router.post("/", response_model=List[SeedRecommendationResponse])
async def get_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered seed recommendations for a farm"""
    # Verify farm ownership
    farm = db.query(Farm).filter(
        Farm.id == request.farm_id,
        Farm.owner_id == current_user.id
    ).first()
    
    if not farm:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )
    
    try:
        # Get available seeds
        seed_query = db.query(Seed).filter(Seed.is_available == True)
        
        if request.preferred_crops:
            seed_query = seed_query.filter(Seed.crop_type.in_(request.preferred_crops))
        
        available_seeds = seed_query.all()
        
        if not available_seeds:
            raise HTTPException(
                status_code=404,
                detail="No suitable seeds found for the specified criteria"
            )
        
        # Generate recommendations
        preferences = {
            "budget_constraint": request.budget_constraint,
            "risk_tolerance": request.risk_tolerance,
            "market_preference": request.market_preference,
            "include_experimental": request.include_experimental
        }
        
        recommendations = recommendation_engine.generate_recommendations(
            farm, available_seeds, request.season, request.year, preferences
        )
        
        # Save recommendations to database
        db_recommendations = []
        for rec in recommendations:
            seed = next(s for s in available_seeds if s.id == rec.seed_id)
            
            db_rec = SeedRecommendation(
                farm_id=request.farm_id,
                seed_id=rec.seed_id,
                season=request.season,
                year=request.year,
                suitability_score=rec.compatibility_score,
                climate_match_score=rec.climate_match_score,
                soil_match_score=rec.soil_match_score,
                risk_score=rec.risk_score,
                confidence_level=rec.confidence_level,
                expected_yield=rec.yield_prediction,
                reasoning={"reasons": rec.reasons},
                recommendation_date=datetime.utcnow()
            )
            
            db.add(db_rec)
            db_recommendations.append({
                "id": 0,  # Will be set after commit
                "seed_id": rec.seed_id,
                "seed_name": seed.variety_name,
                "crop_type": seed.crop_type,
                "suitability_score": rec.compatibility_score,
                "climate_match_score": rec.climate_match_score,
                "soil_match_score": rec.soil_match_score,
                "market_potential_score": 0.7,  # Default
                "risk_score": rec.risk_score,
                "confidence_level": rec.confidence_level,
                "expected_yield": rec.yield_prediction,
                "expected_profit": None,  # Would need market data
                "reasoning": {"reasons": rec.reasons},
                "risk_factors": ["Climate variability", "Market fluctuations"],
                "planting_window": {"start": f"{request.year}-03-01", "end": f"{request.year}-04-30"},
                "seed_rate": seed.yield_potential * 0.1 if seed.yield_potential else 25,  # Estimated
                "fertilizer_recommendation": {
                    "NPK": "50-25-25 kg/ha",
                    "organic": "5 tons/ha compost"
                },
                "irrigation_schedule": None,
                "pest_management": {
                    "preventive": "Use certified seeds, crop rotation",
                    "monitoring": "Weekly field scouting"
                }
            })
        
        db.commit()
        
        return db_recommendations
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )

@router.get("/farm/{farm_id}")
async def get_farm_recommendations(
    farm_id: int,
    season: Optional[Season] = None,
    year: Optional[int] = None,
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get historical recommendations for a farm"""
    # Verify farm ownership
    farm = db.query(Farm).filter(
        Farm.id == farm_id,
        Farm.owner_id == current_user.id
    ).first()
    
    if not farm:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )
    
    query = db.query(SeedRecommendation).filter(SeedRecommendation.farm_id == farm_id)
    
    if season:
        query = query.filter(SeedRecommendation.season == season)
    
    if year:
        query = query.filter(SeedRecommendation.year == year)
    
    recommendations = query.order_by(
        SeedRecommendation.recommendation_date.desc()
    ).limit(limit).all()
    
    return {
        "farm_id": farm_id,
        "recommendations": recommendations,
        "count": len(recommendations)
    }

@router.get("/adaptation-guidance/{farm_id}")
async def get_adaptation_guidance(
    farm_id: int,
    season: Season = Query(..., description="Season for guidance"),
    year: int = Query(..., ge=2024, le=2035, description="Year for guidance"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> AdaptationGuidance:
    """Get climate adaptation guidance for a farm"""
    # Verify farm ownership
    farm = db.query(Farm).filter(
        Farm.id == farm_id,
        Farm.owner_id == current_user.id
    ).first()
    
    if not farm:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )
    
    try:
        # Get climate projections and risks
        projections = climate_service.get_climate_projections(
            farm.latitude, farm.longitude, year - datetime.now().year
        )
        
        weather_patterns = weather_service.get_seasonal_patterns(farm.latitude, farm.longitude)
        climate_risks = climate_service.calculate_climate_risks(weather_patterns, projections)
        
        # Generate guidance
        guidance = AdaptationGuidance(
            farm_id=farm_id,
            season=season,
            year=year,
            climate_alerts=[],
            irrigation_recommendations=[],
            planting_schedule={},
            pest_disease_forecast=[],
            market_timing={},
            emergency_measures=[],
            confidence_level=0.8
        )
        
        # Climate alerts
        if climate_risks.get("drought_risk", 0) > 0.6:
            guidance.climate_alerts.append({
                "type": "drought_warning",
                "severity": "high" if climate_risks["drought_risk"] > 0.8 else "medium",
                "message": "High drought risk predicted for this season",
                "action": "Consider drought-tolerant varieties and water conservation"
            })
        
        if climate_risks.get("flood_risk", 0) > 0.4:
            guidance.climate_alerts.append({
                "type": "flood_warning",
                "severity": "medium",
                "message": "Increased flood risk expected",
                "action": "Improve drainage and consider flood-tolerant varieties"
            })
        
        # Irrigation recommendations
        if farm.irrigation_available:
            if climate_risks.get("drought_risk", 0) > 0.5:
                guidance.irrigation_recommendations.append({
                    "timing": "early_season",
                    "frequency": "2-3 times per week",
                    "amount": "25-30mm per week",
                    "method": "drip irrigation recommended for water efficiency"
                })
        else:
            if climate_risks.get("drought_risk", 0) > 0.6:
                guidance.irrigation_recommendations.append({
                    "recommendation": "Consider installing irrigation system",
                    "alternatives": "Use mulching and water harvesting techniques",
                    "priority": "high"
                })
        
        # Planting schedule
        if season == "A":
            guidance.planting_schedule = {
                "optimal_start": f"{year}-03-15",
                "optimal_end": f"{year}-04-15",
                "early_warning": "Monitor weather forecasts before planting",
                "backup_plan": "Have fast-maturing varieties ready"
            }
        else:  # Season B
            guidance.planting_schedule = {
                "optimal_start": f"{year}-09-01",
                "optimal_end": f"{year}-10-15",
                "early_warning": "Be prepared for variable rainfall",
                "backup_plan": "Consider drought-tolerant options"
            }
        
        # Pest and disease forecast
        guidance.pest_disease_forecast.append({
            "pest_type": "Fall Armyworm",
            "risk_level": "medium",
            "peak_period": "Early growing season",
            "management": "Monitor weekly, use pheromone traps"
        })
        
        # Market timing
        guidance.market_timing = {
            "optimal_harvest_period": "Peak dry season for best prices",
            "storage_advice": "Ensure proper drying to 12-14% moisture content",
            "market_outlook": "Stable to increasing demand expected"
        }
        
        # Emergency measures
        if climate_risks.get("overall_risk", 0) > 0.6:
            guidance.emergency_measures.extend([
                "Maintain emergency seed reserve",
                "Diversify with short-season varieties",
                "Strengthen farmer group participation",
                "Consider crop insurance options"
            ])
        
        return guidance
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating adaptation guidance: {str(e)}"
        )

@router.post("/{recommendation_id}/feedback")
async def provide_recommendation_feedback(
    recommendation_id: int,
    feedback: str = Query(..., description="Feedback: accepted, rejected, or implemented"),
    notes: Optional[str] = Query(None, description="Additional notes"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Provide feedback on a recommendation"""
    # Get recommendation and verify ownership
    recommendation = db.query(SeedRecommendation).join(Farm).filter(
        SeedRecommendation.id == recommendation_id,
        Farm.owner_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=404,
            detail="Recommendation not found"
        )
    
    # Update feedback
    recommendation.farmer_feedback = feedback
    if notes:
        recommendation.implementation_notes = notes
    
    db.commit()
    
    return {
        "message": "Feedback recorded successfully",
        "recommendation_id": recommendation_id,
        "feedback": feedback
    }

@router.get("/statistics")
async def get_recommendation_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get recommendation statistics for the current user"""
    # Get user's farms
    user_farms = db.query(Farm).filter(Farm.owner_id == current_user.id).all()
    farm_ids = [farm.id for farm in user_farms]
    
    if not farm_ids:
        return {
            "total_recommendations": 0,
            "accepted_recommendations": 0,
            "implemented_recommendations": 0,
            "top_recommended_crops": [],
            "success_rate": 0.0
        }
    
    # Get recommendations for user's farms
    recommendations = db.query(SeedRecommendation).filter(
        SeedRecommendation.farm_id.in_(farm_ids)
    ).all()
    
    total_recommendations = len(recommendations)
    accepted = len([r for r in recommendations if r.farmer_feedback == "accepted"])
    implemented = len([r for r in recommendations if r.farmer_feedback == "implemented"])
    
    # Get top recommended crops
    crop_counts = {}
    for rec in recommendations:
        seed = db.query(Seed).filter(Seed.id == rec.seed_id).first()
        if seed:
            crop_type = seed.crop_type
            crop_counts[crop_type] = crop_counts.get(crop_type, 0) + 1
    
    top_crops = sorted(crop_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_recommendations": total_recommendations,
        "accepted_recommendations": accepted,
        "implemented_recommendations": implemented,
        "top_recommended_crops": [{"crop": crop, "count": count} for crop, count in top_crops],
        "success_rate": round((accepted + implemented) / total_recommendations * 100, 1) if total_recommendations > 0 else 0.0,
        "farms_count": len(user_farms)
    }