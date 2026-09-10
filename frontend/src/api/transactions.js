import { apiFetch } from "./client";

export function uploadTransactionsCsv(file) {
  const formData = new FormData();
  formData.append("file", file);

  return apiFetch("/transactions/upload", {
    method: "POST",
    body: formData,
    isFormData: true,
  });
}

export function listTransactions(skip = 0, limit = 100) {
  return apiFetch(`/transactions/?skip=${skip}&limit=${limit}`);
}