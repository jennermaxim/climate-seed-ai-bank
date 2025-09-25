from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from models import get_db
from models.database_models import Seed, MarketData
from models.pydantic_models import SeedCreate, SeedResponse, CropType
from .auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[SeedResponse])
async def get_seeds(
    crop_type: Optional[CropType] = None,
    is_available: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get list of seeds with optional filtering"""
    query = db.query(Seed)
    
    if crop_type:
        query = query.filter(Seed.crop_type == crop_type)
    
    if is_available is not None:
        query = query.filter(Seed.is_available == is_available)
    
    seeds = query.offset(skip).limit(limit).all()
    return seeds

@router.get("/search")
async def search_seeds(
    q: str = Query(..., min_length=2, description="Search query"),
    crop_type: Optional[CropType] = None,
    drought_tolerance_min: Optional[float] = Query(None, ge=0, le=1),
    heat_tolerance_min: Optional[float] = Query(None, ge=0, le=1),
    yield_potential_min: Optional[float] = Query(None, ge=0),
    maturity_days_max: Optional[int] = Query(None, ge=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search seeds by name, characteristics, or traits"""
    query = db.query(Seed).filter(Seed.is_available == True)
    
    # Text search in variety name and scientific name
    query = query.filter(
        (Seed.variety_name.ilike(f"%{q}%")) |
        (Seed.scientific_name.ilike(f"%{q}%")) |
        (Seed.seed_company.ilike(f"%{q}%"))
    )
    
    # Apply filters
    if crop_type:
        query = query.filter(Seed.crop_type == crop_type)
    
    if drought_tolerance_min is not None:
        query = query.filter(Seed.drought_tolerance >= drought_tolerance_min)
    
    if heat_tolerance_min is not None:
        query = query.filter(Seed.heat_tolerance >= heat_tolerance_min)
    
    if yield_potential_min is not None:
        query = query.filter(Seed.yield_potential >= yield_potential_min)
    
    if maturity_days_max is not None:
        query = query.filter(Seed.maturity_days <= maturity_days_max)
    
    # Order by relevance (exact matches first, then partial matches)
    query = query.order_by(
        Seed.variety_name.ilike(f"%{q}%").desc(),
        Seed.yield_potential.desc()
    )
    
    seeds = query.offset(skip).limit(limit).all()
    
    return {
        "query": q,
        "results": seeds,
        "count": len(seeds)
    }

@router.get("/{seed_id}", response_model=SeedResponse)
async def get_seed(seed_id: int, db: Session = Depends(get_db)):
    """Get a specific seed by ID"""
    seed = db.query(Seed).filter(Seed.id == seed_id).first()
    
    if not seed:
        raise HTTPException(
            status_code=404,
            detail="Seed not found"
        )
    
    return seed

@router.get("/crop-types/available")
async def get_available_crop_types(db: Session = Depends(get_db)):
    """Get list of available crop types"""
    crop_types = db.query(Seed.crop_type).filter(
        Seed.is_available == True
    ).distinct().all()
    
    return {
        "crop_types": [ct[0] for ct in crop_types],
        "count": len(crop_types)
    }

@router.get("/{seed_id}/characteristics")
async def get_seed_characteristics(seed_id: int, db: Session = Depends(get_db)):
    """Get detailed characteristics of a seed"""
    seed = db.query(Seed).filter(Seed.id == seed_id).first()
    
    if not seed:
        raise HTTPException(
            status_code=404,
            detail="Seed not found"
        )
    
    return {
        "seed_info": {
            "variety_name": seed.variety_name,
            "scientific_name": seed.scientific_name,
            "crop_type": seed.crop_type,
            "seed_company": seed.seed_company,
            "release_year": seed.release_year
        },
        "growth_characteristics": {
            "maturity_days": seed.maturity_days,
            "yield_potential": seed.yield_potential,
            "plant_height": seed.plant_height,
            "seed_size": seed.seed_size
        },
        "climate_adaptation": {
            "drought_tolerance": seed.drought_tolerance,
            "flood_tolerance": seed.flood_tolerance,
            "heat_tolerance": seed.heat_tolerance,
            "cold_tolerance": seed.cold_tolerance,
            "adaptation_score": (seed.drought_tolerance + seed.flood_tolerance + 
                               seed.heat_tolerance + seed.cold_tolerance) / 4
        },
        "soil_requirements": {
            "preferred_ph_range": f"{seed.preferred_ph_min}-{seed.preferred_ph_max}" if seed.preferred_ph_min and seed.preferred_ph_max else None,
            "nitrogen_requirement": seed.nitrogen_requirement,
            "phosphorus_requirement": seed.phosphorus_requirement,
            "potassium_requirement": seed.potassium_requirement
        },
        "environmental_conditions": {
            "rainfall_range": f"{seed.min_rainfall}-{seed.max_rainfall} mm" if seed.min_rainfall and seed.max_rainfall else None,
            "temperature_range": f"{seed.optimal_temp_min}-{seed.optimal_temp_max}°C" if seed.optimal_temp_min and seed.optimal_temp_max else None,
            "altitude_range": f"{seed.altitude_min}-{seed.altitude_max}m" if seed.altitude_min and seed.altitude_max else None
        },
        "nutritional_value": {
            "protein_content": seed.protein_content,
            "carbohydrate_content": seed.carbohydrate_content,
            "fat_content": seed.fat_content,
            "vitamin_content": seed.vitamin_content,
            "mineral_content": seed.mineral_content
        },
        "certification": {
            "is_certified": seed.is_certified,
            "is_available": seed.is_available
        }
    }

@router.get("/{seed_id}/suitability")
async def get_seed_suitability(
    seed_id: int,
    latitude: float = Query(..., ge=-1.5, le=4.0, description="Farm latitude"),
    longitude: float = Query(..., ge=29.5, le=35.0, description="Farm longitude"),
    season: str = Query("A", description="Growing season (A or B)"),
    db: Session = Depends(get_db)
):
    """Get suitability analysis for a seed at a specific location"""
    from services.recommendation_engine import SeedRecommendationEngine
    from services.soil_service import SoilAnalysisService
    from services.climate_service import WeatherDataService, ClimateProjectionService
    
    seed = db.query(Seed).filter(Seed.id == seed_id).first()
    
    if not seed:
        raise HTTPException(
            status_code=404,
            detail="Seed not found"
        )
    
    try:
        # Initialize services
        soil_service = SoilAnalysisService()
        weather_service = WeatherDataService()
        climate_service = ClimateProjectionService()
        
        # Get environmental analysis
        soil_data = soil_service.get_soil_data_from_coordinates(latitude, longitude)
        weather_patterns = weather_service.get_seasonal_patterns(latitude, longitude)
        projections = climate_service.get_climate_projections(latitude, longitude)
        climate_risks = climate_service.calculate_climate_risks(weather_patterns, projections)
        
        # Analyze soil suitability
        soil_suitability = soil_service.analyze_soil_suitability(soil_data, seed.crop_type)
        
        # Create temporary farm object for analysis
        temp_farm = type('Farm', (), {
            'latitude': latitude,
            'longitude': longitude,
            'elevation': 1200,  # Default for Uganda
            'id': 0
        })()
        
        # Get AI recommendation
        engine = SeedRecommendationEngine()
        recommendations = engine.generate_recommendations(
            temp_farm, [seed], season, datetime.now().year
        )
        
        rec = recommendations[0] if recommendations else None
        
        return {
            "seed": {
                "id": seed.id,
                "variety_name": seed.variety_name,
                "crop_type": seed.crop_type
            },
            "location": {"latitude": latitude, "longitude": longitude},
            "season": season,
            "suitability_analysis": {
                "overall_score": rec.compatibility_score if rec else 0.5,
                "climate_match": rec.climate_match_score if rec else 0.5,
                "soil_match": rec.soil_match_score if rec else soil_suitability.suitability_score,
                "risk_level": rec.risk_score if rec else 0.5,
                "confidence": rec.confidence_level if rec else 0.5
            },
            "predictions": {
                "expected_yield": rec.yield_prediction if rec else seed.yield_potential,
                "yield_range": {
                    "min": (rec.yield_prediction * 0.8) if rec else (seed.yield_potential * 0.8),
                    "max": (rec.yield_prediction * 1.2) if rec else (seed.yield_potential * 1.2)
                }
            },
            "recommendations": {
                "reasons": rec.reasons if rec else ["Analysis completed"],
                "soil_recommendations": soil_suitability.recommendations,
                "climate_adaptations": climate_service.get_adaptation_recommendations(
                    climate_risks, seed.crop_type
                )
            },
            "environmental_conditions": {
                "soil_ph": soil_data.ph_level if soil_data else None,
                "soil_texture": soil_data.texture if soil_data else None,
                "climate_risk": climate_risks.get("overall_risk", 0.3),
                "seasonal_rainfall": weather_patterns.get("seasonal", {}).get(
                    "wet_season_1" if season == "A" else "wet_season_2", {}
                ).get("total_rainfall")
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing suitability: {str(e)}"
        )

@router.get("/{seed_id}/market-data")
async def get_seed_market_data(seed_id: int, db: Session = Depends(get_db)):
    """Get market data for a seed"""
    seed = db.query(Seed).filter(Seed.id == seed_id).first()
    
    if not seed:
        raise HTTPException(
            status_code=404,
            detail="Seed not found"
        )
    
    # Get market data (this would come from MarketData table when implemented)
    market_data = db.query(MarketData).filter(
        MarketData.seed_id == seed_id
    ).order_by(MarketData.price_date.desc()).limit(10).all()
    
    return {
        "seed": {
            "id": seed.id,
            "variety_name": seed.variety_name,
            "crop_type": seed.crop_type
        },
        "market_data": market_data,
        "summary": {
            "latest_price": market_data[0].price_per_kg if market_data else None,
            "price_trend": market_data[0].price_trend if market_data else None,
            "demand_level": market_data[0].demand_level if market_data else None,
            "data_points": len(market_data)
        }
    }

@router.get("/compare/{seed_id1}/{seed_id2}")
async def compare_seeds(seed_id1: int, seed_id2: int, db: Session = Depends(get_db)):
    """Compare two seeds side by side"""
    seed1 = db.query(Seed).filter(Seed.id == seed_id1).first()
    seed2 = db.query(Seed).filter(Seed.id == seed_id2).first()
    
    if not seed1 or not seed2:
        raise HTTPException(
            status_code=404,
            detail="One or both seeds not found"
        )
    
    def seed_summary(seed):
        return {
            "id": seed.id,
            "variety_name": seed.variety_name,
            "crop_type": seed.crop_type,
            "maturity_days": seed.maturity_days,
            "yield_potential": seed.yield_potential,
            "drought_tolerance": seed.drought_tolerance,
            "flood_tolerance": seed.flood_tolerance,
            "heat_tolerance": seed.heat_tolerance,
            "cold_tolerance": seed.cold_tolerance,
            "preferred_ph_range": f"{seed.preferred_ph_min}-{seed.preferred_ph_max}" if seed.preferred_ph_min and seed.preferred_ph_max else None,
            "rainfall_range": f"{seed.min_rainfall}-{seed.max_rainfall}" if seed.min_rainfall and seed.max_rainfall else None,
            "protein_content": seed.protein_content,
            "adaptation_score": (seed.drought_tolerance + seed.flood_tolerance + 
                               seed.heat_tolerance + seed.cold_tolerance) / 4
        }
    
    comparison = {
        "seed1": seed_summary(seed1),
        "seed2": seed_summary(seed2),
        "comparison": {
            "same_crop_type": seed1.crop_type == seed2.crop_type,
            "maturity_difference": abs((seed1.maturity_days or 0) - (seed2.maturity_days or 0)),
            "yield_difference": abs((seed1.yield_potential or 0) - (seed2.yield_potential or 0)),
            "adaptation_difference": abs(
                ((seed1.drought_tolerance + seed1.flood_tolerance + seed1.heat_tolerance + seed1.cold_tolerance) / 4) -
                ((seed2.drought_tolerance + seed2.flood_tolerance + seed2.heat_tolerance + seed2.cold_tolerance) / 4)
            )
        },
        "recommendations": []
    }
    
    # Add comparison recommendations
    if comparison["comparison"]["same_crop_type"]:
        if seed1.yield_potential and seed2.yield_potential:
            if seed1.yield_potential > seed2.yield_potential:
                comparison["recommendations"].append(f"{seed1.variety_name} has higher yield potential")
            elif seed2.yield_potential > seed1.yield_potential:
                comparison["recommendations"].append(f"{seed2.variety_name} has higher yield potential")
        
        if seed1.drought_tolerance > seed2.drought_tolerance:
            comparison["recommendations"].append(f"{seed1.variety_name} is more drought tolerant")
        elif seed2.drought_tolerance > seed1.drought_tolerance:
            comparison["recommendations"].append(f"{seed2.variety_name} is more drought tolerant")
    else:
        comparison["recommendations"].append("Different crop types - consider seasonal rotation")
    
    return comparison