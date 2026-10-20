import React from 'react';
import { cn } from '../../utils/cn';
import { Button } from './Button';
import { FolderSearch } from 'lucide-react';

export interface EmptyStateProps {
  icon?: React.ReactNode;
  message: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  message,
  actionLabel,
  onAction,
  className,
}) => {
  return (
    <div className={cn('flex flex-col items-center justify-center p-8 text-center', className)}>
      <div className="mb-3 rounded-full bg-bg-3 border border-border p-3 text-accent">
        {icon || <FolderSearch className="h-6 w-6" />}
      </div>
      <p className="text-sm font-medium text-text-muted mb-4 max-w-xs">{message}</p>
      {actionLabel && onAction && (
        <Button variant="primary" size="sm" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
};
