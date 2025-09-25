from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime

from models import get_db
from models.database_models import Farm, User, SoilProfile, ClimateRecord, CropCycle
from models.pydantic_models import (
    FarmCreate, FarmResponse, SoilProfileCreate, SoilProfileResponse,
    ClimateRecordCreate, ClimateRecordResponse, CropCycleCreate, CropCycleResponse
)
from .auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=FarmResponse)
async def create_farm(
    farm: FarmCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new farm for the current user"""
    db_farm = Farm(**farm.dict(), owner_id=current_user.id)
    db.add(db_farm)
    db.commit()
    db.refresh(db_farm)
    return db_farm

@router.get("/", response_model=List[FarmResponse])
async def get_my_farms(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all farms owned by the current user"""
    farms = db.query(Farm).filter(Farm.owner_id == current_user.id).all()
    return farms

@router.get("/{farm_id}", response_model=FarmResponse)
async def get_farm(
    farm_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific farm by ID"""
    farm = db.query(Farm).filter(
        Farm.id == farm_id,
        Farm.owner_id == current_user.id
    ).first()
    
    if not farm:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )
    
    return farm

@router.put("/{farm_id}", response_model=FarmResponse)
async def update_farm(
    farm_id: int,
    farm_update: FarmCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a farm"""
    db_farm = db.query(Farm).filter(
        Farm.id == farm_id,
        Farm.owner_id == current_user.id
    ).first()
    
    if not db_farm:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )
    
    for field, value in farm_update.dict().items():
        setattr(db_farm, field, value)
    
    db_farm.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_farm)
    
    return db_farm

@router.delete("/{farm_id}")
async def delete_farm(
    farm_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a farm"""
    db_farm = db.query(Farm).filter(
        Farm.id == farm_id,
        Farm.owner_id == current_user.id
    ).first()
    
    if not db_farm:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )
    
    db.delete(db_farm)
    db.commit()
    
    return {"message": "Farm deleted successfully"}

# Soil Profile endpoints
@router.post("/{farm_id}/soil-profiles", response_model=SoilProfileResponse)
async def create_soil_profile(
    farm_id: int,
    soil_profile: SoilProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a soil profile for a farm"""
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
    
    db_soil_profile = SoilProfile(**soil_profile.dict(), farm_id=farm_id)
    db.add(db_soil_profile)
    db.commit()
    db.refresh(db_soil_profile)
    
    return db_soil_profile

@router.get("/{farm_id}/soil-profiles", response_model=List[SoilProfileResponse])
async def get_soil_profiles(
    farm_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all soil profiles for a farm"""
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
    
    soil_profiles = db.query(SoilProfile).filter(SoilProfile.farm_id == farm_id).all()
    return soil_profiles

# Climate Record endpoints
@router.post("/{farm_id}/climate-records", response_model=ClimateRecordResponse)
async def create_climate_record(
    farm_id: int,
    climate_record: ClimateRecordCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a climate record for a farm"""
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
    
    db_climate_record = ClimateRecord(**climate_record.dict(), farm_id=farm_id)
    db.add(db_climate_record)
    db.commit()
    db.refresh(db_climate_record)
    
    return db_climate_record

@router.get("/{farm_id}/climate-records", response_model=List[ClimateRecordResponse])
async def get_climate_records(
    farm_id: int,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get climate records for a farm"""
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
    
    climate_records = db.query(ClimateRecord).filter(
        ClimateRecord.farm_id == farm_id
    ).order_by(ClimateRecord.record_date.desc()).limit(limit).all()
    
    return climate_records

# Crop Cycle endpoints
@router.post("/{farm_id}/crop-cycles", response_model=CropCycleResponse)
async def create_crop_cycle(
    farm_id: int,
    crop_cycle: CropCycleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a crop cycle record for a farm"""
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
    
    db_crop_cycle = CropCycle(**crop_cycle.dict(), farm_id=farm_id)
    
    # Calculate profit if cost and revenue are provided
    if db_crop_cycle.total_cost and db_crop_cycle.total_revenue:
        db_crop_cycle.profit = db_crop_cycle.total_revenue - db_crop_cycle.total_cost
    
    db.add(db_crop_cycle)
    db.commit()
    db.refresh(db_crop_cycle)
    
    return db_crop_cycle

@router.get("/{farm_id}/crop-cycles", response_model=List[CropCycleResponse])
async def get_crop_cycles(
    farm_id: int,
    season: Optional[str] = None,
    year: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get crop cycles for a farm"""
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
    
    query = db.query(CropCycle).filter(CropCycle.farm_id == farm_id)
    
    if season:
        query = query.filter(CropCycle.season == season)
    
    if year:
        query = query.filter(CropCycle.year == year)
    
    crop_cycles = query.order_by(CropCycle.year.desc(), CropCycle.season.desc()).all()
    
    return crop_cycles

@router.get("/{farm_id}/dashboard")
async def get_farm_dashboard(
    farm_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get dashboard data for a farm"""
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
    
    # Get recent crop cycles
    recent_cycles = db.query(CropCycle).filter(
        CropCycle.farm_id == farm_id
    ).order_by(CropCycle.year.desc(), CropCycle.season.desc()).limit(5).all()
    
    # Calculate performance metrics
    total_cycles = len(recent_cycles)
    avg_yield = sum(c.yield_achieved or 0 for c in recent_cycles) / total_cycles if total_cycles > 0 else 0
    total_profit = sum(c.profit or 0 for c in recent_cycles)
    
    # Get latest soil profile
    latest_soil = db.query(SoilProfile).filter(
        SoilProfile.farm_id == farm_id
    ).order_by(SoilProfile.test_date.desc()).first()
    
    # Get recent climate records
    recent_climate = db.query(ClimateRecord).filter(
        ClimateRecord.farm_id == farm_id
    ).order_by(ClimateRecord.record_date.desc()).limit(30).all()
    
    return {
        "farm": farm,
        "performance": {
            "total_cycles": total_cycles,
            "average_yield": round(avg_yield, 2),
            "total_profit": round(total_profit, 2),
            "cultivated_area": farm.cultivated_area,
            "utilization_rate": round((farm.cultivated_area / farm.total_area) * 100, 1)
        },
        "latest_soil_profile": latest_soil,
        "recent_crop_cycles": recent_cycles,
        "climate_summary": {
            "records_count": len(recent_climate),
            "avg_temperature": round(sum(c.temp_avg or 0 for c in recent_climate) / len(recent_climate), 1) if recent_climate else None,
            "total_rainfall": round(sum(c.rainfall or 0 for c in recent_climate), 1) if recent_climate else None
        }
    }