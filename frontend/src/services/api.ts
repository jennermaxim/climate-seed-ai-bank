import axios, { AxiosResponse } from 'axios';
import {
  User,
  Farm,
  Seed,
  SeedRecommendation,
  DashboardStats,
  YieldTrend,
  SeedPerformance,
  LoginRequest,
  LoginResponse,
  CreateUserRequest,
  CreateFarmRequest,
  RecommendationRequest,
  AdaptationGuidance,
  ClimateData,
  SoilProfile
} from '../types/api';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response: AxiosResponse<LoginResponse> = await apiClient.post('/api/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  register: async (userData: CreateUserRequest): Promise<User> => {
    const response: AxiosResponse<User> = await apiClient.post('/api/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response: AxiosResponse<User> = await apiClient.get('/api/auth/me');
    return response.data;
  },
};

// Farms API
export const farmsAPI = {
  getFarms: async (): Promise<Farm[]> => {
    const response: AxiosResponse<Farm[]> = await apiClient.get('/api/farms/');
    return response.data;
  },

  getFarm: async (farmId: number): Promise<Farm> => {
    const response: AxiosResponse<Farm> = await apiClient.get(`/api/farms/${farmId}`);
    return response.data;
  },

  createFarm: async (farmData: CreateFarmRequest): Promise<Farm> => {
    const response: AxiosResponse<Farm> = await apiClient.post('/api/farms/', farmData);
    return response.data;
  },

  updateFarm: async (farmId: number, farmData: Partial<CreateFarmRequest>): Promise<Farm> => {
    const response: AxiosResponse<Farm> = await apiClient.put(`/api/farms/${farmId}`, farmData);
    return response.data;
  },

  deleteFarm: async (farmId: number): Promise<void> => {
    await apiClient.delete(`/api/farms/${farmId}`);
  },

  getFarmClimateData: async (farmId: number, days?: number): Promise<ClimateData[]> => {
    const response: AxiosResponse<ClimateData[]> = await apiClient.get(
      `/api/farms/${farmId}/climate${days ? `?days=${days}` : ''}`
    );
    return response.data;
  },

  getFarmSoilProfile: async (farmId: number): Promise<SoilProfile> => {
    const response: AxiosResponse<SoilProfile> = await apiClient.get(`/api/farms/${farmId}/soil`);
    return response.data;
  },
};

// Seeds API
export const seedsAPI = {
  getSeeds: async (cropType?: string): Promise<Seed[]> => {
    const response: AxiosResponse<Seed[]> = await apiClient.get(
      `/api/seeds/${cropType ? `?crop_type=${cropType}` : ''}`
    );
    return response.data;
  },

  getSeed: async (seedId: number): Promise<Seed> => {
    const response: AxiosResponse<Seed> = await apiClient.get(`/api/seeds/${seedId}`);
    return response.data;
  },

  searchSeeds: async (query: string, filters?: Record<string, any>): Promise<Seed[]> => {
    const params = new URLSearchParams({ q: query });
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value.toString());
      });
    }
    const response: AxiosResponse<Seed[]> = await apiClient.get(`/api/seeds/search?${params}`);
    return response.data;
  },
};

// Recommendations API
export const recommendationsAPI = {
  getRecommendations: async (request: RecommendationRequest): Promise<SeedRecommendation[]> => {
    const response: AxiosResponse<SeedRecommendation[]> = await apiClient.post(
      '/api/recommendations/',
      request
    );
    return response.data;
  },

  getFarmRecommendations: async (farmId: number): Promise<SeedRecommendation[]> => {
    const response: AxiosResponse<SeedRecommendation[]> = await apiClient.get(
      `/api/recommendations/farm/${farmId}`
    );
    return response.data;
  },

  getAdaptationGuidance: async (farmId: number, seedId?: number): Promise<AdaptationGuidance> => {
    const response: AxiosResponse<AdaptationGuidance> = await apiClient.get(
      `/api/recommendations/adaptation/${farmId}${seedId ? `?seed_id=${seedId}` : ''}`
    );
    return response.data;
  },

  getQuickRecommendation: async (latitude: number, longitude: number, cropType?: string): Promise<SeedRecommendation[]> => {
    const params = new URLSearchParams({
      latitude: latitude.toString(),
      longitude: longitude.toString(),
    });
    if (cropType) params.append('crop_type', cropType);
    
    const response: AxiosResponse<SeedRecommendation[]> = await apiClient.get(
      `/api/recommendations/quick?${params}`
    );
    return response.data;
  },
};

// Analytics API
export const analyticsAPI = {
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response: AxiosResponse<DashboardStats> = await apiClient.get('/api/analytics/dashboard');
    return response.data;
  },

  getYieldTrends: async (
    farmId?: number,
    period?: 'monthly' | 'quarterly' | 'yearly'
  ): Promise<YieldTrend[]> => {
    const params = new URLSearchParams();
    if (farmId) params.append('farm_id', farmId.toString());
    if (period) params.append('period', period);

    const response: AxiosResponse<{trends: YieldTrend[], summary: any}> = await apiClient.get(
      `/api/analytics/yield-trends?${params}`
    );
    return response.data.trends; // Extract the trends array from the response
  },

  getSeedPerformance: async (
    limit?: number,
    cropType?: string
  ): Promise<SeedPerformance[]> => {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());
    if (cropType) params.append('crop_type', cropType);

    const response: AxiosResponse<SeedPerformance[]> = await apiClient.get(
      `/api/analytics/seed-performance?${params}`
    );
    return response.data;
  },

  getPolicyDashboard: async (region?: string): Promise<any> => {
    const params = region ? `?region=${region}` : '';
    const response = await apiClient.get(`/api/analytics/policy-dashboard${params}`);
    return response.data;
  },
};

// Helper functions
export const setAuthToken = (token: string) => {
  localStorage.setItem('access_token', token);
};

export const clearAuthToken = () => {
  localStorage.removeItem('access_token');
};

export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('access_token');
};