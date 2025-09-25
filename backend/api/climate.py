from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from models import get_db
from models.database_models import Farm, User, ClimateRecord
from services.climate_service import WeatherDataService
from services.uganda_service import uganda_service, UgandanLocation
from .auth import get_current_active_user

router = APIRouter()

# Initialize services
weather_service = WeatherDataService()

@router.get("/weather-for-farms")
async def get_weather_for_farms(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current weather data for all user's farms"""
    # Get user's farms
    farms = db.query(Farm).filter(Farm.owner_id == current_user.id).all()
    
    if not farms:
        return []
    
    weather_data = []
    
    for farm in farms:
        try:
            # Get weather data for farm location
            weather = await weather_service.get_current_weather(
                farm.latitude, 
                farm.longitude
            )
            
            weather_data.append({
                "farm_id": farm.id,
                "location": f"{farm.farm_name}, {farm.district}",
                "temperature": weather.get("temperature", 25),
                "humidity": weather.get("humidity", 60),
                "rainfall": weather.get("rainfall", 0),
                "wind_speed": weather.get("wind_speed", 5),
                "visibility": weather.get("visibility", 10),
                "weather_description": weather.get("description", "Clear sky")
            })
        except Exception as e:
            # Fallback to mock data if API fails
            weather_data.append({
                "farm_id": farm.id,
                "location": f"{farm.farm_name}, {farm.district}",
                "temperature": 26,
                "humidity": 65,
                "rainfall": 2.5,
                "wind_speed": 3.2,
                "visibility": 8.5,
                "weather_description": "Partly cloudy"
            })
    
    return weather_data

@router.get("/alerts")
async def get_climate_alerts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get climate alerts for user's farms"""
    # Get user's farms
    farms = db.query(Farm).filter(Farm.owner_id == current_user.id).all()
    
    if not farms:
        return []
    
    # Mock alert data - in real implementation, this would come from weather monitoring
    alerts = []
    
    # Check recent climate records for potential alerts
    recent_date = datetime.now() - timedelta(days=7)
    recent_records = db.query(ClimateRecord).join(Farm).filter(
        Farm.owner_id == current_user.id,
        ClimateRecord.record_date >= recent_date
    ).all()
    
    # Generate mock alerts based on farm conditions
    for farm in farms[:2]:  # Limit to first 2 farms for demo
        if farm.district in ["Arua", "Gulu", "Moroto"]:  # Drier regions
            alerts.append({
                "id": len(alerts) + 1,
                "alert_type": "Drought Warning",
                "severity": "medium",
                "farm_name": farm.farm_name,
                "message": f"Low rainfall predicted for {farm.district}. Consider drought-resistant varieties.",
                "created_at": (datetime.now() - timedelta(days=2)).isoformat()
            })
        
        if farm.district in ["Kampala", "Jinja", "Mbale"]:  # Wetter regions
            alerts.append({
                "id": len(alerts) + 1,
                "alert_type": "Heavy Rainfall",
                "severity": "low",
                "farm_name": farm.farm_name,
                "message": f"Heavy rains expected in {farm.district}. Ensure proper drainage.",
                "created_at": (datetime.now() - timedelta(days=1)).isoformat()
            })
    
    return alerts

@router.get("/farm/{farm_id}/weather")
async def get_farm_weather(
    farm_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed weather data for a specific farm"""
    # Verify farm ownership
    farm = db.query(Farm).filter(
        Farm.id == farm_id,
        Farm.owner_id == current_user.id
    ).first()
    
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    try:
        # Get current weather
        current_weather = await weather_service.get_current_weather(
            farm.latitude, 
            farm.longitude
        )
        
        # Get historical data (mock for now)
        historical_data = []
        for i in range(7):  # Last 7 days
            date = datetime.now() - timedelta(days=i)
            historical_data.append({
                "date": date.date().isoformat(),
                "temperature_max": 28 + (i % 3),
                "temperature_min": 18 + (i % 2),
                "rainfall": max(0, 5 - i),
                "humidity": 65 + (i % 10)
            })
        
        return {
            "farm_id": farm.id,
            "farm_name": farm.farm_name,
            "location": f"{farm.district}, {farm.sub_county}",
            "current_weather": current_weather,
            "historical_data": historical_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch weather data: {str(e)}"
        )