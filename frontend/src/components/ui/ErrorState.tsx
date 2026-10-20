import React from 'react';
import { cn } from '../../utils/cn';
import { Button } from './Button';
import { AlertTriangle } from 'lucide-react';

export interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  message = 'Failed to load data from server.',
  onRetry,
  className,
}) => {
  return (
    <div
      className={cn(
        'flex flex-col sm:flex-row items-center justify-between gap-4 rounded-card border border-danger/40 bg-danger/10 p-5 shadow-sm',
        className
      )}
    >
      <div className="flex items-center gap-3">
        <div className="rounded-full bg-danger/20 p-2 text-danger flex-shrink-0">
          <AlertTriangle className="h-5 w-5" />
        </div>
        <p className="text-sm font-medium text-danger">{message}</p>
      </div>
      {onRetry && (
        <Button variant="ghost" size="sm" onClick={onRetry} className="border-danger/40 text-danger hover:bg-danger/20 hover:border-danger">
          Retry
        </Button>
      )}
    </div>
  );
};
