import React from 'react';
import { Paper, Typography, Box, Tooltip, IconButton } from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Doughnut, Pie } from 'react-chartjs-2';
import type { ConsistencyData, RunData } from '../api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  ChartTooltip,
  Legend,
  ArcElement
);

interface AnalyticsDashboardProps {
  consistency: ConsistencyData | null;
  runs: RunData[];
}

const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ consistency, runs }) => {
  if (!consistency || Object.keys(consistency).length === 0) {
    return null;
  }

  // 1. Original: Measurement Variance (CV) - Bar
  const ammeters = Object.keys(consistency);
  const cvData = ammeters.map(a => {
    const stat = consistency[a];
    return stat.mean_of_means ? Math.abs(stat.std_dev_of_means / stat.mean_of_means) : 0;
  });
  
  const barData = {
    labels: ammeters.map(a => a.toUpperCase()),
    datasets: [
      {
        label: 'Coefficient of Variation (CV)',
        data: cvData,
        backgroundColor: 'rgba(59, 130, 246, 0.7)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
      },
    ],
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top' as const },
      title: { display: true, text: 'Measurement Variance (CV)' },
    },
  };

  // 2. Original: Measurement Drift (Std Dev) - Doughnut
  const stdDevData = ammeters.map(a => consistency[a].std_dev_of_means || 0);
  
  const doughnutData = {
    labels: ammeters.map(a => a.toUpperCase()),
    datasets: [
      {
        data: stdDevData,
        backgroundColor: [
          'rgba(16, 185, 129, 0.7)',
          'rgba(245, 158, 11, 0.7)',
          'rgba(239, 68, 68, 0.7)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom' as const },
      title: { display: true, text: 'Measurement Drift (Relative Consistency)' },
    },
  };

  // 3. New: Overall Run Status Distribution - Doughnut
  const statusCounts: Record<string, number> = { PASS: 0, FAIL: 0, ERROR: 0, PARTIAL: 0 };
  runs.forEach(r => {
    const s = r.status.toUpperCase();
    if (statusCounts[s] !== undefined) statusCounts[s]++;
    else statusCounts[s] = 1;
  });

  const pieLabels = Object.keys(statusCounts).filter(k => statusCounts[k] > 0);
  const pieData = pieLabels.map(k => statusCounts[k]);
  const pieColors: Record<string, string> = {
    PASS: "rgba(40, 167, 69, 0.8)",
    FAIL: "rgba(220, 53, 69, 0.8)",
    ERROR: "rgba(255, 193, 7, 0.8)",
    PARTIAL: "rgba(13, 202, 240, 0.8)",
  };

  const statusPieData = {
    labels: pieLabels,
    datasets: [
      {
        data: pieData,
        backgroundColor: pieLabels.map(k => pieColors[k] || "rgba(108, 117, 125, 0.8)"),
        borderWidth: 0,
      }
    ]
  };

  const statusPieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom' as const },
      title: { display: true, text: 'Overall Run Status Distribution' }
    }
  };

  // 4. New: Pass Rate by Ammeter - Bar
  const ammeterTypes: Record<string, { pass: number, total: number }> = {};
  runs.forEach(r => {
    const am = r.ammeter_type;
    if (!ammeterTypes[am]) ammeterTypes[am] = { pass: 0, total: 0 };
    ammeterTypes[am].total++;
    if (r.status.toUpperCase() === "PASS") ammeterTypes[am].pass++;
  });

  const passRateLabels = Object.keys(ammeterTypes);
  const passRateDataValues = passRateLabels.map(k => {
    const total = ammeterTypes[k].total;
    return total > 0 ? (ammeterTypes[k].pass / total) * 100 : 0;
  });

  const passRateData = {
    labels: passRateLabels.map(a => a.toUpperCase()),
    datasets: [
      {
        label: 'Pass Rate (%)',
        data: passRateDataValues,
        backgroundColor: 'rgba(59, 130, 246, 0.7)',
        borderRadius: 6,
      }
    ]
  };

  const passRateOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: { max: 100 }
    },
    plugins: {
      legend: { display: false },
      title: { display: true, text: 'Pass Rate by Ammeter Type (%)' }
    }
  };

  return (
    <Paper sx={{ p: 3, mb: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Global Analytics
        </Typography>
        <Tooltip title="This dashboard aggregates statistics across all ammeters to analyze overall network health, drift, variance, and pass rates over time.">
          <IconButton size="small" sx={{ ml: 1, color: 'text.secondary' }}>
            <InfoIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
      <Typography variant="body2" color="text.secondary" gutterBottom sx={{ mb: 4 }}>
        Relative consistency, drift analysis, and historical status across different hardware models.
      </Typography>
      
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 4 }}>
        <Box sx={{ height: 300 }}>
          <Tooltip title="Compares the Coefficient of Variation (CV) between ammeters. Lower CV means higher precision and less variance in measurements.">
            <Box sx={{ height: '100%' }}><Bar data={barData} options={barOptions} /></Box>
          </Tooltip>
        </Box>
        <Box sx={{ height: 300, display: 'flex', justifyContent: 'center' }}>
          <Tooltip title="Shows the relative Standard Deviation (Drift) between devices. A larger share indicates more drift over time.">
            <Box sx={{ height: '100%', width: '100%' }}><Doughnut data={doughnutData} options={doughnutOptions} /></Box>
          </Tooltip>
        </Box>
        <Box sx={{ height: 300, display: 'flex', justifyContent: 'center' }}>
          <Tooltip title="Distribution of PASS, FAIL, ERROR, and PARTIAL statuses across all recorded test runs.">
            <Box sx={{ height: '100%', width: '100%' }}><Pie data={statusPieData} options={statusPieOptions as any} /></Box>
          </Tooltip>
        </Box>
        <Box sx={{ height: 300 }}>
          <Tooltip title="The percentage of tests that resulted in a PASS for each ammeter type.">
            <Box sx={{ height: '100%' }}><Bar data={passRateData} options={passRateOptions} /></Box>
          </Tooltip>
        </Box>
      </Box>
    </Paper>
  );
};

export default AnalyticsDashboard;
