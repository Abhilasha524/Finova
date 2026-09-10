import { apiFetch } from "./client";

export function detectAnomalies() {
  return apiFetch("/anomalies/detect", { method: "POST" });
}

export function listAnomalies() {
  return apiFetch("/anomalies/");
}