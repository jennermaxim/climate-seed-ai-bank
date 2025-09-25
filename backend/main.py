from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

from models import get_db, create_tables, init_sample_data
from models.database_models import User, Farm, Seed, SeedRecommendation
from models.pydantic_models import (
    UserCreate, UserResponse, FarmCreate, FarmResponse,
    SoilProfileCreate, SoilProfileResponse, RecommendationRequest,
    SeedRecommendationResponse, Token, TokenData
)
from services.recommendation_engine import SeedRecommendationEngine
from services.climate_service import WeatherDataService
from services.soil_service import SoilAnalysisService
from api.auth import get_current_user, create_access_token, authenticate_user
from api.farms import router as farms_router
from api.seeds import router as seeds_router
from api.recommendations import router as recommendations_router
from api.analytics import router as analytics_router
from api.climate import router as climate_router

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Climate-Adaptive Seed AI Bank",
    description="AI-powered platform for climate-resilient agriculture in Uganda",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
recommendation_engine = SeedRecommendationEngine()
weather_service = WeatherDataService()
soil_service = SoilAnalysisService()

# Create database tables and initialize sample data
@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    create_tables()
    init_sample_data()
    
    # Try to load pre-trained models
    try:
        recommendation_engine.load_models()
    except Exception as e:
        print(f"No pre-trained models found: {e}")

# Include API routers
app.include_router(farms_router, prefix="/api/farms", tags=["Farms"])
app.include_router(seeds_router, prefix="/api/seeds", tags=["Seeds"])
app.include_router(recommendations_router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(climate_router, prefix="/api/climate", tags=["Climate"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Climate-Adaptive Seed AI Bank",
        "version": "1.0.0",
        "description": "AI-powered platform for climate-resilient agriculture in Uganda",
        "docs_url": "/api/docs",
        "status": "active"
    }

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "recommendation_engine": "active" if recommendation_engine.is_trained else "basic",
            "weather_service": "active",
            "soil_service": "active"
        }
    }

# User authentication endpoints
@app.post("/api/auth/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    from api.auth import create_user
    return create_user(db, user)

@app.post("/api/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """User login endpoint"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

# Quick recommendation endpoint (simplified)
@app.post("/api/quick-recommendation")
async def get_quick_recommendation(
    latitude: float,
    longitude: float,
    crop_type: str = "maize",
    season: str = "A",
    db: Session = Depends(get_db)
):
    """Get quick seed recommendation based on location and crop type"""
    try:
        # Get available seeds for the crop type
        seeds = db.query(Seed).filter(
            Seed.crop_type == crop_type,
            Seed.is_available == True
        ).limit(5).all()
        
        if not seeds:
            raise HTTPException(
                status_code=404,
                detail=f"No seeds available for crop type: {crop_type}"
            )
        
        # Create temporary farm object for analysis
        temp_farm = type('Farm', (), {
            'latitude': latitude,
            'longitude': longitude,
            'elevation': 1200,  # Default elevation for Uganda
            'id': 0
        })()
        
        # Generate recommendations
        recommendations = recommendation_engine.generate_recommendations(
            temp_farm, seeds, season, datetime.now().year
        )
        
        # Format response
        results = []
        for rec in recommendations[:3]:  # Top 3 recommendations
            seed = next(s for s in seeds if s.id == rec.seed_id)
            results.append({
                "variety_name": seed.variety_name,
                "crop_type": seed.crop_type,
                "compatibility_score": round(rec.compatibility_score, 2),
                "expected_yield": round(rec.yield_prediction, 1),
                "risk_level": "Low" if rec.risk_score < 0.3 else "Medium" if rec.risk_score < 0.7 else "High",
                "main_benefits": rec.reasons[:2],
                "maturity_days": seed.maturity_days,
                "drought_tolerance": seed.drought_tolerance
            })
        
        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "crop_type": crop_type,
            "season": season,
            "recommendations": results,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )

# Climate analysis endpoint
@app.get("/api/climate-analysis")
async def get_climate_analysis(latitude: float, longitude: float):
    """Get climate analysis for a location"""
    try:
        # Get current weather
        current_weather = weather_service.get_current_weather(latitude, longitude)
        
        # Get seasonal patterns
        seasonal_patterns = weather_service.get_seasonal_patterns(latitude, longitude)
        
        # Get climate projections
        from services.climate_service import ClimateProjectionService
        climate_service = ClimateProjectionService()
        projections = climate_service.get_climate_projections(latitude, longitude)
        
        # Calculate risks
        climate_risks = climate_service.calculate_climate_risks(seasonal_patterns, projections)
        
        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "current_weather": {
                "temperature": current_weather.temperature_avg if current_weather else None,
                "rainfall": current_weather.rainfall if current_weather else None,
                "humidity": current_weather.humidity if current_weather else None
            },
            "seasonal_summary": seasonal_patterns.get("seasonal", {}),
            "climate_risks": climate_risks,
            "projections_summary": {
                "avg_temp_increase": sum(p.temperature_change for p in projections[:5]) / 5 if projections else 0,
                "avg_precip_change": sum(p.precipitation_change for p in projections[:5]) / 5 if projections else 0
            },
            "analysis_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing climate: {str(e)}"
        )

# Soil analysis endpoint
@app.get("/api/soil-analysis")
async def get_soil_analysis(latitude: float, longitude: float, crop_type: str = "maize"):
    """Get soil analysis for a location"""
    try:
        # Get soil data
        soil_data = soil_service.get_soil_data_from_coordinates(latitude, longitude)
        
        if not soil_data:
            raise HTTPException(
                status_code=500,
                detail="Unable to retrieve soil data for this location"
            )
        
        # Analyze suitability for crop
        suitability = soil_service.analyze_soil_suitability(soil_data, crop_type)
        
        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "soil_properties": {
                "ph_level": round(soil_data.ph_level, 1),
                "organic_matter": round(soil_data.organic_matter, 1),
                "nitrogen": round(soil_data.nitrogen, 1),
                "phosphorus": round(soil_data.phosphorus, 1),
                "potassium": round(soil_data.potassium, 1),
                "texture": soil_data.texture,
                "drainage": soil_data.drainage
            },
            "crop_suitability": {
                "crop_type": crop_type,
                "suitability_score": round(suitability.suitability_score, 2),
                "suitability_level": (
                    "Excellent" if suitability.suitability_score > 0.8 else
                    "Good" if suitability.suitability_score > 0.6 else
                    "Fair" if suitability.suitability_score > 0.4 else
                    "Poor"
                ),
                "limiting_factors": suitability.limiting_factors,
                "recommendations": suitability.recommendations,
                "confidence_level": round(suitability.confidence_level, 2)
            },
            "analysis_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing soil: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["./"]
    )