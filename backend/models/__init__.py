from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .database_models import Base
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./climate_seed_bank.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    """Database session dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database with sample data
def init_sample_data():
    """Initialize database with sample seed varieties for Uganda"""
    from .database_models import Seed
    
    db = SessionLocal()
    try:
        # Check if we already have seeds
        if db.query(Seed).first():
            return
        
        # Sample seed varieties common in Uganda
        sample_seeds = [
            {
                "variety_name": "Longe 10H",
                "scientific_name": "Zea mays L.",
                "crop_type": "maize",
                "seed_company": "NARO",
                "release_year": 2015,
                "maturity_days": 120,
                "yield_potential": 6.5,
                "plant_height": 250,
                "seed_size": "medium",
                "drought_tolerance": 0.7,
                "flood_tolerance": 0.4,
                "heat_tolerance": 0.6,
                "cold_tolerance": 0.5,
                "preferred_ph_min": 5.8,
                "preferred_ph_max": 7.0,
                "nitrogen_requirement": "medium",
                "phosphorus_requirement": "medium",
                "potassium_requirement": "medium",
                "min_rainfall": 500,
                "max_rainfall": 1200,
                "optimal_temp_min": 18,
                "optimal_temp_max": 30,
                "altitude_min": 1000,
                "altitude_max": 2100,
                "protein_content": 9.5,
                "carbohydrate_content": 73.0,
                "fat_content": 4.5,
                "is_certified": True,
                "is_available": True
            },
            {
                "variety_name": "NAROBEAN 1",
                "scientific_name": "Phaseolus vulgaris L.",
                "crop_type": "beans",
                "seed_company": "NARO",
                "release_year": 2010,
                "maturity_days": 90,
                "yield_potential": 2.5,
                "plant_height": 40,
                "seed_size": "medium",
                "drought_tolerance": 0.6,
                "flood_tolerance": 0.3,
                "heat_tolerance": 0.5,
                "cold_tolerance": 0.7,
                "preferred_ph_min": 6.0,
                "preferred_ph_max": 7.5,
                "nitrogen_requirement": "low",
                "phosphorus_requirement": "high",
                "potassium_requirement": "medium",
                "min_rainfall": 400,
                "max_rainfall": 800,
                "optimal_temp_min": 16,
                "optimal_temp_max": 28,
                "altitude_min": 1200,
                "altitude_max": 2500,
                "protein_content": 22.0,
                "carbohydrate_content": 60.0,
                "fat_content": 1.5,
                "is_certified": True,
                "is_available": True
            },
            {
                "variety_name": "NAROCASS 1",
                "scientific_name": "Manihot esculenta Crantz",
                "crop_type": "cassava",
                "seed_company": "NARO",
                "release_year": 2011,
                "maturity_days": 365,
                "yield_potential": 25.0,
                "plant_height": 200,
                "seed_size": "large",
                "drought_tolerance": 0.9,
                "flood_tolerance": 0.3,
                "heat_tolerance": 0.8,
                "cold_tolerance": 0.4,
                "preferred_ph_min": 4.5,
                "preferred_ph_max": 7.0,
                "nitrogen_requirement": "low",
                "phosphorus_requirement": "medium",
                "potassium_requirement": "high",
                "min_rainfall": 600,
                "max_rainfall": 1500,
                "optimal_temp_min": 20,
                "optimal_temp_max": 35,
                "altitude_min": 500,
                "altitude_max": 1800,
                "protein_content": 1.4,
                "carbohydrate_content": 38.0,
                "fat_content": 0.3,
                "is_certified": True,
                "is_available": True
            },
            {
                "variety_name": "Ejumula",
                "scientific_name": "Ipomoea batatas L.",
                "crop_type": "sweet_potato",
                "seed_company": "CIP",
                "release_year": 2007,
                "maturity_days": 120,
                "yield_potential": 20.0,
                "plant_height": 30,
                "seed_size": "medium",
                "drought_tolerance": 0.7,
                "flood_tolerance": 0.4,
                "heat_tolerance": 0.7,
                "cold_tolerance": 0.5,
                "preferred_ph_min": 5.5,
                "preferred_ph_max": 7.0,
                "nitrogen_requirement": "medium",
                "phosphorus_requirement": "medium",
                "potassium_requirement": "high",
                "min_rainfall": 500,
                "max_rainfall": 1000,
                "optimal_temp_min": 18,
                "optimal_temp_max": 30,
                "altitude_min": 500,
                "altitude_max": 2300,
                "protein_content": 1.6,
                "carbohydrate_content": 20.0,
                "fat_content": 0.1,
                "is_certified": True,
                "is_available": True
            },
            {
                "variety_name": "Serenut 5R",
                "scientific_name": "Arachis hypogaea L.",
                "crop_type": "groundnuts",
                "seed_company": "NaSARRI",
                "release_year": 2016,
                "maturity_days": 105,
                "yield_potential": 3.0,
                "plant_height": 45,
                "seed_size": "medium",
                "drought_tolerance": 0.8,
                "flood_tolerance": 0.2,
                "heat_tolerance": 0.7,
                "cold_tolerance": 0.4,
                "preferred_ph_min": 6.0,
                "preferred_ph_max": 7.5,
                "nitrogen_requirement": "low",
                "phosphorus_requirement": "high",
                "potassium_requirement": "medium",
                "min_rainfall": 500,
                "max_rainfall": 1000,
                "optimal_temp_min": 20,
                "optimal_temp_max": 30,
                "altitude_min": 500,
                "altitude_max": 1500,
                "protein_content": 25.0,
                "carbohydrate_content": 16.0,
                "fat_content": 49.0,
                "is_certified": True,
                "is_available": True
            }
        ]
        
        for seed_data in sample_seeds:
            seed = Seed(**seed_data)
            db.add(seed)
        
        db.commit()
        print("Sample seed data initialized successfully")
        
    except Exception as e:
        print(f"Error initializing sample data: {e}")
        db.rollback()
    finally:
        db.close()