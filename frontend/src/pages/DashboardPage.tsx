import React from 'react';
import { Box } from '@mui/material';
import type { RunData, ConsistencyData } from '../api';
import ControlPanel from '../components/ControlPanel';
import GlobalStatsTable from '../components/GlobalStatsTable';
import AnalyticsDashboard from '../components/AnalyticsDashboard';
import RunsTable from '../components/RunsTable';

interface DashboardPageProps {
  runs: RunData[];
  consistency: ConsistencyData;
  onRunComplete: () => void;
}

const DashboardPage: React.FC<DashboardPageProps> = ({ runs, consistency, onRunComplete }) => {
  return (
    <Box>
      <ControlPanel onRunComplete={onRunComplete} />
      <GlobalStatsTable runs={runs} />
      <AnalyticsDashboard consistency={consistency} runs={runs} />
      <RunsTable runs={runs} />
    </Box>
  );
};

export default DashboardPage;
