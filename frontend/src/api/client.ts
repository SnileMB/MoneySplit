import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Types
export interface Person {
  name: string;
  work_share: number;
}

export interface ProjectCreate {
  num_people: number;
  revenue: number;
  costs: number[];
  country: string;
  tax_type: "Individual" | "Business";
  people: Person[];
}

export interface Record {
  id: number;
  num_people: number;
  revenue: number;
  total_costs: number;
  group_income: number;
  individual_income: number;
  tax_origin: string;
  tax_option: string;
  tax_amount: number;
  net_income_per_person: number;
  net_income_group: number;
  created_at: string;
}

export interface PersonResponse {
  id: number;
  name: string;
  work_share: number;
  gross_income: number;
  tax_paid: number;
  net_income: number;
}

export interface RecordWithPeople extends Record {
  people: PersonResponse[];
}

export interface Statistics {
  total_records: number;
  total_revenue: number;
  total_costs: number;
  total_tax: number;
  total_net_income: number;
  average_tax_rate: number;
  total_people_entries: number;
  unique_people: number;
}

export interface Forecast {
  success: boolean;
  predictions: {
    month: string;
    revenue: number;
    confidence: string;
    lower_bound: number;
    upper_bound: number;
    range: string;
  }[];
  trend: string;
  trend_strength: number;
  r2_score: number;
  confidence: string;
  confidence_description: string;
  historical_avg: number;
  model_slope: number;
  growth_rate: number;
  model_type: string;
  explanation: string;
  data_quality: string;
  recommendations?: string[];
}

// API Functions
export interface RecordUpdate {
  field: string;
  value: string | number;
}

export interface TaxBracket {
  id: number;
  country: string;
  tax_type: string;
  income_limit: number;
  rate: number;
}

export interface TaxBracketCreate {
  country: string;
  tax_type: string;
  income_limit: number;
  rate: number;
}

export const projectsApi = {
  create: (data: ProjectCreate) => apiClient.post("/projects", data),
  getRecords: (limit = 10) => apiClient.get<Record[]>(`/records?limit=${limit}`),
  getRecord: (id: number) => apiClient.get<RecordWithPeople>(`/records/${id}`),
  updateRecord: (id: number, update: RecordUpdate) => apiClient.put(`/records/${id}`, update),
  deleteRecord: (id: number) => apiClient.delete(`/records/${id}`),
};

export const taxBracketsApi = {
  getTaxBrackets: (country: string, taxType: string) => apiClient.get<TaxBracket[]>(`/tax-brackets?country=${country}&tax_type=${taxType}`),
  createTaxBracket: (data: TaxBracketCreate) => apiClient.post("/tax-brackets", data),
  deleteTaxBracket: (id: number) => apiClient.delete(`/tax-brackets/${id}`),
};

export const reportsApi = {
  getStatistics: () => apiClient.get<Statistics>("/reports/statistics"),
  getRevenueSummary: () => apiClient.get("/reports/revenue-summary"),
  getTopPeople: (limit = 10) => apiClient.get(`/reports/top-people?limit=${limit}`),
};

export const forecastApi = {
  getRevenueForecast: (months = 3) => apiClient.get<Forecast>(`/forecast/revenue?months=${months}`),
  getComprehensive: () => apiClient.get("/forecast/comprehensive"),
  getTaxOptimization: () => apiClient.get("/forecast/tax-optimization"),
  getTrends: () => apiClient.get("/forecast/trends"),
};

export const exportApi = {
  exportRecordPDF: (id: number) => `${API_BASE_URL}/export/record/${id}/pdf`,
  exportSummaryPDF: () => `${API_BASE_URL}/export/summary/pdf`,
  exportForecastPDF: () => `${API_BASE_URL}/export/forecast/pdf`,
};

export const visualizationApi = {
  getRevenueSummary: () => `${API_BASE_URL}/visualizations/revenue-summary`,
  getMonthlyTrends: () => `${API_BASE_URL}/visualizations/monthly-trends`,
  getWorkDistribution: () => `${API_BASE_URL}/visualizations/work-distribution`,
  getTaxComparison: () => `${API_BASE_URL}/visualizations/tax-comparison`,
  getPersonPerformance: (name: string) => `${API_BASE_URL}/visualizations/person-performance/${name}`,
  getProjectProfitability: () => `${API_BASE_URL}/visualizations/project-profitability`,
};
