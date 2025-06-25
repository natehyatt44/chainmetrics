'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './card';
import { MetricCard } from './metric-card';
import { useMetricsSummary } from '@/hooks/useHBARData';
import { Activity, Zap, Clock } from 'lucide-react';

export function NetworkStatus() {
  const { data: summary, isLoading } = useMetricsSummary();

  const networkData = summary?.network;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Network Status</h2>
          <p className="text-muted-foreground">
            Hedera network performance metrics
          </p>
        </div>
      </div>

      {networkData?.status === 'coming_soon' ? (
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center gap-2">
              <Activity className="h-5 w-5 text-muted-foreground" />
              Network Metrics Coming Soon
            </CardTitle>
            <CardDescription>
              Real-time TPS and transaction data will be available soon
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 md:gap-6 grid-cols-1 sm:grid-cols-2">
            <MetricCard
              title="Transactions Per Second"
              value="TBD"
              icon={<Zap className="h-4 w-4 text-muted-foreground" />}
              isLoading={isLoading}
            />
            <MetricCard
              title="24h Transactions"
              value="TBD"
              icon={<Clock className="h-4 w-4 text-muted-foreground" />}
              isLoading={isLoading}
            />
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:gap-6 grid-cols-1 sm:grid-cols-2">
          <MetricCard
            title="Transactions Per Second"
            value={networkData?.tps || 0}
            icon={<Zap className="h-4 w-4 text-muted-foreground" />}
            isLoading={isLoading}
          />
          <MetricCard
            title="24h Transactions"
            value={networkData?.transactions_24h || 0}
            icon={<Clock className="h-4 w-4 text-muted-foreground" />}
            isLoading={isLoading}
          />
        </div>
      )}
    </div>
  );
}