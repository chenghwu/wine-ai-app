export function getLastUpdatedLabel(rawValue: string): string {
  if (rawValue && rawValue !== "unknown") return rawValue;

  const twoWeeksAgo = new Date();
  twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14);

  return twoWeeksAgo.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }); // e.g., "April 24, 2025"
}