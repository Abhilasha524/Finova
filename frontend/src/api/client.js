import { getToken } from "./token";

export const API_BASE_URL = "http://127.0.0.1:8000";

export async function apiFetch(
  path,
  {
    method = "GET",
    body,
    isFormData = false,
    requiresAuth = true,
  } = {}
) {
  const headers = {};

  if (!isFormData && body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  if (requiresAuth) {
    const token = getToken();

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: isFormData
      ? body
      : body !== undefined
      ? JSON.stringify(body)
      : undefined,
  });

  const text = await response.text();

  let data = null;

  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;

    if (data?.detail) {
      if (Array.isArray(data.detail)) {
        message = data.detail
          .map((item) => {
            const field = item.loc?.slice(1).join(".") || "field";
            return `${field}: ${item.msg}`;
          })
          .join(" | ");
      } else {
        message = data.detail;
      }
    }

    const error = new Error(message);
    error.status = response.status;
    error.data = data;

    throw error;
  }

  return data;
}