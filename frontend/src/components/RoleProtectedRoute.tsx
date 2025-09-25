import React from 'react';
import { Alert, Box } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

interface RoleProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles: string[];
}

const RoleProtectedRoute: React.FC<RoleProtectedRouteProps> = ({ 
  children, 
  requiredRoles 
}) => {
  const { user } = useAuth();
  
  if (!user) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Authentication required. Please log in to access this page.
        </Alert>
      </Box>
    );
  }

  const hasRequiredRole = requiredRoles.includes(user.user_type);
  
  if (!hasRequiredRole) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="warning">
          Access denied. You don't have permission to view this page.
          <br />
          Required roles: {requiredRoles.join(', ')}
          <br />
          Your role: {user.user_type}
        </Alert>
      </Box>
    );
  }

  return <>{children}</>;
};

export default RoleProtectedRoute;