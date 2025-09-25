import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import RoleProtectedRoute from './components/RoleProtectedRoute';
import Layout from './components/Layout';
import LoginPage from './components/LoginPage';
import FarmerDashboard from './components/FarmerDashboard';
import PolicyDashboard from './components/PolicyDashboard';
import FarmsPage from './components/FarmsPage';
import SeedsPage from './components/SeedsPage';
import RecommendationsPage from './components/RecommendationsPage';
import ClimatePage from './components/ClimatePage';

const theme = createTheme({
  palette: {
    primary: {
      main: '#4caf50',
    },
    secondary: {
      main: '#ff9800',
    },
    background: {
      default: '#f5f5f5',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/"
              element={
                <PrivateRoute>
                  <Layout />
                </PrivateRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<FarmerDashboard />} />
              <Route path="farms" element={<FarmsPage />} />
              <Route path="seeds" element={<SeedsPage />} />
              <Route path="recommendations" element={<RecommendationsPage />} />
              <Route path="climate" element={<ClimatePage />} />
              <Route path="analytics" element={<div>Analytics Page (Coming Soon)</div>} />
              <Route path="policy" element={
                <RoleProtectedRoute requiredRoles={['admin', 'policy_maker']}>
                  <PolicyDashboard />
                </RoleProtectedRoute>
              } />
              <Route path="settings" element={<div>Settings Page (Coming Soon)</div>} />
              <Route path="help" element={<div>Help & Support Page (Coming Soon)</div>} />
            </Route>
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
