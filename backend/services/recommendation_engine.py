import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime
import os

# Mock ML imports for now - replace with actual imports when ML packages are available
try:
    import numpy as np
    import pandas as pd
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, r2_score
    import joblib
    ML_AVAILABLE = True
except ImportError:
    # Fallback for when ML packages are not available
    np = None
    pd = None
    StandardScaler = None
    MinMaxScaler = None
    RandomForestRegressor = None
    GradientBoostingRegressor = None
    train_test_split = None
    mean_absolute_error = None
    r2_score = None
    joblib = None
    ML_AVAILABLE = False
    print("Warning: ML packages not available, using fallback recommendations")

from .climate_service import WeatherDataService, ClimateProjectionService
from .soil_service import SoilAnalysisService
from models.database_models import Seed, Farm, CropCycle, SoilProfile, ClimateRecord

logger = logging.getLogger(__name__)

@dataclass
class EnvironmentalConditions:
    """Environmental conditions for a farm"""
    temperature_avg: float
    temperature_range: float
    annual_rainfall: float
    rainfall_variability: float
    humidity_avg: float
    soil_ph: float
    soil_organic_matter: float
    soil_nitrogen: float
    soil_phosphorus: float
    soil_potassium: float
    soil_texture_score: float
    drainage_score: float
    altitude: float
    climate_risk_score: float

@dataclass
class SeedCompatibility:
    """Seed compatibility analysis result"""
    seed_id: int
    compatibility_score: float
    climate_match_score: float
    soil_match_score: float
    yield_prediction: float
    risk_score: float
    confidence_level: float
    reasons: List[str]

class SeedRecommendationEngine:
    """AI-powered seed recommendation engine"""
    
    def __init__(self):
        self.weather_service = WeatherDataService()
        self.climate_service = ClimateProjectionService()
        self.soil_service = SoilAnalysisService()
        
        # Model storage
        self.models = {}
        self.scalers = {}
        self.is_trained = False
        
        # Use fallback mode if ML packages are not available
        self.use_fallback = not ML_AVAILABLE
        
        if self.use_fallback:
            logging.warning("Using fallback recommendation mode - ML packages not available")
        
        # Feature weights for recommendation scoring
        self.feature_weights = {
            "climate_compatibility": 0.3,
            "soil_compatibility": 0.25,
            "yield_potential": 0.2,
            "risk_tolerance": 0.15,
            "market_factors": 0.1
        }
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models for different prediction tasks"""
        if not ML_AVAILABLE:
            self.models = {}
            self.scalers = {}
            return
            
        self.models = {
            "yield_predictor": GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            ),
            "climate_compatibility": RandomForestRegressor(
                n_estimators=100,
                max_depth=8,
                random_state=42
            ),
            "soil_compatibility": RandomForestRegressor(
                n_estimators=100,
                max_depth=8,
                random_state=42
            ),
            "risk_predictor": GradientBoostingRegressor(
                n_estimators=80,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        }
        
        self.scalers = {
            "environmental": StandardScaler(),
            "seed_features": StandardScaler(),
            "yield_features": MinMaxScaler()
        }
    
    def train_models(self, training_data=None) -> Dict[str, float]:
        """Train the recommendation models using historical data"""
        if not ML_AVAILABLE:
            logging.info("ML packages not available, skipping model training")
            return {"status": "skipped", "fallback_mode": True}
            
        try:
            logging.info("Starting model training...")
            
            # Prepare features
            env_features = self._extract_environmental_features(training_data)
            seed_features = self._extract_seed_features(training_data)
            
            # Combine features
            X = np.concatenate([env_features, seed_features], axis=1)
            
            # Prepare targets
            y_yield = training_data["yield_achieved"].values
            y_climate = training_data["climate_compatibility_score"].values
            y_soil = training_data["soil_compatibility_score"].values
            y_risk = training_data["risk_score"].values
            
            # Split data
            X_train, X_test, y_yield_train, y_yield_test = train_test_split(
                X, y_yield, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scalers["environmental"].fit_transform(X_train)
            X_test_scaled = self.scalers["environmental"].transform(X_test)
            
            # Train models
            model_performance = {}
            
            # Yield predictor
            self.models["yield_predictor"].fit(X_train_scaled, y_yield_train)
            yield_pred = self.models["yield_predictor"].predict(X_test_scaled)
            model_performance["yield_r2"] = r2_score(y_yield_test, yield_pred)
            model_performance["yield_mae"] = mean_absolute_error(y_yield_test, yield_pred)
            
            # Climate compatibility
            _, _, y_climate_train, y_climate_test = train_test_split(
                X, y_climate, test_size=0.2, random_state=42
            )
            self.models["climate_compatibility"].fit(X_train_scaled, y_climate_train)
            climate_pred = self.models["climate_compatibility"].predict(X_test_scaled)
            model_performance["climate_r2"] = r2_score(y_climate_test, climate_pred)
            
            # Soil compatibility
            _, _, y_soil_train, y_soil_test = train_test_split(
                X, y_soil, test_size=0.2, random_state=42
            )
            self.models["soil_compatibility"].fit(X_train_scaled, y_soil_train)
            soil_pred = self.models["soil_compatibility"].predict(X_test_scaled)
            model_performance["soil_r2"] = r2_score(y_soil_test, soil_pred)
            
            # Risk predictor
            _, _, y_risk_train, y_risk_test = train_test_split(
                X, y_risk, test_size=0.2, random_state=42
            )
            self.models["risk_predictor"].fit(X_train_scaled, y_risk_train)
            risk_pred = self.models["risk_predictor"].predict(X_test_scaled)
            model_performance["risk_r2"] = r2_score(y_risk_test, risk_pred)
            
            self.is_trained = True
            logger.info("Model training completed successfully")
            
            return model_performance
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            return {}
    
    def generate_recommendations(self, farm: Farm, available_seeds: List[Seed], 
                               season: str, year: int, preferences: Dict = None) -> List[SeedCompatibility]:
        """Generate seed recommendations for a farm"""
        try:
            logger.info(f"Generating recommendations for farm {farm.id}, season {season}, year {year}")
            
            # Get environmental conditions
            env_conditions = self._analyze_environmental_conditions(farm, season, year)
            
            # Analyze each seed
            recommendations = []
            for seed in available_seeds:
                compatibility = self._analyze_seed_compatibility(seed, env_conditions, farm, preferences)
                recommendations.append(compatibility)
            
            # Sort by compatibility score
            recommendations.sort(key=lambda x: x.compatibility_score, reverse=True)
            
            # Return top recommendations
            return recommendations[:10]
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _analyze_environmental_conditions(self, farm: Farm, season: str, year: int) -> EnvironmentalConditions:
        """Analyze environmental conditions for a farm"""
        try:
            # Get weather patterns
            weather_patterns = self.weather_service.get_seasonal_patterns(farm.latitude, farm.longitude)
            
            # Get climate projections
            projections = self.climate_service.get_climate_projections(
                farm.latitude, farm.longitude, year - datetime.now().year
            )
            
            # Get soil data
            soil_data = self.soil_service.get_soil_data_from_coordinates(farm.latitude, farm.longitude)
            
            # Calculate climate risk
            climate_risks = self.climate_service.calculate_climate_risks(weather_patterns, projections)
            
            # Extract seasonal data
            seasonal_key = self._get_seasonal_key(season)
            seasonal_data = weather_patterns.get("seasonal", {}).get(seasonal_key, {})
            
            return EnvironmentalConditions(
                temperature_avg=seasonal_data.get("avg_temp", 25),
                temperature_range=seasonal_data.get("extreme_temps", {}).get("max", 30) - 
                               seasonal_data.get("extreme_temps", {}).get("min", 20),
                annual_rainfall=weather_patterns.get("annual_summary", {}).get("total_annual_rainfall", 1200),
                rainfall_variability=self._calculate_rainfall_variability(weather_patterns),
                humidity_avg=seasonal_data.get("avg_humidity", 70),
                soil_ph=soil_data.ph_level if soil_data else 6.5,
                soil_organic_matter=soil_data.organic_matter if soil_data else 2.5,
                soil_nitrogen=soil_data.nitrogen if soil_data else 25,
                soil_phosphorus=soil_data.phosphorus if soil_data else 20,
                soil_potassium=soil_data.potassium if soil_data else 120,
                soil_texture_score=self._texture_to_score(soil_data.texture if soil_data else "loam"),
                drainage_score=self._drainage_to_score(soil_data.drainage if soil_data else "good"),
                altitude=farm.elevation or 1200,
                climate_risk_score=climate_risks.get("overall_risk", 0.3)
            )
            
        except Exception as e:
            logger.error(f"Error analyzing environmental conditions: {e}")
            # Return default conditions
            return EnvironmentalConditions(
                temperature_avg=25, temperature_range=10, annual_rainfall=1200,
                rainfall_variability=0.3, humidity_avg=70, soil_ph=6.5,
                soil_organic_matter=2.5, soil_nitrogen=25, soil_phosphorus=20,
                soil_potassium=120, soil_texture_score=0.7, drainage_score=0.7,
                altitude=1200, climate_risk_score=0.3
            )
    
    def _analyze_seed_compatibility(self, seed: Seed, env_conditions: EnvironmentalConditions, 
                                  farm: Farm, preferences: Dict = None) -> SeedCompatibility:
        """Analyze compatibility between a seed and environmental conditions"""
        try:
            # Climate compatibility analysis
            climate_score = self._calculate_climate_compatibility(seed, env_conditions)
            
            # Soil compatibility analysis
            soil_score = self._calculate_soil_compatibility(seed, env_conditions)
            
            # Yield prediction
            if self.is_trained:
                yield_prediction = self._predict_yield(seed, env_conditions)
            else:
                yield_prediction = self._estimate_yield_simple(seed, env_conditions)
            
            # Risk assessment
            risk_score = self._calculate_risk_score(seed, env_conditions)
            
            # Market factors (if available in preferences)
            market_score = self._calculate_market_score(seed, preferences)
            
            # Overall compatibility score
            compatibility_score = (
                climate_score * self.feature_weights["climate_compatibility"] +
                soil_score * self.feature_weights["soil_compatibility"] +
                (yield_prediction / (seed.yield_potential or 1)) * self.feature_weights["yield_potential"] +
                (1 - risk_score) * self.feature_weights["risk_tolerance"] +
                market_score * self.feature_weights["market_factors"]
            )
            
            # Generate reasoning
            reasons = self._generate_reasoning(seed, env_conditions, climate_score, soil_score, risk_score)
            
            # Calculate confidence level
            confidence = self._calculate_confidence_level(env_conditions, seed)
            
            return SeedCompatibility(
                seed_id=seed.id,
                compatibility_score=min(1.0, max(0.0, compatibility_score)),
                climate_match_score=climate_score,
                soil_match_score=soil_score,
                yield_prediction=yield_prediction,
                risk_score=risk_score,
                confidence_level=confidence,
                reasons=reasons
            )
            
        except Exception as e:
            logger.error(f"Error analyzing seed compatibility for seed {seed.id}: {e}")
            return SeedCompatibility(
                seed_id=seed.id,
                compatibility_score=0.5,
                climate_match_score=0.5,
                soil_match_score=0.5,
                yield_prediction=seed.yield_potential or 1.0,
                risk_score=0.5,
                confidence_level=0.3,
                reasons=["Analysis error occurred"]
            )
    
    def _calculate_climate_compatibility(self, seed: Seed, env_conditions: EnvironmentalConditions) -> float:
        """Calculate climate compatibility score"""
        try:
            scores = []
            
            # Temperature compatibility
            if seed.optimal_temp_min and seed.optimal_temp_max:
                temp_score = self._score_range_compatibility(
                    env_conditions.temperature_avg,
                    seed.optimal_temp_min,
                    seed.optimal_temp_max
                )
                scores.append(temp_score)
            
            # Rainfall compatibility
            if seed.min_rainfall and seed.max_rainfall:
                rainfall_score = self._score_range_compatibility(
                    env_conditions.annual_rainfall,
                    seed.min_rainfall,
                    seed.max_rainfall
                )
                scores.append(rainfall_score)
            
            # Altitude compatibility
            if seed.altitude_min and seed.altitude_max:
                altitude_score = self._score_range_compatibility(
                    env_conditions.altitude,
                    seed.altitude_min,
                    seed.altitude_max
                )
                scores.append(altitude_score)
            
            # Drought tolerance vs climate risk
            drought_tolerance_score = seed.drought_tolerance * (1 - env_conditions.climate_risk_score)
            scores.append(drought_tolerance_score)
            
            # Flood tolerance (inversely related to drainage)
            flood_risk = max(0, 1 - env_conditions.drainage_score)
            flood_tolerance_score = 1 - abs(seed.flood_tolerance - flood_risk)
            scores.append(flood_tolerance_score)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception as e:
            logger.error(f"Error calculating climate compatibility: {e}")
            return 0.5
    
    def _calculate_soil_compatibility(self, seed: Seed, env_conditions: EnvironmentalConditions) -> float:
        """Calculate soil compatibility score"""
        try:
            scores = []
            
            # pH compatibility
            if seed.preferred_ph_min and seed.preferred_ph_max:
                ph_score = self._score_range_compatibility(
                    env_conditions.soil_ph,
                    seed.preferred_ph_min,
                    seed.preferred_ph_max
                )
                scores.append(ph_score)
            
            # Nutrient requirements vs availability
            nutrient_scores = []
            
            # Nitrogen
            n_requirement = self._requirement_to_score(seed.nitrogen_requirement)
            n_availability = min(1.0, env_conditions.soil_nitrogen / 50)  # Normalize to 0-1
            n_score = 1 - abs(n_requirement - n_availability)
            nutrient_scores.append(n_score)
            
            # Phosphorus
            p_requirement = self._requirement_to_score(seed.phosphorus_requirement)
            p_availability = min(1.0, env_conditions.soil_phosphorus / 40)
            p_score = 1 - abs(p_requirement - p_availability)
            nutrient_scores.append(p_score)
            
            # Potassium
            k_requirement = self._requirement_to_score(seed.potassium_requirement)
            k_availability = min(1.0, env_conditions.soil_potassium / 200)
            k_score = 1 - abs(k_requirement - k_availability)
            nutrient_scores.append(k_score)
            
            scores.extend(nutrient_scores)
            
            # Organic matter compatibility
            om_score = min(1.0, env_conditions.soil_organic_matter / 4.0)  # Higher is better
            scores.append(om_score)
            
            # Texture compatibility (crop-specific)
            texture_score = self._calculate_texture_compatibility(seed.crop_type, env_conditions.soil_texture_score)
            scores.append(texture_score)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception as e:
            logger.error(f"Error calculating soil compatibility: {e}")
            return 0.5
    
    def _calculate_risk_score(self, seed: Seed, env_conditions: EnvironmentalConditions) -> float:
        """Calculate risk score (0 = low risk, 1 = high risk)"""
        try:
            risk_factors = []
            
            # Climate change risk
            climate_risk = env_conditions.climate_risk_score
            
            # Adaptation capacity of seed
            adaptation_score = np.mean([
                seed.drought_tolerance,
                seed.flood_tolerance,
                seed.heat_tolerance,
                seed.cold_tolerance
            ])
            
            # Environmental mismatch risk
            climate_mismatch = 1 - self._calculate_climate_compatibility(seed, env_conditions)
            soil_mismatch = 1 - self._calculate_soil_compatibility(seed, env_conditions)
            
            # Rainfall variability risk
            variability_risk = env_conditions.rainfall_variability
            
            # Combine risk factors
            total_risk = (
                climate_risk * 0.3 +
                (1 - adaptation_score) * 0.25 +
                climate_mismatch * 0.2 +
                soil_mismatch * 0.15 +
                variability_risk * 0.1
            )
            
            return min(1.0, max(0.0, total_risk))
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 0.5
    
    def _predict_yield(self, seed: Seed, env_conditions: EnvironmentalConditions) -> float:
        """Predict yield using trained model"""
        try:
            if not ML_AVAILABLE or not self.is_trained:
                return self._estimate_yield_simple(seed, env_conditions)
            
            # Prepare features
            env_features = self._environmental_conditions_to_features(env_conditions)
            seed_features = self._seed_to_features(seed)
            
            features = np.concatenate([env_features, seed_features]).reshape(1, -1)
            features_scaled = self.scalers["environmental"].transform(features)
            
            predicted_yield = self.models["yield_predictor"].predict(features_scaled)[0]
            
            # Ensure reasonable bounds
            max_yield = seed.yield_potential or 5.0
            return max(0.1, min(predicted_yield, max_yield * 1.2))
            
        except Exception as e:
            logger.error(f"Error predicting yield: {e}")
            return self._estimate_yield_simple(seed, env_conditions)
    
    def _estimate_yield_simple(self, seed: Seed, env_conditions: EnvironmentalConditions) -> float:
        """Simple yield estimation based on compatibility scores"""
        try:
            base_yield = seed.yield_potential or 2.0
            
            climate_factor = self._calculate_climate_compatibility(seed, env_conditions)
            soil_factor = self._calculate_soil_compatibility(seed, env_conditions)
            risk_factor = 1 - self._calculate_risk_score(seed, env_conditions)
            
            yield_factor = (climate_factor * 0.4 + soil_factor * 0.4 + risk_factor * 0.2)
            
            return base_yield * yield_factor
            
        except Exception as e:
            logger.error(f"Error in simple yield estimation: {e}")
            return seed.yield_potential or 2.0
    
    def _calculate_market_score(self, seed: Seed, preferences: Dict = None) -> float:
        """Calculate market compatibility score"""
        try:
            if not preferences:
                return 0.7  # Default neutral score
            
            score = 0.7
            
            # Market demand preference
            market_demand = getattr(seed, 'market_demand', 'medium')
            if preferences.get('market_preference') == 'export' and market_demand == 'high':
                score += 0.2
            elif preferences.get('market_preference') == 'local' and market_demand in ['medium', 'high']:
                score += 0.1
            
            # Budget considerations
            if preferences.get('budget_constraint'):
                # Assume lower cost seeds get higher score if budget is constrained
                # This would need actual cost data
                pass
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating market score: {e}")
            return 0.7
    
    def _generate_reasoning(self, seed: Seed, env_conditions: EnvironmentalConditions, 
                          climate_score: float, soil_score: float, risk_score: float) -> List[str]:
        """Generate human-readable reasoning for recommendation"""
        reasons = []
        
        try:
            # Climate reasoning
            if climate_score > 0.8:
                reasons.append(f"Excellent climate match for {seed.variety_name}")
            elif climate_score > 0.6:
                reasons.append(f"Good climate compatibility for {seed.variety_name}")
            else:
                reasons.append(f"Climate challenges may affect {seed.variety_name} performance")
            
            # Soil reasoning
            if soil_score > 0.8:
                reasons.append("Soil conditions are ideal for this variety")
            elif soil_score > 0.6:
                reasons.append("Soil conditions are suitable with minor adjustments")
            else:
                reasons.append("Soil amendments recommended for optimal performance")
            
            # Risk reasoning
            if risk_score < 0.3:
                reasons.append("Low risk option with stable performance expected")
            elif risk_score < 0.6:
                reasons.append("Moderate risk with good adaptation potential")
            else:
                reasons.append("Higher risk option requiring careful management")
            
            # Specific trait highlights
            if seed.drought_tolerance > 0.7:
                reasons.append("High drought tolerance suitable for dry conditions")
            
            if seed.yield_potential and seed.yield_potential > 5:
                reasons.append("High yield potential variety")
            
            return reasons
            
        except Exception as e:
            logger.error(f"Error generating reasoning: {e}")
            return [f"Analysis completed for {seed.variety_name}"]
    
    # Helper methods
    def _get_seasonal_key(self, season: str) -> str:
        """Convert season to seasonal pattern key"""
        mapping = {
            "A": "wet_season_1",
            "B": "wet_season_2",
            "perennial": "wet_season_1"  # Default for perennials
        }
        return mapping.get(season, "wet_season_1")
    
    def _calculate_rainfall_variability(self, weather_patterns: Dict) -> float:
        """Calculate rainfall variability from weather patterns"""
        try:
            monthly_data = weather_patterns.get("monthly", {})
            if not monthly_data:
                return 0.3  # Default
            
            rainfall_values = [data.get("avg_rainfall", 0) for data in monthly_data.values()]
            if not rainfall_values:
                return 0.3
            
            mean_rainfall = np.mean(rainfall_values)
            std_rainfall = np.std(rainfall_values)
            
            return std_rainfall / mean_rainfall if mean_rainfall > 0 else 0.3
            
        except Exception as e:
            logger.error(f"Error calculating rainfall variability: {e}")
            return 0.3
    
    def _texture_to_score(self, texture: str) -> float:
        """Convert soil texture to numerical score"""
        texture_scores = {
            "clay": 0.4, "sandy_clay": 0.5, "silty_clay": 0.6,
            "sandy_clay_loam": 0.7, "clay_loam": 0.8, "silty_clay_loam": 0.7,
            "sandy_loam": 0.8, "loam": 1.0, "silt_loam": 0.9,
            "silt": 0.6, "loamy_sand": 0.6, "sand": 0.4
        }
        return texture_scores.get(texture, 0.7)
    
    def _drainage_to_score(self, drainage: str) -> float:
        """Convert drainage level to numerical score"""
        drainage_scores = {"poor": 0.3, "fair": 0.6, "good": 0.8, "excellent": 1.0}
        return drainage_scores.get(drainage, 0.7)
    
    def _requirement_to_score(self, requirement: str) -> float:
        """Convert requirement level to numerical score"""
        requirement_scores = {"low": 0.3, "medium": 0.6, "high": 0.9}
        return requirement_scores.get(requirement, 0.6)
    
    def _score_range_compatibility(self, value: float, min_val: float, max_val: float) -> float:
        """Score how well a value fits within an optimal range"""
        if min_val <= value <= max_val:
            return 1.0
        elif value < min_val:
            return max(0.0, 1 - (min_val - value) / min_val)
        else:
            return max(0.0, 1 - (value - max_val) / max_val)
    
    def _calculate_texture_compatibility(self, crop_type: str, texture_score: float) -> float:
        """Calculate texture compatibility for specific crop"""
        # Crop-specific texture preferences
        texture_preferences = {
            "maize": 0.8,      # Prefers loam, clay_loam
            "beans": 0.9,      # Prefers well-drained soils
            "cassava": 0.7,    # Tolerates various textures
            "sweet_potato": 0.9, # Prefers sandy_loam
            "groundnuts": 0.9,   # Prefers sandy_loam
            "rice": 0.3        # Prefers clay (opposite of texture_score)
        }
        
        preference = texture_preferences.get(crop_type, 0.7)
        
        if crop_type == "rice":
            # Rice prefers clay soils (low texture_score)
            return 1 - texture_score
        else:
            # Most crops prefer well-draining soils
            return min(1.0, texture_score * preference)
    
    def _calculate_confidence_level(self, env_conditions: EnvironmentalConditions, seed: Seed) -> float:
        """Calculate confidence level for the recommendation"""
        confidence = 1.0
        
        # Reduce confidence for missing data
        if env_conditions.climate_risk_score == 0.3:  # Default value
            confidence -= 0.1
        
        if not seed.yield_potential:
            confidence -= 0.1
        
        if not seed.optimal_temp_min or not seed.optimal_temp_max:
            confidence -= 0.1
        
        if not self.is_trained:
            confidence -= 0.2
        
        return max(0.3, confidence)
    
    def _extract_environmental_features(self, data) -> Optional[object]:
        """Extract environmental features for model training"""
        # This would be implemented when we have actual training data
        # For now, return dummy features
        return np.random.random((len(data), 15))
    
    def _extract_seed_features(self, data) -> Optional[object]:
        """Extract seed features for model training"""
        # This would be implemented when we have actual training data
        # For now, return dummy features
        return np.random.random((len(data), 10))
    
    def _environmental_conditions_to_features(self, env_conditions: EnvironmentalConditions) -> Optional[object]:
        """Convert environmental conditions to feature array"""
        return np.array([
            env_conditions.temperature_avg,
            env_conditions.temperature_range,
            env_conditions.annual_rainfall,
            env_conditions.rainfall_variability,
            env_conditions.humidity_avg,
            env_conditions.soil_ph,
            env_conditions.soil_organic_matter,
            env_conditions.soil_nitrogen,
            env_conditions.soil_phosphorus,
            env_conditions.soil_potassium,
            env_conditions.soil_texture_score,
            env_conditions.drainage_score,
            env_conditions.altitude,
            env_conditions.climate_risk_score,
            0  # Placeholder for additional features
        ])
    
    def _seed_to_features(self, seed: Seed) -> Optional[object]:
        """Convert seed characteristics to feature array"""
        return np.array([
            seed.maturity_days or 120,
            seed.yield_potential or 2.0,
            seed.drought_tolerance,
            seed.flood_tolerance,
            seed.heat_tolerance,
            seed.cold_tolerance,
            seed.preferred_ph_min or 6.0,
            seed.preferred_ph_max or 7.0,
            seed.min_rainfall or 500,
            seed.max_rainfall or 1200
        ])
    
    def save_models(self, model_path: str = "./models"):
        """Save trained models to disk"""
        try:
            os.makedirs(model_path, exist_ok=True)
            
            for name, model in self.models.items():
                joblib.dump(model, os.path.join(model_path, f"{name}.pkl"))
            
            for name, scaler in self.scalers.items():
                joblib.dump(scaler, os.path.join(model_path, f"{name}_scaler.pkl"))
            
            logger.info(f"Models saved to {model_path}")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def load_models(self, model_path: str = "./models"):
        """Load trained models from disk"""
        try:
            for name in self.models.keys():
                model_file = os.path.join(model_path, f"{name}.pkl")
                if os.path.exists(model_file):
                    self.models[name] = joblib.load(model_file)
            
            for name in self.scalers.keys():
                scaler_file = os.path.join(model_path, f"{name}_scaler.pkl")
                if os.path.exists(scaler_file):
                    self.scalers[name] = joblib.load(scaler_file)
            
            self.is_trained = True
            logger.info(f"Models loaded from {model_path}")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.is_trained = False