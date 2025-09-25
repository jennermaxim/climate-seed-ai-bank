import requests
try:
    import numpy as np
    import pandas as pd
    HAS_NUMPY = True
    HAS_PANDAS = True
except ImportError:
    print("Warning: numpy/pandas not available, using fallback for climate calculations")
    HAS_NUMPY = False
    HAS_PANDAS = False

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import os
from dotenv import load_dotenv
from .uganda_service import uganda_service, UgandanLocation

load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class WeatherData:
    """Weather data structure"""
    temperature_min: float
    temperature_max: float
    temperature_avg: float
    rainfall: float
    humidity: float
    wind_speed: float
    solar_radiation: Optional[float] = None
    pressure: Optional[float] = None
    date: datetime = None

@dataclass
class ClimateProjection:
    """Climate projection data structure"""
    year: int
    temperature_change: float
    precipitation_change: float
    extreme_events_probability: Dict[str, float]
    confidence_level: float

class WeatherDataService:
    """Service for retrieving weather data from various sources"""
    
    def __init__(self):
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
        self.nasa_api_key = os.getenv("NASA_POWER_API_KEY")
        self.base_urls = {
            "openweather": "https://api.openweathermap.org/data/2.5",
            "nasa": "https://power.larc.nasa.gov/api/temporal/daily/point",
            "worldbank": "https://climateapi.worldbank.org/climateweb/rest/v1"
        }
        
        # Cache for frequently accessed data
        self._weather_cache = {}
        self._cache_duration = timedelta(hours=1)  # Cache for 1 hour
    
    def get_current_weather(self, latitude: float, longitude: float) -> Optional[WeatherData]:
        """Get current weather data for a location"""
        try:
            if not self.openweather_api_key:
                logger.warning("OpenWeather API key not configured")
                return self._generate_synthetic_weather(latitude, longitude)
            
            url = f"{self.base_urls['openweather']}/weather"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.openweather_api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return WeatherData(
                temperature_min=data["main"]["temp_min"],
                temperature_max=data["main"]["temp_max"],
                temperature_avg=data["main"]["temp"],
                rainfall=data.get("rain", {}).get("1h", 0) or data.get("rain", {}).get("3h", 0) or 0,
                humidity=data["main"]["humidity"],
                wind_speed=data["wind"]["speed"] * 3.6,  # Convert m/s to km/h
                pressure=data["main"]["pressure"],
                date=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return self._generate_synthetic_weather(latitude, longitude)
    
    def get_historical_weather(self, latitude: float, longitude: float, 
                             start_date: datetime, end_date: datetime) -> List[WeatherData]:
        """Get historical weather data for a location and date range"""
        try:
            if not self.nasa_api_key:
                logger.warning("NASA API key not configured, using synthetic data")
                return self._generate_synthetic_historical_weather(latitude, longitude, start_date, end_date)
            
            # NASA POWER API for historical weather data
            url = f"{self.base_urls['nasa']}"
            params = {
                "start": start_date.strftime("%Y%m%d"),
                "end": end_date.strftime("%Y%m%d"),
                "latitude": latitude,
                "longitude": longitude,
                "community": "AG",
                "parameters": "T2M_MIN,T2M_MAX,T2M,PRECTOTCORR,RH2M,WS2M,ALLSKY_SFC_SW_DWN",
                "format": "JSON"
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            weather_data = []
            properties = data["properties"]["parameter"]
            
            for date_str in properties["T2M"]:
                try:
                    date_obj = datetime.strptime(date_str, "%Y%m%d")
                    weather_data.append(WeatherData(
                        temperature_min=properties["T2M_MIN"].get(date_str, 0),
                        temperature_max=properties["T2M_MAX"].get(date_str, 0),
                        temperature_avg=properties["T2M"].get(date_str, 0),
                        rainfall=properties["PRECTOTCORR"].get(date_str, 0),
                        humidity=properties["RH2M"].get(date_str, 50),
                        wind_speed=properties["WS2M"].get(date_str, 0),
                        solar_radiation=properties["ALLSKY_SFC_SW_DWN"].get(date_str, 0),
                        date=date_obj
                    ))
                except Exception as e:
                    logger.error(f"Error parsing weather data for date {date_str}: {e}")
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Error fetching historical weather data: {e}")
            return self._generate_synthetic_historical_weather(latitude, longitude, start_date, end_date)
    
    def get_seasonal_patterns(self, latitude: float, longitude: float, years: int = 5) -> Dict[str, Dict]:
        """Get seasonal weather patterns for a location"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=years * 365)
            
            historical_data = self.get_historical_weather(latitude, longitude, start_date, end_date)
            
            # Group by month and calculate statistics
            monthly_stats = {}
            for month in range(1, 13):
                month_data = [w for w in historical_data if w.date.month == month]
                if month_data:
                    monthly_stats[f"month_{month:02d}"] = {
                        "avg_temp": np.mean([w.temperature_avg for w in month_data]),
                        "avg_rainfall": np.mean([w.rainfall for w in month_data]),
                        "avg_humidity": np.mean([w.humidity for w in month_data]),
                        "temp_variability": np.std([w.temperature_avg for w in month_data]),
                        "rainfall_variability": np.std([w.rainfall for w in month_data])
                    }
            
            # Define seasons for Uganda
            seasons = {
                "dry_season_1": {"months": [12, 1, 2], "name": "First Dry Season"},
                "wet_season_1": {"months": [3, 4, 5], "name": "First Wet Season (Season A)"},
                "dry_season_2": {"months": [6, 7, 8], "name": "Second Dry Season"},
                "wet_season_2": {"months": [9, 10, 11], "name": "Second Wet Season (Season B)"}
            }
            
            seasonal_patterns = {}
            for season_key, season_info in seasons.items():
                season_data = [w for w in historical_data if w.date.month in season_info["months"]]
                if season_data:
                    seasonal_patterns[season_key] = {
                        "name": season_info["name"],
                        "avg_temp": np.mean([w.temperature_avg for w in season_data]),
                        "total_rainfall": np.sum([w.rainfall for w in season_data]),
                        "avg_humidity": np.mean([w.humidity for w in season_data]),
                        "extreme_temps": {
                            "max": max([w.temperature_max for w in season_data]),
                            "min": min([w.temperature_min for w in season_data])
                        }
                    }
            
            return {
                "monthly": monthly_stats,
                "seasonal": seasonal_patterns,
                "annual_summary": {
                    "avg_annual_temp": np.mean([w.temperature_avg for w in historical_data]),
                    "total_annual_rainfall": np.sum([w.rainfall for w in historical_data if w.date.year == end_date.year - 1]),
                    "wettest_month": max(monthly_stats.keys(), key=lambda k: monthly_stats[k]["avg_rainfall"]),
                    "driest_month": min(monthly_stats.keys(), key=lambda k: monthly_stats[k]["avg_rainfall"])
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating seasonal patterns: {e}")
            return {}
    
    def _generate_synthetic_weather(self, latitude: float, longitude: float) -> WeatherData:
        """Generate synthetic weather data based on Uganda's climate patterns"""
        # Base values adjusted for Uganda's climate
        base_temp = 25 + (latitude - 1) * 2  # Temperature varies with latitude
        month = datetime.now().month
        
        # Seasonal adjustments for Uganda
        if month in [12, 1, 2]:  # Dry season 1
            temp_adj = 2
            rainfall = np.random.normal(10, 5)
        elif month in [3, 4, 5]:  # Wet season 1 (Season A)
            temp_adj = -1
            rainfall = np.random.normal(150, 50)
        elif month in [6, 7, 8]:  # Dry season 2
            temp_adj = 1
            rainfall = np.random.normal(50, 20)
        else:  # Wet season 2 (Season B)
            temp_adj = -0.5
            rainfall = np.random.normal(120, 40)
        
        temp_avg = base_temp + temp_adj + np.random.normal(0, 2)
        
        return WeatherData(
            temperature_min=temp_avg - 5 + np.random.normal(0, 1),
            temperature_max=temp_avg + 5 + np.random.normal(0, 1),
            temperature_avg=temp_avg,
            rainfall=max(0, rainfall),
            humidity=np.random.normal(70, 10),
            wind_speed=np.random.normal(10, 3),
            date=datetime.now()
        )
    
    def _generate_synthetic_historical_weather(self, latitude: float, longitude: float, 
                                             start_date: datetime, end_date: datetime) -> List[WeatherData]:
        """Generate synthetic historical weather data"""
        weather_data = []
        current_date = start_date
        
        while current_date <= end_date:
            # Simulate seasonal patterns for Uganda
            month = current_date.month
            base_temp = 25 + (latitude - 1) * 2
            
            if month in [12, 1, 2]:  # Dry season 1
                temp_adj = 2
                rainfall_mean = 10
            elif month in [3, 4, 5]:  # Wet season 1
                temp_adj = -1
                rainfall_mean = 150
            elif month in [6, 7, 8]:  # Dry season 2
                temp_adj = 1
                rainfall_mean = 50
            else:  # Wet season 2
                temp_adj = -0.5
                rainfall_mean = 120
            
            temp_avg = base_temp + temp_adj + np.random.normal(0, 2)
            rainfall = max(0, np.random.normal(rainfall_mean, rainfall_mean * 0.3))
            
            weather_data.append(WeatherData(
                temperature_min=temp_avg - 5 + np.random.normal(0, 1),
                temperature_max=temp_avg + 5 + np.random.normal(0, 1),
                temperature_avg=temp_avg,
                rainfall=rainfall,
                humidity=np.random.normal(70, 10),
                wind_speed=np.random.normal(10, 3),
                date=current_date
            ))
            
            current_date += timedelta(days=1)
        
        return weather_data
    
    # Uganda-specific weather methods
    def get_weather_for_ugandan_location(self, location_name: str) -> Optional[WeatherData]:
        """Get current weather for a named Ugandan location"""
        location = uganda_service.get_location(location_name)
        if not location:
            logger.error(f"Unknown Ugandan location: {location_name}")
            return None
        
        return self.get_current_weather(location.latitude, location.longitude)
    
    def get_regional_weather_uganda(self, region: str) -> Dict[str, WeatherData]:
        """Get weather data for all locations in a Ugandan region"""
        from .uganda_service import UgandaRegion
        
        try:
            region_enum = UgandaRegion(region)
            locations = uganda_service.get_locations_by_region(region_enum)
        except ValueError:
            logger.error(f"Invalid Ugandan region: {region}")
            return {}
        
        weather_data = {}
        for location in locations:
            weather = self.get_current_weather(location.latitude, location.longitude)
            if weather:
                weather_data[location.name] = weather
        
        return weather_data
    
    def get_seasonal_forecast_uganda(self, location_name: str, months_ahead: int = 3) -> List[WeatherData]:
        """Get seasonal weather forecast for Ugandan location using historical patterns"""
        location = uganda_service.get_location(location_name)
        if not location:
            logger.error(f"Unknown Ugandan location: {location_name}")
            return []
        
        # Get historical data for seasonal patterns
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * 3)  # 3 years of data
        
        historical_data = self.get_historical_weather(
            location.latitude, location.longitude, start_date, end_date
        )
        
        if not historical_data:
            return self._generate_synthetic_seasonal_forecast(location, months_ahead)
        
        # Generate forecast based on historical seasonal patterns
        forecast = []
        current_date = datetime.now()
        
        for i in range(months_ahead * 30):  # Daily forecast for specified months
            forecast_date = current_date + timedelta(days=i)
            day_of_year = forecast_date.timetuple().tm_yday
            
            # Find similar days in historical data (±7 days)
            similar_days = [
                data for data in historical_data
                if abs(data.date.timetuple().tm_yday - day_of_year) <= 7
            ]
            
            if similar_days:
                # Average historical data for similar days
                avg_temp_min = sum(d.temperature_min for d in similar_days) / len(similar_days)
                avg_temp_max = sum(d.temperature_max for d in similar_days) / len(similar_days)
                avg_temp = sum(d.temperature_avg for d in similar_days) / len(similar_days)
                avg_rainfall = sum(d.rainfall for d in similar_days) / len(similar_days)
                avg_humidity = sum(d.humidity for d in similar_days) / len(similar_days)
                avg_wind = sum(d.wind_speed for d in similar_days) / len(similar_days)
                
                forecast.append(WeatherData(
                    temperature_min=avg_temp_min,
                    temperature_max=avg_temp_max,
                    temperature_avg=avg_temp,
                    rainfall=avg_rainfall,
                    humidity=avg_humidity,
                    wind_speed=avg_wind,
                    date=forecast_date
                ))
            else:
                # Fallback to location's typical climate
                forecast.append(self._generate_weather_for_ugandan_location(location, forecast_date))
        
        return forecast
    
    def _generate_weather_for_ugandan_location(self, location: UgandanLocation, date: datetime) -> WeatherData:
        """Generate weather data based on Ugandan location characteristics"""
        import random
        import math
        
        # Seasonal adjustment based on Uganda's climate patterns
        day_of_year = date.timetuple().tm_yday
        
        # Uganda has two rainy seasons: March-May and September-December
        wet_season_1 = 60 <= day_of_year <= 150  # March-May
        wet_season_2 = 244 <= day_of_year <= 365  # September-December
        is_wet_season = wet_season_1 or wet_season_2
        
        # Temperature varies with elevation and latitude
        base_temp = 25 - (location.elevation / 300)  # Temperature decreases with elevation
        temp_variation = 5 * math.sin((day_of_year - 81) * math.pi / 182)  # Seasonal variation
        
        temp_avg = base_temp + temp_variation + random.uniform(-2, 2)
        temp_min = temp_avg - 5 + random.uniform(-2, 2)
        temp_max = temp_avg + 7 + random.uniform(-2, 2)
        
        # Rainfall based on seasonal patterns and location
        if is_wet_season:
            rainfall = location.annual_rainfall_avg / 150 + random.uniform(0, 15)
        else:
            rainfall = location.annual_rainfall_avg / 600 + random.uniform(0, 5)
        
        # Humidity is higher during wet seasons
        humidity = (75 if is_wet_season else 60) + random.uniform(-10, 15)
        
        # Wind speed varies by region (Northern regions typically windier)
        base_wind = 8 if location.region.value == "Northern" else 5
        wind_speed = base_wind + random.uniform(-2, 4)
        
        return WeatherData(
            temperature_min=max(10, temp_min),
            temperature_max=min(40, temp_max),
            temperature_avg=temp_avg,
            rainfall=max(0, rainfall),
            humidity=max(30, min(95, humidity)),
            wind_speed=max(0, wind_speed),
            date=date
        )
    
    def _generate_synthetic_seasonal_forecast(self, location: UgandanLocation, months_ahead: int) -> List[WeatherData]:
        """Generate synthetic seasonal forecast for Ugandan location"""
        forecast = []
        current_date = datetime.now()
        
        for i in range(months_ahead * 30):
            forecast_date = current_date + timedelta(days=i)
            forecast.append(self._generate_weather_for_ugandan_location(location, forecast_date))
        
        return forecast

class ClimateProjectionService:
    """Service for climate projections and analysis"""
    
    def __init__(self):
        self.base_url = os.getenv("CLIMATE_API_URL", "https://climateapi.worldbank.org/climateweb/rest/v1")
    
    def get_climate_projections(self, latitude: float, longitude: float, 
                               years_ahead: int = 10) -> List[ClimateProjection]:
        """Get climate projections for a location"""
        try:
            # For now, generate synthetic projections based on IPCC scenarios
            projections = []
            
            for year_offset in range(1, years_ahead + 1):
                projection_year = datetime.now().year + year_offset
                
                # Conservative projection based on IPCC data for East Africa
                temp_change = 0.2 * year_offset + np.random.normal(0, 0.1)  # ~2°C by 2050
                precip_change = -2.0 * year_offset + np.random.normal(0, 5)  # Slight decrease in rainfall
                
                extreme_events = {
                    "drought": min(0.9, 0.05 + 0.02 * year_offset),  # Increasing drought probability
                    "flood": min(0.8, 0.03 + 0.01 * year_offset),   # Slight increase in flood risk
                    "heat_wave": min(0.9, 0.02 + 0.03 * year_offset)  # Increasing heat wave risk
                }
                
                projections.append(ClimateProjection(
                    year=projection_year,
                    temperature_change=temp_change,
                    precipitation_change=precip_change,
                    extreme_events_probability=extreme_events,
                    confidence_level=max(0.6, 0.9 - 0.02 * year_offset)  # Decreasing confidence over time
                ))
            
            return projections
            
        except Exception as e:
            logger.error(f"Error generating climate projections: {e}")
            return []
    
    def calculate_climate_risks(self, weather_patterns: Dict, projections: List[ClimateProjection]) -> Dict[str, float]:
        """Calculate climate risk indices"""
        try:
            risks = {
                "drought_risk": 0.0,
                "flood_risk": 0.0,
                "temperature_stress_risk": 0.0,
                "rainfall_variability_risk": 0.0,
                "overall_risk": 0.0
            }
            
            if not projections:
                return risks
            
            # Calculate drought risk based on precipitation projections
            avg_precip_change = np.mean([p.precipitation_change for p in projections])
            drought_prob = np.mean([p.extreme_events_probability.get("drought", 0) for p in projections])
            risks["drought_risk"] = min(1.0, (abs(avg_precip_change) / 20) * 0.5 + drought_prob * 0.5)
            
            # Calculate flood risk
            flood_prob = np.mean([p.extreme_events_probability.get("flood", 0) for p in projections])
            rainfall_variability = weather_patterns.get("annual_summary", {}).get("rainfall_variability", 0)
            risks["flood_risk"] = min(1.0, flood_prob * 0.7 + (rainfall_variability / 100) * 0.3)
            
            # Calculate temperature stress risk
            avg_temp_change = np.mean([p.temperature_change for p in projections])
            heat_wave_prob = np.mean([p.extreme_events_probability.get("heat_wave", 0) for p in projections])
            risks["temperature_stress_risk"] = min(1.0, (avg_temp_change / 4) * 0.6 + heat_wave_prob * 0.4)
            
            # Calculate rainfall variability risk
            monthly_data = weather_patterns.get("monthly", {})
            if monthly_data:
                variabilities = [data.get("rainfall_variability", 0) for data in monthly_data.values()]
                avg_variability = np.mean(variabilities) if variabilities else 0
                risks["rainfall_variability_risk"] = min(1.0, avg_variability / 50)
            
            # Calculate overall risk as weighted average
            risks["overall_risk"] = (
                risks["drought_risk"] * 0.3 +
                risks["flood_risk"] * 0.2 +
                risks["temperature_stress_risk"] * 0.3 +
                risks["rainfall_variability_risk"] * 0.2
            )
            
            return risks
            
        except Exception as e:
            logger.error(f"Error calculating climate risks: {e}")
            return {
                "drought_risk": 0.5,
                "flood_risk": 0.3,
                "temperature_stress_risk": 0.4,
                "rainfall_variability_risk": 0.3,
                "overall_risk": 0.4
            }
    
    def get_adaptation_recommendations(self, climate_risks: Dict[str, float], 
                                     crop_type: str) -> List[Dict[str, str]]:
        """Get climate adaptation recommendations based on risks"""
        recommendations = []
        
        # Drought adaptation
        if climate_risks.get("drought_risk", 0) > 0.5:
            recommendations.extend([
                {
                    "category": "drought_adaptation",
                    "recommendation": "Invest in drought-tolerant seed varieties",
                    "priority": "high",
                    "implementation": "Select seeds with drought tolerance score > 0.7"
                },
                {
                    "category": "water_management",
                    "recommendation": "Implement water conservation techniques",
                    "priority": "high",
                    "implementation": "Use mulching, rainwater harvesting, and drip irrigation"
                }
            ])
        
        # Flood adaptation
        if climate_risks.get("flood_risk", 0) > 0.4:
            recommendations.extend([
                {
                    "category": "flood_adaptation",
                    "recommendation": "Improve drainage systems",
                    "priority": "medium",
                    "implementation": "Create drainage channels and raise planting beds"
                },
                {
                    "category": "timing",
                    "recommendation": "Adjust planting schedules to avoid peak flood season",
                    "priority": "high",
                    "implementation": "Plant early in the season before heavy rains"
                }
            ])
        
        # Temperature stress adaptation
        if climate_risks.get("temperature_stress_risk", 0) > 0.5:
            recommendations.extend([
                {
                    "category": "temperature_adaptation",
                    "recommendation": "Use heat-tolerant varieties",
                    "priority": "high",
                    "implementation": "Select seeds with heat tolerance score > 0.6"
                },
                {
                    "category": "microclimate",
                    "recommendation": "Create shade and windbreaks",
                    "priority": "medium",
                    "implementation": "Plant trees or use shade nets during extreme heat"
                }
            ])
        
        # General recommendations
        if climate_risks.get("overall_risk", 0) > 0.4:
            recommendations.extend([
                {
                    "category": "diversification",
                    "recommendation": "Diversify crop varieties and planting times",
                    "priority": "high",
                    "implementation": "Plant multiple varieties with different maturity periods"
                },
                {
                    "category": "monitoring",
                    "recommendation": "Implement weather monitoring systems",
                    "priority": "medium",
                    "implementation": "Use weather forecasts and early warning systems"
                }
            ])
        
        return recommendations

# Create service instances
weather_service = WeatherDataService()
climate_projection_service = ClimateProjectionService()

# Create a unified climate service for backward compatibility
class ClimateService:
    """Unified climate service combining weather and projection services"""
    def __init__(self):
        self.weather_service = weather_service
        self.projection_service = climate_projection_service
    
    async def get_weather_for_ugandan_location(self, location_name: str):
        """Get weather for a Ugandan location (async wrapper)"""
        return self.weather_service.get_weather_for_ugandan_location(location_name)
    
    async def get_regional_weather_uganda(self, region: str):
        """Get regional weather for Uganda (async wrapper)"""
        return self.weather_service.get_regional_weather_uganda(region)

climate_service = ClimateService()