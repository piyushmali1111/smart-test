import React from 'react';
import { cn } from '../../utils/cn';
import { DotsMenu } from './DotsMenu';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  subtitle?: string;
  menu?: boolean;
  onExportCsv?: () => void;
  exportFilename?: string;
  glow?: boolean;
  interactive?: boolean;
  headerAction?: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  menu = false,
  onExportCsv,
  exportFilename,
  glow = false,
  interactive = true,
  headerAction,
  children,
  className,
  ...props
}) => {
  return (
    <div
      className={cn(
        'group relative rounded-card border border-border bg-bg-2 p-5 transition-all duration-200',
        'shadow-card',
        interactive && 'hover:-translate-y-0.5 hover:border-border-strong hover:shadow-glow-sm',
        glow && 'border-border-strong shadow-glow-sm',
        className
      )}
      {...props}
    >
      {(title || subtitle || menu || headerAction) && (
        <div className="mb-4 flex items-center justify-between gap-2">
          <div>
            {title && (
              <h3 className="font-heading text-lg font-bold tracking-tight text-text-main">
                {title}
              </h3>
            )}
            {subtitle && (
              <p className="mt-0.5 text-xs text-text-muted">{subtitle}</p>
            )}
          </div>
          <div className="flex items-center gap-2">
            {headerAction}
            {menu && (
              <DotsMenu
                onExportCsv={onExportCsv}
                exportFilename={exportFilename || (title ? `${title.toLowerCase().replace(/\s+/g, '_')}.csv` : 'chart_data.csv')}
              />
            )}
          </div>
        </div>
      )}
      {children}
    </div>
  );
};
