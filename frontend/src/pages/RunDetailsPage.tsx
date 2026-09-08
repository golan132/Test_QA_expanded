import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Typography, Paper, Chip, IconButton, Grid, Button, Stack } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import DownloadIcon from '@mui/icons-material/Download';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import type { RunData } from '../api';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend);

interface RunDetailsPageProps {
  runs: RunData[];
}

const StatCard = ({ label, value }: { label: string; value: string | number | undefined | null }) => (
  <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'background.paper' }} elevation={1} variant="outlined">
    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>{label}</Typography>
    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>{value !== undefined && value !== null ? value : 'N/A'}</Typography>
  </Paper>
);

const RunDetailsPage: React.FC<RunDetailsPageProps> = ({ runs }) => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const run = runs.find(r => r.test_id === id);

  if (!run) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h5" color="error">Run not found</Typography>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate(-1)} sx={{ mt: 2 }}>Go Back</Button>
      </Box>
    );
  }

  const stats = run.statistics || {};
  const measurements = run.measurements || [];
  const successfulMeasurements = measurements.filter(m => m.success && m.value !== null);

  // Line Chart Data (Time series)
  const lineChartData = {
    labels: successfulMeasurements.map(m => new Date(m.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: 'Measurement Value (Amps)',
        data: successfulMeasurements.map(m => m.value),
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.2)',
        borderWidth: 2,
        pointRadius: 4,
        tension: 0.1
      }
    ]
  };

  const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { mode: 'index' as const, intersect: false },
    },
    scales: {
      x: { display: false }, // Hide x-axis labels if too many points
      y: { beginAtZero: true }
    }
  };

  // Bar Chart Data (Statistical overview)
  const barChartData = {
    labels: ['Mean', 'Median', 'Min', 'Max', 'RMS'],
    datasets: [
      {
        label: 'Current (A)',
        data: [stats.mean || 0, stats.median || 0, stats.min || 0, stats.max || 0, stats.rms || 0],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(139, 92, 246, 0.8)',
        ],
        borderRadius: 4
      }
    ]
  };

  const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton onClick={() => navigate(-1)} sx={{ mr: 2 }} color="primary">
            <ArrowBackIcon />
          </IconButton>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
              Run Details: {run.test_id}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {new Date(run.timestamp).toLocaleString()} | {run.ammeter_type.toUpperCase()} | 
              <Chip label={run.status} size="small" sx={{ ml: 1 }} color={run.status === 'PASS' ? 'success' : 'error'} />
            </Typography>
          </Box>
        </Box>
        <Stack direction="row" spacing={2}>
          <Button 
            variant="outlined" 
            startIcon={<DownloadIcon />}
            href={`http://localhost:8000/api/export/${run.test_id}/csv`}
            target="_blank"
          >
            CSV
          </Button>
          <Button 
            variant="outlined" 
            startIcon={<DownloadIcon />}
            href={`http://localhost:8000/api/export/${run.test_id}/time_series`}
            target="_blank"
          >
            Time Series
          </Button>
          <Button 
            variant="outlined" 
            startIcon={<DownloadIcon />}
            href={`http://localhost:8000/api/export/${run.test_id}/histogram`}
            target="_blank"
          >
            Histogram
          </Button>
        </Stack>
      </Box>

      <Paper sx={{ p: 4, mb: 4 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>Statistical Breakdown</Typography>
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr 1fr', sm: 'repeat(3, 1fr)', md: 'repeat(4, 1fr)' }, gap: 2 }}>
          <StatCard label="Mean" value={typeof stats.mean === 'number' ? stats.mean.toFixed(4) : stats.mean} />
          <StatCard label="Median" value={typeof stats.median === 'number' ? stats.median.toFixed(4) : stats.median} />
          <StatCard label="Std Dev" value={typeof stats.std_dev === 'number' ? stats.std_dev.toFixed(4) : stats.std_dev} />
          <StatCard label="Variance" value={typeof stats.variance === 'number' ? stats.variance.toFixed(4) : stats.variance} />
          <StatCard label="Min" value={typeof stats.min === 'number' ? stats.min.toFixed(4) : stats.min} />
          <StatCard label="Max" value={typeof stats.max === 'number' ? stats.max.toFixed(4) : stats.max} />
          <StatCard label="RMS" value={typeof stats.rms === 'number' ? stats.rms.toFixed(4) : stats.rms} />
          <StatCard label="SNR" value={typeof stats.snr === 'number' ? stats.snr.toFixed(4) : stats.snr} />
        </Box>
      </Paper>

      <Grid container spacing={4} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, md: 7 }}>
          <Paper sx={{ p: 4, height: 400 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>Time-Series Measurements</Typography>
            {successfulMeasurements.length > 0 ? (
              <Box sx={{ height: 300 }}>
                <Line data={lineChartData} options={lineChartOptions} />
              </Box>
            ) : (
              <Typography color="text.secondary" sx={{ fontStyle: 'italic' }}>No successful measurements to graph.</Typography>
            )}
          </Paper>
        </Grid>
        <Grid size={{ xs: 12, md: 5 }}>
          <Paper sx={{ p: 4, height: 400 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>Statistical Overview</Typography>
            <Box sx={{ height: 300 }}>
              <Bar data={barChartData} options={barChartOptions} />
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {run.errors && run.errors.length > 0 && (
        <Paper sx={{ p: 4, borderLeft: '6px solid', borderColor: 'error.main' }}>
          <Typography variant="h6" gutterBottom color="error" sx={{ fontWeight: 'bold' }}>Captured Errors ({run.errors.length})</Typography>
          <Box sx={{ p: 2, bgcolor: 'error.light', color: 'error.contrastText', borderRadius: 2 }}>
            {run.errors.map((err, idx) => (
              <Typography key={idx} variant="body2" sx={{ fontFamily: 'monospace', mb: 1 }}>
                [{new Date(err.timestamp).toLocaleTimeString()}] {err.error_type}: {err.error_message}
              </Typography>
            ))}
          </Box>
        </Paper>
      )}
    </Box>
  );
};

export default RunDetailsPage;
