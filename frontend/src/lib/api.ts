import { HBARData, PriceHistoryData, MetricsSummary, HealthResponse, TokenData } from '@/types/api';

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

  async getTopTokens(limit: number = 10): Promise<TokenData[]> {
    try {
      return await this.fetchApi<TokenData[]>(`/tokens/top?limit=${limit}`);
    } catch (error) {
      console.error('Failed to fetch top tokens:', error);
      // Return mock data for development
      return [
        {
          token_id: '0.0.456858',
          name: 'USD Coin',
          symbol: 'USDC',
          price_usd: 1.00,
          market_cap: 6500000000,
          volume_24h: 182000000,
          price_change_24h: 0.02,
        },
        {
          token_id: '0.0.1456986',
          name: 'HBAR[X]',
          symbol: 'HBARX',
          price_usd: 0.155,
          market_cap: 65000000,
          volume_24h: 1200000,
          price_change_24h: 1.8,
        },
        {
          token_id: '0.0.731861',
          name: 'SaucerSwap',
          symbol: 'SAUCE',
          price_usd: 0.08,
          market_cap: 12000000,
          volume_24h: 850000,
          price_change_24h: -2.1,
        },
      ];
    }
  }

  async refreshTokenData(): Promise<boolean> {
    try {
      await fetch(`${this.baseUrl}/tokens/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      return true;
    } catch (error) {
      console.error('Failed to refresh token data:', error);
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
  topTokens: (limit: number = 10) => apiClient.getTopTokens(limit),
};