import { apiFetch } from "./client";

export function getAnalyticsSummary() {
  return apiFetch("/analytics/summary");
}