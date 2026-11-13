let token = localStorage.getItem("token");

export function setToken(t) {
  token = t;
  t ? localStorage.setItem("token", t) : localStorage.removeItem("token");
}
export const hasToken = () => Boolean(token);

/** ข้อผิดพลาดจาก API: messages = รายการข้อความที่แสดงให้ผู้ใช้ได้ทั้งหมด */
export class ApiError extends Error {
  constructor(messages) {
    super(messages[0]);
    this.messages = messages;
  }
}

async function request(path, options = {}) {
  const headers = {
    ...(options.body && !(options.body instanceof FormData) ? { "Content-Type": "application/json" } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
  let res;
  try {
    res = await fetch(`/api${path}`, { ...options, headers });
  } catch {
    throw new ApiError(["เชื่อมต่อเซิร์ฟเวอร์ไม่ได้ กรุณาลองใหม่อีกครั้ง"]);
  }
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    if (res.status === 401 && token) {
      setToken(null); // token หมดอายุ -> ให้ App พากลับหน้าเข้าสู่ระบบ
      window.dispatchEvent(new Event("auth-expired"));
    }
    const d = body.detail;
    const messages = typeof d === "string" ? [d] : Array.isArray(d?.errors) ? d.errors : ["เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง"];
    throw new ApiError(messages);
  }
  return body;
}

const send = (method, path, data) => request(path, { method, body: data === undefined ? undefined : JSON.stringify(data) });
const qs = (o) => {
  const p = new URLSearchParams(Object.entries(o).filter(([, v]) => v));
  return p.toString() ? `?${p}` : "";
};

export const api = {
  register: (d) => send("POST", "/auth/register", d),
  login: (d) => send("POST", "/auth/login", d),
  me: () => request("/me"),
  meta: () => request("/meta"),
  stats: () => request("/stats"),
  cases: (filters = {}) => request(`/cases${qs(filters)}`),
  createCase: (d) => send("POST", "/cases", d),
  createHero: (d) => send("POST", "/heroes", d),
  updateHero: (id, d) => send("PUT", `/heroes/${id}`, d),
  setHeroStatus: (id, status) => send("PATCH", `/heroes/${id}/status`, { status }),
  myHeroes: () => request("/me/heroes"),
  myCases: () => request("/me/cases"),
  myRequests: () => request("/me/requests"),
  match: (id) => request(`/matches/${id}`),
  sendMessage: (id, body) => send("POST", `/matches/${id}/messages`, { body }),
  sharePhone: (id) => send("POST", `/matches/${id}/share-phone`),
  decline: (id) => send("POST", `/matches/${id}/decline`),
  confirm: (id) => send("POST", `/matches/${id}/confirm`),
  upload: (file) => {
    const fd = new FormData();
    fd.append("file", file);
    return request("/uploads", { method: "POST", body: fd });
  },
};
