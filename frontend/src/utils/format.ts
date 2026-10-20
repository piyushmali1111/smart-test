export function formatSeconds(sec: number): string {
  if (sec < 0.001) return '< 1 ms';
  if (sec < 1) return `${Math.round(sec * 1000)} ms`;
  return `${sec.toFixed(1)} s`;
}

export function formatMs(ms: number): string {
  if (ms < 1) return `${ms.toFixed(1)} ms`;
  return `${Math.round(ms)} ms`;
}

export function formatPct(val: number, decimals = 1): string {
  return `${val.toFixed(decimals)}%`;
}

export function formatNumber(val: number): string {
  return new Intl.NumberFormat().format(val);
}

export function formatRisk(val: number): string {
  return val.toFixed(2);
}
