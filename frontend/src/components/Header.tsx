import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Box,
  useTheme,
} from '@mui/material';
import {
  Menu as MenuIcon,
  AccountCircle,
  Notifications,
  Settings,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

interface HeaderProps {
  onMenuClick: () => void;
  mobileOpen: boolean;
}

const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  const theme = useTheme();
  const { user, logout } = useAuth();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleProfileMenuClose();
    logout();
  };

  const getUserDisplayName = () => {
    return user?.full_name || user?.username || 'User';
  };

  const getUserTypeLabel = () => {
    switch (user?.user_type) {
      case 'farmer':
        return 'Farmer';
      case 'admin':
        return 'Administrator';
      case 'policy_maker':
        return 'Policy Maker';
      default:
        return 'User';
    }
  };

  return (
    <AppBar
      position="fixed"
      sx={{
        zIndex: theme.zIndex.drawer + 1,
        backgroundColor: '#2e7d32',
      }}
    >
      <Toolbar>
        <IconButton
          color="inherit"
          aria-label="open drawer"
          edge="start"
          onClick={onMenuClick}
          sx={{ mr: 2, display: { sm: 'none' } }}
        >
          <MenuIcon />
        </IconButton>

        <Typography
          variant="h6"
          noWrap
          component="div"
          sx={{ flexGrow: 1, display: 'flex', alignItems: 'center' }}
        >
          🌱 Climate-Adaptive Seed AI Bank
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <IconButton color="inherit">
            <Notifications />
          </IconButton>

          <IconButton color="inherit">
            <Settings />
          </IconButton>

          <Button
            color="inherit"
            startIcon={<AccountCircle />}
            onClick={handleProfileMenuOpen}
            sx={{ textTransform: 'none' }}
          >
            {getUserDisplayName()}
          </Button>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleProfileMenuClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
          >
            <MenuItem disabled>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="subtitle1">{getUserDisplayName()}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {getUserTypeLabel()}
                </Typography>
              </Box>
            </MenuItem>
            <MenuItem onClick={handleProfileMenuClose}>Profile</MenuItem>
            <MenuItem onClick={handleProfileMenuClose}>Settings</MenuItem>
            <MenuItem onClick={handleLogout}>Logout</MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;