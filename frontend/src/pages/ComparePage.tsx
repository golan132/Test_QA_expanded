import React, { useState, useMemo } from 'react';
import { Box, Typography, Paper, Autocomplete, TextField, Grid } from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import type { RunData } from '../api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend
);

interface ComparePageProps {
  runs: RunData[];
}

const colors = [
  'rgba(59, 130, 246, 0.8)', // blue
  'rgba(16, 185, 129, 0.8)', // green
  'rgba(245, 158, 11, 0.8)', // yellow
  'rgba(239, 68, 68, 0.8)',  // red
  'rgba(139, 92, 246, 0.8)', // purple
];

const ComparePage: React.FC<ComparePageProps> = ({ runs }) => {
  const [selectedRuns, setSelectedRuns] = useState<RunData[]>([]);

  // Filter only successful runs that have statistics
  const validRuns = useMemo(() => {
    return runs.filter(r => r.status === 'PASS' && r.statistics);
  }, [runs]);

  const options = validRuns.map(run => ({
    label: `${run.ammeter_type.toUpperCase()} - ${new Date(run.timestamp).toLocaleString()}`,
    id: run.test_id,
    run
  }));

  const selectedOptions = selectedRuns.map(run => ({
    label: `${run.ammeter_type.toUpperCase()} - ${new Date(run.timestamp).toLocaleString()}`,
    id: run.test_id,
    run
  }));

  // Prepare Bar Chart Data (Mean comparison)
  const barData = useMemo(() => {
    return {
      labels: selectedRuns.map(r => r.ammeter_type.toUpperCase()),
      datasets: [
        {
          label: 'Mean Current',
          data: selectedRuns.map(r => r.statistics?.mean || 0),
          backgroundColor: selectedRuns.map((_, i) => colors[i % colors.length]),
        }
      ]
    };
  }, [selectedRuns]);

  // Prepare Line Chart Data (Time series comparison)
  const lineData = useMemo(() => {
    // Find maximum number of samples across selected runs
    let maxSamples = 0;
    selectedRuns.forEach(r => {
      if (r.measurements && r.measurements.length > maxSamples) {
        maxSamples = r.measurements.length;
      }
    });

    const labels = Array.from({ length: maxSamples }, (_, i) => `Sample ${i + 1}`);

    const datasets = selectedRuns.map((run, i) => {
      const data = run.measurements?.map(m => m.value) || [];
      return {
        label: `${run.ammeter_type.toUpperCase()} (${new Date(run.timestamp).toLocaleTimeString()})`,
        data: data,
        borderColor: colors[i % colors.length],
        backgroundColor: colors[i % colors.length],
        tension: 0.1
      };
    });

    return { labels, datasets };
  }, [selectedRuns]);

  return (
    <Box>
      <Paper sx={{ p: 4, mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          Run Comparison Analysis
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Select multiple historical runs below to compare their statistical metrics and time-series data side-by-side.
        </Typography>

        <Autocomplete
          multiple
          options={options}
          getOptionLabel={(option) => option.label}
          value={selectedOptions}
          onChange={(_, newValue) => {
            setSelectedRuns(newValue.map(v => v.run));
          }}
          isOptionEqualToValue={(option, value) => option.id === value.id}
          renderInput={(params) => (
            <TextField
              {...params}
              variant="outlined"
              label="Select Runs to Compare"
              placeholder="Search by ammeter or date..."
            />
          )}
        />
      </Paper>

      {selectedRuns.length > 0 ? (
        <Grid container spacing={4}>
          <Grid size={{ xs: 12, md: 6 }}>
            <Paper sx={{ p: 3, height: 400 }}>
              <Typography variant="h6" align="center" gutterBottom>Mean Current Comparison</Typography>
              <Box sx={{ height: 320 }}>
                <Bar 
                  data={barData} 
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } }
                  }} 
                />
              </Box>
            </Paper>
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <Paper sx={{ p: 3, height: 400 }}>
              <Typography variant="h6" align="center" gutterBottom>Time-Series Measurement Overlay</Typography>
              <Box sx={{ height: 320 }}>
                <Line 
                  data={lineData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom' } },
                    scales: { y: { beginAtZero: false } }
                  }}
                />
              </Box>
            </Paper>
          </Grid>
        </Grid>
      ) : (
        <Paper sx={{ p: 6, textAlign: 'center', bgcolor: 'background.default', border: '1px dashed', borderColor: 'divider' }}>
          <Typography color="text.secondary">
            Please select at least one run from the dropdown above to begin comparison.
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default ComparePage;
