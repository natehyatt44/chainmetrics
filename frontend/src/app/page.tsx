'use client';

import React from 'react';
import { SWRConfig } from 'swr';
import { Header } from '@/components/layout/header';
import { HBARMetrics } from '@/components/ui/hbar-metrics';
import { NetworkStatus } from '@/components/ui/network-status';
import { useCurrentHBARData, useMetricsSummary } from '@/hooks/useHBARData';

export default function Home() {
  const { refresh: refreshHBAR } = useCurrentHBARData();
  const { refresh: refreshSummary, data: summary } = useMetricsSummary();

  const handleRefresh = async () => {
    await Promise.all([refreshHBAR(), refreshSummary()]);
  };

  return (
    <SWRConfig
      value={{
        refreshInterval: 30000,
        revalidateOnFocus: false,
        dedupingInterval: 10000,
      }}
    >
      <div className="min-h-screen bg-background">
        <Header
          onRefresh={handleRefresh}
          lastUpdated={summary?.timestamp}
        />
        
        <main className="container mx-auto px-4 py-8 space-y-8">
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
              Hedera Analytics Dashboard
            </h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Real-time metrics and insights for the Hedera Hashgraph network and HBAR token
            </p>
          </div>

          <div className="space-y-12">
            <HBARMetrics />
            <NetworkStatus />
          </div>

          <footer className="border-t pt-8 mt-16">
            <div className="flex flex-col sm:flex-row justify-between items-center text-sm text-muted-foreground">
              <p>© 2025 ChainMetrics. Real-time Hedera analytics.</p>
              <p>Data provided by CoinGecko and Hedera Mirror Node</p>
            </div>
          </footer>
        </main>
      </div>
    </SWRConfig>
  );
}
