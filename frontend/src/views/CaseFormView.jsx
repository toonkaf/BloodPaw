import { useState } from "react";
import { api } from "../api/client.js";
import Field from "../components/Field.jsx";

export const BLOOD = { dog: ["DEA 1.1+", "DEA 1.1-", "ไม่ทราบ"], cat: ["A", "B", "AB", "ไม่ทราบ"] };

export default function CaseFormView({ go }) {
  const [form, setForm] = useState({ pet_name: "", species: "dog", blood_type: "DEA 1.1-", hospital: "", province: "",
    urgency: "urgent", contact_phone: "", note: "" });
  const [error, setError] = useState("");
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });
  const setSpecies = (e) => setForm({ ...form, species: e.target.value, blood_type: BLOOD[e.target.value][0] });

  async function submit(e) {
    e.preventDefault();
    setError("");
    try { await api.createCase(form); go("/cases"); } catch (err) { setError(err.message); }
  }

  return (
    <form className="form" onSubmit={submit}>
      <h2>ประกาศเคสด่วน</h2>
      {error && <div className="alert" role="alert">{error}</div>}
      <Field label="ชื่อสัตว์ป่วย"><input value={form.pet_name} onChange={set("pet_name")} required /></Field>
      <div className="row2">
        <Field label="ชนิดสัตว์">
          <select value={form.species} onChange={setSpecies}><option value="dog">สุนัข</option><option value="cat">แมว</option></select>
        </Field>
        <Field label="หมู่เลือดที่ต้องการ">
          <select value={form.blood_type} onChange={set("blood_type")}>{BLOOD[form.species].map((b) => <option key={b}>{b}</option>)}</select>
        </Field>
      </div>
      <Field label="โรงพยาบาลสัตว์"><input value={form.hospital} onChange={set("hospital")} required /></Field>
      <div className="row2">
        <Field label="จังหวัด"><input value={form.province} onChange={set("province")} required /></Field>
        <Field label="ความเร่งด่วน">
          <select value={form.urgency} onChange={set("urgency")}><option value="normal">ทั่วไป</option><option value="urgent">ด่วน</option><option value="critical">วิกฤต</option></select>
        </Field>
      </div>
      <Field label="เบอร์ติดต่อ"><input inputMode="tel" placeholder="0812345678" value={form.contact_phone} onChange={set("contact_phone")} required /></Field>
      <Field label="รายละเอียดเพิ่มเติม"><textarea value={form.note} onChange={set("note")} maxLength={500} /></Field>
      <div className="center"><button className="btn wide" type="submit">ประกาศเคส</button></div>
    </form>
  );
}
