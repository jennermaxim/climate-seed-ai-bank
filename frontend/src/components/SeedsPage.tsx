import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  InputAdornment,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  Divider
} from '@mui/material';
import {
  Search as SearchIcon,
  Agriculture as AgricultureIcon,
  Schedule as ScheduleIcon,
  Info as InfoIcon
} from '@mui/icons-material';

interface Seed {
  id: number;
  name: string;
  variety: string;
  crop_type: string;
  description: string;
  planting_season: string;
  maturity_days: number;
  yield_per_hectare: number;
  resistance_traits: string[];
  price_per_kg?: number;
  availability: 'available' | 'limited' | 'out_of_stock';
}

const cropTypes = ['Cereal', 'Legume', 'Vegetable', 'Root Crop', 'Fruit', 'Cash Crop'];
const seasons = ['First Rains', 'Second Rains', 'Dry Season', 'Year Round'];

const SeedsPage: React.FC = () => {
  const [seeds, setSeeds] = useState<Seed[]>([]);
  const [filteredSeeds, setFilteredSeeds] = useState<Seed[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCropType, setSelectedCropType] = useState('');
  const [selectedSeason, setSelectedSeason] = useState('');
  const [selectedSeed, setSelectedSeed] = useState<Seed | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);

  useEffect(() => {
    loadSeeds();
  }, []);

  useEffect(() => {
    const filterSeeds = () => {
      let filtered = seeds;

      if (searchTerm) {
        filtered = filtered.filter(seed => 
          seed.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          seed.variety.toLowerCase().includes(searchTerm.toLowerCase()) ||
          seed.description.toLowerCase().includes(searchTerm.toLowerCase())
        );
      }

      if (selectedCropType) {
        filtered = filtered.filter(seed => seed.crop_type === selectedCropType);
      }

      if (selectedSeason) {
        filtered = filtered.filter(seed => 
          seed.planting_season.includes(selectedSeason) ||
          seed.planting_season === 'Year Round'
        );
      }

      setFilteredSeeds(filtered);
    };

    filterSeeds();
  }, [seeds, searchTerm, selectedCropType, selectedSeason]);

  const loadSeeds = async () => {
    try {
      setLoading(true);
      // Mock data for now
      const mockSeeds: Seed[] = [
        {
          id: 1,
          name: 'NERICA 4',
          variety: 'Upland Rice',
          crop_type: 'Cereal',
          description: 'High-yielding drought-tolerant rice variety suitable for Uganda uplands',
          planting_season: 'First Rains',
          maturity_days: 120,
          yield_per_hectare: 4500,
          resistance_traits: ['Drought Tolerant', 'Disease Resistant'],
          price_per_kg: 8000,
          availability: 'available'
        },
        {
          id: 2,
          name: 'Longe 5',
          variety: 'Sweet Potato',
          crop_type: 'Root Crop',
          description: 'Orange-fleshed sweet potato with high vitamin A content',
          planting_season: 'Year Round',
          maturity_days: 90,
          yield_per_hectare: 25000,
          resistance_traits: ['Virus Resistant', 'Drought Tolerant'],
          price_per_kg: 2500,
          availability: 'available'
        }
      ];
      
      setSeeds(mockSeeds);
    } catch (err) {
      setError('Error loading seeds catalog');
      console.error('Error loading seeds:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSeedDetail = (seed: Seed) => {
    setSelectedSeed(seed);
    setDetailDialogOpen(true);
  };

  const getAvailabilityColor = (availability: string) => {
    switch (availability) {
      case 'available': return 'success';
      case 'limited': return 'warning';
      case 'out_of_stock': return 'error';
      default: return 'default';
    }
  };

  const getAvailabilityText = (availability: string) => {
    switch (availability) {
      case 'available': return 'Available';
      case 'limited': return 'Limited Stock';
      case 'out_of_stock': return 'Out of Stock';
      default: return 'Unknown';
    }
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
        Seeds Catalog
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Discover climate-adaptive seed varieties suitable for Uganda's diverse agricultural zones.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="center">
            <TextField
              fullWidth
              placeholder="Search seeds..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
            <TextField
              fullWidth
              select
              label="Crop Type"
              value={selectedCropType}
              onChange={(e) => setSelectedCropType(e.target.value)}
            >
              <MenuItem value="">All Crop Types</MenuItem>
              {cropTypes.map((type) => (
                <MenuItem key={type} value={type}>{type}</MenuItem>
              ))}
            </TextField>
            <TextField
              fullWidth
              select
              label="Planting Season"
              value={selectedSeason}
              onChange={(e) => setSelectedSeason(e.target.value)}
            >
              <MenuItem value="">All Seasons</MenuItem>
              {seasons.map((season) => (
                <MenuItem key={season} value={season}>{season}</MenuItem>
              ))}
            </TextField>
          </Stack>
        </CardContent>
      </Card>

      {/* Seeds List */}
      {filteredSeeds.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <AgricultureIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No seeds found
            </Typography>
            <Typography color="text.secondary">
              Try adjusting your search or filter criteria.
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Stack spacing={2}>
          {filteredSeeds.map((seed) => (
            <Card key={seed.id}>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Box>
                    <Typography variant="h6" component="h2">
                      {seed.name}
                    </Typography>
                    <Typography color="text.secondary">
                      {seed.variety} • {seed.crop_type}
                    </Typography>
                  </Box>
                  <Chip
                    label={getAvailabilityText(seed.availability)}
                    color={getAvailabilityColor(seed.availability) as any}
                    size="small"
                  />
                </Box>
                
                <Typography variant="body2" paragraph>
                  {seed.description}
                </Typography>

                <Stack direction="row" spacing={2} mb={2}>
                  <Box display="flex" alignItems="center">
                    <ScheduleIcon sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
                    <Typography variant="body2">
                      {seed.maturity_days} days
                    </Typography>
                  </Box>
                  <Box display="flex" alignItems="center">
                    <AgricultureIcon sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
                    <Typography variant="body2">
                      {seed.yield_per_hectare.toLocaleString()} kg/ha
                    </Typography>
                  </Box>
                  {seed.price_per_kg && (
                    <Typography variant="body2" color="primary">
                      {seed.price_per_kg.toLocaleString()} UGX/kg
                    </Typography>
                  )}
                </Stack>

                <Stack direction="row" spacing={1} mb={2}>
                  {seed.resistance_traits.map((trait, index) => (
                    <Chip key={index} label={trait} size="small" variant="outlined" />
                  ))}
                </Stack>

                <Button
                  variant="outlined"
                  startIcon={<InfoIcon />}
                  onClick={() => handleSeedDetail(seed)}
                >
                  View Details
                </Button>
              </CardContent>
            </Card>
          ))}
        </Stack>
      )}

      {/* Seed Detail Dialog */}
      <Dialog
        open={detailDialogOpen}
        onClose={() => setDetailDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        {selectedSeed && (
          <>
            <DialogTitle>
              <Box>
                <Typography variant="h5">{selectedSeed.name}</Typography>
                <Typography color="text.secondary">
                  {selectedSeed.variety} • {selectedSeed.crop_type}
                </Typography>
              </Box>
            </DialogTitle>
            
            <DialogContent>
              <Typography paragraph>{selectedSeed.description}</Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="h6" gutterBottom>Growing Information</Typography>
              <Typography><strong>Planting Season:</strong> {selectedSeed.planting_season}</Typography>
              <Typography><strong>Maturity Period:</strong> {selectedSeed.maturity_days} days</Typography>
              <Typography><strong>Expected Yield:</strong> {selectedSeed.yield_per_hectare.toLocaleString()} kg/hectare</Typography>
              {selectedSeed.price_per_kg && (
                <Typography><strong>Price:</strong> {selectedSeed.price_per_kg.toLocaleString()} UGX/kg</Typography>
              )}
              
              <Box mt={2}>
                <Typography variant="h6" gutterBottom>Resistance Traits</Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  {selectedSeed.resistance_traits.map((trait, index) => (
                    <Chip key={index} label={trait} color="primary" variant="outlined" />
                  ))}
                </Stack>
              </Box>
            </DialogContent>
            
            <DialogActions>
              <Button onClick={() => setDetailDialogOpen(false)}>Close</Button>
              {selectedSeed.availability === 'available' && (
                <Button variant="contained" color="primary">
                  Request Seeds
                </Button>
              )}
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default SeedsPage;