# API Reference

## Overview

The Climate-Adaptive Seed AI Bank API provides comprehensive endpoints for managing farms, seeds, recommendations, and analytics. All endpoints return JSON responses and follow RESTful conventions.

**Base URL**: `http://localhost:8000`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Authentication Flow

1. **Register** or **Login** to get access token
2. **Include token** in subsequent requests
3. **Token expires** after configured time (default: 30 minutes)
4. **Refresh** token by logging in again

## Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created successfully  
- `400`: Bad Request (validation error)
- `401`: Unauthorized (missing/invalid token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `422`: Validation Error (invalid input data)
- `500`: Internal Server Error

## Endpoints

### Authentication

#### POST /auth/token
Login and receive access token.

**Request Body:**
```json
{
  "username": "farmer@eclimate.seed.ai.bank.ug",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "farmer@climate.seed.ai.bank.ug",
    "full_name": "Farmer Name",
    "user_type": "farmer",
    "location": "Kampala, Uganda"
  }
}
```

#### POST /auth/register
Create new user account.

**Request Body:**
```json
{
  "email": "newfarmer@climate.seed.ai.bank.ug",
  "password": "securepassword",
  "full_name": "Farmer Name",
  "phone": "+256740639860",
  "location": "Mbale, Uganda",
  "user_type": "farmer"
}
```

**Response:**
```json
{
  "id": 2,
  "email": "newfarmer@climate.seed.ai.bank.ug",
  "full_name": "Farmer Name",
  "user_type": "farmer",
  "location": "Mbale, Uganda",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### GET /auth/users/me
Get current user profile (requires authentication).

**Response:**
```json
{
  "id": 1,
  "email": "farmer@climate.seed.ai.bank.ug",
  "full_name": "Farmer Name",
  "phone": "+256740639860",
  "location": "Kampala, Uganda",
  "user_type": "farmer",
  "created_at": "2024-01-10T08:00:00Z",
  "last_login": "2024-01-15T10:30:00Z"
}
```

### Farm Management

#### GET /farms/
List all farms for the authenticated user.

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum records to return (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "name": "Main Farm",
    "location": "Kampala District",
    "latitude": 0.3476,
    "longitude": 32.5825,
    "size_hectares": 5.0,
    "soil_type": "clay_loam",
    "irrigation": true,
    "created_at": "2024-01-10T08:00:00Z"
  }
]
```

#### POST /farms/
Create a new farm.

**Request Body:**
```json
{
  "name": "East Field Farm",
  "location": "Jinja District",
  "latitude": 0.4297,
  "longitude": 33.2044,
  "size_hectares": 3.5,
  "soil_type": "sandy_loam",
  "irrigation": false,
  "infrastructure": ["storage", "processing"]
}
```

**Response:**
```json
{
  "id": 2,
  "name": "East Field Farm",
  "location": "Jinja District",
  "latitude": 0.4297,
  "longitude": 33.2044,
  "size_hectares": 3.5,
  "soil_type": "sandy_loam",
  "irrigation": false,
  "infrastructure": ["storage", "processing"],
  "user_id": 1,
  "created_at": "2024-01-15T11:00:00Z"
}
```

#### GET /farms/{farm_id}
Get details of a specific farm.

**Path Parameters:**
- `farm_id` (int): Farm identifier

**Response:**
```json
{
  "id": 1,
  "name": "Main Farm",
  "location": "Kampala District",
  "latitude": 0.3476,
  "longitude": 32.5825,
  "size_hectares": 5.0,
  "soil_type": "clay_loam",
  "irrigation": true,
  "infrastructure": ["storage", "greenhouse"],
  "user_id": 1,
  "created_at": "2024-01-10T08:00:00Z",
  "soil_profile": {
    "ph": 6.5,
    "organic_matter": 3.2,
    "nitrogen": 45,
    "phosphorus": 15,
    "potassium": 120
  },
  "climate_records": [
    {
      "date": "2024-01-15",
      "temperature_avg": 24.5,
      "temperature_max": 30.2,
      "temperature_min": 18.8,
      "rainfall": 12.5,
      "humidity": 75.3
    }
  ]
}
```

#### PUT /farms/{farm_id}
Update farm information.

**Request Body:**
```json
{
  "name": "Updated Main Farm",
  "size_hectares": 5.5,
  "irrigation": true,
  "infrastructure": ["storage", "greenhouse", "processing"]
}
```

#### DELETE /farms/{farm_id}
Delete a farm.

**Response:** `204 No Content`

### Seed Catalog

#### GET /seeds/
Browse available seed varieties.

**Query Parameters:**
- `skip` (int): Pagination offset
- `limit` (int): Records per page
- `crop_type` (string): Filter by crop type
- `climate_zone` (string): Filter by climate suitability
- `drought_tolerance` (string): Filter by drought tolerance level

**Response:**
```json
[
  {
    "id": 1,
    "name": "NAROSORG 1",
    "crop_type": "sorghum",
    "variety": "improved",
    "maturity_days": 120,
    "yield_potential": 3500,
    "drought_tolerance": "high",
    "pest_resistance": ["striga", "aphids"],
    "climate_zones": ["semi_arid", "sub_humid"],
    "genetic_profile": {
      "drought_genes": ["DRO1", "HARDY"],
      "yield_genes": ["YLD1", "GS3"],
      "disease_resistance": ["Rpi1", "Sr24"]
    }
  }
]
```

#### GET /seeds/{seed_id}
Get detailed information about a specific seed variety.

**Response:**
```json
{
  "id": 1,
  "name": "NAROSORG 1",
  "crop_type": "sorghum",
  "variety": "improved",
  "maturity_days": 120,
  "yield_potential": 3500,
  "drought_tolerance": "high",
  "pest_resistance": ["striga", "aphids"],
  "climate_zones": ["semi_arid", "sub_humid"],
  "soil_requirements": {
    "ph_min": 5.5,
    "ph_max": 7.5,
    "organic_matter_min": 2.0,
    "drainage": "well_drained"
  },
  "genetic_profile": {
    "drought_genes": ["DRO1", "HARDY"],
    "yield_genes": ["YLD1", "GS3"],
    "disease_resistance": ["Rpi1", "Sr24"]
  },
  "planting_guide": {
    "season": "first_rains",
    "spacing": "30cm x 15cm",
    "seed_rate": "8-10 kg/ha",
    "fertilizer": "50-30-20 NPK"
  }
}
```

#### GET /seeds/search
Search seeds by various criteria.

**Query Parameters:**
- `q` (string): General search query
- `crop_type` (string): Specific crop type
- `drought_tolerance` (string): Drought tolerance level
- `maturity_days_max` (int): Maximum maturity period
- `yield_potential_min` (int): Minimum yield potential

### Recommendations

#### POST /recommendations/
Generate seed recommendations for a farm.

**Request Body:**
```json
{
  "farm_id": 1,
  "season": "first_rains_2024",
  "planting_date": "2024-03-15",
  "target_yield": 3000,
  "risk_tolerance": "moderate",
  "budget_per_hectare": 500000
}
```

**Response:**
```json
{
  "farm_id": 1,
  "recommendations": [
    {
      "seed": {
        "id": 1,
        "name": "NAROSORG 1",
        "crop_type": "sorghum"
      },
      "compatibility_score": 0.92,
      "predicted_yield": 3200,
      "risk_level": "low",
      "reasoning": [
        "Excellent drought tolerance matches your farm's climate",
        "High compatibility with clay loam soil",
        "Good resistance to local pest pressures"
      ],
      "planting_recommendations": {
        "optimal_planting_date": "2024-03-20",
        "seed_quantity": "40kg",
        "estimated_cost": 320000,
        "fertilizer_recommendation": "50-30-20 NPK at 150kg/ha"
      }
    }
  ],
  "climate_analysis": {
    "seasonal_forecast": {
      "rainfall_prediction": "above_normal",
      "temperature_trend": "slightly_warmer",
      "drought_risk": "low"
    }
  },
  "generated_at": "2024-01-15T12:00:00Z"
}
```

#### GET /recommendations/farm/{farm_id}
Get existing recommendations for a farm.

**Query Parameters:**
- `season` (string): Filter by season
- `limit` (int): Number of recommendations to return

#### POST /recommendations/adaptation/
Get climate adaptation guidance.

**Request Body:**
```json
{
  "farm_id": 1,
  "climate_scenario": "drought_2024",
  "adaptation_type": "immediate"
}
```

**Response:**
```json
{
  "farm_id": 1,
  "scenario": "drought_2024",
  "adaptations": [
    {
      "category": "seed_selection",
      "priority": "high",
      "action": "Switch to drought-tolerant varieties",
      "specific_recommendations": [
        "Replace maize with drought-tolerant sorghum",
        "Consider early-maturing bean varieties"
      ],
      "timeline": "immediate",
      "cost_estimate": 150000
    },
    {
      "category": "water_management",
      "priority": "high", 
      "action": "Implement water conservation",
      "specific_recommendations": [
        "Install drip irrigation system",
        "Practice mulching to retain soil moisture",
        "Construct water harvesting structures"
      ],
      "timeline": "2-4 weeks",
      "cost_estimate": 800000
    }
  ]
}
```

### Analytics

#### GET /analytics/dashboard
Get dashboard statistics for the authenticated user.

**Response:**
```json
{
  "user_stats": {
    "total_farms": 3,
    "total_area": 12.5,
    "active_recommendations": 8,
    "yield_improvement": 15.3
  },
  "recent_activity": [
    {
      "type": "recommendation_generated",
      "farm_name": "Main Farm",
      "timestamp": "2024-01-15T12:00:00Z"
    }
  ],
  "alerts": [
    {
      "type": "climate_warning",
      "severity": "medium",
      "message": "Drought conditions expected in 2 weeks",
      "farm_id": 1
    }
  ]
}
```

#### GET /analytics/yield-trends
Get yield trend analysis.

**Query Parameters:**
- `farm_id` (int): Specific farm (optional)
- `period` (string): Time period (month, season, year)
- `crop_type` (string): Filter by crop type

**Response:**
```json
{
  "trends": [
    {
      "period": "2023_first_rains",
      "average_yield": 2800,
      "farms_count": 3,
      "improvement": 12.5
    },
    {
      "period": "2023_second_rains", 
      "average_yield": 3100,
      "farms_count": 3,
      "improvement": 18.2
    }
  ],
  "projections": [
    {
      "period": "2024_first_rains",
      "predicted_yield": 3300,
      "confidence": 0.85
    }
  ]
}
```

#### GET /analytics/seed-performance
Get seed variety performance metrics.

**Response:**
```json
{
  "performance_by_seed": [
    {
      "seed_name": "NAROSORG 1",
      "crop_type": "sorghum",
      "adoption_rate": 0.75,
      "average_yield": 3200,
      "success_rate": 0.92,
      "farms_using": 15
    }
  ],
  "regional_performance": [
    {
      "region": "Central Uganda",
      "top_performing_seeds": [
        {
          "name": "NAROSORG 1",
          "yield": 3400
        }
      ]
    }
  ]
}
```

## Data Models

### User
```json
{
  "id": "integer",
  "email": "string (email format)",
  "full_name": "string",
  "phone": "string (optional)",
  "location": "string",
  "user_type": "farmer | admin | policy_maker",
  "created_at": "datetime",
  "last_login": "datetime (optional)"
}
```

### Farm
```json
{
  "id": "integer",
  "name": "string",
  "location": "string", 
  "latitude": "float",
  "longitude": "float",
  "size_hectares": "float",
  "soil_type": "clay | sand | loam | clay_loam | sandy_loam | silt_loam",
  "irrigation": "boolean",
  "infrastructure": "array of strings",
  "user_id": "integer",
  "created_at": "datetime"
}
```

### Seed
```json
{
  "id": "integer",
  "name": "string",
  "crop_type": "string",
  "variety": "traditional | improved | hybrid",
  "maturity_days": "integer",
  "yield_potential": "integer (kg/ha)",
  "drought_tolerance": "low | medium | high",
  "pest_resistance": "array of strings",
  "climate_zones": "array of strings",
  "genetic_profile": "object",
  "soil_requirements": "object",
  "planting_guide": "object"
}
```

### Recommendation
```json
{
  "id": "integer",
  "farm_id": "integer",
  "seed_id": "integer",
  "compatibility_score": "float (0-1)",
  "predicted_yield": "integer",
  "risk_level": "low | medium | high",
  "reasoning": "array of strings",
  "planting_recommendations": "object",
  "season": "string",
  "generated_at": "datetime"
}
```

## Rate Limits

- **Authentication endpoints**: 5 requests per minute
- **General API endpoints**: 100 requests per minute  
- **Recommendation generation**: 10 requests per minute
- **Analytics endpoints**: 50 requests per minute

## Webhooks (Future Feature)

Planned webhook events:
- `recommendation.generated`
- `climate.alert`
- `farm.updated`
- `yield.recorded`

## SDKs and Libraries

### Python SDK (Planned)
```python
from climate_seed_api import ClimateAPI

api = ClimateAPI(api_key="your-api-key")
farms = api.farms.list()
recommendations = api.recommendations.generate(farm_id=1)
```

### JavaScript SDK (Planned)
```javascript
import { ClimateAPI } from 'climate-seed-api-js';

const api = new ClimateAPI('your-api-key');
const farms = await api.farms.list();
const recommendations = await api.recommendations.generate(1);
```

## Changelog

### Version 1.0.0 (Current)
- Initial release with core functionality
- Authentication and user management
- Farm and seed management
- AI-powered recommendations
- Basic analytics dashboard

### Planned Features (v1.1.0)
- Policy maker analytics dashboard
- Advanced climate projections
- Market price integration
- Mobile app API support
- Webhook notifications

---

*Complete API documentation for the Climate-Adaptive Seed AI Bank platform.*