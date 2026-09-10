import { apiFetch } from "./client";

export function getPersona() {
  return apiFetch("/persona/");
}