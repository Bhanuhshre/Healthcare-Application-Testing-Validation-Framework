const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

let authToken = null;

export function setAuthToken(token) {
  authToken = token;
}

async function request(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request to ${path} failed with status ${response.status}`);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export const api = {
  login: (email, password) => {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);
    return fetch(`${BASE_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form,
    }).then((r) => {
      if (!r.ok) throw new Error("Login failed");
      return r.json();
    });
  },
  listPatients: () => request("/api/patients"),
  createPatient: (patient) =>
    request("/api/patients", { method: "POST", body: JSON.stringify(patient) }),
  listDoctors: () => request("/api/doctors"),
  listAppointments: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/appointments${query ? `?${query}` : ""}`);
  },
  createAppointment: (appointment) =>
    request("/api/appointments", { method: "POST", body: JSON.stringify(appointment) }),
};
