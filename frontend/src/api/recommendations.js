import { apiFetch } from "./client";

export function getRecommendations() {
  return apiFetch("/recommendations/");
}