let token = localStorage.getItem("token");

export function setToken(t) {
  token = t;
  t ? localStorage.setItem("token", t) : localStorage.removeItem("token");
}
export const hasToken = () => Boolean(token);

async function request(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    if (res.status === 401 && token) setToken(null); // token หมดอายุ
    const detail = typeof body.detail === "string" ? body.detail : "ข้อมูลที่กรอกไม่ถูกต้อง กรุณาตรวจสอบอีกครั้ง";
    throw new Error(detail);
  }
  return body;
}

const post = (path, data) => request(path, { method: "POST", body: JSON.stringify(data) });
const qs = (o) => {
  const p = new URLSearchParams(Object.entries(o).filter(([, v]) => v));
  return p.toString() ? `?${p}` : "";
};

export const api = {
  register: (d) => post("/auth/register", d),
  login: (d) => post("/auth/login", d),
  me: () => request("/me"),
  stats: () => request("/stats"),
  cases: (filters = {}) => request(`/cases${qs(filters)}`),
  createCase: (d) => post("/cases", d),
  closeCase: (id) => post(`/cases/${id}/close`, {}),
  heroes: (filters = {}) => request(`/heroes${qs(filters)}`),
  createHero: (d) => post("/heroes", d),
  setHeroAvailable: (id, available) => request(`/heroes/${id}`, { method: "PATCH", body: JSON.stringify({ available }) }),
  myCases: () => request("/me/cases"),
  myHeroes: () => request("/me/heroes"),
};
