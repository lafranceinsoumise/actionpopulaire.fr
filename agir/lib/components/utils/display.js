const NBSP = "\u00A0";

export function displayNumber(n, decimals) {
  if (!decimals) decimals = 0;
  const s = Math.round(n * Math.pow(10, decimals))
    .toString()
    .padStart(decimals + 1, "0");
  return (
    (s.slice(0, s.length - decimals) || "0") +
    (decimals > 0 ? "," + s.slice(s.length - decimals) : "")
  );
}

export function parsePrice(s) {
  const m = s.match(/^([0-9]+)(?:[,.]([0-9]{0,2}))?$/);

  if (m !== null) {
    const newText = m[1] + (m[2] || "00").slice(0, 3);
    return parseInt(newText);
  }

  return null;
}

export function displayPrice(n, forceCents = false) {
  if (!forceCents && n % 100 === 0) {
    return displayNumber(n / 100, 0) + NBSP + "€";
  }

  return displayNumber(n / 100, 2) + NBSP + "€";
}
