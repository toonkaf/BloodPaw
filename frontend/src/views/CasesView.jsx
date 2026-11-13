import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import { ErrorList } from "../components/Alerts.jsx";
import { CaseCard } from "../components/Cards.jsx";
import { SPECIES, URGENCY } from "../lib/format.js";

export default function CasesView({ meta }) {
  const [filters, setFilters] = useState({ hospital: "", species: "", blood_type: "", urgency: "" });
  const [cases, setCases] = useState([]);
  const [errors, setErrors] = useState([]);

  useEffect(() => {
    api.cases(filters).then((c) => { setCases(c); setErrors([]); }).catch((e) => setErrors(e.messages));
  }, [filters]);

  const set = (k) => (e) => setFilters({ ...filters, [k]: e.target.value });
  const bloodOptions = [...new Set(Object.values(meta?.case_blood_types || {}).flat())];
  const Select = ({ label, k, options }) => (
    <label className="field">
      <span className="field-label">{label}</span>
      <select value={filters[k]} onChange={set(k)}>
        <option value="">ทั้งหมด</option>
        {options.map(([v, text]) => <option key={v} value={v}>{text}</option>)}
      </select>
    </label>
  );

  return (
    <div className="cases-layout">
      <aside className="side">
        <h2>เคสด่วนทั้งหมด</h2>
        <Select label="โรงพยาบาล" k="hospital" options={(meta?.hospitals || []).map((h) => [h, h])} />
        <Select label="ชนิด" k="species" options={Object.entries(SPECIES)} />
        <Select label="กรุ๊ปเลือด" k="blood_type" options={bloodOptions.map((b) => [b, b])} />
        <Select label="ระดับ" k="urgency" options={Object.entries(URGENCY)} />
      </aside>
      <section className="list-panel">
        <ErrorList messages={errors} />
        {cases.length === 0 && errors.length === 0 && <div className="empty">ไม่พบเคสด่วนตามเงื่อนไขที่เลือก</div>}
        {cases.map((c) => <CaseCard key={c.id} c={c} />)}
      </section>
    </div>
  );
}
