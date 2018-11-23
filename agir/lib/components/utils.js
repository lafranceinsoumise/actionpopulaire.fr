const NBSP = '\xa0';

export function displayNumber(n, decimals) {
  if (!decimals) decimals = 0;
  const s = Math.round(n * Math.pow(10, decimals)).toString().padStart(decimals + 1, '0');
  return (s.slice(0, -decimals) | '0') + ',' + s.slice(-2);
}

export function displayPrice(n) {
  return displayNumber(n, 2) + NBSP + '€';
}
