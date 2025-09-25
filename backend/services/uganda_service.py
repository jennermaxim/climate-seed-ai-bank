"""
Uganda-specific geographical and agricultural data service
Provides real coordinates and regional information for API integration
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum

class UgandaRegion(str, Enum):
    CENTRAL = "Central"
    WESTERN = "Western"
    EASTERN = "Eastern"
    NORTHERN = "Northern"

class ClimateZone(str, Enum):
    LAKE_VICTORIA_BASIN = "Lake Victoria Basin"
    CENTRAL_PLATEAU = "Central Plateau"
    WESTERN_HIGHLANDS = "Western Highlands"
    NORTHERN_SAVANNA = "Northern Savanna"
    EASTERN_HIGHLANDS = "Eastern Highlands"

@dataclass
class UgandanLocation:
    """Ugandan location with agricultural context"""
    name: str
    district: str
    region: UgandaRegion
    climate_zone: ClimateZone
    latitude: float
    longitude: float
    elevation: float  # meters above sea level
    annual_rainfall_avg: int  # mm per year
    temperature_range: Tuple[float, float]  # (min, max) in Celsius
    main_crops: List[str]
    soil_types: List[str]

class UgandaLocationService:
    """Service providing Uganda-specific geographical and agricultural data"""
    
    def __init__(self):
        self.locations = {
            # Central Region
            "kampala": UgandanLocation(
                name="Kampala",
                district="Kampala",
                region=UgandaRegion.CENTRAL,
                climate_zone=ClimateZone.LAKE_VICTORIA_BASIN,
                latitude=0.3476,
                longitude=32.5825,
                elevation=1190,
                annual_rainfall_avg=1200,
                temperature_range=(16, 28),
                main_crops=["maize", "beans", "banana", "sweet_potato"],
                soil_types=["ferralsols", "acrisols"]
            ),
            "wakiso": UgandanLocation(
                name="Wakiso",
                district="Wakiso",
                region=UgandaRegion.CENTRAL,
                climate_zone=ClimateZone.CENTRAL_PLATEAU,
                latitude=0.4044,
                longitude=32.4597,
                elevation=1200,
                annual_rainfall_avg=1300,
                temperature_range=(17, 27),
                main_crops=["banana", "coffee", "maize", "beans"],
                soil_types=["ferralsols", "nitisols"]
            ),
            "mukono": UgandanLocation(
                name="Mukono",
                district="Mukono",
                region=UgandaRegion.CENTRAL,
                climate_zone=ClimateZone.CENTRAL_PLATEAU,
                latitude=0.3536,
                longitude=32.7455,
                elevation=1150,
                annual_rainfall_avg=1250,
                temperature_range=(16, 28),
                main_crops=["banana", "coffee", "maize", "cassava"],
                soil_types=["ferralsols", "acrisols"]
            ),
            
            # Western Region
            "mbarara": UgandanLocation(
                name="Mbarara",
                district="Mbarara",
                region=UgandaRegion.WESTERN,
                climate_zone=ClimateZone.WESTERN_HIGHLANDS,
                latitude=-0.6103,
                longitude=30.6587,
                elevation=1420,
                annual_rainfall_avg=900,
                temperature_range=(15, 27),
                main_crops=["banana", "sorghum", "millet", "beans"],
                soil_types=["acrisols", "lixisols"]
            ),
            "fort_portal": UgandanLocation(
                name="Fort Portal",
                district="Kabarole",
                region=UgandaRegion.WESTERN,
                climate_zone=ClimateZone.WESTERN_HIGHLANDS,
                latitude=0.6645,
                longitude=30.2746,
                elevation=1540,
                annual_rainfall_avg=1500,
                temperature_range=(14, 25),
                main_crops=["tea", "banana", "beans", "irish_potato"],
                soil_types=["andosols", "nitisols"]
            ),
            "kasese": UgandanLocation(
                name="Kasese",
                district="Kasese",
                region=UgandaRegion.WESTERN,
                climate_zone=ClimateZone.WESTERN_HIGHLANDS,
                latitude=0.1833,
                longitude=30.0833,
                elevation=950,
                annual_rainfall_avg=1000,
                temperature_range=(16, 30),
                main_crops=["cotton", "maize", "beans", "cassava"],
                soil_types=["vertisols", "fluvisols"]
            ),
            
            # Eastern Region
            "jinja": UgandanLocation(
                name="Jinja",
                district="Jinja",
                region=UgandaRegion.EASTERN,
                climate_zone=ClimateZone.LAKE_VICTORIA_BASIN,
                latitude=0.4244,
                longitude=33.2042,
                elevation=1134,
                annual_rainfall_avg=1200,
                temperature_range=(17, 29),
                main_crops=["sugarcane", "banana", "maize", "rice"],
                soil_types=["ferralsols", "fluvisols"]
            ),
            "mbale": UgandanLocation(
                name="Mbale",
                district="Mbale",
                region=UgandaRegion.EASTERN,
                climate_zone=ClimateZone.EASTERN_HIGHLANDS,
                latitude=1.0827,
                longitude=34.1758,
                elevation=1200,
                annual_rainfall_avg=1300,
                temperature_range=(15, 26),
                main_crops=["arabica_coffee", "banana", "beans", "maize"],
                soil_types=["andosols", "nitisols"]
            ),
            "soroti": UgandanLocation(
                name="Soroti",
                district="Soroti",
                region=UgandaRegion.EASTERN,
                climate_zone=ClimateZone.NORTHERN_SAVANNA,
                latitude=1.7147,
                longitude=33.6111,
                elevation=1140,
                annual_rainfall_avg=900,
                temperature_range=(18, 32),
                main_crops=["sorghum", "millet", "groundnuts", "cassava"],
                soil_types=["lixisols", "plinthosols"]
            ),
            
            # Northern Region
            "gulu": UgandanLocation(
                name="Gulu",
                district="Gulu",
                region=UgandaRegion.NORTHERN,
                climate_zone=ClimateZone.NORTHERN_SAVANNA,
                latitude=2.7794,
                longitude=32.2992,
                elevation=1100,
                annual_rainfall_avg=1100,
                temperature_range=(19, 33),
                main_crops=["sorghum", "millet", "groundnuts", "sesame"],
                soil_types=["acrisols", "lixisols"]
            ),
            "lira": UgandanLocation(
                name="Lira",
                district="Lira",
                region=UgandaRegion.NORTHERN,
                climate_zone=ClimateZone.NORTHERN_SAVANNA,
                latitude=2.2490,
                longitude=32.8999,
                elevation=1060,
                annual_rainfall_avg=1200,
                temperature_range=(18, 31),
                main_crops=["rice", "sorghum", "groundnuts", "beans"],
                soil_types=["plinthosols", "acrisols"]
            ),
            "arua": UgandanLocation(
                name="Arua",
                district="Arua",
                region=UgandaRegion.NORTHERN,
                climate_zone=ClimateZone.NORTHERN_SAVANNA,
                latitude=3.0197,
                longitude=30.9108,
                elevation=1200,
                annual_rainfall_avg=1100,
                temperature_range=(19, 32),
                main_crops=["tobacco", "cassava", "beans", "groundnuts"],
                soil_types=["lixisols", "acrisols"]
            )
        }
        
        # Major agricultural regions with typical coordinates for broader area queries
        self.regional_centers = {
            UgandaRegion.CENTRAL: (0.3476, 32.5825),  # Kampala
            UgandaRegion.WESTERN: (-0.6103, 30.6587),  # Mbarara
            UgandaRegion.EASTERN: (1.0827, 34.1758),   # Mbale
            UgandaRegion.NORTHERN: (2.7794, 32.2992)   # Gulu
        }
        
        # Climate-adapted crop varieties for Uganda
        self.ugandan_crop_varieties = {
            "maize": [
                {"name": "Longe 5", "maturity_days": 120, "yield_potential": 6.0, "drought_tolerance": 0.7},
                {"name": "Longe 10H", "maturity_days": 140, "yield_potential": 8.5, "drought_tolerance": 0.8},
                {"name": "PH4", "maturity_days": 135, "yield_potential": 9.0, "drought_tolerance": 0.6},
                {"name": "SC Duma 43", "maturity_days": 125, "yield_potential": 7.5, "drought_tolerance": 0.8}
            ],
            "beans": [
                {"name": "NABE 15", "maturity_days": 90, "yield_potential": 2.5, "drought_tolerance": 0.8},
                {"name": "NABE 14", "maturity_days": 85, "yield_potential": 2.2, "drought_tolerance": 0.7},
                {"name": "K20", "maturity_days": 95, "yield_potential": 2.8, "drought_tolerance": 0.6},
                {"name": "NABE 12C", "maturity_days": 80, "yield_potential": 2.0, "drought_tolerance": 0.9}
            ],
            "cassava": [
                {"name": "NAROCASS 1", "maturity_days": 365, "yield_potential": 25.0, "drought_tolerance": 0.9},
                {"name": "TME 14", "maturity_days": 330, "yield_potential": 22.0, "drought_tolerance": 0.8},
                {"name": "Magana", "maturity_days": 300, "yield_potential": 18.0, "drought_tolerance": 0.7}
            ],
            "sweet_potato": [
                {"name": "NASPOT 10 O", "maturity_days": 120, "yield_potential": 20.0, "drought_tolerance": 0.7},
                {"name": "NASPOT 11", "maturity_days": 135, "yield_potential": 25.0, "drought_tolerance": 0.6},
                {"name": "Ejumula", "maturity_days": 150, "yield_potential": 15.0, "drought_tolerance": 0.8}
            ],
            "groundnuts": [
                {"name": "Serenut 5R", "maturity_days": 105, "yield_potential": 2.5, "drought_tolerance": 0.8},
                {"name": "Red Beauty", "maturity_days": 95, "yield_potential": 2.2, "drought_tolerance": 0.9},
                {"name": "Serenut 4T", "maturity_days": 110, "yield_potential": 2.8, "drought_tolerance": 0.7}
            ]
        }
    
    def get_location(self, name: str) -> Optional[UgandanLocation]:
        """Get location data by name"""
        return self.locations.get(name.lower())
    
    def get_locations_by_region(self, region: UgandaRegion) -> List[UgandanLocation]:
        """Get all locations in a specific region"""
        return [loc for loc in self.locations.values() if loc.region == region]
    
    def get_locations_by_climate_zone(self, zone: ClimateZone) -> List[UgandanLocation]:
        """Get all locations in a specific climate zone"""
        return [loc for loc in self.locations.values() if loc.climate_zone == zone]
    
    def get_regional_center(self, region: UgandaRegion) -> Tuple[float, float]:
        """Get the central coordinates for a region"""
        return self.regional_centers[region]
    
    def get_suitable_crops(self, location_name: str) -> List[str]:
        """Get main crops suitable for a location"""
        location = self.get_location(location_name)
        return location.main_crops if location else []
    
    def get_crop_varieties(self, crop_type: str) -> List[Dict]:
        """Get Ugandan varieties for a specific crop"""
        return self.ugandan_crop_varieties.get(crop_type, [])
    
    def find_nearest_location(self, latitude: float, longitude: float) -> Optional[UgandanLocation]:
        """Find the nearest defined location to given coordinates"""
        min_distance = float('inf')
        nearest_location = None
        
        for location in self.locations.values():
            # Simple Euclidean distance calculation
            distance = ((latitude - location.latitude) ** 2 + 
                       (longitude - location.longitude) ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                nearest_location = location
        
        return nearest_location
    
    def get_all_locations(self) -> List[UgandanLocation]:
        """Get all available locations"""
        return list(self.locations.values())
    
    def get_location_names(self) -> List[str]:
        """Get list of all location names"""
        return [loc.name for loc in self.locations.values()]

# Global instance
uganda_service = UgandaLocationService()