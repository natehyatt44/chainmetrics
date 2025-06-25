import { HBARData, PriceHistoryData, MetricsSummary, HealthResponse } from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async fetchApi<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async getHealth(): Promise<HealthResponse> {
    return this.fetchApi<HealthResponse>('/health');
  }

  async getCurrentHBARData(): Promise<HBARData | null> {
    try {
      return await this.fetchApi<HBARData>('/hbar/current');
    } catch (error) {
      console.error('Failed to fetch current HBAR data:', error);
      return null;
    }
  }

  async getHBARHistory(days: number = 7): Promise<PriceHistoryData[]> {
    try {
      return await this.fetchApi<PriceHistoryData[]>(`/hbar/history?days=${days}`);
    } catch (error) {
      console.error('Failed to fetch HBAR history:', error);
      return [];
    }
  }

  async getMetricsSummary(): Promise<MetricsSummary | null> {
    try {
      return await this.fetchApi<MetricsSummary>('/metrics/summary');
    } catch (error) {
      console.error('Failed to fetch metrics summary:', error);
      return null;
    }
  }

  async refreshHBARData(): Promise<boolean> {
    try {
      await fetch(`${this.baseUrl}/hbar/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      return true;
    } catch (error) {
      console.error('Failed to refresh HBAR data:', error);
      return false;
    }
  }
}

export const apiClient = new ApiClient(API_BASE_URL);

// SWR fetcher functions
export const fetchers = {
  hbarCurrent: () => apiClient.getCurrentHBARData(),
  hbarHistory: (days: number) => apiClient.getHBARHistory(days),
  metricsSummary: () => apiClient.getMetricsSummary(),
  health: () => apiClient.getHealth(),
};