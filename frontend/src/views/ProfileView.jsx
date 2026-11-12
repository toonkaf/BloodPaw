import { useEffect, useState } from "react";
import { api, setToken } from "../api/client.js";
import CaseCard from "../components/CaseCard.jsx";

export default function ProfileView({ user, onLogout }) {
  const [cases, setCases] = useState([]);
  const [heroes, setHeroes] = useState([]);
  const [error, setError] = useState("");

  const load = () => Promise.all([api.myCases(), api.myHeroes()]).then(([c, h]) => { setCases(c); setHeroes(h); })
    .catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  const act = (fn) => async (...a) => { try { await fn(...a); load(); } catch (e) { setError(e.message); } };
  const close = act((id) => api.closeCase(id));
  const toggle = act((h) => api.setHeroAvailable(h.id, !h.available));

  return (
    <>
      <div className="case-head" style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: "2.4rem" }}>สวัสดี {user.full_name}</h2>
        <button className="btn" onClick={() => { setToken(null); onLogout(); }}>ออกจากระบบ</button>
      </div>
      {error && <div className="alert" role="alert">{error}</div>}
      <div className="profile-grid">
        <section>
          <h2 className="section-title" style={{ marginTop: 0 }}>เคสของฉัน</h2>
          <div className="list-panel">
            {cases.length === 0 && <div className="empty">ยังไม่มีเคสที่ประกาศ</div>}
            {cases.map((c) => <CaseCard key={c.id} c={c} user={user} onClose={close} />)}
          </div>
        </section>
        <section>
          <h2 className="section-title" style={{ marginTop: 0 }}>ฮีโร่ของฉัน</h2>
          <div className="list-panel">
            {heroes.length === 0 && <div className="empty">ยังไม่ได้ลงทะเบียนฮีโร่</div>}
            {heroes.map((h) => (
              <article className="case" key={h.id}>
                <div className="case-head">
                  <h3>{h.name} · {h.species === "dog" ? "สุนัข" : "แมว"} · {h.blood_type}</h3>
                  <span className="badge" style={{ background: h.available ? "var(--mint)" : "#d9d9d2" }}>{h.available ? "พร้อมบริจาค" : "พักก่อน"}</span>
                </div>
                <div className="meta"><span>⚖️ {h.weight_kg} กก.</span><span>📍 {h.province}</span></div>
                <div><button className="btn small" onClick={() => toggle(h)}>{h.available ? "ตั้งเป็นพักก่อน" : "ตั้งเป็นพร้อมบริจาค"}</button></div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </>
  );
}
