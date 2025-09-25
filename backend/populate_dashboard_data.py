"""
Script to populate missing dashboard data for better user experience
Creates seed recommendations, crop cycles, and other data needed for meaningful dashboards
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import SessionLocal
from models.database_models import User, Farm, Seed, SeedRecommendation, CropCycle, ClimateRecord
from services.uganda_service import uganda_service

def create_seed_recommendations():
    """Create seed recommendations for all farms"""
    db = SessionLocal()
    try:
        print("Creating seed recommendations...")
        
        # Clear existing recommendations
        db.query(SeedRecommendation).delete()
        
        farms = db.query(Farm).all()
        seeds = db.query(Seed).all()
        
        recommendations = []
        
        for farm in farms:
            # Get location info for this farm
            location = uganda_service.find_nearest_location(farm.latitude, farm.longitude)
            
            # Recommend 3-5 seeds per farm based on location characteristics
            suitable_seeds = []
            for seed in seeds:
                # Match crop types to location's main crops
                if seed.crop_type in location.main_crops[:3]:  # Top 3 crops for location
                    suitable_seeds.append(seed)
            
            # If no perfect matches, use any seeds
            if not suitable_seeds:
                suitable_seeds = seeds[:5]
            
            # Create recommendations
            for i, seed in enumerate(suitable_seeds[:4]):  # Max 4 per farm
                suitability_score = 0.9 - (i * 0.1)  # Descending suitability
                confidence_level = 0.8 + (random.random() * 0.2)  # 0.8 to 1.0
                reasoning = {
                    "climate_match": f"Suitable for {location.climate_zone.value} climate zone",
                    "regional_fit": f"Recommended for {location.region.value} region",
                    "crop_history": f"Good performance with {seed.crop_type} in this area"
                }
                
                recommendation = SeedRecommendation(
                    farm_id=farm.id,
                    seed_id=seed.id,
                    season="Season A" if i % 2 == 0 else "Season B",
                    year=2025,
                    suitability_score=suitability_score,
                    climate_match_score=random.uniform(0.7, 0.95),
                    soil_match_score=random.uniform(0.6, 0.9),
                    market_potential_score=random.uniform(0.5, 0.85),
                    risk_score=random.uniform(0.1, 0.4),
                    confidence_level=confidence_level,
                    reasoning=reasoning,
                    expected_yield=seed.yield_potential * random.uniform(0.8, 1.0),
                    expected_profit=random.uniform(500000, 1500000),  # UGX per hectare
                    risk_factors=["drought", "pests"] if suitability_score < 0.8 else ["market_fluctuation"],
                    planting_window={"start": "2025-03-01", "end": "2025-04-15"} if i % 2 == 0 else {"start": "2025-09-01", "end": "2025-10-15"},
                    seed_rate=random.uniform(15, 30),  # kg per hectare
                    is_active=True,
                    recommendation_date=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                recommendations.append(recommendation)
        
        db.add_all(recommendations)
        db.commit()
        print(f"✅ Created {len(recommendations)} seed recommendations")
        return recommendations
        
    except Exception as e:
        print(f"❌ Error creating recommendations: {e}")
        db.rollback()
        return []
    finally:
        db.close()

def create_crop_cycles():
    """Create sample crop cycles for farms"""
    db = SessionLocal()
    try:
        print("Creating crop cycles...")
        
        # Clear existing cycles
        db.query(CropCycle).delete()
        
        farms = db.query(Farm).all()
        seeds = db.query(Seed).all()
        
        cycles = []
        
        for farm in farms:
            # Create 2-3 crop cycles per farm (different seasons/years)
            num_cycles = random.randint(2, 4)
            
            for i in range(num_cycles):
                seed = random.choice(seeds)
                
                # Randomize seasons and years
                season = "Season A" if i % 2 == 0 else "Season B"
                year = 2024 if i < 2 else 2023
                
                # Calculate dates
                planting_date = datetime(year, 3 if season == "Season A" else 9, random.randint(1, 28))
                harvest_date = planting_date + timedelta(days=seed.maturity_days + random.randint(-10, 10))
                
                # Generate realistic yield data
                base_yield = seed.yield_potential
                actual_yield = base_yield * random.uniform(0.6, 1.2)  # Some variation
                area = random.uniform(0.5, 3.0)  # 0.5 to 3 hectares
                total_production = actual_yield * area
                
                cycle = CropCycle(
                    farm_id=farm.id,
                    seed_id=seed.id,
                    season=season,
                    year=year,
                    planting_date=planting_date,
                    harvest_date=harvest_date if harvest_date < datetime.now() else None,
                    area_planted=area,
                    yield_achieved=actual_yield if harvest_date < datetime.now() else None,
                    total_production=total_production if harvest_date < datetime.now() else None,
                    total_cost=random.uniform(200000, 800000),  # UGX
                    total_revenue=random.uniform(300000, 1200000) if harvest_date < datetime.now() else None,
                    germination_rate=random.uniform(75, 95),
                    survival_rate=random.uniform(80, 95),
                    grain_quality=random.choice(["excellent", "good", "good", "fair"]),
                    created_at=planting_date
                )
                
                # Calculate profit if revenue exists
                if cycle.total_revenue:
                    cycle.profit = cycle.total_revenue - cycle.total_cost
                
                cycles.append(cycle)
        
        db.add_all(cycles)
        db.commit()
        print(f"✅ Created {len(cycles)} crop cycles")
        return cycles
        
    except Exception as e:
        print(f"❌ Error creating crop cycles: {e}")
        db.rollback()
        return []
    finally:
        db.close()

def create_additional_users_and_farms():
    """Create additional users for admin and policy maker testing"""
    db = SessionLocal()
    try:
        print("Creating additional farms for diverse user experience...")
        
        # Get existing users
        farmer1 = db.query(User).filter(User.username == "farmer1").first()
        admin = db.query(User).filter(User.username == "admin").first()
        policy1 = db.query(User).filter(User.username == "policy1").first()
        
        # Redistribute some farms to admin and policy maker for testing
        all_farms = db.query(Farm).all()
        
        # Assign some farms to admin (for oversight)
        admin_farms = all_farms[8:10]  # 2 farms
        for farm in admin_farms:
            farm.owner_id = admin.id
        
        # Policy makers don't typically own farms, but we'll give them access to aggregate data
        
        db.commit()
        print(f"✅ Redistributed farms: farmer1={len(all_farms)-2}, admin=2, policy1=0")
        
    except Exception as e:
        print(f"❌ Error redistributing farms: {e}")
        db.rollback()
    finally:
        db.close()

def populate_dashboard_data():
    """Main function to populate all dashboard data"""
    print("=== Populating Dashboard Data for Better UX ===\n")
    
    # Create recommendations
    recommendations = create_seed_recommendations()
    
    # Create crop cycles
    cycles = create_crop_cycles()
    
    # Redistribute farms
    create_additional_users_and_farms()
    
    print(f"\n=== Summary ===")
    print(f"✅ {len(recommendations)} seed recommendations created")
    print(f"✅ {len(cycles)} crop cycles created")
    print(f"✅ Farms redistributed among users")
    print(f"\nDashboards should now show meaningful data for:")
    print(f"  🚜 farmer1: 10 farms with recommendations and crop history")
    print(f"  🏢 admin: 2 farms for oversight and system management")
    print(f"  🏛️  policy1: Access to aggregate policy data")
    print(f"\nYour Climate-Adaptive Seed AI Bank dashboards are now ready! 📊")

if __name__ == "__main__":
    populate_dashboard_data()