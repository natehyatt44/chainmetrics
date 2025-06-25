'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { RefreshCw, Sun, Moon } from 'lucide-react';

interface HeaderProps {
  onRefresh?: () => void;
  isRefreshing?: boolean;
  lastUpdated?: string;
}

export function Header({ onRefresh, isRefreshing = false, lastUpdated }: HeaderProps) {
  const [isDark, setIsDark] = React.useState(false);

  React.useEffect(() => {
    // Check for saved theme preference or default to dark mode
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const shouldBeDark = savedTheme === 'dark' || (!savedTheme && prefersDark);
    
    setIsDark(shouldBeDark);
    document.documentElement.classList.toggle('dark', shouldBeDark);
  }, []);

  const toggleTheme = () => {
    const newTheme = !isDark;
    setIsDark(newTheme);
    document.documentElement.classList.toggle('dark', newTheme);
    localStorage.setItem('theme', newTheme ? 'dark' : 'light');
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-full bg-gradient-to-r from-hedera-500 to-hedera-600" />
            <div>
              <h1 className="text-xl font-bold">ChainMetrics</h1>
              <p className="text-xs text-muted-foreground">Hedera Analytics</p>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {lastUpdated && (
            <div className="hidden sm:block text-sm text-muted-foreground">
              Last updated: {new Date(lastUpdated).toLocaleTimeString()}
            </div>
          )}
          
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className={cn(
              'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
              'disabled:pointer-events-none disabled:opacity-50',
              'hover:bg-accent hover:text-accent-foreground',
              'h-9 w-9'
            )}
            title="Refresh data"
          >
            <RefreshCw className={cn('h-4 w-4', isRefreshing && 'animate-spin')} />
          </button>

          <button
            onClick={toggleTheme}
            className={cn(
              'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
              'hover:bg-accent hover:text-accent-foreground',
              'h-9 w-9'
            )}
            title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
          >
            {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>
        </div>
      </div>
    </header>
  );
}