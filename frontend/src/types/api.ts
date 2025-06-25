export interface HBARData {
  timestamp: string;
  price_usd: number;
  market_cap: number;
  volume_24h: number;
  price_change_24h: number;
  circulating_supply: number;
  market_cap_rank: number;
}

export interface PriceHistoryData {
  timestamp: string;
  price_usd: number;
  volume_24h: number;
}

export interface NetworkMetrics {
  status: string;
  tps: number | null;
  transactions_24h: number | null;
}

export interface TokenMetrics {
  status: string;
  top_tokens: TokenData[];
}

export interface TokenData {
  token_id: string;
  name: string;
  symbol: string;
  price_usd: number | null;
  market_cap: number | null;
  volume_24h: number | null;
  price_change_24h: number | null;
}

export interface MetricsSummary {
  timestamp: string;
  hbar: HBARData | null;
  network: NetworkMetrics;
  tokens: TokenMetrics;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  database_connected: boolean;
  version: string;
}

export interface ApiError {
  message: string;
  status?: number;
}