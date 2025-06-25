'use client';

import React from 'react';
import useSWR from 'swr';
import { fetchers } from '@/lib/api';
import { TokenData } from '@/types/api';
import { formatCurrency, formatLargeNumber, formatPercentage } from '@/lib/utils';
import { Coins, TrendingUp, TrendingDown, BarChart3 } from 'lucide-react';

interface TokenRowProps {
  token: TokenData;
  rank: number;
  maxVolume: number;
}

function TokenRow({ token, rank, maxVolume }: TokenRowProps) {
  const volumePercentage = token.volume_24h ? (token.volume_24h / maxVolume) * 100 : 0;
  const isPositiveChange = (token.price_change_24h || 0) >= 0;

  return (
    <div className="flex items-center justify-between p-4 border-b border-border/50 hover:bg-muted/30 transition-colors">
      <div className="flex items-center space-x-4 flex-1">
        {/* Rank */}
        <div className="w-8 text-center">
          <span className="text-lg font-bold text-muted-foreground">#{rank}</span>
        </div>
        
        {/* Token Info */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <Coins className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-semibold text-foreground">{token.symbol}</div>
            <div className="text-sm text-muted-foreground">{token.name}</div>
          </div>
        </div>
      </div>

      {/* Metrics */}
      <div className="flex items-center space-x-8">
        {/* Price */}
        <div className="text-right min-w-[100px]">
          <div className="font-semibold">
            {token.price_usd ? formatCurrency(token.price_usd) : 'N/A'}
          </div>
          {token.price_change_24h !== null && (
            <div className={`text-sm flex items-center justify-end ${
              isPositiveChange ? 'text-green-600' : 'text-red-600'
            }`}>
              {isPositiveChange ? (
                <TrendingUp className="w-3 h-3 mr-1" />
              ) : (
                <TrendingDown className="w-3 h-3 mr-1" />
              )}
              {formatPercentage(token.price_change_24h)}
            </div>
          )}
        </div>

        {/* Market Cap */}
        <div className="text-right min-w-[120px]">
          <div className="text-sm text-muted-foreground">Market Cap</div>
          <div className="font-medium">
            {token.market_cap ? formatLargeNumber(token.market_cap) : 'N/A'}
          </div>
        </div>

        {/* Volume with Bar Chart */}
        <div className="text-right min-w-[150px]">
          <div className="text-sm text-muted-foreground">24h Volume</div>
          <div className="font-medium">
            {token.volume_24h ? formatLargeNumber(token.volume_24h) : 'N/A'}
          </div>
          {/* Volume Bar */}
          <div className="mt-1 h-2 bg-muted rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full transition-all duration-500"
              style={{ width: `${Math.max(5, volumePercentage)}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export function TokenChart() {
  const { data: tokens, error, isLoading } = useSWR('topTokens', () => fetchers.topTokens(10));

  if (error) {
    return (
      <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-6">
        <div className="flex items-center space-x-2">
          <BarChart3 className="w-5 h-5 text-destructive" />
          <p className="text-sm text-destructive font-medium">
            Failed to load token data. Showing sample data instead.
          </p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold tracking-tight">Top DeFi Tokens</h2>
            <p className="text-muted-foreground">
              Most active tokens on the Hedera network
            </p>
          </div>
          <BarChart3 className="w-8 h-8 text-muted-foreground" />
        </div>
        
        <div className="border rounded-lg overflow-hidden bg-card">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex items-center justify-between p-4 border-b border-border/50 animate-pulse">
              <div className="flex items-center space-x-4">
                <div className="w-8 h-6 bg-muted rounded" />
                <div className="w-10 h-10 bg-muted rounded-full" />
                <div className="space-y-2">
                  <div className="w-16 h-4 bg-muted rounded" />
                  <div className="w-24 h-3 bg-muted rounded" />
                </div>
              </div>
              <div className="flex space-x-8">
                <div className="w-20 h-6 bg-muted rounded" />
                <div className="w-24 h-6 bg-muted rounded" />
                <div className="w-28 h-6 bg-muted rounded" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const maxVolume = Math.max(...(tokens?.map(t => t.volume_24h || 0) || [0]));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Top DeFi Tokens</h2>
          <p className="text-muted-foreground">
            Most active tokens on the Hedera network
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <BarChart3 className="w-8 h-8 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">{tokens?.length || 0} tokens</span>
        </div>
      </div>

      <div className="border rounded-lg overflow-hidden bg-card shadow-sm">
        {/* Header */}
        <div className="flex items-center justify-between p-4 bg-muted/20 border-b">
          <div className="flex items-center space-x-4 flex-1">
            <div className="w-8"></div>
            <div className="font-semibold text-sm text-muted-foreground uppercase tracking-wide">
              Token
            </div>
          </div>
          <div className="flex items-center space-x-8">
            <div className="text-sm font-semibold text-muted-foreground uppercase tracking-wide min-w-[100px] text-right">
              Price
            </div>
            <div className="text-sm font-semibold text-muted-foreground uppercase tracking-wide min-w-[120px] text-right">
              Market Cap
            </div>
            <div className="text-sm font-semibold text-muted-foreground uppercase tracking-wide min-w-[150px] text-right">
              Volume (24h)
            </div>
          </div>
        </div>

        {/* Token List */}
        {tokens?.map((token, index) => (
          <TokenRow 
            key={token.token_id} 
            token={token} 
            rank={index + 1}
            maxVolume={maxVolume}
          />
        ))}

        {(!tokens || tokens.length === 0) && (
          <div className="p-8 text-center">
            <BarChart3 className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">No token data available</p>
          </div>
        )}
      </div>

      {tokens && tokens.length > 0 && (
        <div className="text-xs text-muted-foreground text-center">
          Data refreshed every 10 minutes • Volume bars show relative 24h trading activity
        </div>
      )}
    </div>
  );
}