import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api",
  timeout: 15000,
});

export async function getHealth() {
  const response = await api.get("/health");
  return response.data;
}

export async function getDocuments() {
  const response = await api.get("/documents");
  return response.data;
}

export async function uploadDocument({ file, subject, description }) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("subject", subject || "General");
  if (description) {
    formData.append("description", description);
  }

  const response = await api.post("/documents/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function retryDocument(documentId) {
  const response = await api.post(`/documents/${documentId}/retry`);
  return response.data;
}

export async function sendChatMessage({ message, subject, documentId }) {
  const response = await api.post("/chat", {
    message,
    subject: subject || null,
    document_id: documentId || null,
  });
  return response.data;
}
