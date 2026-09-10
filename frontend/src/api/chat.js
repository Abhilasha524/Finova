import { apiFetch } from "./client";

export function sendChatMessage(message) {
  return apiFetch("/chat/", {
    method: "POST",
    body: {
      message,
    },
  });
}