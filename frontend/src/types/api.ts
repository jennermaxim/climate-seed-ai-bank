// API Types and Interfaces

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  is_active: boolean;
  user_type: 'farmer' | 'admin' | 'policy_maker';
  created_at: string;
}

export interface Farm {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  size_hectares: number;
  soil_type: string;
  current_crops: string[];
  established_date: string;
  owner_id: number;
  created_at: string;
}

export interface Seed {
  id: number;
  name: string;
  variety: string;
  crop_type: string;
  description?: string;
  genetic_profile: Record<string, any>;
  optimal_conditions: Record<string, any>;
  disease_resistance: string[];
  maturity_days: number;
  yield_potential_kg_ha: number;
  drought_tolerance: 'low' | 'medium' | 'high';
  heat_tolerance: 'low' | 'medium' | 'high';
  pest_resistance: 'low' | 'medium' | 'high';
  created_at: string;
}

export interface SeedRecommendation {
  id: number;
  seed: Seed;
  compatibility_score: number;
  predicted_yield: number;
  confidence_level: number;
  reasoning: string;
  environmental_factors: Record<string, any>;
  risk_assessment: Record<string, any>;
  created_at: string;
}

export interface ClimateData {
  temperature: number;
  humidity: number;
  precipitation: number;
  wind_speed: number;
  pressure: number;
  date: string;
}

export interface SoilProfile {
  ph: number;
  organic_matter: number;
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  texture: 'clay' | 'silt' | 'sand' | 'loam';
  drainage: 'poor' | 'moderate' | 'good' | 'excellent';
}

export interface DashboardStats {
  total_farms: number;
  total_recommendations: number;
  active_crop_cycles: number;
  avg_yield_improvement: number;
  climate_alerts: number;
  top_performing_seeds: Array<{
    seed_name: string;
    avg_yield: number;
    adoption_rate: number;
  }>;
  regional_performance: Array<{
    region: string;
    yield_improvement: number;
    adoption_rate: number;
  }>;
  recent_alerts: Array<{
    type: string;
    message: string;
    severity: 'low' | 'medium' | 'high';
    date: string;
  }>;
}

export interface YieldTrend {
  period: string;
  actual_yield: number;
  predicted_yield: number;
  improvement_percentage: number;
}

export interface SeedPerformance {
  seed_id: number;
  seed_name: string;
  total_adoptions: number;
  avg_yield: number;
  success_rate: number;
  consistency_score: number;
  climate_adaptability: Record<string, any>;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface CreateUserRequest {
  username: string;
  email: string;
  full_name: string;
  password: string;
  user_type?: 'farmer' | 'admin' | 'policy_maker';
}

export interface CreateFarmRequest {
  name: string;
  latitude: number;
  longitude: number;
  size_hectares: number;
  soil_type: string;
  current_crops?: string[];
}

export interface RecommendationRequest {
  farm_id: number;
  crop_type?: string;
  season?: string;
  budget_range?: string;
  risk_tolerance?: 'low' | 'medium' | 'high';
  climate_projection_years?: number;
}

export interface AdaptationGuidance {
  immediate_actions: string[];
  seasonal_recommendations: Record<string, string[]>;
  long_term_strategies: string[];
  risk_mitigation: string[];
  resource_requirements: Record<string, any>;
  expected_outcomes: Record<string, any>;
}