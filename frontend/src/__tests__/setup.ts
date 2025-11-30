/**
 * Test Setup and Fixtures
 * Provides mocking utilities and test data for React component tests
 */
import axios from "axios";

// Mock axios module
jest.mock("axios");
const mockedAxios = axios as jest.Mocked<typeof axios>;

/**
 * Test Data Fixtures
 */
export const mockProjects = [
  {
    record_id: 1,
    num_people: 2,
    revenue: 10000,
    total_costs: 1000,
    tax_amount: 1500,
    net_income_per_person: 4250,
    net_income_group: 8500,
    created_at: "2024-01-01T00:00:00Z",
  },
  {
    record_id: 2,
    num_people: 3,
    revenue: 20000,
    total_costs: 2000,
    tax_amount: 3000,
    net_income_per_person: 5333.33,
    net_income_group: 17000,
    created_at: "2024-01-02T00:00:00Z",
  },
];

export const mockTaxBrackets = [
  {
    bracket_id: 1,
    country: "US",
    income_min: 0,
    income_max: 10000,
    tax_rate: 0.1,
  },
  {
    bracket_id: 2,
    country: "US",
    income_min: 10000,
    income_max: 50000,
    tax_rate: 0.15,
  },
  {
    bracket_id: 3,
    country: "US",
    income_min: 50000,
    income_max: 100000,
    tax_rate: 0.22,
  },
];

export const mockPeople = [
  {
    person_id: 1,
    name: "Alice Smith",
    percentage: 50,
    revenue_assigned: 5000,
  },
  {
    person_id: 2,
    name: "Bob Johnson",
    percentage: 50,
    revenue_assigned: 5000,
  },
];

export const mockReports = {
  revenue_summary: {
    total_revenue: 100000,
    total_costs: 10000,
    net_income: 90000,
    average_project_revenue: 15000,
  },
  statistics: {
    total_projects: 6,
    total_people: 8,
    average_tax_rate: 0.18,
    highest_revenue: 25000,
  },
  top_people: [
    {
      name: "Alice Smith",
      total_revenue: 30000,
      total_net_income: 24000,
    },
    {
      name: "Bob Johnson",
      total_revenue: 25000,
      total_net_income: 20000,
    },
  ],
};

/**
 * API Mock Setup Utilities
 */
export function setupAxiosMocks() {
  mockedAxios.get.mockResolvedValue({ data: {} });
  mockedAxios.post.mockResolvedValue({ data: {} });
  mockedAxios.put.mockResolvedValue({ data: {} });
  mockedAxios.delete.mockResolvedValue({ data: {} });
}

export function mockGetProjects() {
  mockedAxios.get.mockResolvedValueOnce({ data: mockProjects });
}

export function mockGetTaxBrackets() {
  mockedAxios.get.mockResolvedValueOnce({ data: mockTaxBrackets });
}

export function mockGetPeople() {
  mockedAxios.get.mockResolvedValueOnce({ data: mockPeople });
}

export function mockGetReports() {
  mockedAxios.get.mockResolvedValueOnce({ data: mockReports });
}

export function mockCreateProject(data: Record<string, unknown>) {
  mockedAxios.post.mockResolvedValueOnce({ data });
}

export function mockGetErrors() {
  mockedAxios.get.mockRejectedValueOnce({
    response: { status: 404, data: { detail: "Not found" } },
  });
}

export { mockedAxios };
