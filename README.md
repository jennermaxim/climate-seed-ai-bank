# Climate-Adaptive Seed AI Bank

## Overview

The Climate-Adaptive Seed AI Bank is a comprehensive digital platform designed to revolutionize agriculture in Uganda by providing AI-powered seed recommendations based on climate resilience, soil conditions, and environmental projections. This platform serves farmers, agricultural advisors, and policymakers with data-driven insights for climate-adaptive agriculture.

## Key Features

### For Farmers
- **Smart Seed Recommendations**: AI-powered suggestions based on your farm's location, soil conditions, and climate projections
- **Real-time Climate Data**: Access to current and projected weather patterns
- **Yield Predictions**: Expected yield estimates for different seed varieties
- **Risk Assessment**: Comprehensive analysis of climate and agricultural risks
- **Farm Management**: Track multiple farms, crop cycles, and performance metrics
- **Adaptation Guidance**: Step-by-step recommendations for climate resilience

### For Policymakers
- **National Agricultural Intelligence**: Aggregated data insights across regions
- **Food Security Analytics**: Monitoring and prediction of food production trends
- **Climate Impact Assessment**: Understanding climate change effects on agriculture
- **Regional Performance Comparison**: Identify high and low-performing areas
- **Policy Effectiveness Tracking**: Measure impact of agricultural policies

### For Agricultural Advisors
- **Multi-farm Overview**: Manage recommendations for multiple clients
- **Historical Performance Analysis**: Track success rates of previous recommendations
- **Seasonal Planning Tools**: Optimize planting schedules and crop rotations
- **Market Intelligence**: Price trends and market demand insights

## System Architecture

### Backend (FastAPI + Python)
```
backend/
├── main.py                 # Application entry point
├── models/
│   ├── __init__.py        # Database configuration
│   ├── database_models.py # SQLAlchemy ORM models
│   └── pydantic_models.py # API request/response schemas
├── services/
│   ├── climate_service.py      # Weather and climate data processing
│   ├── soil_service.py         # Soil analysis and assessment
│   └── recommendation_engine.py # AI recommendation system
├── api/
│   ├── auth.py            # Authentication endpoints
│   ├── farms.py           # Farm management API
│   ├── seeds.py           # Seed catalog API
│   ├── recommendations.py # Recommendation API
│   └── analytics.py       # Dashboard and analytics API
└── data/
    └── seeds.json         # Sample seed database
```

### Frontend (React + TypeScript)
```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.tsx          # Navigation header
│   │   ├── Sidebar.tsx         # Navigation sidebar
│   │   ├── Layout.tsx          # Main layout wrapper
│   │   ├── FarmerDashboard.tsx # Farmer dashboard
│   │   ├── LoginPage.tsx       # Authentication page
│   │   └── PrivateRoute.tsx    # Route protection
│   ├── contexts/
│   │   └── AuthContext.tsx     # Authentication state management
│   ├── services/
│   │   └── api.ts              # API client functions
│   ├── types/
│   │   └── api.ts              # TypeScript type definitions
│   └── App.tsx                 # Main application component
└── public/                     # Static assets
```

## Quick Start

### Prerequisites
- Python 3.8+ (Backend)
- Node.js 14+ and npm (Frontend)
- Virtual environment tool (recommended)

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/jennermaxim/climate-seed-ai-bank.git
cd climate-seed-ai-bank/backend
```

2. **Create and activate virtual environment**
```bash
python -m venv .venv
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 python-multipart==0.0.6 \
    python-jose[cryptography]==3.3.0 passlib[bcrypt]==1.7.4 sqlalchemy==2.0.23 \
    databases==0.8.0 requests==2.31.0 python-dotenv==1.0.0
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env file with your API keys and settings
```

5. **Run the backend server**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000 with interactive documentation at http://localhost:8000/docs

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd ../frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment**
```bash
echo "REACT_APP_API_URL=http://localhost:8000" > .env
```

4. **Start development server**
```bash
npm start
```

The frontend will be available at http://localhost:3000

## Configuration

### Backend Environment Variables (.env)
```env
# Database
DATABASE_URL=sqlite:///./climate_seed_bank.db

# JWT Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs
OPENWEATHER_API_KEY=your-openweather-api-key
NASA_POWER_API_KEY=your-nasa-power-api-key
SOILGRIDS_API_KEY=your-soilgrids-api-key

# Application Settings
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend Environment Variables (.env)
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_MAP_DEFAULT_LAT=0.3476
REACT_APP_MAP_DEFAULT_LNG=32.5825
REACT_APP_MAP_DEFAULT_ZOOM=7
```

## Database Models

### Core Entities

#### User
- Authentication and profile information
- User types: farmer, admin, policy_maker
- Location and contact details

#### Farm
- Geographic location and size
- Soil characteristics and infrastructure
- Ownership and operational details

#### Seed
- Variety information and genetic profiles
- Climate and soil requirements
- Yield potential and resistance traits

#### Recommendation
- AI-generated seed suggestions
- Compatibility scores and reasoning
- Risk assessments and yield predictions

#### Climate Records
- Historical and current weather data
- Climate projections and trends
- Seasonal patterns and variability

## AI Recommendation Engine

The system uses machine learning models for intelligent seed recommendations:

### Features Used
- **Environmental**: Temperature, precipitation, humidity, soil conditions
- **Genetic**: Seed traits, disease resistance, drought tolerance
- **Historical**: Past performance data, yield records, success rates

### Models
- **Random Forest**: Climate-soil compatibility scoring
- **Gradient Boosting**: Yield prediction and risk assessment
- **Ensemble Methods**: Combined recommendation scoring

### Recommendation Process
1. **Environmental Analysis**: Current and projected conditions
2. **Seed Matching**: Compatibility with farm conditions
3. **Risk Assessment**: Climate and market risk evaluation
4. **Yield Prediction**: Expected performance estimates
5. **Ranking**: Final recommendation scores and reasoning

## External API Integrations

### OpenWeather API
- Current weather conditions
- 5-day weather forecasts
- Historical weather data

### NASA POWER API  
- Solar radiation data
- Long-term climate records
- Agro-meteorological parameters

### SoilGrids API
- Global soil property data
- Soil texture and nutrient information
- Terrain and elevation data

### Google Earth Engine (Planned)
- Satellite imagery analysis
- Vegetation indices (NDVI, EVI)
- Land use classification

## User Interface

### Dashboard Features
- **Key Metrics Cards**: Farm count, yield improvements, alerts
- **Interactive Charts**: Yield trends, performance analytics
- **Map Visualization**: Farm locations and regional data
- **Alert System**: Climate warnings and recommendations

### Navigation Structure
```
Dashboard
├── My Farms (Farmers)
├── Seed Catalog
├── Recommendations
├── Climate Data
├── Analytics (Admin/Policy)
└── Settings
```

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt encryption for user passwords
- **CORS Protection**: Configured cross-origin resource sharing
- **Input Validation**: Pydantic model validation
- **Role-based Access**: Different permissions for user types

## Analytics and Reporting

### Farmer Analytics
- Personal farm performance metrics
- Recommendation success rates
- Yield trend analysis
- Climate impact assessments

### Administrative Analytics
- System-wide usage statistics
- Regional performance comparisons
- Seed adoption rates
- Climate trend analysis

### Policy Analytics
- National food security indicators
- Regional agricultural productivity
- Climate adaptation effectiveness
- Market trend analysis

## Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Testing  
```bash
cd frontend
npm test
```

### API Testing
Use the interactive API documentation at http://localhost:8000/docs for manual testing.

## Deployment

### Backend Deployment

#### Using Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Using Cloud Services
- **Heroku**: Deploy with Procfile
- **AWS Lambda**: Use Mangum for serverless deployment
- **Google Cloud Run**: Container-based deployment

### Frontend Deployment

#### Build Production Version
```bash
npm run build
```

#### Deploy to Netlify/Vercel
```bash
# Build and deploy automatically via git integration
```

## Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Standards
- **Python**: Follow PEP 8 style guide
- **TypeScript**: Use ESLint and Prettier
- **Git**: Conventional commit messages
- **Documentation**: Update README for new features

## API Documentation

### Authentication Endpoints
```
POST /auth/token        # Login and get access token
POST /auth/register     # Create new user account
GET  /auth/users/me     # Get current user profile
```

### Farm Management
```
GET    /farms/          # List user's farms
POST   /farms/          # Create new farm
GET    /farms/{id}      # Get farm details
PUT    /farms/{id}      # Update farm information
DELETE /farms/{id}      # Delete farm
```

### Seed Catalog
```
GET /seeds/             # Browse seed varieties
GET /seeds/{id}         # Get seed details
GET /seeds/search       # Search seeds by criteria
```

### Recommendations
```
POST /recommendations/              # Generate recommendations
GET  /recommendations/farm/{id}     # Get farm recommendations
GET  /recommendations/adaptation/   # Get adaptation guidance
```

### Analytics
```
GET /analytics/dashboard        # Dashboard statistics
GET /analytics/yield-trends     # Yield trend analysis
GET /analytics/seed-performance # Seed performance metrics
```

## Troubleshooting

### Common Issues

#### Backend Won't Start
- Check Python version (3.8+)
- Verify all dependencies are installed
- Ensure database is accessible
- Check environment variables

#### Frontend Build Fails
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version (14+)

#### API Requests Fail
- Verify backend is running on correct port
- Check CORS configuration
- Validate API URL in frontend .env
- Confirm authentication tokens

#### Database Errors
- Check database connection string
- Verify database permissions
- Run database migrations
- Check for schema changes

---

*Building climate-resilient agriculture, one seed recommendation at a time.* 
