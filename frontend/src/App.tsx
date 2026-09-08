import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Link as RouterLink, useLocation } from 'react-router-dom';
import { ThemeProvider, CssBaseline, Container, Typography, AppBar, Toolbar, Tabs, Tab } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';

import theme from './theme';
import { getRuns, getConsistency, type RunData, type ConsistencyData } from './api';
import DashboardPage from './pages/DashboardPage';
import ComparePage from './pages/ComparePage';
import RunDetailsPage from './pages/RunDetailsPage';

function AppContent() {
  const [runs, setRuns] = useState<RunData[]>([]);
  const [consistency, setConsistency] = useState<ConsistencyData>({});
  const location = useLocation();

  const loadData = async () => {
    try {
      const [runsRes, consRes] = await Promise.all([
        getRuns(),
        getConsistency()
      ]);
      setRuns(runsRes.data);
      setConsistency(consRes.data);
    } catch (error) {
      console.error("Failed to load data:", error);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const currentTab = location.pathname === '/compare' ? 1 : 0;

  return (
    <>
      <AppBar position="static" color="transparent" elevation={0} sx={{ borderBottom: '1px solid', borderColor: 'divider', mb: 4 }}>
        <Toolbar>
          <DashboardIcon sx={{ mr: 2, color: 'primary.main' }} />
          <Typography variant="h6" color="text.primary" sx={{ mr: 4, fontWeight: 700 }}>
            Ammeter QA Dashboard
          </Typography>
          <Tabs value={currentTab} textColor="primary" indicatorColor="primary">
            <Tab label="Dashboard" component={RouterLink} to="/" />
            <Tab label="Compare Runs" component={RouterLink} to="/compare" />
          </Tabs>
        </Toolbar>
      </AppBar>
      
      <Container maxWidth="lg" sx={{ pb: 8 }}>
        <Routes>
          <Route path="/" element={<DashboardPage runs={runs} consistency={consistency} onRunComplete={loadData} />} />
          <Route path="/compare" element={<ComparePage runs={runs} />} />
          <Route path="/run/:id" element={<RunDetailsPage runs={runs} />} />
        </Routes>
      </Container>
    </>
  );
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
