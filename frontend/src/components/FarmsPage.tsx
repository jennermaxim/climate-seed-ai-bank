import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Chip,
  IconButton,
  Alert,
  CircularProgress,
  Stack
} from '@mui/material';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon, LocationOn as LocationIcon } from '@mui/icons-material';

interface Farm {
  id: number;
  farm_name: string;
  latitude: number;
  longitude: number;
  district: string;
  sub_county?: string;
  village?: string;
  total_area: number;
  cultivated_area: number;
  irrigation_available: boolean;
  irrigation_type?: string;
  storage_capacity?: number;
  market_distance?: number;
  road_access: string;
}

const ugandaDistricts = [
  'Kampala', 'Wakiso', 'Mukono', 'Jinja', 'Mbale', 'Gulu', 'Lira', 'Arua',
  'Mbarara', 'Masaka', 'Fort Portal', 'Kabale', 'Soroti', 'Moroto'
];

const FarmsPage: React.FC = () => {
  const [farms, setFarms] = useState<Farm[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingFarm, setEditingFarm] = useState<Farm | null>(null);
  const [formData, setFormData] = useState({
    farm_name: '',
    latitude: '',
    longitude: '',
    district: '',
    sub_county: '',
    village: '',
    total_area: '',
    cultivated_area: '',
    irrigation_available: false,
    irrigation_type: '',
    storage_capacity: '',
    market_distance: '',
    road_access: 'good'
  });

  useEffect(() => {
    loadFarms();
  }, []);

  const loadFarms = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token'); // Use the same key as AuthContext
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/farms/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setFarms(data);
      } else {
        setError('Failed to load farms');
      }
    } catch (err) {
      setError('Error loading farms');
      console.error('Error loading farms:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      const farmData = {
        ...formData,
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude),
        total_area: parseFloat(formData.total_area),
        cultivated_area: parseFloat(formData.cultivated_area),
        storage_capacity: formData.storage_capacity ? parseFloat(formData.storage_capacity) : undefined,
        market_distance: formData.market_distance ? parseFloat(formData.market_distance) : undefined,
      };

      const url = editingFarm 
        ? `${process.env.REACT_APP_API_URL}/api/farms/${editingFarm.id}`
        : `${process.env.REACT_APP_API_URL}/api/farms`;
      
      const method = editingFarm ? 'PUT' : 'POST';
      const token = localStorage.getItem('access_token'); // Use the same key as AuthContext
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(farmData),
      });

      if (response.ok) {
        await loadFarms();
        handleCloseDialog();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to save farm');
      }
    } catch (err) {
      setError('Error saving farm');
      console.error('Error saving farm:', err);
    }
  };

  const handleEdit = (farm: Farm) => {
    setEditingFarm(farm);
    setFormData({
      farm_name: farm.farm_name,
      latitude: farm.latitude.toString(),
      longitude: farm.longitude.toString(),
      district: farm.district,
      sub_county: farm.sub_county || '',
      village: farm.village || '',
      total_area: farm.total_area.toString(),
      cultivated_area: farm.cultivated_area.toString(),
      irrigation_available: farm.irrigation_available,
      irrigation_type: farm.irrigation_type || '',
      storage_capacity: farm.storage_capacity?.toString() || '',
      market_distance: farm.market_distance?.toString() || '',
      road_access: farm.road_access
    });
    setOpenDialog(true);
  };

  const handleDelete = async (farmId: number) => {
    if (window.confirm('Are you sure you want to delete this farm?')) {
      try {
        const token = localStorage.getItem('access_token'); // Use the same key as AuthContext
        const response = await fetch(`${process.env.REACT_APP_API_URL}/api/farms/${farmId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          await loadFarms();
        } else {
          setError('Failed to delete farm');
        }
      } catch (err) {
        setError('Error deleting farm');
        console.error('Error deleting farm:', err);
      }
    }
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingFarm(null);
    setFormData({
      farm_name: '',
      latitude: '',
      longitude: '',
      district: '',
      sub_county: '',
      village: '',
      total_area: '',
      cultivated_area: '',
      irrigation_available: false,
      irrigation_type: '',
      storage_capacity: '',
      market_distance: '',
      road_access: 'good'
    });
    setError('');
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
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
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          My Farms
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Add Farm
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {farms.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <LocationIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No farms registered yet
            </Typography>
            <Typography color="text.secondary" paragraph>
              Start by adding your first farm to get personalized recommendations and climate data.
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setOpenDialog(true)}
              size="large"
            >
              Add Your First Farm
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Stack spacing={3}>
          {farms.map((farm) => (
            <Card key={farm.id}>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Typography variant="h6" component="h2">
                    {farm.farm_name}
                  </Typography>
                  <Box>
                    <IconButton size="small" onClick={() => handleEdit(farm)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton size="small" onClick={() => handleDelete(farm.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Box>
                
                <Typography color="text.secondary" gutterBottom>
                  {farm.district}, {farm.sub_county}
                </Typography>
                
                <Box mt={2}>
                  <Typography variant="body2">
                    <strong>Total Area:</strong> {farm.total_area} hectares
                  </Typography>
                  <Typography variant="body2">
                    <strong>Cultivated:</strong> {farm.cultivated_area} hectares
                  </Typography>
                  <Typography variant="body2">
                    <strong>Road Access:</strong> {farm.road_access}
                  </Typography>
                  {farm.irrigation_available && (
                    <Chip 
                      label={`Irrigation: ${farm.irrigation_type || 'Available'}`}
                      size="small" 
                      color="primary" 
                      sx={{ mt: 1 }}
                    />
                  )}
                </Box>
              </CardContent>
            </Card>
          ))}
        </Stack>
      )}

      {/* Add/Edit Farm Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingFarm ? 'Edit Farm' : 'Add New Farm'}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              fullWidth
              label="Farm Name"
              value={formData.farm_name}
              onChange={(e) => handleInputChange('farm_name', e.target.value)}
              required
            />
            
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                fullWidth
                select
                label="District"
                value={formData.district}
                onChange={(e) => handleInputChange('district', e.target.value)}
                required
              >
                {ugandaDistricts.map((district) => (
                  <MenuItem key={district} value={district}>
                    {district}
                  </MenuItem>
                ))}
              </TextField>
              
              <TextField
                fullWidth
                label="Sub County"
                value={formData.sub_county}
                onChange={(e) => handleInputChange('sub_county', e.target.value)}
              />
            </Stack>

            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                fullWidth
                label="Village"
                value={formData.village}
                onChange={(e) => handleInputChange('village', e.target.value)}
              />
              
              <TextField
                fullWidth
                select
                label="Road Access"
                value={formData.road_access}
                onChange={(e) => handleInputChange('road_access', e.target.value)}
              >
                <MenuItem value="good">Good</MenuItem>
                <MenuItem value="fair">Fair</MenuItem>
                <MenuItem value="poor">Poor</MenuItem>
              </TextField>
            </Stack>

            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                fullWidth
                type="number"
                label="Latitude"
                value={formData.latitude}
                onChange={(e) => handleInputChange('latitude', e.target.value)}
                required
                helperText="Example: 0.3476 (for Kampala)"
              />
              
              <TextField
                fullWidth
                type="number"
                label="Longitude"
                value={formData.longitude}
                onChange={(e) => handleInputChange('longitude', e.target.value)}
                required
                helperText="Example: 32.5825 (for Kampala)"
              />
            </Stack>

            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                fullWidth
                type="number"
                label="Total Area (hectares)"
                value={formData.total_area}
                onChange={(e) => handleInputChange('total_area', e.target.value)}
                required
              />
              
              <TextField
                fullWidth
                type="number"
                label="Cultivated Area (hectares)"
                value={formData.cultivated_area}
                onChange={(e) => handleInputChange('cultivated_area', e.target.value)}
                required
              />
            </Stack>

            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                fullWidth
                type="number"
                label="Storage Capacity (tons)"
                value={formData.storage_capacity}
                onChange={(e) => handleInputChange('storage_capacity', e.target.value)}
              />
              
              <TextField
                fullWidth
                type="number"
                label="Market Distance (km)"
                value={formData.market_distance}
                onChange={(e) => handleInputChange('market_distance', e.target.value)}
              />
            </Stack>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingFarm ? 'Update' : 'Add'} Farm
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FarmsPage;