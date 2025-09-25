import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  LinearProgress
} from '@mui/material';
import {
  WbSunny as SunnyIcon,
  Thermostat as ThermostatIcon,
  Opacity as OpacityIcon,
  Air as AirIcon,
  Visibility as VisibilityIcon,
  Warning as WarningIcon
} from '@mui/icons-material';

interface WeatherData {
  temperature: number;
  humidity: number;
  rainfall: number;
  wind_speed: number;
  visibility: number;
  weather_description: string;
  location: string;
}

interface ClimateAlert {
  id: number;
  alert_type: string;
  severity: 'low' | 'medium' | 'high';
  message: string;
  farm_name: string;
  created_at: string;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
};

const ClimatePage: React.FC = () => {
  const [weatherData, setWeatherData] = useState<WeatherData[]>([]);
  const [alerts, setAlerts] = useState<ClimateAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    loadClimateData();
    loadAlerts();
  }, []);

  const loadClimateData = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/climate/weather-for-farms`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setWeatherData(data);
      } else {
        setError('Failed to load weather data');
      }
    } catch (err) {
      setError('Error loading weather data');
      console.error('Error loading weather data:', err);
    }
  };

  const loadAlerts = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/climate/alerts`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setAlerts(data);
      } else {
        console.log('No alerts available');
      }
    } catch (err) {
      console.error('Error loading alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'info';
      case 'medium': return 'warning';
      case 'high': return 'error';
      default: return 'default';
    }
  };

  const getHumidityLevel = (humidity: number) => {
    if (humidity < 30) return { level: 'Low', color: 'error' };
    if (humidity < 60) return { level: 'Normal', color: 'success' };
    return { level: 'High', color: 'warning' };
  };

  const getTemperatureStatus = (temp: number) => {
    if (temp < 15) return { status: 'Cool', color: 'info' };
    if (temp < 25) return { status: 'Moderate', color: 'success' };
    if (temp < 35) return { status: 'Warm', color: 'warning' };
    return { status: 'Hot', color: 'error' };
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
        Climate & Weather Data
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Real-time weather conditions and climate alerts for your farms.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Current Weather" />
          <Tab label="Climate Alerts" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        {weatherData.length === 0 ? (
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 6 }}>
              <SunnyIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No weather data available
              </Typography>
              <Typography color="text.secondary">
                Add your farms to get weather data for your locations.
              </Typography>
            </CardContent>
          </Card>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {weatherData.map((weather, index) => (
              <Card key={index}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">{weather.location}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {weather.weather_description}
                    </Typography>
                  </Box>

                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', minWidth: 150 }}>
                      <ThermostatIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Box>
                        <Typography variant="h5">{weather.temperature}°C</Typography>
                        <Chip
                          label={getTemperatureStatus(weather.temperature).status}
                          color={getTemperatureStatus(weather.temperature).color as any}
                          size="small"
                        />
                      </Box>
                    </Box>

                    <Box sx={{ display: 'flex', alignItems: 'center', minWidth: 150 }}>
                      <OpacityIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Box>
                        <Typography variant="h6">{weather.humidity}%</Typography>
                        <Typography variant="caption">Humidity</Typography>
                        <br />
                        <Chip
                          label={getHumidityLevel(weather.humidity).level}
                          color={getHumidityLevel(weather.humidity).color as any}
                          size="small"
                        />
                      </Box>
                    </Box>

                    <Box sx={{ display: 'flex', alignItems: 'center', minWidth: 150 }}>
                      <AirIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Box>
                        <Typography variant="h6">{weather.wind_speed} m/s</Typography>
                        <Typography variant="caption">Wind Speed</Typography>
                      </Box>
                    </Box>

                    <Box sx={{ display: 'flex', alignItems: 'center', minWidth: 150 }}>
                      <VisibilityIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Box>
                        <Typography variant="h6">{weather.visibility} km</Typography>
                        <Typography variant="caption">Visibility</Typography>
                      </Box>
                    </Box>
                  </Box>

                  {weather.rainfall > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" gutterBottom>
                        Rainfall: {weather.rainfall}mm
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={Math.min(weather.rainfall / 50 * 100, 100)} 
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>
                  )}
                </CardContent>
              </Card>
            ))}
          </Box>
        )}
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        {alerts.length === 0 ? (
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 6 }}>
              <WarningIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No climate alerts
              </Typography>
              <Typography color="text.secondary">
                You'll be notified here when there are important weather or climate conditions affecting your farms.
              </Typography>
            </CardContent>
          </Card>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Alert Type</TableCell>
                  <TableCell>Severity</TableCell>
                  <TableCell>Farm</TableCell>
                  <TableCell>Message</TableCell>
                  <TableCell>Date</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {alerts.map((alert) => (
                  <TableRow key={alert.id}>
                    <TableCell>{alert.alert_type}</TableCell>
                    <TableCell>
                      <Chip
                        label={alert.severity}
                        color={getSeverityColor(alert.severity) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{alert.farm_name}</TableCell>
                    <TableCell>{alert.message}</TableCell>
                    <TableCell>
                      {new Date(alert.created_at).toLocaleDateString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </TabPanel>
    </Box>
  );
};

export default ClimatePage;