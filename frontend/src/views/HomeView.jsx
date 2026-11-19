import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import { ErrorList } from "../components/Alerts.jsx";
import { CaseCard } from "../components/Cards.jsx";

const STEPS = ["เข้าสู่ระบบ", "ลงทะเบียนฮีโร่/ประกาศเคสด่วน", "ตรวจสอบหน้าโปรไฟล์", "ติดต่อยืนยัน"];

export default function HomeView({ go }) {
  const [stats, setStats] = useState({ cases_searching: 0, heroes_available: 0, cases_success: 0 });
  const [cases, setCases] = useState([]);
  const [errors, setErrors] = useState([]);

  useEffect(() => {
    Promise.all([api.stats(), api.cases({ sort: "latest", limit: 3 })])
      .then(([s, c]) => { setStats(s); setCases(c); })
      .catch((e) => setErrors(e.messages));
  }, []);

  return (
    <>
      <section className="home-top">
        <div>
          <h1>ช่วยน้องหาเลือดได้เร็วขึ้น</h1>
          <p></p>
          <div className="btn-row">
            <button className="btn" onClick={() => go("/cases/new")}>+ ประกาศเคสด่วน</button>
            <button className="btn" onClick={() => go("/hero")}>ลงทะเบียนฮีโร่</button>
          </div>
        </div>
        <div className="dash">
          <h3>Dashboard</h3>
          <div className="stat red"><span>เคสที่กำลังตามหา</span><span>[ {stats.cases_searching} ]</span></div>
          <div className="stat mint"><span>ฮีโร่ที่พร้อมบริจาค</span><span>[ {stats.heroes_available} ]</span></div>
          <div className="stat sage"><span>ปิดเคสสำเร็จ</span><span>[ {stats.cases_success} ]</span></div>
        </div>
      </section>
      <ErrorList messages={errors} />

      <h2 className="section-title">เคสด่วนล่าสุด</h2>
      <div className="cards3">
        {cases.length === 0 && <div className="empty" style={{ gridColumn: "1 / -1" }}>ยังไม่มีเคสด่วนในขณะนี้</div>}
        {cases.map((c) => <CaseCard key={c.id} c={c} compact />)}
      </div>

      <h2 className="section-title">ใช้งานอย่างไร</h2>
      <div className="steps">
        {STEPS.map((s, i) => (
          <span key={s} style={{ display: "contents" }}>
            <span className="step">{s}</span>
            {i < STEPS.length - 1 && <span className="arrow">→</span>}
          </span>
        ))}
      </div>
    </>
  );
}
