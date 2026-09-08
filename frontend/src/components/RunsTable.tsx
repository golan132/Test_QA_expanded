import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Paper, Typography, Box, Table, TableBody, TableCell, TableContainer, 
  TableHead, TableRow, Chip, Tooltip, TableSortLabel 
} from '@mui/material';
import type { RunData } from '../api';

const getStatusColor = (status: string | undefined): "success" | "error" | "warning" | "default" => {
  switch (status?.toUpperCase()) {
    case 'PASS': return 'success';
    case 'FAIL': return 'error';
    case 'ERROR': return 'warning';
    default: return 'default';
  }
}

interface RunsTableProps {
  runs: RunData[];
}

type Order = 'asc' | 'desc';
type OrderBy = 'timestamp' | 'ammeter_type' | 'expected_samples' | 'successful_samples' | 'passRate' | 'status';

const RunsTable: React.FC<RunsTableProps> = ({ runs }) => {
  const navigate = useNavigate();
  const [order, setOrder] = React.useState<Order>('desc');
  const [orderBy, setOrderBy] = React.useState<OrderBy>('timestamp');

  const handleRequestSort = (property: OrderBy) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const sortedRuns = React.useMemo(() => {
    return [...runs].sort((a, b) => {
      let valA: any = a[orderBy as keyof RunData];
      let valB: any = b[orderBy as keyof RunData];

      if (orderBy === 'passRate') {
        valA = a.expected_samples > 0 ? (a.successful_samples / a.expected_samples) : 0;
        valB = b.expected_samples > 0 ? (b.successful_samples / b.expected_samples) : 0;
      }

      if (valA < valB) return order === 'asc' ? -1 : 1;
      if (valA > valB) return order === 'asc' ? 1 : -1;
      return 0;
    });
  }, [runs, order, orderBy]);

  const createSortHandler = (property: OrderBy) => () => {
    handleRequestSort(property);
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>Recent Test Executions</Typography>
      <TableContainer>
        <Table sx={{ minWidth: 650 }}>
          <TableHead>
            <TableRow sx={{ bgcolor: 'background.default' }}>
              <TableCell>
                <Tooltip title="The time the test was executed">
                  <TableSortLabel active={orderBy === 'timestamp'} direction={orderBy === 'timestamp' ? order : 'asc'} onClick={createSortHandler('timestamp')}>
                    Timestamp
                  </TableSortLabel>
                </Tooltip>
              </TableCell>
              <TableCell>
                <Tooltip title="The specific ammeter tested (e.g. Greenlee, Entes)">
                  <TableSortLabel active={orderBy === 'ammeter_type'} direction={orderBy === 'ammeter_type' ? order : 'asc'} onClick={createSortHandler('ammeter_type')}>
                    Ammeter
                  </TableSortLabel>
                </Tooltip>
              </TableCell>
              <TableCell align="center">
                <Tooltip title="Number of measurements expected">
                  <TableSortLabel active={orderBy === 'expected_samples'} direction={orderBy === 'expected_samples' ? order : 'asc'} onClick={createSortHandler('expected_samples')}>
                    Expected
                  </TableSortLabel>
                </Tooltip>
              </TableCell>
              <TableCell align="center">
                <Tooltip title="Number of successful measurements">
                  <TableSortLabel active={orderBy === 'successful_samples'} direction={orderBy === 'successful_samples' ? order : 'asc'} onClick={createSortHandler('successful_samples')}>
                    Successful
                  </TableSortLabel>
                </Tooltip>
              </TableCell>
              <TableCell align="center">
                <Tooltip title="The percentage of successful measurements during the run">
                  <TableSortLabel active={orderBy === 'passRate'} direction={orderBy === 'passRate' ? order : 'asc'} onClick={createSortHandler('passRate')}>
                    Pass Rate
                  </TableSortLabel>
                </Tooltip>
              </TableCell>
              <TableCell align="center">
                <Tooltip title="The final verdict of the test run">
                  <TableSortLabel active={orderBy === 'status'} direction={orderBy === 'status' ? order : 'asc'} onClick={createSortHandler('status')}>
                    Status
                  </TableSortLabel>
                </Tooltip>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedRuns.map((run, i) => {
              const expected = run.expected_samples || 0;
              const successful = run.successful_samples || 0;
              const passRate = expected > 0 ? ((successful / expected) * 100).toFixed(1) : 0;
              return (
                <TableRow 
                  key={i} 
                  hover 
                  onClick={() => navigate(`/run/${run.test_id}`)}
                  sx={{ cursor: 'pointer', transition: '0.2s', '&:hover': { bgcolor: 'action.hover' } }}
                >
                  <TableCell>{new Date(run.timestamp).toLocaleString()}</TableCell>
                  <TableCell sx={{ textTransform: 'uppercase', fontWeight: 500 }}>
                    {run.ammeter_type}
                  </TableCell>
                  <TableCell align="center">{expected}</TableCell>
                  <TableCell align="center">{successful}</TableCell>
                  <TableCell align="center">{passRate}%</TableCell>
                  <TableCell align="center">
                    <Chip label={run.status} size="small" color={getStatusColor(run.status)} />
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
      {runs.length === 0 && (
        <Box sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">No historical runs found.</Typography>
        </Box>
      )}
    </Paper>
  );
};

export default RunsTable;
