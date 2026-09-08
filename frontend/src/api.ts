import axios, { type AxiosResponse } from 'axios';

export interface Measurement {
  timestamp: string;
  value: number | null;
  success: boolean;
}

export interface RunError {
  timestamp: string;
  error_type: string;
  error_message: string;
}

export interface RunStatistics {
  mean?: number | null;
  median?: number | null;
  std_dev?: number | null;
  min?: number | null;
  max?: number | null;
  rms?: number | null;
  variance?: number | null;
  cv?: number | null;
  snr?: number | null;
}

export interface RunData {
  test_id: string;
  timestamp: string;
  ammeter_type: string;
  status: string;
  expected_samples: number;
  successful_samples: number;
  statistics?: RunStatistics;
  measurements?: Measurement[];
  errors?: RunError[];
}

export interface ConsistencyStats {
  historical_runs: number;
  mean_of_means: number;
  std_dev_of_means: number;
}

export interface ConsistencyData {
  [key: string]: ConsistencyStats;
}

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
});

export const getRuns = (): Promise<AxiosResponse<RunData[]>> => api.get('/runs');
export const getConsistency = (): Promise<AxiosResponse<ConsistencyData>> => api.get('/consistency');
export interface RunParams {
  ammeter?: string;
  count?: number | null;
  duration?: number | null;
  frequency?: number | null;
}

export const runTests = (params?: RunParams): Promise<AxiosResponse<any>> => api.post('/run', params || {});
export const runErrors = (): Promise<AxiosResponse<any>> => api.post('/run_errors');

export default api;
