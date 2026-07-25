import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

export const complaintsApi = {
  list: () => api.get("/complaints").then((r) => r.data),
  get: (id) => api.get(`/complaints/${id}`).then((r) => r.data),
  commit: (payload) => api.post("/complaints", payload).then((r) => r.data),
  update: (id, payload) => api.put(`/complaints/${id}`, payload).then((r) => r.data),
  dashboardStats: () => api.get("/complaints/stats/dashboard").then((r) => r.data),
};

export const copilotApi = {
  sendMessage: (sessionId, message, existingFields) =>
    api
      .post("/copilot/message", {
        session_id: sessionId,
        message,
        existing_fields: existingFields || {},
      })
      .then((r) => r.data),

  upload: (sessionId, file, existingFields) => {
    const form = new FormData();
    form.append("session_id", sessionId);
    form.append("existing_fields_json", JSON.stringify(existingFields || {}));
    form.append("file", file);
    return api
      .post("/copilot/upload", form, { headers: { "Content-Type": "multipart/form-data" } })
      .then((r) => r.data);
  },
};

export default api;
