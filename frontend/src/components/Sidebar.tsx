import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Divider,
  Box,
  useTheme,
} from '@mui/material';
import {
  Dashboard,
  Agriculture,
  Grass,
  Analytics,
  TrendingUp,
  LocationOn,
  Settings,
  Help,
  Policy,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const drawerWidth = 240;

interface SidebarProps {
  mobileOpen: boolean;
  onMobileClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ mobileOpen, onMobileClose }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();

  const menuItems = [
    {
      text: 'Dashboard',
      icon: <Dashboard />,
      path: '/dashboard',
      roles: ['farmer', 'admin', 'policy_maker'],
    },
    {
      text: 'My Farms',
      icon: <Agriculture />,
      path: '/farms',
      roles: ['farmer', 'admin'],
    },
    {
      text: 'Seed Catalog',
      icon: <Grass />,
      path: '/seeds',
      roles: ['farmer', 'admin', 'policy_maker'],
    },
    {
      text: 'Recommendations',
      icon: <TrendingUp />,
      path: '/recommendations',
      roles: ['farmer', 'admin'],
    },
    {
      text: 'Climate Data',
      icon: <LocationOn />,
      path: '/climate',
      roles: ['farmer', 'admin', 'policy_maker'],
    },
    {
      text: 'Analytics',
      icon: <Analytics />,
      path: '/analytics',
      roles: ['admin', 'policy_maker'],
    },
  ];

  const policyItems = [
    {
      text: 'Policy Dashboard',
      icon: <Policy />,
      path: '/policy',
      roles: ['policy_maker', 'admin'],
    },
  ];

  const settingsItems = [
    {
      text: 'Settings',
      icon: <Settings />,
      path: '/settings',
      roles: ['farmer', 'admin', 'policy_maker'],
    },
    {
      text: 'Help & Support',
      icon: <Help />,
      path: '/help',
      roles: ['farmer', 'admin', 'policy_maker'],
    },
  ];

  const handleItemClick = (path: string) => {
    navigate(path);
    if (mobileOpen) {
      onMobileClose();
    }
  };

  const isItemVisible = (roles: string[]) => {
    return !user?.user_type || roles.includes(user.user_type);
  };

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  const renderMenuItems = (items: typeof menuItems) => (
    <List>
      {items
        .filter((item) => isItemVisible(item.roles))
        .map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              onClick={() => handleItemClick(item.path)}
              selected={isActive(item.path)}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: theme.palette.primary.light + '20',
                  '&:hover': {
                    backgroundColor: theme.palette.primary.light + '30',
                  },
                },
              }}
            >
              <ListItemIcon
                sx={{
                  color: isActive(item.path)
                    ? theme.palette.primary.main
                    : 'inherit',
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                sx={{
                  '& .MuiListItemText-primary': {
                    color: isActive(item.path)
                      ? theme.palette.primary.main
                      : 'inherit',
                    fontWeight: isActive(item.path) ? 600 : 400,
                  },
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
    </List>
  );

  const drawer = (
    <div>
      <Toolbar />
      <Box sx={{ overflow: 'auto' }}>
        {renderMenuItems(menuItems)}
        
        {user?.user_type === 'policy_maker' || user?.user_type === 'admin' ? (
          <>
            <Divider sx={{ my: 1 }} />
            {renderMenuItems(policyItems)}
          </>
        ) : null}
        
        <Divider sx={{ my: 1 }} />
        {renderMenuItems(settingsItems)}
      </Box>
    </div>
  );

  return (
    <Box
      component="nav"
      sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
    >
      {/* Mobile drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={onMobileClose}
        ModalProps={{
          keepMounted: true,
        }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: drawerWidth,
          },
        }}
      >
        {drawer}
      </Drawer>

      {/* Desktop drawer */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: drawerWidth,
          },
        }}
        open
      >
        {drawer}
      </Drawer>
    </Box>
  );
};

export default Sidebar;