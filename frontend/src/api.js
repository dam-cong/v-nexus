const API_BASE = import.meta.env.VITE_API_BASE || "";

export class OfflineError extends Error {
  constructor(message = 'Không có kết nối mạng') {
    super(message);
    this.name = 'OfflineError';
  }
}

export function getToken() {
  return localStorage.getItem("vnexus_token");
}

export function setToken(token) {
  localStorage.setItem("vnexus_token", token);
}

export function removeToken() {
  localStorage.removeItem("vnexus_token");
  localStorage.removeItem("vnexus_user");
}

export function getUser() {
  try {
    const raw = localStorage.getItem("vnexus_user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setUser(user) {
  localStorage.setItem("vnexus_user", JSON.stringify(user));
}

export async function apiFetch(path, options = {}) {
  if (!navigator.onLine) {
    throw new OfflineError();
  }
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (res.status === 401) {
    removeToken();
    window.location.reload();
    throw new Error("Phiên đăng nhập đã hết hạn");
  }
  return res;
}
