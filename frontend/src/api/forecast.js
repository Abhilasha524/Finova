import { apiFetch } from "./client";

export function getForecast(months = 3) {
  return apiFetch(`/forecast/?months=${months}`);
}