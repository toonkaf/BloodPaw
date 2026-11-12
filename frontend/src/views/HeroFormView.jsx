import { useState } from "react";
import { api } from "../api/client.js";
import Field from "../components/Field.jsx";
import { BLOOD } from "./CaseFormView.jsx";

export default function HeroFormView({ go }) {
  const [form, setForm] = useState({ name: "", species: "dog", blood_type: "DEA 1.1-", weight_kg: "", province: "", contact_phone: "" });
  const [error, setError] = useState("");
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });
  const setSpecies = (e) => setForm({ ...form, species: e.target.value, blood_type: BLOOD[e.target.value][0] });

  async function submit(e) {
    e.preventDefault();
    setError("");
    try { await api.createHero({ ...form, weight_kg: Number(form.weight_kg) }); go("/profile"); } catch (err) { setError(err.message); }
  }

  return (
    <form className="form" onSubmit={submit}>
      <h2>ลงทะเบียนฮีโร่</h2>
      {error && <div className="alert" role="alert">{error}</div>}
      <Field label="ชื่อฮีโร่ (สัตว์เลี้ยง)"><input value={form.name} onChange={set("name")} required /></Field>
      <div className="row2">
        <Field label="ชนิดสัตว์">
          <select value={form.species} onChange={setSpecies}><option value="dog">สุนัข</option><option value="cat">แมว</option></select>
        </Field>
        <Field label="หมู่เลือด">
          <select value={form.blood_type} onChange={set("blood_type")}>{BLOOD[form.species].map((b) => <option key={b}>{b}</option>)}</select>
        </Field>
      </div>
      <div className="row2">
        <Field label="น้ำหนัก (กก.)"><input type="number" step="0.1" min="0" value={form.weight_kg} onChange={set("weight_kg")} required /></Field>
        <Field label="จังหวัด"><input value={form.province} onChange={set("province")} required /></Field>
      </div>
      <Field label="เบอร์ติดต่อเจ้าของ"><input inputMode="tel" placeholder="0812345678" value={form.contact_phone} onChange={set("contact_phone")} required /></Field>
      <div className="center"><button className="btn wide" type="submit">ลงทะเบียน</button></div>
    </form>
  );
}
