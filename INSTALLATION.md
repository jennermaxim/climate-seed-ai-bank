# Installation Guide

## System Requirements

### Hardware Requirements
- **Minimum**: 4GB RAM, 20GB disk space, 1 CPU core
- **Recommended**: 8GB RAM, 50GB disk space, 2+ CPU cores
- **For production**: 16GB RAM, 100GB disk space, 4+ CPU cores

### Software Requirements
- **Python**: 3.8 or higher
- **Node.js**: 14.0 or higher  
- **npm**: 6.0 or higher
- **Git**: Latest version
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18+)

## Step-by-Step Installation

### 1. System Preparation

#### On Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm git curl
```

#### On macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required packages
brew install python nodejs npm git
```

#### On Windows
1. Download and install [Python 3.8+](https://python.org/downloads/)
2. Download and install [Node.js 14+](https://nodejs.org/download/)
3. Download and install [Git](https://git-scm.com/download/win)

### 2. Clone the Repository
```bash
git clone https://github.com/jennermaxim/climate-seed-ai-bank.git
cd climate-seed-ai-bank
```

### 3. Backend Setup

#### Create Virtual Environment
```bash
cd backend

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

#### Install Python Dependencies
```bash
# Core dependencies
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install python-multipart==0.0.6
pip install python-jose[cryptography]==3.3.0
pip install passlib[bcrypt]==1.7.4
pip install sqlalchemy==2.0.23
pip install databases==0.8.0
pip install requests==2.31.0
pip install python-dotenv==1.0.0

# Optional ML dependencies (for advanced features)
pip install scikit-learn==1.3.2
pip install pandas==2.1.3
pip install numpy==1.25.2
pip install tensorflow==2.14.0
```

Or install all at once:
```bash
pip install -r requirements.txt
```

#### Configure Environment Variables
```bash
# Copy example environment file
cp .env.example .env

# Edit the .env file with your settings
nano .env
```

Required environment variables:
```env
# Database Configuration
DATABASE_URL=sqlite:///./climate_seed_bank.db

# Security Settings
SECRET_KEY=your-super-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External API Keys (optional but recommended)
OPENWEATHER_API_KEY=your-openweather-api-key
NASA_POWER_API_KEY=your-nasa-power-api-key
SOILGRIDS_API_KEY=your-soilgrids-api-key

# Application Settings
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Database Configuration (for PostgreSQL in production)
# DATABASE_URL=postgresql://username:password@localhost:5432/climate_seed_bank
```

#### Initialize Database
```bash
# The database will be created automatically when you first run the application
python -c "from models import init_db; init_db()"
```

### 4. Frontend Setup

#### Navigate to Frontend Directory
```bash
cd ../frontend
```

#### Install Node.js Dependencies
```bash
# Install all dependencies
npm install

# If you encounter permission issues on Linux/macOS:
sudo npm install -g npm@latest
npm install
```

#### Configure Frontend Environment
```bash
# Create environment file
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# For production, update with your actual backend URL
# echo "REACT_APP_API_URL=https://your-backend-domain.com" > .env
```

### 5. Start the Application

#### Start Backend Server
```bash
cd backend

# Ensure virtual environment is activated
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at:
- **Main API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

#### Start Frontend Development Server
```bash
# In a new terminal window
cd frontend

# Start React development server
npm start
```

The frontend will be available at:
- **Application**: http://localhost:3000

## Verification Steps

### 1. Test Backend
```bash
# Test the health endpoint
curl http://localhost:8000/

# Should return: {"message": "Climate-Adaptive Seed AI Bank API"}
```

### 2. Test Frontend
Open your browser and navigate to http://localhost:3000. You should see the login page.

### 3. Create Test Account
1. Go to http://localhost:3000
2. Click "Sign Up" or use the registration endpoint
3. Create a test account
4. Login and explore the dashboard

### 4. Test API Endpoints
Visit http://localhost:8000/docs to interact with the API documentation.

## Production Deployment

### Backend Production Setup

#### 1. Use PostgreSQL Database
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib  # Ubuntu
brew install postgresql  # macOS

# Create database and user
sudo -u postgres createdb climate_seed_bank
sudo -u postgres createuser climate_user

# Update .env file
DATABASE_URL=postgresql://climate_user:password@localhost:5432/climate_seed_bank
```

#### 2. Production Dependencies
```bash
pip install gunicorn
pip install psycopg2-binary  # For PostgreSQL
```

#### 3. Production Environment
```env
DEBUG=false
SECRET_KEY=your-very-secure-production-key
CORS_ORIGINS=https://yourdomain.com
DATABASE_URL=postgresql://user:pass@localhost:5432/climate_seed_bank
```

#### 4. Run with Gunicorn
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Production Setup

#### 1. Build Production Version
```bash
cd frontend
npm run build
```

#### 2. Serve with Web Server
```bash
# Using serve package
npm install -g serve
serve -s build -l 3000

# Or copy build/ contents to your web server
cp -r build/* /var/www/html/
```

## Docker Deployment

### Backend Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile
```dockerfile
FROM node:16-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Build application
RUN npm run build

# Use nginx to serve
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
```

### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/climate_seed_bank
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=climate_seed_bank
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Troubleshooting

### Common Installation Issues

#### Python Virtual Environment Issues
```bash
# If python3 -m venv doesn't work
sudo apt install python3-venv  # Ubuntu
brew install python  # macOS

# Alternative: use virtualenv
pip install virtualenv
virtualenv .venv
```

#### Node.js Permission Issues
```bash
# Fix npm permissions on Linux/macOS
sudo chown -R $(whoami) ~/.npm
sudo chown -R $(whoami) /usr/local/lib/node_modules
```

#### Database Connection Issues
```bash
# For SQLite permissions
chmod 666 climate_seed_bank.db
chmod 775 .

# For PostgreSQL connection issues
sudo systemctl start postgresql  # Linux
brew services start postgresql  # macOS
```

#### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
netstat -tulpn | grep 8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn main:app --port 8001
```

#### CORS Issues
Ensure your `.env` file includes:
```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Getting Help

If you encounter issues:

1. **Check the logs** for error messages
2. **Verify all dependencies** are installed correctly
3. **Ensure all services are running** (database, backend, frontend)
4. **Check firewall settings** if accessing from other machines
5. **Review environment variables** for typos or missing values

For additional support:
- Check the GitHub Issues page
- Review the troubleshooting section in README.md
- Contact the development team

## Performance Optimization

### Backend Optimization
```bash
# Use production WSGI server
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Enable database connection pooling
pip install asyncpg  # For PostgreSQL async
```

### Frontend Optimization
```bash
# Analyze bundle size
npm run build
npx webpack-bundle-analyzer build/static/js/*.js

# Enable gzip compression in nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

### Database Optimization
```sql
-- Create indexes for frequently queried fields
CREATE INDEX idx_farms_user_id ON farms(user_id);
CREATE INDEX idx_seeds_climate_zone ON seeds(climate_zone);
CREATE INDEX idx_recommendations_farm_id ON seed_recommendations(farm_id);
```

---

*Installation complete! Your Climate-Adaptive Seed AI Bank is ready to help build climate-resilient agriculture.*