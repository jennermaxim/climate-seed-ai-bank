import requests
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    print("Warning: numpy not available, using fallback for soil calculations")
    HAS_NUMPY = False

from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import json
import os
from dotenv import load_dotenv
from .uganda_service import uganda_service, UgandanLocation

load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class SoilData:
    """Soil data structure"""
    ph_level: float
    organic_matter: float
    nitrogen: float
    phosphorus: float
    potassium: float
    texture: str
    drainage: str
    depth: float
    salinity: float
    cec: Optional[float] = None  # Cation Exchange Capacity
    bulk_density: Optional[float] = None

@dataclass
class SoilSuitability:
    """Soil suitability analysis result"""
    suitability_score: float
    limiting_factors: List[str]
    recommendations: List[str]
    confidence_level: float

class SoilAnalysisService:
    """Service for soil analysis and recommendations"""
    
    def __init__(self):
        # SoilGrids API endpoint (no API key required)
        self.soilgrids_url = "https://rest.isric.org/soilgrids/v2.0"
        
        # Cache for soil data to avoid repeated API calls
        self._soil_cache = {}
        
        # SoilGrids property mappings
        self.soilgrids_properties = {
            "phh2o": "ph_level",           # pH in water
            "ocd": "organic_matter",       # Organic carbon density
            "nitrogen": "nitrogen",        # Total nitrogen
            "bdod": "bulk_density",       # Bulk density
            "cec": "cec",                 # Cation exchange capacity
            "clay": "clay_content",       # Clay content
            "sand": "sand_content",       # Sand content
            "silt": "silt_content"        # Silt content
        }
        
        # Soil texture classification
        self.texture_classes = {
            "clay": {"clay": (40, 100), "silt": (0, 60), "sand": (0, 45)},
            "sandy_clay": {"clay": (35, 40), "silt": (0, 20), "sand": (45, 65)},
            "silty_clay": {"clay": (35, 40), "silt": (40, 60), "sand": (0, 20)},
            "sandy_clay_loam": {"clay": (20, 35), "silt": (0, 28), "sand": (45, 80)},
            "clay_loam": {"clay": (27, 40), "silt": (15, 53), "sand": (20, 45)},
            "silty_clay_loam": {"clay": (27, 40), "silt": (40, 73), "sand": (0, 20)},
            "sandy_loam": {"clay": (0, 20), "silt": (0, 50), "sand": (50, 85)},
            "loam": {"clay": (7, 27), "silt": (28, 50), "sand": (23, 52)},
            "silt_loam": {"clay": (0, 27), "silt": (50, 88), "sand": (0, 50)},
            "silt": {"clay": (0, 12), "silt": (80, 100), "sand": (0, 20)},
            "loamy_sand": {"clay": (0, 15), "silt": (0, 30), "sand": (70, 90)},
            "sand": {"clay": (0, 10), "silt": (0, 15), "sand": (85, 100)}
        }
        
        # Crop-specific soil requirements
        self.crop_requirements = {
            "maize": {
                "ph_range": (5.8, 7.0),
                "organic_matter_min": 2.0,
                "nitrogen": "medium",
                "phosphorus": "medium",
                "potassium": "medium",
                "preferred_textures": ["loam", "clay_loam", "silt_loam"],
                "drainage": ["good", "excellent"],
                "depth_min": 50
            },
            "beans": {
                "ph_range": (6.0, 7.5),
                "organic_matter_min": 2.5,
                "nitrogen": "low",  # Nitrogen-fixing
                "phosphorus": "high",
                "potassium": "medium",
                "preferred_textures": ["loam", "sandy_loam", "clay_loam"],
                "drainage": ["good", "excellent"],
                "depth_min": 40
            },
            "cassava": {
                "ph_range": (4.5, 7.0),
                "organic_matter_min": 1.5,
                "nitrogen": "low",
                "phosphorus": "medium",
                "potassium": "high",
                "preferred_textures": ["sandy_loam", "loam", "clay_loam"],
                "drainage": ["good", "fair"],
                "depth_min": 100
            },
            "sweet_potato": {
                "ph_range": (5.5, 7.0),
                "organic_matter_min": 2.0,
                "nitrogen": "medium",
                "phosphorus": "medium",
                "potassium": "high",
                "preferred_textures": ["sandy_loam", "loam"],
                "drainage": ["excellent", "good"],
                "depth_min": 30
            },
            "groundnuts": {
                "ph_range": (6.0, 7.5),
                "organic_matter_min": 2.0,
                "nitrogen": "low",  # Nitrogen-fixing
                "phosphorus": "high",
                "potassium": "medium",
                "preferred_textures": ["sandy_loam", "loam"],
                "drainage": ["excellent", "good"],
                "depth_min": 40
            },
            "rice": {
                "ph_range": (5.5, 7.0),
                "organic_matter_min": 2.5,
                "nitrogen": "high",
                "phosphorus": "medium",
                "potassium": "medium",
                "preferred_textures": ["clay", "clay_loam", "silty_clay"],
                "drainage": ["poor", "fair"],  # Rice tolerates poor drainage
                "depth_min": 20
            }
        }
    
    def get_soil_data_from_coordinates(self, latitude: float, longitude: float) -> Optional[SoilData]:
        """Get soil data from SoilGrids API based on coordinates"""
        try:
            # Properties to fetch from SoilGrids
            properties = [
                "phh2o",      # pH in water
                "soc",        # Soil organic carbon
                "nitrogen",   # Total nitrogen
                "cec",        # Cation exchange capacity
                "bdod",       # Bulk density
                "sand",       # Sand content
                "silt",       # Silt content
                "clay"        # Clay content
            ]
            
            # Depth layer (0-30cm topsoil)
            depth = "0-30cm"
            
            soil_data = {}
            
            for prop in properties:
                try:
                    url = f"{self.soilgrids_url}/query"
                    params = {
                        "lon": longitude,
                        "lat": latitude,
                        "property": prop,
                        "depth": depth,
                        "value": "mean"
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        soil_data[prop] = data.get("properties", {}).get(prop, {}).get("mean", 0)
                    
                except Exception as e:
                    logger.warning(f"Failed to fetch {prop} from SoilGrids: {e}")
                    soil_data[prop] = None
            
            # Convert and calculate derived properties
            ph = soil_data.get("phh2o", 65) / 10  # Convert from pH*10 to pH
            organic_carbon = soil_data.get("soc", 15) / 10  # Convert from g/kg*10 to %
            organic_matter = organic_carbon * 1.72 if organic_carbon else 2.5  # Approximate conversion
            
            # Texture classification
            sand_pct = soil_data.get("sand", 400) / 10  # Convert from g/kg*10 to %
            silt_pct = soil_data.get("silt", 300) / 10
            clay_pct = soil_data.get("clay", 300) / 10
            
            texture = self._classify_texture(sand_pct, silt_pct, clay_pct)
            drainage = self._estimate_drainage(texture, organic_matter)
            
            return SoilData(
                ph_level=ph,
                organic_matter=organic_matter,
                nitrogen=soil_data.get("nitrogen", 2000) / 100,  # Convert mg/kg to ppm
                phosphorus=np.random.normal(25, 10),  # Estimated, as not available from SoilGrids
                potassium=np.random.normal(150, 50),  # Estimated
                texture=texture,
                drainage=drainage,
                depth=100,  # Default depth, would need additional data source
                salinity=0.2,  # Default low salinity for Uganda
                cec=soil_data.get("cec", 150) / 10,  # Convert from cmol/kg*10 to cmol/kg
                bulk_density=soil_data.get("bdod", 1400) / 100  # Convert from cg/cm³*100 to g/cm³
            )
            
        except Exception as e:
            logger.error(f"Error fetching soil data from SoilGrids: {e}")
            return self._generate_synthetic_soil_data(latitude, longitude)
    
    def analyze_soil_suitability(self, soil_data: SoilData, crop_type: str) -> SoilSuitability:
        """Analyze soil suitability for a specific crop"""
        try:
            if crop_type not in self.crop_requirements:
                return SoilSuitability(
                    suitability_score=0.5,
                    limiting_factors=["Unknown crop type"],
                    recommendations=["Crop requirements not available"],
                    confidence_level=0.3
                )
            
            requirements = self.crop_requirements[crop_type]
            score_components = []
            limiting_factors = []
            recommendations = []
            
            # pH suitability
            ph_min, ph_max = requirements["ph_range"]
            if ph_min <= soil_data.ph_level <= ph_max:
                ph_score = 1.0
            elif soil_data.ph_level < ph_min:
                ph_score = max(0, 1 - (ph_min - soil_data.ph_level) / 2)
                limiting_factors.append("Soil too acidic")
                recommendations.append(f"Apply lime to raise pH to {ph_min}-{ph_max}")
            else:
                ph_score = max(0, 1 - (soil_data.ph_level - ph_max) / 2)
                limiting_factors.append("Soil too alkaline")
                recommendations.append(f"Apply sulfur or organic matter to lower pH to {ph_min}-{ph_max}")
            
            score_components.append(("pH", ph_score, 0.2))
            
            # Organic matter
            om_min = requirements["organic_matter_min"]
            if soil_data.organic_matter >= om_min:
                om_score = min(1.0, soil_data.organic_matter / (om_min * 2))
            else:
                om_score = soil_data.organic_matter / om_min
                limiting_factors.append("Low organic matter")
                recommendations.append("Increase organic matter through compost, manure, or cover crops")
            
            score_components.append(("Organic Matter", om_score, 0.15))
            
            # Texture suitability
            preferred_textures = requirements["preferred_textures"]
            if soil_data.texture in preferred_textures:
                texture_score = 1.0
            else:
                texture_score = 0.6
                limiting_factors.append(f"Suboptimal soil texture: {soil_data.texture}")
                recommendations.append("Consider soil amendments to improve texture")
            
            score_components.append(("Texture", texture_score, 0.15))
            
            # Drainage suitability
            preferred_drainage = requirements["drainage"]
            drainage_levels = {"poor": 1, "fair": 2, "good": 3, "excellent": 4}
            
            if soil_data.drainage in preferred_drainage:
                drainage_score = 1.0
            else:
                current_level = drainage_levels.get(soil_data.drainage, 2)
                preferred_levels = [drainage_levels.get(d, 2) for d in preferred_drainage]
                min_preferred = min(preferred_levels)
                max_preferred = max(preferred_levels)
                
                if current_level < min_preferred:
                    drainage_score = max(0.3, current_level / min_preferred)
                    limiting_factors.append("Poor drainage")
                    recommendations.append("Improve drainage through channels or raised beds")
                else:
                    drainage_score = max(0.3, max_preferred / current_level)
                    limiting_factors.append("Excessive drainage")
                    recommendations.append("Improve water retention through mulching or organic matter")
            
            score_components.append(("Drainage", drainage_score, 0.15))
            
            # Nutrient levels
            nutrient_scores = self._evaluate_nutrients(soil_data, requirements)
            for nutrient, score in nutrient_scores.items():
                score_components.append((nutrient, score["score"], score["weight"]))
                if score["score"] < 0.7:
                    limiting_factors.extend(score["limitations"])
                    recommendations.extend(score["recommendations"])
            
            # Depth suitability
            depth_min = requirements["depth_min"]
            if soil_data.depth >= depth_min:
                depth_score = 1.0
            else:
                depth_score = max(0.3, soil_data.depth / depth_min)
                limiting_factors.append("Shallow soil depth")
                recommendations.append("Consider deep tillage or raised beds")
            
            score_components.append(("Depth", depth_score, 0.1))
            
            # Calculate weighted average score
            total_score = sum(score * weight for _, score, weight in score_components)
            total_weight = sum(weight for _, _, weight in score_components)
            suitability_score = total_score / total_weight if total_weight > 0 else 0.5
            
            # Confidence level based on data completeness
            confidence = self._calculate_confidence(soil_data)
            
            return SoilSuitability(
                suitability_score=suitability_score,
                limiting_factors=limiting_factors,
                recommendations=recommendations,
                confidence_level=confidence
            )
            
        except Exception as e:
            logger.error(f"Error analyzing soil suitability: {e}")
            return SoilSuitability(
                suitability_score=0.5,
                limiting_factors=["Analysis error"],
                recommendations=["Unable to complete soil analysis"],
                confidence_level=0.3
            )
    
    def _classify_texture(self, sand_pct: float, silt_pct: float, clay_pct: float) -> str:
        """Classify soil texture based on sand, silt, clay percentages"""
        try:
            # Normalize percentages to sum to 100
            total = sand_pct + silt_pct + clay_pct
            if total > 0:
                sand_pct = (sand_pct / total) * 100
                silt_pct = (silt_pct / total) * 100
                clay_pct = (clay_pct / total) * 100
            
            # Find matching texture class
            for texture, ranges in self.texture_classes.items():
                if (ranges["clay"][0] <= clay_pct <= ranges["clay"][1] and
                    ranges["silt"][0] <= silt_pct <= ranges["silt"][1] and
                    ranges["sand"][0] <= sand_pct <= ranges["sand"][1]):
                    return texture
            
            # Default classification if no match
            if clay_pct > 40:
                return "clay"
            elif sand_pct > 70:
                return "sandy_loam"
            else:
                return "loam"
                
        except Exception as e:
            logger.error(f"Error classifying texture: {e}")
            return "loam"
    
    def _estimate_drainage(self, texture: str, organic_matter: float) -> str:
        """Estimate drainage based on texture and organic matter"""
        drainage_map = {
            "sand": "excellent",
            "loamy_sand": "excellent",
            "sandy_loam": "good",
            "loam": "good",
            "silt_loam": "fair",
            "silt": "fair",
            "sandy_clay_loam": "fair",
            "clay_loam": "fair",
            "silty_clay_loam": "poor",
            "sandy_clay": "poor",
            "silty_clay": "poor",
            "clay": "poor"
        }
        
        base_drainage = drainage_map.get(texture, "fair")
        
        # Adjust for organic matter (improves structure and drainage)
        if organic_matter > 4:
            if base_drainage == "poor":
                return "fair"
            elif base_drainage == "fair":
                return "good"
        
        return base_drainage
    
    def _evaluate_nutrients(self, soil_data: SoilData, requirements: Dict) -> Dict:
        """Evaluate nutrient levels against crop requirements"""
        nutrients = {}
        
        # Nitrogen evaluation
        n_req = requirements.get("nitrogen", "medium")
        n_thresholds = {"low": 20, "medium": 40, "high": 60}
        n_threshold = n_thresholds.get(n_req, 40)
        
        if soil_data.nitrogen >= n_threshold:
            n_score = 1.0
            n_limitations = []
            n_recommendations = []
        else:
            n_score = soil_data.nitrogen / n_threshold
            n_limitations = ["Low nitrogen levels"]
            n_recommendations = ["Apply nitrogen fertilizer or organic matter"]
        
        nutrients["Nitrogen"] = {
            "score": n_score,
            "weight": 0.15,
            "limitations": n_limitations,
            "recommendations": n_recommendations
        }
        
        # Phosphorus evaluation
        p_req = requirements.get("phosphorus", "medium")
        p_thresholds = {"low": 15, "medium": 25, "high": 40}
        p_threshold = p_thresholds.get(p_req, 25)
        
        if soil_data.phosphorus >= p_threshold:
            p_score = 1.0
            p_limitations = []
            p_recommendations = []
        else:
            p_score = soil_data.phosphorus / p_threshold
            p_limitations = ["Low phosphorus levels"]
            p_recommendations = ["Apply phosphorus fertilizer or rock phosphate"]
        
        nutrients["Phosphorus"] = {
            "score": p_score,
            "weight": 0.15,
            "limitations": p_limitations,
            "recommendations": p_recommendations
        }
        
        # Potassium evaluation
        k_req = requirements.get("potassium", "medium")
        k_thresholds = {"low": 80, "medium": 120, "high": 200}
        k_threshold = k_thresholds.get(k_req, 120)
        
        if soil_data.potassium >= k_threshold:
            k_score = 1.0
            k_limitations = []
            k_recommendations = []
        else:
            k_score = soil_data.potassium / k_threshold
            k_limitations = ["Low potassium levels"]
            k_recommendations = ["Apply potassium fertilizer or wood ash"]
        
        nutrients["Potassium"] = {
            "score": k_score,
            "weight": 0.15,
            "limitations": k_limitations,
            "recommendations": k_recommendations
        }
        
        return nutrients
    
    def _calculate_confidence(self, soil_data: SoilData) -> float:
        """Calculate confidence level based on data completeness and quality"""
        confidence = 1.0
        
        # Reduce confidence for missing or default values
        if soil_data.ph_level == 6.5:  # Default pH
            confidence -= 0.1
        if soil_data.organic_matter == 2.5:  # Default OM
            confidence -= 0.1
        if soil_data.nitrogen == 20:  # Default N
            confidence -= 0.1
        if soil_data.phosphorus < 10 or soil_data.phosphorus > 100:  # Unrealistic P values
            confidence -= 0.1
        if soil_data.potassium < 50 or soil_data.potassium > 300:  # Unrealistic K values
            confidence -= 0.1
        
        return max(0.3, confidence)
    
    def _generate_synthetic_soil_data(self, latitude: float, longitude: float) -> SoilData:
        """Generate synthetic soil data based on Uganda's soil patterns"""
        # Uganda's soil characteristics vary by region
        # Northern Uganda: generally more sandy, lower organic matter
        # Central/Western: more fertile, higher organic matter
        # Eastern: variable, often clay soils in lowlands
        
        if latitude > 2.0:  # Northern Uganda
            ph = np.random.normal(6.2, 0.5)
            organic_matter = np.random.normal(2.0, 0.5)
            texture = np.random.choice(["sandy_loam", "loam", "clay_loam"], p=[0.4, 0.4, 0.2])
        elif latitude < 0.5:  # Southern/Central Uganda
            ph = np.random.normal(6.0, 0.4)
            organic_matter = np.random.normal(3.0, 0.7)
            texture = np.random.choice(["loam", "clay_loam", "clay"], p=[0.3, 0.4, 0.3])
        else:  # Central Uganda
            ph = np.random.normal(6.5, 0.3)
            organic_matter = np.random.normal(2.8, 0.6)
            texture = np.random.choice(["loam", "clay_loam", "silt_loam"], p=[0.4, 0.3, 0.3])
        
        return SoilData(
            ph_level=max(4.0, min(8.0, ph)),
            organic_matter=max(1.0, organic_matter),
            nitrogen=np.random.normal(25, 8),
            phosphorus=np.random.normal(20, 10),
            potassium=np.random.normal(120, 40),
            texture=texture,
            drainage=self._estimate_drainage(texture, organic_matter),
            depth=np.random.normal(80, 20),
            salinity=np.random.normal(0.3, 0.2),
            cec=np.random.normal(15, 5),
            bulk_density=np.random.normal(1.3, 0.2)
        )
    
    # Uganda-specific soil methods
    def get_soil_for_ugandan_location(self, location_name: str) -> Optional[SoilData]:
        """Get soil data for a named Ugandan location using SoilGrids API"""
        location = uganda_service.get_location(location_name)
        if not location:
            logger.error(f"Unknown Ugandan location: {location_name}")
            return None
        
        # Check cache first
        cache_key = f"{location_name}_{location.latitude}_{location.longitude}"
        if cache_key in self._soil_cache:
            cached_data, timestamp = self._soil_cache[cache_key]
            # Use cached data if less than 24 hours old
            if (datetime.now() - timestamp).total_seconds() < 86400:
                return cached_data
        
        # Fetch fresh data from SoilGrids API
        soil_data = self.get_soil_data_from_coordinates(location.latitude, location.longitude)
        
        # Cache the result
        if soil_data:
            from datetime import datetime
            self._soil_cache[cache_key] = (soil_data, datetime.now())
        
        return soil_data
    
    def get_regional_soil_uganda(self, region: str) -> Dict[str, SoilData]:
        """Get soil data for all locations in a Ugandan region"""
        from .uganda_service import UgandaRegion
        
        try:
            region_enum = UgandaRegion(region)
            locations = uganda_service.get_locations_by_region(region_enum)
        except ValueError:
            logger.error(f"Invalid Ugandan region: {region}")
            return {}
        
        soil_data = {}
        for location in locations:
            soil = self.get_soil_data_from_coordinates(location.latitude, location.longitude)
            if soil:
                soil_data[location.name] = soil
        
        return soil_data
    
    def analyze_crop_suitability_uganda(self, location_name: str, crop_type: str) -> Optional[SoilSuitability]:
        """Analyze crop suitability for a specific Ugandan location"""
        soil_data = self.get_soil_for_ugandan_location(location_name)
        if not soil_data:
            return None
        
        return self.analyze_soil_suitability(soil_data, crop_type)
    
    def get_recommended_crops_for_location(self, location_name: str) -> List[Dict[str, any]]:
        """Get crop recommendations based on soil and climate suitability for a Ugandan location"""
        location = uganda_service.get_location(location_name)
        if not location:
            logger.error(f"Unknown Ugandan location: {location_name}")
            return []
        
        soil_data = self.get_soil_for_ugandan_location(location_name)
        if not soil_data:
            return []
        
        recommendations = []
        
        # Analyze suitability for location's main crops
        for crop in location.main_crops:
            suitability = self.analyze_soil_suitability(soil_data, crop)
            
            # Get Uganda-specific varieties for this crop
            varieties = uganda_service.get_crop_varieties(crop)
            
            recommendations.append({
                "crop": crop,
                "suitability_score": suitability.suitability_score,
                "confidence": suitability.confidence_level,
                "limiting_factors": suitability.limiting_factors,
                "recommendations": suitability.recommendations,
                "ugandan_varieties": varieties,
                "climate_zone": location.climate_zone.value,
                "region": location.region.value
            })
        
        # Sort by suitability score
        recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)
        
        return recommendations
    
    def get_soil_health_report_uganda(self, location_name: str) -> Dict[str, any]:
        """Generate comprehensive soil health report for Ugandan location"""
        location = uganda_service.get_location(location_name)
        soil_data = self.get_soil_for_ugandan_location(location_name)
        
        if not location or not soil_data:
            return {"error": "Location not found or soil data unavailable"}
        
        # Analyze soil health metrics
        health_metrics = {
            "overall_health": "good",  # Will be calculated
            "ph_status": "optimal" if 6.0 <= soil_data.ph_level <= 7.0 else "needs_adjustment",
            "organic_matter_status": "adequate" if soil_data.organic_matter >= 2.5 else "low",
            "nutrient_status": {
                "nitrogen": "adequate" if soil_data.nitrogen >= 20 else "low",
                "phosphorus": "adequate" if soil_data.phosphorus >= 15 else "low", 
                "potassium": "adequate" if soil_data.potassium >= 100 else "low"
            },
            "physical_properties": {
                "texture": soil_data.texture,
                "drainage": soil_data.drainage,
                "bulk_density": "good" if soil_data.bulk_density <= 1.4 else "compacted"
            }
        }
        
        # Calculate overall health score
        health_score = 0
        if health_metrics["ph_status"] == "optimal":
            health_score += 25
        if health_metrics["organic_matter_status"] == "adequate":
            health_score += 25
        if all(status == "adequate" for status in health_metrics["nutrient_status"].values()):
            health_score += 25
        if health_metrics["physical_properties"]["bulk_density"] == "good":
            health_score += 25
        
        if health_score >= 75:
            health_metrics["overall_health"] = "excellent"
        elif health_score >= 50:
            health_metrics["overall_health"] = "good"
        else:
            health_metrics["overall_health"] = "poor"
        
        # Generate improvement recommendations
        improvement_recommendations = []
        
        if health_metrics["ph_status"] != "optimal":
            if soil_data.ph_level < 6.0:
                improvement_recommendations.append("Apply agricultural lime to increase soil pH")
            else:
                improvement_recommendations.append("Apply organic matter or sulfur to reduce soil pH")
        
        if health_metrics["organic_matter_status"] == "low":
            improvement_recommendations.append("Incorporate compost, manure, or crop residues to increase organic matter")
        
        for nutrient, status in health_metrics["nutrient_status"].items():
            if status == "low":
                improvement_recommendations.append(f"Apply {nutrient}-rich fertilizers or organic amendments")
        
        if health_metrics["physical_properties"]["bulk_density"] == "compacted":
            improvement_recommendations.append("Implement reduced tillage and add organic matter to improve soil structure")
        
        return {
            "location": location.name,
            "district": location.district,
            "region": location.region.value,
            "climate_zone": location.climate_zone.value,
            "soil_data": {
                "ph": soil_data.ph_level,
                "organic_matter": soil_data.organic_matter,
                "nitrogen": soil_data.nitrogen,
                "phosphorus": soil_data.phosphorus,
                "potassium": soil_data.potassium,
                "texture": soil_data.texture,
                "drainage": soil_data.drainage,
                "bulk_density": soil_data.bulk_density,
                "cec": soil_data.cec
            },
            "health_metrics": health_metrics,
            "health_score": health_score,
            "improvement_recommendations": improvement_recommendations,
            "suitable_crops": location.main_crops,
            "soil_types": location.soil_types
        }

# Create service instances
soil_analysis_service = SoilAnalysisService()

# Create a unified soil service for backward compatibility
class SoilService:
    """Unified soil service"""
    def __init__(self):
        self.analysis_service = soil_analysis_service
    
    async def get_soil_for_ugandan_location(self, location_name: str):
        """Get soil data for a Ugandan location (async wrapper)"""
        return self.analysis_service.get_soil_for_ugandan_location(location_name)
    
    async def assess_soil_health_uganda(self, location_name: str):
        """Assess soil health for Uganda (async wrapper)"""
        return self.analysis_service.get_soil_health_report_uganda(location_name)

soil_service = SoilService()