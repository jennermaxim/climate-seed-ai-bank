import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area
} from 'recharts';
import { TrendingUp, TrendingDown, Warning, CheckCircle } from '@mui/icons-material';
import { analyticsAPI } from '../services/api';

interface PolicyMetrics {
  national_food_security: {
    security_index: number;
    trend: 'increasing' | 'decreasing' | 'stable';
    at_risk_regions: string[];
    production_forecast: number;
  };
  seed_adoption: {
    total_farmers: number;
    adoption_rate: number;
    top_varieties: Array<{
      name: string;
      adoption_percentage: number;
      regions: string[];
    }>;
  };
  climate_resilience: {
    adaptation_score: number;
    vulnerable_regions: string[];
    climate_ready_percentage: number;
  };
  regional_performance: Array<{
    region: string;
    yield_trend: number;
    farmer_count: number;
    avg_yield: number;
    risk_level: 'low' | 'medium' | 'high';
  }>;
  intervention_impact: {
    programs_active: number;
    farmers_reached: number;
    yield_improvement: number;
    cost_effectiveness: number;
  };
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
};

const PolicyDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<PolicyMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [selectedRegion, setSelectedRegion] = useState<string>('all');
  const [selectedTimeframe, setSelectedTimeframe] = useState<string>('12months');

  useEffect(() => {
    const fetchPolicyMetrics = async () => {
      try {
        setLoading(true);
        const response = await analyticsAPI.getPolicyDashboard(
          selectedRegion === 'all' ? undefined : selectedRegion
        );
        setMetrics(response);
        setError(null);
      } catch (err) {
        setError('Failed to load policy analytics data');
        console.error('Error fetching policy metrics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPolicyMetrics();
  }, [selectedRegion, selectedTimeframe]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleRegionChange = (event: SelectChangeEvent) => {
    setSelectedRegion(event.target.value);
  };

  const handleTimeframeChange = (event: SelectChangeEvent) => {
    setSelectedTimeframe(event.target.value);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ margin: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!metrics) return null;

  const foodSecurityColor = metrics.national_food_security.security_index >= 70 ? '#4caf50' : 
                           metrics.national_food_security.security_index >= 50 ? '#ff9800' : '#f44336';

  const pieColors = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Policy Analytics Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Region</InputLabel>
            <Select value={selectedRegion} onChange={handleRegionChange} label="Region">
              <MenuItem value="all">All Regions</MenuItem>
              <MenuItem value="central">Central</MenuItem>
              <MenuItem value="eastern">Eastern</MenuItem>
              <MenuItem value="northern">Northern</MenuItem>
              <MenuItem value="western">Western</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Timeframe</InputLabel>
            <Select value={selectedTimeframe} onChange={handleTimeframeChange} label="Timeframe">
              <MenuItem value="6months">6 Months</MenuItem>
              <MenuItem value="12months">12 Months</MenuItem>
              <MenuItem value="24months">24 Months</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Box>

      {/* Key Metrics Overview */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Food Security Index
                  </Typography>
                  <Typography variant="h4" sx={{ color: foodSecurityColor }}>
                    {metrics.national_food_security.security_index}%
                  </Typography>
                </Box>
                {metrics.national_food_security.trend === 'increasing' ? (
                  <TrendingUp sx={{ color: '#4caf50', fontSize: 40 }} />
                ) : metrics.national_food_security.trend === 'decreasing' ? (
                  <TrendingDown sx={{ color: '#f44336', fontSize: 40 }} />
                ) : (
                  <CheckCircle sx={{ color: '#ff9800', fontSize: 40 }} />
                )}
              </Box>
              <Typography variant="body2" color="textSecondary">
                {metrics.national_food_security.at_risk_regions.length} regions at risk
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Farmers
              </Typography>
              <Typography variant="h4">
                {metrics.seed_adoption.total_farmers.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {metrics.seed_adoption.adoption_rate}% adoption rate
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Climate Resilience
              </Typography>
              <Typography variant="h4">
                {metrics.climate_resilience.adaptation_score}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {metrics.climate_resilience.climate_ready_percentage}% climate-ready
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Programs
              </Typography>
              <Typography variant="h4">
                {metrics.intervention_impact.programs_active}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {metrics.intervention_impact.farmers_reached.toLocaleString()} farmers reached
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Alerts Section */}
      {metrics.national_food_security.at_risk_regions.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Box>
            <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
              <Warning sx={{ mr: 1, verticalAlign: 'middle' }} />
              Food Security Alerts
            </Typography>
            <Typography>
              The following regions require immediate attention:
            </Typography>
            <Box sx={{ mt: 1 }}>
              {metrics.national_food_security.at_risk_regions.map((region) => (
                <Chip key={region} label={region} color="warning" size="small" sx={{ mr: 1, mb: 1 }} />
              ))}
            </Box>
          </Box>
        </Alert>
      )}

      {/* Detailed Analytics Tabs */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="Regional Performance" />
            <Tab label="Seed Adoption" />
            <Tab label="Program Impact" />
            <Tab label="Climate Adaptation" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          <Typography variant="h6" gutterBottom>
            Regional Yield Performance
          </Typography>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={metrics.regional_performance}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="region" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="avg_yield" fill="#8884d8" name="Average Yield (kg/ha)" />
              <Bar dataKey="farmer_count" fill="#82ca9d" name="Number of Farmers" />
            </BarChart>
          </ResponsiveContainer>

          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Risk Assessment by Region
            </Typography>
            <Grid container spacing={2}>
              {metrics.regional_performance.map((region) => (
                <Grid size={{ xs: 12, sm: 6, md: 4 }} key={region.region}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6">{region.region}</Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                        <Chip
                          label={region.risk_level}
                          color={region.risk_level === 'low' ? 'success' : 
                                region.risk_level === 'medium' ? 'warning' : 'error'}
                          size="small"
                        />
                        <Typography variant="body2">
                          {region.yield_trend > 0 ? '+' : ''}{region.yield_trend}% yield trend
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" gutterBottom>
            Top Seed Varieties Adoption
          </Typography>
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={metrics.seed_adoption.top_varieties}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, adoption_percentage }) => `${name}: ${adoption_percentage}%`}
                outerRadius={120}
                fill="#8884d8"
                dataKey="adoption_percentage"
              >
                {metrics.seed_adoption.top_varieties.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={pieColors[index % pieColors.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>

          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Seed Variety Details
            </Typography>
            <Grid container spacing={2}>
              {metrics.seed_adoption.top_varieties.map((variety, index) => (
                <Grid size={{ xs: 12, sm: 6 }} key={variety.name}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6">{variety.name}</Typography>
                      <Typography color="primary" variant="h4">
                        {variety.adoption_percentage}%
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Regions: {variety.regions.join(', ')}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            Program Impact Metrics
          </Typography>
          <Grid container spacing={3}>
            <Grid size={{ xs: 12, md: 6 }}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Yield Improvement
                  </Typography>
                  <Typography variant="h3" color="primary">
                    +{metrics.intervention_impact.yield_improvement}%
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Average improvement across all programs
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Cost Effectiveness
                  </Typography>
                  <Typography variant="h3" color="success.main">
                    ${metrics.intervention_impact.cost_effectiveness}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Cost per farmer reached (USD)
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Program Reach Timeline
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={[
                { month: 'Jan', farmers: 1200 },
                { month: 'Feb', farmers: 1800 },
                { month: 'Mar', farmers: 2500 },
                { month: 'Apr', farmers: 3200 },
                { month: 'May', farmers: 4100 },
                { month: 'Jun', farmers: metrics.intervention_impact.farmers_reached }
              ]}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="farmers" stroke="#8884d8" fill="#8884d8" fillOpacity={0.3} />
              </AreaChart>
            </ResponsiveContainer>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Typography variant="h6" gutterBottom>
            Climate Adaptation Status
          </Typography>
          <Grid container spacing={3}>
            <Grid size={{ xs: 12, md: 8 }}>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={[
                  { category: 'Drought Resistant Seeds', percentage: 78 },
                  { category: 'Water Management', percentage: 65 },
                  { category: 'Early Warning Systems', percentage: 52 },
                  { category: 'Climate Insurance', percentage: 34 },
                  { category: 'Soil Conservation', percentage: 71 }
                ]}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="percentage" fill="#82ca9d" />
                </BarChart>
              </ResponsiveContainer>
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <Box>
                <Typography variant="h6" gutterBottom>
                  Vulnerable Regions
                </Typography>
                {metrics.climate_resilience.vulnerable_regions.map((region) => (
                  <Chip
                    key={region}
                    label={region}
                    color="warning"
                    sx={{ mr: 1, mb: 1 }}
                    icon={<Warning />}
                  />
                ))}
              </Box>
            </Grid>
          </Grid>
        </TabPanel>
      </Card>
    </Box>
  );
};

export default PolicyDashboard;