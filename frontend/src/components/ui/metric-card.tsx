import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './card';
import { Skeleton } from './skeleton';
import { cn, formatCurrency, formatLargeNumber, formatPercentage, getPercentageColor } from '@/lib/utils';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon?: React.ReactNode;
  isLoading?: boolean;
  className?: string;
  valuePrefix?: string;
  valueSuffix?: string;
  trend?: 'up' | 'down' | 'neutral';
}

export function MetricCard({
  title,
  value,
  change,
  changeLabel = '24h',
  icon,
  isLoading = false,
  className,
  valuePrefix = '',
  valueSuffix = '',
  trend,
}: MetricCardProps) {
  if (isLoading) {
    return (
      <Card className={cn('p-6', className)}>
        <div className="flex items-center justify-between space-y-0 pb-2">
          <Skeleton className="h-4 w-[100px]" />
          {icon && <Skeleton className="h-4 w-4" />}
        </div>
        <div className="space-y-2">
          <Skeleton className="h-8 w-[120px]" />
          <Skeleton className="h-4 w-[80px]" />
        </div>
      </Card>
    );
  }

  const getTrendIcon = () => {
    if (trend === 'up' || (change !== undefined && change > 0)) {
      return <TrendingUp className="h-4 w-4 text-crypto-green" />;
    }
    if (trend === 'down' || (change !== undefined && change < 0)) {
      return <TrendingDown className="h-4 w-4 text-crypto-red" />;
    }
    return <Minus className="h-4 w-4 text-muted-foreground" />;
  };

  const formatValue = (val: string | number): string => {
    if (typeof val === 'number') {
      if (valuePrefix === '$') {
        return formatCurrency(val);
      }
      if (valueSuffix === '%') {
        return formatPercentage(val);
      }
      if (val > 1000000) {
        return formatLargeNumber(val);
      }
      return val.toLocaleString();
    }
    return val;
  };

  return (
    <Card className={cn('transition-all duration-200 hover:shadow-lg', className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">
          {valuePrefix}
          {formatValue(value)}
          {valueSuffix}
        </div>
        {change !== undefined && (
          <div className="flex items-center pt-1">
            {getTrendIcon()}
            <p className={cn(
              'text-xs ml-1',
              getPercentageColor(change)
            )}>
              {formatPercentage(change)} {changeLabel}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

interface StatsGridProps {
  children: React.ReactNode;
  className?: string;
}

export function StatsGrid({ children, className }: StatsGridProps) {
  return (
    <div className={cn(
      'grid gap-4 md:gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
      className
    )}>
      {children}
    </div>
  );
}