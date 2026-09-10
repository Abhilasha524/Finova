import { apiFetch } from "./client";

export function getGoals() {
  return apiFetch("/goals/");
}

export function createGoal(goal) {
  return apiFetch("/goals/", {
    method: "POST",
    body: goal,
  });
}

export function deleteGoal(goalId) {
  return apiFetch(`/goals/${goalId}`, {
    method: "DELETE",
  });
}