'use client';

import React from 'react';
import { MetricCard, StatsGrid } from './metric-card';
import { useCurrentHBARData } from '@/hooks/useHBARData';
import { formatCurrency, formatLargeNumber, formatPercentage } from '@/lib/utils';
import { DollarSign, TrendingUp, BarChart3, Hash } from 'lucide-react';

export function HBARMetrics() {
  const { data: hbarData, isLoading, error } = useCurrentHBARData();

  if (error) {
    return (
      <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4">
        <p className="text-sm text-destructive">
          Failed to load HBAR data. Please try refreshing the page.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">HBAR Metrics</h2>
          <p className="text-muted-foreground">
            Real-time Hedera Hashgraph token metrics
          </p>
        </div>
      </div>

      <StatsGrid>
        <MetricCard
          title="Price (USD)"
          value={hbarData?.price_usd || 0}
          change={hbarData?.price_change_24h}
          icon={<DollarSign className="h-4 w-4 text-muted-foreground" />}
          isLoading={isLoading}
          valuePrefix="$"
        />

        <MetricCard
          title="Market Cap"
          value={formatLargeNumber(hbarData?.market_cap || 0)}
          icon={<BarChart3 className="h-4 w-4 text-muted-foreground" />}
          isLoading={isLoading}
        />

        <MetricCard
          title="24h Volume"
          value={formatLargeNumber(hbarData?.volume_24h || 0)}
          icon={<TrendingUp className="h-4 w-4 text-muted-foreground" />}
          isLoading={isLoading}
        />

        <MetricCard
          title="Market Rank"
          value={hbarData?.market_cap_rank || 0}
          icon={<Hash className="h-4 w-4 text-muted-foreground" />}
          isLoading={isLoading}
          valuePrefix="#"
        />
      </StatsGrid>

      {hbarData && (
        <div className="grid gap-4 md:gap-6 grid-cols-1 lg:grid-cols-2">
          <MetricCard
            title="Circulating Supply"
            value={formatLargeNumber(hbarData.circulating_supply)}
            className="col-span-1"
            valueSuffix=" HBAR"
          />
          
          <MetricCard
            title="Price Change (24h)"
            value={formatPercentage(hbarData.price_change_24h)}
            change={hbarData.price_change_24h}
            className="col-span-1"
          />
        </div>
      )}
    </div>
  );
}