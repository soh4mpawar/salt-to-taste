// Format grams to human-readable measurement
export function formatSalt(grams: number, saltType: string = "Diamond Crystal Kosher"): string {
  const tsp = gramsToTsp(grams, saltType);
  if (tsp < 0.25) return `${grams.toFixed(1)}g`;
  if (tsp < 1) return `${(tsp * 4).toFixed(0)}¼ tsp (${grams.toFixed(1)}g)`;
  if (tsp < 3) return `${tsp.toFixed(1)} tsp (${grams.toFixed(1)}g)`;
  const tbsp = tsp / 3;
  return `${tbsp.toFixed(1)} tbsp (${grams.toFixed(1)}g)`;
}

const DENSITY_G_PER_TSP: Record<string, number> = {
  "Diamond Crystal Kosher": 4.8,
  "Morton Kosher": 7.7,
  "Fine Sea Salt": 5.7,
  "Table Salt": 5.9,
  "Maldon Flake": 2.8,
};

export function gramsToTsp(grams: number, saltType: string): number {
  const density = DENSITY_G_PER_TSP[saltType] || 5.0;
  return grams / density;
}

export function getSeverityColor(severity: string): string {
  switch (severity) {
    case "mild": return "text-yellow-600 bg-yellow-50";
    case "moderate": return "text-orange-600 bg-orange-50";
    case "severe": return "text-red-600 bg-red-50";
    default: return "text-green-600 bg-green-50";
  }
}

export function getSodiumWarningLevel(sodiumMg: number, limitMg: number = 2300): "safe" | "caution" | "warning" {
  const pct = sodiumMg / limitMg;
  if (pct > 0.5) return "warning";
  if (pct > 0.3) return "caution";
  return "safe";
}
