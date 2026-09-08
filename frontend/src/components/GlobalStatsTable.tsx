import React from 'react';
import { Paper, Typography, Box, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Tooltip, IconButton, Alert, AlertTitle } from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import type { RunData } from '../api';

interface GlobalStatsTableProps {
  runs: RunData[];
}

const GlobalStatsTable: React.FC<GlobalStatsTableProps> = ({ runs }) => {
  // Aggregate stats per ammeter
  const statsByAmmeter: Record<string, {
    count: number;
    sumMean: number;
    sumMedian: number;
    sumStdDev: number;
    min: number;
    max: number;
  }> = {};

  runs.forEach(run => {
    if (!run.statistics || run.status !== 'PASS') return;
    
    const type = run.ammeter_type.toUpperCase();
    const s = run.statistics;
    
    if (!statsByAmmeter[type]) {
      statsByAmmeter[type] = {
        count: 0,
        sumMean: 0,
        sumMedian: 0,
        sumStdDev: 0,
        min: Number.MAX_VALUE,
        max: Number.MIN_VALUE,
      };
    }

    const a = statsByAmmeter[type];
    if (s.mean !== undefined && s.mean !== null) {
      a.count++;
      a.sumMean += s.mean;
      a.sumMedian += (s.median || 0);
      a.sumStdDev += (s.std_dev || 0);
      if (s.min !== undefined && s.min !== null && s.min < a.min) a.min = s.min;
      if (s.max !== undefined && s.max !== null && s.max > a.max) a.max = s.max;
    }
  });

  const ammeters = Object.keys(statsByAmmeter);

  if (ammeters.length === 0) return null;

  // Find the most reliable ammeter based on lowest average standard deviation
  let bestAmmeter = '';
  let lowestStdDev = Number.MAX_VALUE;

  ammeters.forEach(type => {
    const data = statsByAmmeter[type];
    const avgStdDev = data.count > 0 ? (data.sumStdDev / data.count) : Number.MAX_VALUE;
    if (avgStdDev < lowestStdDev) {
      lowestStdDev = avgStdDev;
      bestAmmeter = type;
    }
  });

  return (
    <Paper sx={{ p: 3, mb: 4 }}>
      {bestAmmeter && (
        <Alert icon={<EmojiEventsIcon fontSize="inherit" />} severity="success" sx={{ mb: 3 }}>
          <AlertTitle>Accuracy Assessment & Relative Precision</AlertTitle>
          Based on historical statistical analysis, the most reliable measurement method is <strong>{bestAmmeter}</strong> (Drift/StdDev: {lowestStdDev.toFixed(5)}A).
        </Alert>
      )}

      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Aggregate Statistical Metrics
        </Typography>
        <Tooltip title="Aggregated statistical metrics across all PASS test runs for each ammeter type.">
          <IconButton size="small" sx={{ ml: 1, color: 'text.secondary' }}>
            <InfoIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow sx={{ bgcolor: 'background.default' }}>
              <TableCell>Ammeter</TableCell>
              <Tooltip title="Average of all recorded Means (Mean of Means)"><TableCell align="right">Avg Mean</TableCell></Tooltip>
              <Tooltip title="Average of all recorded Medians"><TableCell align="right">Avg Median</TableCell></Tooltip>
              <Tooltip title="Average of all recorded Standard Deviations"><TableCell align="right">Avg Std Dev</TableCell></Tooltip>
              <Tooltip title="Absolute Minimum value recorded across all runs"><TableCell align="right">Global Min</TableCell></Tooltip>
              <Tooltip title="Absolute Maximum value recorded across all runs"><TableCell align="right">Global Max</TableCell></Tooltip>
            </TableRow>
          </TableHead>
          <TableBody>
            {ammeters.map(type => {
              const data = statsByAmmeter[type];
              const avgMean = data.count > 0 ? (data.sumMean / data.count).toFixed(4) : 'N/A';
              const avgMedian = data.count > 0 ? (data.sumMedian / data.count).toFixed(4) : 'N/A';
              const avgStdDev = data.count > 0 ? (data.sumStdDev / data.count).toFixed(4) : 'N/A';
              const minStr = data.min === Number.MAX_VALUE ? 'N/A' : data.min.toFixed(4);
              const maxStr = data.max === Number.MIN_VALUE ? 'N/A' : data.max.toFixed(4);

              return (
                <TableRow key={type} hover sx={type === bestAmmeter ? { bgcolor: 'success.light', '&:hover': { bgcolor: 'success.main', opacity: 0.8 } } : {}}>
                  <TableCell sx={{ fontWeight: type === bestAmmeter ? 700 : 500, color: type === bestAmmeter ? 'success.contrastText' : 'inherit' }}>
                    {type} {type === bestAmmeter && '🏆'}
                  </TableCell>
                  <TableCell align="right" sx={{ color: type === bestAmmeter ? 'success.contrastText' : 'inherit' }}>{avgMean}</TableCell>
                  <TableCell align="right" sx={{ color: type === bestAmmeter ? 'success.contrastText' : 'inherit' }}>{avgMedian}</TableCell>
                  <TableCell align="right" sx={{ color: type === bestAmmeter ? 'success.contrastText' : 'inherit' }}>{avgStdDev}</TableCell>
                  <TableCell align="right" sx={{ color: type === bestAmmeter ? 'success.contrastText' : 'inherit' }}>{minStr}</TableCell>
                  <TableCell align="right" sx={{ color: type === bestAmmeter ? 'success.contrastText' : 'inherit' }}>{maxStr}</TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

export default GlobalStatsTable;
