import type { Config } from 'tailwindcss';

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bg-0': 'var(--bg-0)',
        'bg-1': 'var(--bg-1)',
        'bg-2': 'var(--bg-2)',
        'bg-3': 'var(--bg-3)',
        'bg-4': 'var(--bg-4)',

        brand: 'var(--brand)',
        'brand-200': 'var(--brand-200)',
        'brand-600': 'var(--brand-600)',
        'brand-800': 'var(--brand-800)',
        'brand-900': 'var(--brand-900)',
        accent: 'var(--accent)',

        'text-main': 'var(--text)',
        'text-muted': 'var(--text-muted)',
        'text-dim': 'var(--text-dim)',

        border: 'var(--border)',
        'border-strong': 'var(--border-strong)',

        danger: 'var(--danger)',
        warn: 'var(--warn)',
        teal: 'var(--teal)',
        lavender: 'var(--lavender)',
        slate: 'var(--slate)',
        success: 'var(--success)',
      },
      boxShadow: {
        'glow-sm': 'var(--glow-sm)',
        'glow-md': 'var(--glow-md)',
        'glow-accent': 'var(--glow-accent)',
        card: 'var(--shadow-card)',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        heading: ['Manrope', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        card: '20px',
        panel: '14px',
        pill: '12px',
        btn: '10px',
      },
    },
  },
  plugins: [],
} satisfies Config;
