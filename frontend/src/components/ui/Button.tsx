import React from 'react';
import { cn } from '../../utils/cn';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost' | 'icon';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      icon,
      children,
      className,
      disabled,
      ...props
    },
    ref
  ) => {
    const baseStyles =
      'inline-flex items-center justify-center font-medium rounded-btn transition-all duration-200 active:scale-98 disabled:opacity-50 disabled:pointer-events-none cursor-pointer focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand focus-visible:outline-offset-2';

    const sizeStyles = {
      sm: 'text-xs px-3 py-1.5 gap-1.5 h-8',
      md: 'text-sm px-4 py-2 gap-2 h-10',
      lg: 'text-base px-6 py-2.5 gap-2.5 h-12',
    };

    const iconSizeStyles = {
      sm: 'p-1.5 h-8 w-8',
      md: 'p-2 h-10 w-10',
      lg: 'p-2.5 h-12 w-12',
    };

    const variantStyles = {
      primary:
        'bg-brand text-[#0B1020] font-semibold border border-brand/50 hover:bg-[#8AA4FF] hover:shadow-glow-sm',
      ghost:
        'border border-[rgba(148,163,255,0.25)] text-text-muted bg-transparent hover:text-text-main hover:border-brand hover:bg-bg-4',
      icon:
        'border border-transparent text-text-muted hover:text-brand hover:bg-bg-4 hover:border-border',
    };

    const isIconOnly = variant === 'icon' || (!children && icon);

    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={cn(
          baseStyles,
          isIconOnly ? iconSizeStyles[size] : sizeStyles[size],
          variantStyles[variant],
          className
        )}
        {...props}
      >
        {loading ? (
          <Loader2 className="animate-spin text-[#0B1020] h-4 w-4" />
        ) : (
          icon && <span className="flex-shrink-0">{icon}</span>
        )}
        {children && <span>{children}</span>}
      </button>
    );
  }
);

Button.displayName = 'Button';
