import { API_BASE_URL, apiFetch } from "./client";

export function registerUser(email, password) {
  return apiFetch("/auth/register", {
    method: "POST",
    body: { email, password },
    requiresAuth: false,
  });
}

export async function loginUser(email, password) {
  // FastAPI's OAuth2PasswordRequestForm expects form-urlencoded data, not
  // JSON - this is why login can't go through the shared apiFetch helper
  // above. The field is literally called "username" per the OAuth2 spec,
  // even though we're sending an email address into it.
  const formBody = new URLSearchParams();
  formBody.append("grant_type", "password");
  formBody.append("username", email);
  formBody.append("password", password);

  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    body: formBody,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data && data.detail ? data.detail : "Login failed");
  }

  return data; // { access_token, token_type }
}