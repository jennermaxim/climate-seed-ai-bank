import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Paper,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { DashboardStats, YieldTrend } from '../types/api';
import { analyticsAPI } from '../services/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

const mapSeverity = (severity: 'low' | 'medium' | 'high'): 'info' | 'warning' | 'error' => {
  switch (severity) {
    case 'low': return 'info';
    case 'medium': return 'warning';
    case 'high': return 'error';
    default: return 'info';
  }
};

const FarmerDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [yieldTrends, setYieldTrends] = useState<YieldTrend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const [dashboardStats, trends] = await Promise.all([
          analyticsAPI.getDashboardStats(),
          analyticsAPI.getYieldTrends(undefined, 'monthly'),
        ]);

        setStats(dashboardStats);
        setYieldTrends(trends);
        setError(null);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load dashboard data');
        console.error('Dashboard error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!stats) {
    return (
      <Alert severity="info">No dashboard data available</Alert>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Farmer Dashboard
      </Typography>

      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Farms
              </Typography>
              <Typography variant="h4" component="div">
                {stats.total_farms}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Crop Cycles
              </Typography>
              <Typography variant="h4" component="div">
                {stats.active_crop_cycles}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg Yield Improvement
              </Typography>
              <Typography variant="h4" component="div" color="success.main">
                +{stats.avg_yield_improvement}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Climate Alerts
              </Typography>
              <Typography 
                variant="h4" 
                component="div"
                color={stats.climate_alerts > 0 ? 'warning.main' : 'success.main'}
              >
                {stats.climate_alerts}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Yield Trends Chart */}
        <Grid size={{ xs: 12, lg: 8 }}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Yield Trends
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={yieldTrends || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="period" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="actual_yield" 
                  stroke="#8884d8" 
                  name="Actual Yield"
                />
                <Line 
                  type="monotone" 
                  dataKey="predicted_yield" 
                  stroke="#82ca9d" 
                  name="Predicted Yield"
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Recent Alerts */}
        <Grid size={{ xs: 12, lg: 4 }}>
          <Paper sx={{ p: 2, height: 350 }}>
            <Typography variant="h6" gutterBottom>
              Recent Alerts
            </Typography>
            <Box sx={{ maxHeight: 280, overflow: 'auto' }}>
              {stats.recent_alerts.length > 0 ? (
                stats.recent_alerts.map((alert, index) => (
                  <Alert 
                    key={index} 
                    severity={mapSeverity(alert.severity)}
                    sx={{ mb: 1, fontSize: '0.875rem' }}
                  >
                    <Typography variant="body2">
                      {alert.message}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {new Date(alert.date).toLocaleDateString()}
                    </Typography>
                  </Alert>
                ))
              ) : (
                <Typography color="text.secondary">
                  No recent alerts
                </Typography>
              )}
            </Box>
          </Paper>
        </Grid>

        {/* Top Performing Seeds */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Top Performing Seeds
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.top_performing_seeds || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="seed_name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="avg_yield" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Regional Performance */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Regional Performance
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={stats.regional_performance || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.region}: ${entry.yield_improvement}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="yield_improvement"
                >
                  {(stats.regional_performance || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default FarmerDashboard;