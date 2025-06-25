import useSWR from 'swr';
import { fetchers } from '@/lib/api';
import { HBARData, PriceHistoryData, MetricsSummary } from '@/types/api';

export function useCurrentHBARData() {
  const { data, error, isLoading, mutate } = useSWR<HBARData | null>(
    'hbar-current',
    fetchers.hbarCurrent,
    {
      refreshInterval: 30000, // Refresh every 30 seconds
      revalidateOnFocus: true,
      dedupingInterval: 10000, // Dedupe requests within 10 seconds
    }
  );

  return {
    data,
    error,
    isLoading,
    refresh: mutate,
  };
}

export function useHBARHistory(days: number = 7) {
  const { data, error, isLoading } = useSWR<PriceHistoryData[]>(
    ['hbar-history', days],
    () => fetchers.hbarHistory(days),
    {
      refreshInterval: 300000, // Refresh every 5 minutes
      revalidateOnFocus: false,
      dedupingInterval: 60000, // Dedupe requests within 1 minute
    }
  );

  return {
    data: data || [],
    error,
    isLoading,
  };
}

export function useMetricsSummary() {
  const { data, error, isLoading, mutate } = useSWR<MetricsSummary | null>(
    'metrics-summary',
    fetchers.metricsSummary,
    {
      refreshInterval: 60000, // Refresh every minute
      revalidateOnFocus: true,
      dedupingInterval: 30000, // Dedupe requests within 30 seconds
    }
  );

  return {
    data,
    error,
    isLoading,
    refresh: mutate,
  };
}