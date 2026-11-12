import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import CaseCard from "../components/CaseCard.jsx";

export default function CasesView({ user }) {
  const [filters, setFilters] = useState({ status: "searching", species: "", province: "" });
  const [cases, setCases] = useState([]);
  const [error, setError] = useState("");

  const load = () => api.cases(filters).then(setCases).catch((e) => setError(e.message));
  useEffect(() => { load(); }, [filters]);

  const close = async (id) => {
    try { await api.closeCase(id); load(); } catch (e) { setError(e.message); }
  };
  const chip = (key, value, label) => (
    <button className={`chip ${filters[key] === value ? "on" : ""}`} onClick={() => setFilters({ ...filters, [key]: value })}>{label}</button>
  );

  return (
    <div className="cases-layout">
      <aside className="side">
        <h2>เคสด่วนทั้งหมด</h2>
        <div className="chips">{chip("status", "searching", "กำลังตามหา")}{chip("status", "closed", "ปิดเคสแล้ว")}</div>
        <div className="chips">{chip("species", "", "ทั้งหมด")}{chip("species", "dog", "สุนัข")}{chip("species", "cat", "แมว")}</div>
        <div className="field">
          <input placeholder="จังหวัด" value={filters.province} onChange={(e) => setFilters({ ...filters, province: e.target.value })}
                 style={{ padding: "12px 22px", fontSize: "1.05rem" }} />
        </div>
      </aside>
      <section className="list-panel">
        {error && <div className="alert" role="alert">{error}</div>}
        {cases.length === 0 && !error && <div className="empty">ไม่พบเคสตามเงื่อนไขที่เลือก</div>}
        {cases.map((c) => <CaseCard key={c.id} c={c} user={user} onClose={close} />)}
      </section>
    </div>
  );
}
