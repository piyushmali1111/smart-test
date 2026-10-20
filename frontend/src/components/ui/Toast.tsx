import React, { useEffect } from 'react';
import { cn } from '../../utils/cn';
import { CheckCircle2, AlertCircle, X } from 'lucide-react';

export interface ToastProps {
  message: string;
  type?: 'success' | 'error' | 'info';
  onClose: () => void;
  duration?: number;
}

export const Toast: React.FC<ToastProps> = ({
  message,
  type = 'success',
  onClose,
  duration = 3500,
}) => {
  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [onClose, duration]);

  const icons = {
    success: <CheckCircle2 className="h-4 w-4 text-success" />,
    error: <AlertCircle className="h-4 w-4 text-danger" />,
    info: <CheckCircle2 className="h-4 w-4 text-accent" />,
  };

  return (
    <div
      className={cn(
        'fixed bottom-6 right-6 z-50 flex items-center gap-3 rounded-panel border border-border-strong bg-bg-2/95 px-4 py-3 text-xs sm:text-sm font-medium text-text-main shadow-glow-sm backdrop-blur-md animate-in slide-in-from-bottom-5 duration-200'
      )}
    >
      {icons[type]}
      <span>{message}</span>
      <button
        type="button"
        onClick={onClose}
        className="ml-2 text-text-muted hover:text-text-main transition-colors"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
};
