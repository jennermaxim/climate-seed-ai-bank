from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, List, Dict, Any

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    phone_number = Column(String)
    password_hash = Column(String, nullable=False)
    user_type = Column(String, default="farmer")  # farmer, admin, policy_maker
    location = Column(String)  # District/Region in Uganda
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    farms = relationship("Farm", back_populates="owner")

class Farm(Base):
    __tablename__ = "farms"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    farm_name = Column(String, nullable=False)
    
    # Geographic Information
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Float)
    district = Column(String, nullable=False)
    sub_county = Column(String)
    village = Column(String)
    
    # Farm Characteristics
    total_area = Column(Float, nullable=False)  # in hectares
    cultivated_area = Column(Float, nullable=False)
    irrigation_available = Column(Boolean, default=False)
    irrigation_type = Column(String)  # drip, sprinkler, flood, etc.
    
    # Infrastructure
    storage_capacity = Column(Float)  # in tons
    market_distance = Column(Float)  # km to nearest market
    road_access = Column(String)  # good, fair, poor
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="farms")
    soil_profiles = relationship("SoilProfile", back_populates="farm")
    climate_records = relationship("ClimateRecord", back_populates="farm")
    crop_cycles = relationship("CropCycle", back_populates="farm")

class SoilProfile(Base):
    __tablename__ = "soil_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    
    # Soil Composition
    ph_level = Column(Float)
    organic_matter = Column(Float)  # percentage
    nitrogen = Column(Float)  # ppm
    phosphorus = Column(Float)  # ppm
    potassium = Column(Float)  # ppm
    
    # Physical Properties
    soil_texture = Column(String)  # clay, sandy, loamy, etc.
    drainage = Column(String)  # excellent, good, fair, poor
    depth = Column(Float)  # in cm
    salinity = Column(Float)  # dS/m
    
    # Test Information
    test_date = Column(DateTime, nullable=False)
    testing_method = Column(String)
    lab_name = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    farm = relationship("Farm", back_populates="soil_profiles")

class Seed(Base):
    __tablename__ = "seeds"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    variety_name = Column(String, nullable=False, unique=True)
    scientific_name = Column(String, nullable=False)
    crop_type = Column(String, nullable=False)  # maize, beans, cassava, etc.
    seed_company = Column(String)
    release_year = Column(Integer)
    
    # Genetic Profile
    genetic_markers = Column(JSON)  # DNA markers for traits
    parent_varieties = Column(JSON)  # List of parent varieties
    breeding_method = Column(String)  # hybrid, open-pollinated, etc.
    
    # Growth Characteristics
    maturity_days = Column(Integer, nullable=False)
    yield_potential = Column(Float)  # tons per hectare
    plant_height = Column(Float)  # in cm
    seed_size = Column(String)  # small, medium, large
    
    # Climate Adaptation
    drought_tolerance = Column(Float)  # 0-1 scale
    flood_tolerance = Column(Float)  # 0-1 scale
    heat_tolerance = Column(Float)  # 0-1 scale
    cold_tolerance = Column(Float)  # 0-1 scale
    
    # Disease & Pest Resistance
    disease_resistance = Column(JSON)  # {disease_name: resistance_level}
    pest_resistance = Column(JSON)  # {pest_name: resistance_level}
    
    # Soil Requirements
    preferred_ph_min = Column(Float)
    preferred_ph_max = Column(Float)
    nitrogen_requirement = Column(String)  # low, medium, high
    phosphorus_requirement = Column(String)
    potassium_requirement = Column(String)
    
    # Environmental Conditions
    min_rainfall = Column(Float)  # mm per season
    max_rainfall = Column(Float)
    optimal_temp_min = Column(Float)  # Celsius
    optimal_temp_max = Column(Float)
    altitude_min = Column(Float)  # meters
    altitude_max = Column(Float)
    
    # Nutritional Value
    protein_content = Column(Float)  # percentage
    carbohydrate_content = Column(Float)
    fat_content = Column(Float)
    vitamin_content = Column(JSON)
    mineral_content = Column(JSON)
    
    # Market Information
    market_price_range = Column(JSON)  # {min: price, max: price}
    market_demand = Column(String)  # high, medium, low
    shelf_life = Column(Integer)  # days
    processing_suitability = Column(JSON)  # list of processing methods
    
    is_certified = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ClimateRecord(Base):
    __tablename__ = "climate_records"
    
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    
    # Date and Source
    record_date = Column(DateTime, nullable=False)
    data_source = Column(String, nullable=False)  # satellite, weather_station, manual
    
    # Temperature Data
    temp_min = Column(Float)  # Celsius
    temp_max = Column(Float)
    temp_avg = Column(Float)
    
    # Precipitation
    rainfall = Column(Float)  # mm
    humidity = Column(Float)  # percentage
    
    # Other Weather Parameters
    wind_speed = Column(Float)  # km/h
    solar_radiation = Column(Float)  # MJ/m²
    evapotranspiration = Column(Float)  # mm
    
    # Extreme Events
    drought_index = Column(Float)
    flood_risk = Column(Float)
    frost_occurrence = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    farm = relationship("Farm", back_populates="climate_records")

class CropCycle(Base):
    __tablename__ = "crop_cycles"
    
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    seed_id = Column(Integer, ForeignKey("seeds.id"), nullable=False)
    
    # Cycle Information
    season = Column(String, nullable=False)  # A, B, or year for perennials
    year = Column(Integer, nullable=False)
    planting_date = Column(DateTime)
    harvest_date = Column(DateTime)
    
    # Area and Production
    area_planted = Column(Float, nullable=False)  # hectares
    yield_achieved = Column(Float)  # tons per hectare
    total_production = Column(Float)  # tons
    
    # Inputs Used
    fertilizer_used = Column(JSON)  # {type: amount_kg}
    pesticide_used = Column(JSON)  # {type: amount_liters}
    seeds_used = Column(Float)  # kg
    labor_hours = Column(Float)
    
    # Costs and Revenue
    total_cost = Column(Float)  # UGX
    total_revenue = Column(Float)  # UGX
    profit = Column(Float)  # UGX
    
    # Performance Metrics
    germination_rate = Column(Float)  # percentage
    survival_rate = Column(Float)  # percentage
    disease_incidence = Column(JSON)  # {disease: severity}
    pest_incidence = Column(JSON)  # {pest: severity}
    
    # Weather Impact
    weather_events = Column(JSON)  # list of weather events during cycle
    irrigation_used = Column(Float)  # mm equivalent
    
    # Quality Metrics
    grain_quality = Column(String)  # excellent, good, fair, poor
    market_grade = Column(String)
    
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    farm = relationship("Farm", back_populates="crop_cycles")
    seed = relationship("Seed")

class SeedRecommendation(Base):
    __tablename__ = "seed_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    seed_id = Column(Integer, ForeignKey("seeds.id"), nullable=False)
    
    # Recommendation Metadata
    recommendation_date = Column(DateTime, default=datetime.utcnow)
    season = Column(String, nullable=False)  # which season this is for
    year = Column(Integer, nullable=False)
    
    # Scoring
    suitability_score = Column(Float, nullable=False)  # 0-1 scale
    climate_match_score = Column(Float)
    soil_match_score = Column(Float)
    market_potential_score = Column(Float)
    risk_score = Column(Float)  # lower is better
    
    # Confidence and Reasoning
    confidence_level = Column(Float)  # 0-1 scale
    reasoning = Column(JSON)  # detailed reasoning for recommendation
    
    # Expected Outcomes
    expected_yield = Column(Float)  # tons per hectare
    expected_profit = Column(Float)  # UGX per hectare
    risk_factors = Column(JSON)  # list of identified risks
    
    # Implementation Guidance
    planting_window = Column(JSON)  # {start: date, end: date}
    seed_rate = Column(Float)  # kg per hectare
    fertilizer_recommendation = Column(JSON)
    irrigation_schedule = Column(JSON)
    pest_management = Column(JSON)
    
    # Status
    is_active = Column(Boolean, default=True)
    farmer_feedback = Column(String)  # accepted, rejected, implemented
    implementation_notes = Column(Text)
    
    # Relationships
    farm = relationship("Farm")
    seed = relationship("Seed")

class ClimateProjection(Base):
    __tablename__ = "climate_projections"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Location and Time
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    district = Column(String, nullable=False)
    projection_year = Column(Integer, nullable=False)
    scenario = Column(String, nullable=False)  # RCP2.6, RCP4.5, RCP8.5
    
    # Temperature Projections
    temp_increase = Column(Float)  # degrees Celsius above current
    temp_min_avg = Column(Float)
    temp_max_avg = Column(Float)
    
    # Precipitation Projections
    rainfall_change = Column(Float)  # percentage change
    rainfall_variability = Column(Float)  # coefficient of variation
    dry_spell_frequency = Column(Float)  # events per year
    
    # Extreme Events
    drought_probability = Column(Float)  # 0-1 scale
    flood_probability = Column(Float)
    heat_wave_frequency = Column(Float)  # events per year
    
    # Seasonality Changes
    season_shift = Column(JSON)  # changes in season timing
    season_length = Column(JSON)  # changes in season duration
    
    # Model Information
    climate_model = Column(String, nullable=False)
    data_source = Column(String, nullable=False)
    confidence_level = Column(Float)  # 0-1 scale
    
    created_at = Column(DateTime, default=datetime.utcnow)

class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    seed_id = Column(Integer, ForeignKey("seeds.id"), nullable=False)
    
    # Market Information
    market_location = Column(String, nullable=False)
    district = Column(String, nullable=False)
    price_date = Column(DateTime, nullable=False)
    
    # Pricing
    price_per_kg = Column(Float, nullable=False)  # UGX
    price_trend = Column(String)  # increasing, stable, decreasing
    demand_level = Column(String)  # high, medium, low
    supply_level = Column(String)  # surplus, adequate, shortage
    
    # Quality Specifications
    quality_grade = Column(String)
    moisture_content = Column(Float)  # percentage
    purity_level = Column(Float)  # percentage
    
    # Market Dynamics
    seasonal_variation = Column(JSON)  # price variation by month
    buyer_preference = Column(Float)  # 0-1 scale
    export_potential = Column(Boolean, default=False)
    processing_demand = Column(Float)  # percentage going to processing
    
    data_source = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    seed = relationship("Seed")