from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums for consistent data types
class UserType(str, Enum):
    FARMER = "farmer"
    ADMIN = "admin"
    POLICYMAKER = "policy_maker"

class CropType(str, Enum):
    MAIZE = "maize"
    BEANS = "beans"
    CASSAVA = "cassava"
    SWEET_POTATO = "sweet_potato"
    GROUNDNUTS = "groundnuts"
    RICE = "rice"
    SORGHUM = "sorghum"
    MILLET = "millet"
    BANANA = "banana"
    COFFEE = "coffee"

class Season(str, Enum):
    SEASON_A = "A"  # March-June
    SEASON_B = "B"  # September-December
    PERENNIAL = "perennial"

class SoilTexture(str, Enum):
    CLAY = "clay"
    SANDY = "sandy"
    LOAMY = "loamy"
    SILTY = "silty"
    CLAYEY_LOAM = "clayey_loam"
    SANDY_LOAM = "sandy_loam"

class DrainageLevel(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

class RequirementLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# Pydantic Models for API

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    full_name: str = Field(..., min_length=2, max_length=100)
    phone_number: Optional[str] = Field(None, pattern=r'^\+256[0-9]{9}$')
    user_type: UserType = UserType.FARMER
    location: Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class FarmBase(BaseModel):
    farm_name: str = Field(..., min_length=2, max_length=100)
    latitude: float = Field(..., ge=-1.5, le=4.0)  # Uganda's latitude range
    longitude: float = Field(..., ge=29.5, le=35.0)  # Uganda's longitude range
    elevation: Optional[float] = Field(None, ge=500, le=5000)  # meters above sea level
    district: str = Field(..., max_length=50)
    sub_county: Optional[str] = Field(None, max_length=50)
    village: Optional[str] = Field(None, max_length=50)
    total_area: float = Field(..., gt=0, le=10000)  # hectares
    cultivated_area: float = Field(..., gt=0)
    irrigation_available: bool = False
    irrigation_type: Optional[str] = Field(None, max_length=50)
    storage_capacity: Optional[float] = Field(None, ge=0)  # tons
    market_distance: Optional[float] = Field(None, ge=0, le=500)  # km
    road_access: Optional[str] = Field(None, pattern=r'^(good|fair|poor)$')

    @validator('cultivated_area')
    def validate_cultivated_area(cls, v, values):
        if 'total_area' in values and v > values['total_area']:
            raise ValueError('Cultivated area cannot exceed total area')
        return v

class FarmCreate(FarmBase):
    pass

class FarmResponse(FarmBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SoilProfileBase(BaseModel):
    ph_level: Optional[float] = Field(None, ge=3.0, le=10.0)
    organic_matter: Optional[float] = Field(None, ge=0, le=100)  # percentage
    nitrogen: Optional[float] = Field(None, ge=0)  # ppm
    phosphorus: Optional[float] = Field(None, ge=0)  # ppm
    potassium: Optional[float] = Field(None, ge=0)  # ppm
    soil_texture: Optional[SoilTexture] = None
    drainage: Optional[DrainageLevel] = None
    depth: Optional[float] = Field(None, gt=0, le=300)  # cm
    salinity: Optional[float] = Field(None, ge=0)  # dS/m
    test_date: datetime
    testing_method: Optional[str] = Field(None, max_length=100)
    lab_name: Optional[str] = Field(None, max_length=100)

class SoilProfileCreate(SoilProfileBase):
    farm_id: int

class SoilProfileResponse(SoilProfileBase):
    id: int
    farm_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SeedBase(BaseModel):
    variety_name: str = Field(..., min_length=2, max_length=100)
    scientific_name: str = Field(..., min_length=5, max_length=100)
    crop_type: CropType
    seed_company: Optional[str] = Field(None, max_length=100)
    release_year: Optional[int] = Field(None, ge=1900, le=2030)
    maturity_days: int = Field(..., gt=0, le=400)
    yield_potential: Optional[float] = Field(None, gt=0, le=50)  # tons per hectare
    plant_height: Optional[float] = Field(None, gt=0, le=1000)  # cm
    seed_size: Optional[str] = Field(None, pattern=r'^(small|medium|large)$')
    
    # Climate tolerance (0-1 scale)
    drought_tolerance: float = Field(..., ge=0, le=1)
    flood_tolerance: float = Field(..., ge=0, le=1)
    heat_tolerance: float = Field(..., ge=0, le=1)
    cold_tolerance: float = Field(..., ge=0, le=1)
    
    # Soil requirements
    preferred_ph_min: Optional[float] = Field(None, ge=3.0, le=10.0)
    preferred_ph_max: Optional[float] = Field(None, ge=3.0, le=10.0)
    nitrogen_requirement: RequirementLevel = RequirementLevel.MEDIUM
    phosphorus_requirement: RequirementLevel = RequirementLevel.MEDIUM
    potassium_requirement: RequirementLevel = RequirementLevel.MEDIUM
    
    # Environmental conditions
    min_rainfall: Optional[float] = Field(None, ge=0, le=3000)  # mm per season
    max_rainfall: Optional[float] = Field(None, ge=0, le=5000)
    optimal_temp_min: Optional[float] = Field(None, ge=-5, le=45)  # Celsius
    optimal_temp_max: Optional[float] = Field(None, ge=-5, le=50)
    altitude_min: Optional[float] = Field(None, ge=0, le=6000)  # meters
    altitude_max: Optional[float] = Field(None, ge=0, le=6000)
    
    # Nutritional content
    protein_content: Optional[float] = Field(None, ge=0, le=50)  # percentage
    carbohydrate_content: Optional[float] = Field(None, ge=0, le=100)
    fat_content: Optional[float] = Field(None, ge=0, le=50)
    
    is_certified: bool = False
    is_available: bool = True

    @validator('preferred_ph_max')
    def validate_ph_range(cls, v, values):
        if 'preferred_ph_min' in values and values['preferred_ph_min'] is not None and v is not None:
            if v < values['preferred_ph_min']:
                raise ValueError('pH max cannot be less than pH min')
        return v

    @validator('max_rainfall')
    def validate_rainfall_range(cls, v, values):
        if 'min_rainfall' in values and values['min_rainfall'] is not None and v is not None:
            if v < values['min_rainfall']:
                raise ValueError('Max rainfall cannot be less than min rainfall')
        return v

    @validator('optimal_temp_max')
    def validate_temp_range(cls, v, values):
        if 'optimal_temp_min' in values and values['optimal_temp_min'] is not None and v is not None:
            if v < values['optimal_temp_min']:
                raise ValueError('Max temperature cannot be less than min temperature')
        return v

class SeedCreate(SeedBase):
    genetic_markers: Optional[Dict[str, Any]] = None
    parent_varieties: Optional[List[str]] = None
    breeding_method: Optional[str] = None
    disease_resistance: Optional[Dict[str, float]] = None
    pest_resistance: Optional[Dict[str, float]] = None
    vitamin_content: Optional[Dict[str, float]] = None
    mineral_content: Optional[Dict[str, float]] = None
    market_price_range: Optional[Dict[str, float]] = None
    market_demand: Optional[str] = None
    shelf_life: Optional[int] = Field(None, ge=0, le=365)  # days
    processing_suitability: Optional[List[str]] = None

class SeedResponse(SeedBase):
    id: int
    genetic_markers: Optional[Dict[str, Any]] = None
    parent_varieties: Optional[List[str]] = None
    breeding_method: Optional[str] = None
    disease_resistance: Optional[Dict[str, float]] = None
    pest_resistance: Optional[Dict[str, float]] = None
    vitamin_content: Optional[Dict[str, float]] = None
    mineral_content: Optional[Dict[str, float]] = None
    market_price_range: Optional[Dict[str, float]] = None
    market_demand: Optional[str] = None
    shelf_life: Optional[int] = None
    processing_suitability: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ClimateRecordBase(BaseModel):
    record_date: datetime
    data_source: str = Field(..., max_length=50)
    temp_min: Optional[float] = Field(None, ge=-10, le=50)  # Celsius
    temp_max: Optional[float] = Field(None, ge=-10, le=50)
    temp_avg: Optional[float] = Field(None, ge=-10, le=50)
    rainfall: Optional[float] = Field(None, ge=0, le=500)  # mm
    humidity: Optional[float] = Field(None, ge=0, le=100)  # percentage
    wind_speed: Optional[float] = Field(None, ge=0, le=200)  # km/h
    solar_radiation: Optional[float] = Field(None, ge=0, le=50)  # MJ/m²
    evapotranspiration: Optional[float] = Field(None, ge=0, le=20)  # mm
    drought_index: Optional[float] = Field(None, ge=0, le=10)
    flood_risk: Optional[float] = Field(None, ge=0, le=1)
    frost_occurrence: bool = False

class ClimateRecordCreate(ClimateRecordBase):
    farm_id: Optional[int] = None

class ClimateRecordResponse(ClimateRecordBase):
    id: int
    farm_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CropCycleBase(BaseModel):
    seed_id: int
    season: Season
    year: int = Field(..., ge=2000, le=2030)
    planting_date: Optional[datetime] = None
    harvest_date: Optional[datetime] = None
    area_planted: float = Field(..., gt=0)  # hectares
    yield_achieved: Optional[float] = Field(None, ge=0)  # tons per hectare
    total_production: Optional[float] = Field(None, ge=0)  # tons
    seeds_used: Optional[float] = Field(None, ge=0)  # kg
    labor_hours: Optional[float] = Field(None, ge=0)
    total_cost: Optional[float] = Field(None, ge=0)  # UGX
    total_revenue: Optional[float] = Field(None, ge=0)  # UGX
    germination_rate: Optional[float] = Field(None, ge=0, le=100)  # percentage
    survival_rate: Optional[float] = Field(None, ge=0, le=100)  # percentage
    irrigation_used: Optional[float] = Field(None, ge=0)  # mm equivalent
    grain_quality: Optional[str] = Field(None, pattern=r'^(excellent|good|fair|poor)$')
    market_grade: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=1000)

class CropCycleCreate(CropCycleBase):
    farm_id: int
    fertilizer_used: Optional[Dict[str, float]] = None
    pesticide_used: Optional[Dict[str, float]] = None
    disease_incidence: Optional[Dict[str, float]] = None
    pest_incidence: Optional[Dict[str, float]] = None
    weather_events: Optional[List[str]] = None

class CropCycleResponse(CropCycleBase):
    id: int
    farm_id: int
    profit: Optional[float] = None  # calculated field
    fertilizer_used: Optional[Dict[str, float]] = None
    pesticide_used: Optional[Dict[str, float]] = None
    disease_incidence: Optional[Dict[str, float]] = None
    pest_incidence: Optional[Dict[str, float]] = None
    weather_events: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RecommendationRequest(BaseModel):
    farm_id: int
    season: Season
    year: int = Field(..., ge=2024, le=2035)
    preferred_crops: Optional[List[CropType]] = None
    budget_constraint: Optional[float] = Field(None, gt=0)  # UGX
    risk_tolerance: Optional[float] = Field(0.5, ge=0, le=1)  # 0 = risk averse, 1 = risk tolerant
    market_preference: Optional[str] = Field(None, pattern=r'^(local|regional|export)$')
    include_experimental: bool = False

class SeedRecommendationResponse(BaseModel):
    id: int
    seed_id: int
    seed_name: str
    crop_type: str
    suitability_score: float
    climate_match_score: float
    soil_match_score: float
    market_potential_score: float
    risk_score: float
    confidence_level: float
    expected_yield: Optional[float] = None
    expected_profit: Optional[float] = None
    reasoning: Dict[str, Any]
    risk_factors: List[str]
    planting_window: Dict[str, str]
    seed_rate: Optional[float] = None
    fertilizer_recommendation: Optional[Dict[str, Any]] = None
    irrigation_schedule: Optional[Dict[str, Any]] = None
    pest_management: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class ClimateProjectionResponse(BaseModel):
    latitude: float
    longitude: float
    district: str
    projection_year: int
    scenario: str
    temp_increase: Optional[float] = None
    temp_min_avg: Optional[float] = None
    temp_max_avg: Optional[float] = None
    rainfall_change: Optional[float] = None
    rainfall_variability: Optional[float] = None
    drought_probability: Optional[float] = None
    flood_probability: Optional[float] = None
    heat_wave_frequency: Optional[float] = None
    season_shift: Optional[Dict[str, Any]] = None
    season_length: Optional[Dict[str, Any]] = None
    climate_model: str
    confidence_level: float

    class Config:
        from_attributes = True

class MarketDataResponse(BaseModel):
    seed_id: int
    variety_name: str
    crop_type: str
    market_location: str
    district: str
    price_per_kg: float
    price_trend: Optional[str] = None
    demand_level: Optional[str] = None
    supply_level: Optional[str] = None
    quality_grade: Optional[str] = None
    seasonal_variation: Optional[Dict[str, float]] = None
    buyer_preference: Optional[float] = None
    export_potential: bool
    price_date: datetime

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_farmers: int
    total_farms: int
    total_recommendations: int
    active_crop_cycles: int
    avg_yield_improvement: Optional[float] = None
    climate_alerts: int = 0
    top_performing_seeds: List[Dict[str, Any]] = []
    regional_statistics: Dict[str, Any]
    recent_alerts: List[Dict[str, Any]] = []
    regional_performance: List[Dict[str, Any]] = []

class AdaptationGuidance(BaseModel):
    farm_id: int
    season: Season
    year: int
    climate_alerts: List[Dict[str, Any]]
    irrigation_recommendations: List[Dict[str, Any]]
    planting_schedule: Dict[str, Any]
    pest_disease_forecast: List[Dict[str, Any]]
    market_timing: Dict[str, Any]
    emergency_measures: List[str]
    confidence_level: float

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None