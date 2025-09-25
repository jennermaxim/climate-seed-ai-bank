import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  Alert,
  CircularProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  LinearProgress,
  Stack
} from '@mui/material';
import {
  Agriculture as AgricultureIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  WbSunny as SunnyIcon,
  Opacity as OpacityIcon,
  Thermostat as ThermostatIcon
} from '@mui/icons-material';

interface Recommendation {
  id: number;
  seed_id: number;
  seed_name: string;
  crop_type: string;
  suitability_score: number;
  climate_match_score: number;
  soil_match_score: number;
  market_potential_score: number;
  risk_score: number;
  confidence_level: number;
  expected_yield?: number;
  expected_profit?: number;
  reasoning: any;
  risk_factors: string[];
  planting_window: any;
  seed_rate?: number;
  fertilizer_recommendation?: any;
  irrigation_schedule?: any;
  pest_management?: any;
}

const RecommendationsPage: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [selectedRecommendation, setSelectedRecommendation] = useState<Recommendation | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/recommendations/my-recommendations`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setRecommendations(data);
      } else {
        setError('Failed to load recommendations');
      }
    } catch (err) {
      setError('Error loading recommendations');
      console.error('Error loading recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = (recommendation: Recommendation) => {
    setSelectedRecommendation(recommendation);
    setDetailDialogOpen(true);
  };

  const getRiskColor = (riskScore: number) => {
    if (riskScore <= 0.3) return 'success';
    if (riskScore <= 0.7) return 'warning';
    return 'error';
  };

  const getRiskLevel = (riskScore: number): string => {
    if (riskScore <= 0.3) return 'low';
    if (riskScore <= 0.7) return 'medium';
    return 'high';
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'error';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Seed Recommendations
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        AI-powered seed recommendations based on your farm conditions, climate data, and soil analysis.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {recommendations.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <AgricultureIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No recommendations available yet
            </Typography>
            <Typography color="text.secondary" paragraph>
              Add your farms to receive personalized seed recommendations based on your location, climate, and soil conditions.
            </Typography>
            <Button variant="contained" href="/farms">
              Add Your First Farm
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Stack spacing={3}>
          {recommendations.map((recommendation) => (
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                    <Box>
                      <Typography variant="h6" component="h2">
                        {recommendation.seed_name}
                      </Typography>
                      <Typography color="text.secondary" variant="body2">
                        {recommendation.crop_type}
                      </Typography>
                    </Box>
                    <Chip
                      label={`${Math.round(recommendation.confidence_level * 100)}% confidence`}
                      color={getConfidenceColor(recommendation.confidence_level) as any}
                      size="small"
                    />
                  </Box>
                  
                  <Box mb={2}>
                    <Box display="flex" alignItems="center" mb={1}>
                      <ScheduleIcon sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                      <Typography variant="body2">
                        Plant: {typeof recommendation.planting_window === 'object' 
                          ? `${recommendation.planting_window.start} - ${recommendation.planting_window.end}` 
                          : 'Season A'}
                      </Typography>
                    </Box>
                    
                    {recommendation.expected_yield && (
                      <Box display="flex" alignItems="center" mb={1}>
                        <TrendingUpIcon sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                        <Typography variant="body2">
                          Expected: {recommendation.expected_yield.toFixed(1)} tons/hectare
                        </Typography>
                      </Box>
                    )}
                  </Box>

                  <Box mb={2}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Suitability Scores:
                    </Typography>
                    
                    <Box mb={1}>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="caption">Climate Match</Typography>
                        <Typography variant="caption">{Math.round(recommendation.climate_match_score * 100)}%</Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={recommendation.climate_match_score * 100} 
                        sx={{ height: 4, borderRadius: 2 }}
                      />
                    </Box>
                    
                    <Box mb={1}>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="caption">Soil Suitability</Typography>
                        <Typography variant="caption">{Math.round(recommendation.soil_match_score * 100)}%</Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={recommendation.soil_match_score * 100} 
                        sx={{ height: 4, borderRadius: 2 }}
                      />
                    </Box>
                    
                    <Box>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="caption">Market Potential</Typography>
                        <Typography variant="caption">{Math.round(recommendation.market_potential_score * 100)}%</Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={recommendation.market_potential_score * 100} 
                        sx={{ height: 4, borderRadius: 2 }}
                      />
                    </Box>
                  </Box>

                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Chip
                      label={`${getRiskLevel(recommendation.risk_score)} risk`}
                      color={getRiskColor(recommendation.risk_score) as any}
                      size="small"
                    />
                    {recommendation.risk_factors && recommendation.risk_factors.length > 0 && (
                      <Chip
                        icon={<WarningIcon />}
                        label={`${recommendation.risk_factors.length} risk factors`}
                        color="warning"
                        size="small"
                        variant="outlined"
                      />
                    )}
                  </Box>

                  <Button
                    fullWidth
                    variant="outlined"
                    onClick={() => handleViewDetails(recommendation)}
                  >
                    View Details
                  </Button>
                </CardContent>
              </Card>
          ))}
        </Stack>
      )}

      {/* Recommendation Detail Dialog */}
      <Dialog
        open={detailDialogOpen}
        onClose={() => setDetailDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedRecommendation && (
          <>
            <DialogTitle>
              <Box>
                <Typography variant="h5">{selectedRecommendation.seed_name}</Typography>
                <Typography color="text.secondary">
                  {selectedRecommendation.crop_type} recommendation
                </Typography>
              </Box>
            </DialogTitle>
            
            <DialogContent>
              <Stack direction={{ xs: 'column', md: 'row' }} spacing={3}>
                <Box sx={{ flex: 1 }}>
                  <Box mb={2}>
                    <Typography variant="h6" gutterBottom>
                      <TrendingUpIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Performance Metrics
                    </Typography>
                    <Typography><strong>Confidence Score:</strong> {Math.round(selectedRecommendation.confidence_level * 100)}%</Typography>
                    {selectedRecommendation.expected_yield && (
                      <Typography><strong>Expected Yield:</strong> {selectedRecommendation.expected_yield.toFixed(1)} tons/hectare</Typography>
                    )}
                    <Typography><strong>Risk Level:</strong> <Chip label={getRiskLevel(selectedRecommendation.risk_score)} color={getRiskColor(selectedRecommendation.risk_score) as any} size="small" /></Typography>
                    <Typography><strong>Planting Window:</strong> {
                      typeof selectedRecommendation.planting_window === 'object' 
                        ? `${selectedRecommendation.planting_window.start} - ${selectedRecommendation.planting_window.end}` 
                        : 'Season A'
                    }</Typography>
                  </Box>
                </Box>
                
                <Box sx={{ flex: 1 }}>
                  <Box mb={2}>
                    <Typography variant="h6" gutterBottom>
                      <SunnyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Environmental Suitability
                    </Typography>
                    <Box display="flex" alignItems="center" mb={1}>
                      <ThermostatIcon sx={{ mr: 1, fontSize: 16 }} />
                      <Typography>Climate Match: {Math.round(selectedRecommendation.climate_match_score * 100)}%</Typography>
                    </Box>
                    <Box display="flex" alignItems="center" mb={1}>
                      <OpacityIcon sx={{ mr: 1, fontSize: 16 }} />
                      <Typography>Soil Suitability: {Math.round(selectedRecommendation.soil_match_score * 100)}%</Typography>
                    </Box>
                    <Box display="flex" alignItems="center">
                      <TrendingUpIcon sx={{ mr: 1, fontSize: 16 }} />
                      <Typography>Market Potential: {Math.round(selectedRecommendation.market_potential_score * 100)}%</Typography>
                    </Box>
                  </Box>
                </Box>
              </Stack>
              
              <Divider sx={{ my: 2 }} />
              
              {selectedRecommendation.reasoning && (
                <Box mb={3}>
                  <Typography variant="h6" gutterBottom>
                    <CheckCircleIcon sx={{ mr: 1, verticalAlign: 'middle', color: 'success.main' }} />
                    Why This Recommendation?
                  </Typography>
                  <List dense>
                    {Object.entries(selectedRecommendation.reasoning).map(([key, value], index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <CheckCircleIcon color="success" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary={`${key}: ${value}`} />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {selectedRecommendation.risk_factors && selectedRecommendation.risk_factors.length > 0 && (
                <Box mb={3}>
                  <Typography variant="h6" gutterBottom>
                    <WarningIcon sx={{ mr: 1, verticalAlign: 'middle', color: 'warning.main' }} />
                    Risk Factors
                  </Typography>
                  <List dense>
                    {selectedRecommendation.risk_factors.map((riskFactor, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <WarningIcon color="warning" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary={riskFactor} />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {selectedRecommendation.seed_rate && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    <AgricultureIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Planting Guidelines
                  </Typography>
                  <List dense>
                    <ListItem>
                      <ListItemIcon>
                        <AgricultureIcon color="primary" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={`Seed Rate: ${selectedRecommendation.seed_rate.toFixed(1)} kg/hectare`} />
                    </ListItem>
                    {selectedRecommendation.expected_profit && (
                      <ListItem>
                        <ListItemIcon>
                          <TrendingUpIcon color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary={`Expected Profit: UGX ${selectedRecommendation.expected_profit.toLocaleString()}/hectare`} />
                      </ListItem>
                    )}
                  </List>
                </Box>
              )}
            </DialogContent>
            
            <DialogActions>
              <Button onClick={() => setDetailDialogOpen(false)}>Close</Button>
              <Button variant="contained" color="primary">
                Request Seeds
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default RecommendationsPage;