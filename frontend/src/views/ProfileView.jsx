import { useEffect, useState } from "react";
import { api, setToken } from "../api/client.js";
import { ErrorList } from "../components/Alerts.jsx";
import { CaseCard, HeroCard } from "../components/Cards.jsx";

export default function ProfileView({ user, go, onLogout }) {
  const [heroes, setHeroes] = useState([]);
  const [requests, setRequests] = useState([]);
  const [cases, setCases] = useState([]);
  const [errors, setErrors] = useState([]);

  const load = () =>
    Promise.all([api.myHeroes(), api.myRequests(), api.myCases()])
      .then(([h, r, c]) => { setHeroes(h); setRequests(r); setCases(c); })
      .catch((e) => setErrors(e.messages));
  useEffect(() => { load(); }, []);

  const run = (fn, ask) => async (...args) => {
    if (ask && !window.confirm(ask)) return;
    setErrors([]);
    try { await fn(...args); await load(); } catch (e) { setErrors(e.messages); }
  };
  const setStatus = run((h, status) => api.setHeroStatus(h.id, status));
  const rest = (h) => run((x) => api.setHeroStatus(x.id, "resting"),
    requests.length ? "เปลี่ยนเป็น \"พัก\" ระบบจะยกเลิกคำขอที่ได้รับและส่งต่อเคสให้ฮีโร่ตัวอื่น ต้องการดำเนินการต่อหรือไม่?" : null)(h);
  const decline = run((id) => api.decline(id), "ปฏิเสธการจับคู่นี้? ระบบจะนำเคสไปจับคู่ใหม่");
  const confirm = run((id) => api.confirm(id), "ยืนยันว่าสำเร็จแล้ว? เคสจะถูกปิดและย้อนกลับไม่ได้");

  return (
    <>
      <div className="profile-head">
        <h2 className="page-title">โปรไฟล์ของฉัน</h2>
        <button className="btn danger" onClick={() => { setToken(null); onLogout(); }}>ออกจากระบบ</button>
      </div>
      <p className="muted">สวัสดี {user.full_name}</p>
      <ErrorList messages={errors} />

      <section className="panel mint-panel">
        <h3>ฮีโร่ที่ฉันลงทะเบียน</h3>
        {heroes.length === 0 && <div className="empty">ยังไม่ได้ลงทะเบียนฮีโร่ <a onClick={() => go("/hero")}>ลงทะเบียนฮีโร่</a></div>}
        {heroes.map((h) => (
          <div className="hero-block" key={h.id}>
            <HeroCard h={h} truncate>
              <button className="pill-btn yellow edit" onClick={() => go(`/hero/${h.id}/edit`)}>แก้ไข</button>
              <div className="status-row">
                <span>สถานะ:</span>
                <div className="seg" role="group" aria-label="สถานะฮีโร่">
                  <button className={h.status === "resting" ? "on" : ""} onClick={() => h.status !== "resting" && rest(h)}>พัก</button>
                  <button className={h.status === "ready" ? "on ok" : ""} onClick={() => h.status !== "ready" && setStatus(h, "ready")}>พร้อม</button>
                </div>
              </div>
            </HeroCard>
          </div>
        ))}
      </section>

      <section className="panel">
        <h3>คำขอที่ได้รับ</h3>
        {requests.length === 0 && <div className="empty">ยังไม่มีคำขอ ระบบจะจับคู่เคสที่เหมาะกับฮีโร่ของคุณมาแสดงที่นี่</div>}
        {requests.map((r) => (
          <div className="request-row" key={r.match_id}>
            <CaseCard c={r.case} showStatus={false} />
            <div className="side-buttons">
              <button className="pill-btn red" onClick={() => decline(r.match_id)}>ปฏิเสธ</button>
              <button className="pill-btn yellow" onClick={() => go(`/matches/${r.match_id}`)}>ติดต่อสอบถาม</button>
              <button className="pill-btn green" onClick={() => confirm(r.match_id)}>ยืนยัน/สำเร็จ</button>
            </div>
          </div>
        ))}
      </section>

      <section className="panel">
        <h3>เคสด่วนที่ฉันประกาศ</h3>
        {cases.length === 0 && <div className="empty">ยังไม่ได้ประกาศเคสด่วน <a onClick={() => go("/cases/new")}>ประกาศเคสด่วน</a></div>}
        {cases.map((c) => (
          <div className="request-row" key={c.id}>
            <CaseCard c={c} />
            <div className="side-buttons">
              {c.match_id && (
                <>
                  <button className="pill-btn yellow" onClick={() => go(`/matches/${c.match_id}`)}>ติดต่อสอบถาม</button>
                  <button className="pill-btn green" onClick={() => confirm(c.match_id)}>ยืนยัน/สำเร็จ</button>
                </>
              )}
            </div>
          </div>
        ))}
      </section>
    </>
  );
}
