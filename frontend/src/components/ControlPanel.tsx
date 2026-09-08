import React, { useState } from 'react';
import { 
  Box, Button, Paper, Typography, CircularProgress, Alert, Snackbar, 
  TextField, MenuItem, Select, FormControl, InputLabel, Divider, Tooltip
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import BugReportIcon from '@mui/icons-material/BugReport';
import SettingsIcon from '@mui/icons-material/Settings';
import { runTests, runErrors, type RunParams } from '../api';

interface ControlPanelProps {
  onRunComplete?: () => void;
}

const ControlPanel: React.FC<ControlPanelProps> = ({ onRunComplete }) => {
  const [loading, setLoading] = useState(false);
  const [showParams, setShowParams] = useState(false);
  
  // Test parameters state
  const [ammeter, setAmmeter] = useState<string>('all');
  const [count, setCount] = useState<string>('');
  const [duration, setDuration] = useState<string>('');
  const [frequency, setFrequency] = useState<string>('');

  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' as 'info' | 'success' | 'error' });

  const handleRun = async (isStandardTest: boolean) => {
    setLoading(true);
    const type = isStandardTest ? 'Tests' : 'Error Simulation';
    setSnackbar({ open: true, message: `Running ${type}...`, severity: 'info' });
    
    try {
      if (isStandardTest) {
        const params: RunParams = {
          ammeter,
          count: count ? parseInt(count) : null,
          duration: duration ? parseInt(duration) : null,
          frequency: frequency ? parseFloat(frequency) : null,
        };
        await runTests(params);
      } else {
        await runErrors();
      }
      
      setSnackbar({ open: true, message: `${type} completed successfully!`, severity: 'success' });
      if (onRunComplete) onRunComplete();
    } catch (error: any) {
      setSnackbar({ open: true, message: `Error running ${type}: ${error.message}`, severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 3, mb: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: showParams ? 3 : 0 }}>
        <Box>
          <Typography variant="h6" gutterBottom>System Controls</Typography>
          <Typography variant="body2" color="text.secondary">Trigger automated tests and simulations across the ammeter network.</Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Tooltip title="Configure test parameters like count, duration, and frequency">
            <Button 
              variant="text" 
              color="secondary"
              startIcon={<SettingsIcon />}
              onClick={() => setShowParams(!showParams)}
            >
              Parameters
            </Button>
          </Tooltip>
          <Tooltip title="Start a standard data collection test on the selected ammeters">
            <Button
              variant="contained"
              color="primary"
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <PlayArrowIcon />}
              onClick={() => handleRun(true)}
              disabled={loading}
            >
              Run Tests
            </Button>
          </Tooltip>
          <Tooltip title="Trigger the error simulation suite to test timeout handling and error recovery">
            <Button
              variant="outlined"
              color="error"
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <BugReportIcon />}
              onClick={() => handleRun(false)}
              disabled={loading}
            >
              Simulate Errors
            </Button>
          </Tooltip>
        </Box>
      </Box>

      {showParams && (
        <>
          <Divider sx={{ mb: 3 }} />
          <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Target Ammeter</InputLabel>
              <Select
                value={ammeter}
                label="Target Ammeter"
                onChange={(e) => setAmmeter(e.target.value)}
              >
                <MenuItem value="all">All Ammeters</MenuItem>
                <MenuItem value="greenlee">Greenlee</MenuItem>
                <MenuItem value="entes">Entes</MenuItem>
                <MenuItem value="circutor">Circutor</MenuItem>
              </Select>
            </FormControl>
            
            <TextField 
              label="Measurement Count" 
              type="number"
              placeholder="e.g. 50"
              value={count}
              onChange={(e) => setCount(e.target.value)}
              helperText="Overrides default count"
              slotProps={{ inputLabel: { shrink: true } }}
            />

            <TextField 
              label="Duration (Seconds)" 
              type="number"
              placeholder="e.g. 10"
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
              helperText="Overrides count if set"
              slotProps={{ inputLabel: { shrink: true } }}
            />

            <TextField 
              label="Frequency (Hz)" 
              type="number"
              placeholder="e.g. 2.0"
              value={frequency}
              onChange={(e) => setFrequency(e.target.value)}
              helperText="Samples per second"
              slotProps={{ htmlInput: { step: "0.1" }, inputLabel: { shrink: true } }}
            />
          </Box>
        </>
      )}

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
      >
        <Alert severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Paper>
  );
};

export default ControlPanel;
