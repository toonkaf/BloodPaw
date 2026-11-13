import { useState } from "react";
import { api } from "../api/client.js";
import { ErrorList } from "../components/Alerts.jsx";
import { CaseCard } from "../components/Cards.jsx";
import Field from "../components/Field.jsx";
import PhotoUpload from "../components/PhotoUpload.jsx";
import { URGENCY } from "../lib/format.js";

const num = (v) => (v === "" || v == null ? null : Number(v));

export default function CaseFormView({ go, meta }) {
  const [f, setF] = useState({ species: "dog", pet_name: "", breed: "", birth_date: "", weight_kg: "", symptom: "", cause: "",
    photo_url: null, blood_type: "ไม่ระบุ", min_donor_weight: "", hospital: "", vet_name: "", contact_phone: "", urgency: "" });
  const [errors, setErrors] = useState([]);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const bloods = meta?.case_blood_types?.[f.species] || ["ไม่ระบุ"];
  const stdWeight = meta?.min_donor_weight?.[f.species];

  async function submit(e) {
    e.preventDefault();
    setErrors([]);
    if (!f.urgency) return setErrors(["กรุณาเลือกระดับความเร่งด่วน"]);
    try {
      await api.createCase({ ...f, birth_date: f.birth_date || null, weight_kg: num(f.weight_kg), min_donor_weight: num(f.min_donor_weight),
        vet_name: f.vet_name.trim() || null });
      go("/profile");
    } catch (err) { setErrors(err.messages); }
  }

  const preview = { ...f, id: 0, species: f.species, pet_name: f.pet_name || "-", breed: f.breed || "-", symptom: f.symptom || "-",
    cause: f.cause || "-", hospital: f.hospital || "-", urgency: f.urgency || "urgent", status: "searching" };

  return (
    <form className="two-col" onSubmit={submit}>
      <div className="col-main">
        <h2 className="page-title">ประกาศเคสด่วน</h2>
        <ErrorList messages={errors} />
        <section className="panel">
          <h3>ข้อมูลสัตว์ป่วย</h3>
          <div className="grid2">
            <Field label="ชนิด"><select value={f.species} onChange={(e) => setF({ ...f, species: e.target.value, blood_type: "ไม่ระบุ" })}>
              <option value="dog">สุนัข</option><option value="cat">แมว</option></select></Field>
            <Field label="ชื่อ"><input value={f.pet_name} onChange={set("pet_name")} required /></Field>
          </div>
          <div className="grid3f">
            <Field label="สายพันธุ์"><input value={f.breed} onChange={set("breed")} required /></Field>
            <Field label="วันเกิด"><input type="date" value={f.birth_date} onChange={set("birth_date")} /></Field>
            <Field label="น้ำหนัก (กก.)"><input type="number" step="0.1" min="0" value={f.weight_kg} onChange={set("weight_kg")} /></Field>
          </div>
          <div className="grid2">
            <Field label="อาการ"><input value={f.symptom} onChange={set("symptom")} required /></Field>
            <Field label="สาเหตุ"><input value={f.cause} onChange={set("cause")} required /></Field>
          </div>
          <PhotoUpload value={f.photo_url} onChange={(url) => setF({ ...f, photo_url: url })} tone="red" />
        </section>

        <section className="panel">
          <h3>เงื่อนไขที่ต้องการ</h3>
          <div className="grid2">
            <Field label="กรุ๊ปเลือดที่ต้องการ"><select value={f.blood_type} onChange={set("blood_type")}>
              {bloods.map((b) => <option key={b}>{b}</option>)}</select></Field>
            <Field label="น้ำหนักขั้นต่ำ (กก.)" hint={`*สามารถกรอกได้หากไม่ตรงกับเกณฑ์กลาง (เกณฑ์กลาง ${stdWeight ?? "-"} กก.)`}>
              <input type="number" step="0.1" min="0" value={f.min_donor_weight} onChange={set("min_donor_weight")} /></Field>
          </div>
        </section>

        <section className="panel">
          <h3>โรงพยาบาล</h3>
          <Field label="โรงพยาบาล">
            <input list="case-hospitals" value={f.hospital} onChange={set("hospital")} required />
            <datalist id="case-hospitals">{(meta?.hospitals || []).map((h) => <option key={h} value={h} />)}</datalist>
          </Field>
          <div className="grid2">
            <Field label="ชื่อสัตวแพทย์ผู้ดูแล (ถ้ามี)"><input value={f.vet_name} onChange={set("vet_name")} /></Field>
            <Field label="เบอร์โทร" hint="*ไม่เปิดเผยสู่สาธารณะ จะส่งให้ฮีโร่เมื่อกดปุ่ม tel ในหน้าติดต่อเท่านั้น">
              <input inputMode="tel" placeholder="0812345678" value={f.contact_phone} onChange={set("contact_phone")} required /></Field>
          </div>
        </section>

        <div className="level">
          <div className="level-title">ระดับ</div>
          <div className="level-row">
            {Object.entries(URGENCY).map(([v, label]) => (
              <button type="button" key={v} className={`level-btn ${v} ${f.urgency === v ? "on" : ""}`} onClick={() => setF({ ...f, urgency: v })}>{label}</button>
            ))}
          </div>
        </div>
        <div className="actions">
          <button type="button" className="btn" onClick={() => go("/profile")}>ยกเลิก</button>
          <button type="submit" className="btn primary">บันทึก</button>
        </div>
      </div>

      <aside className="col-side">
        <section className="panel sticky">
          <h3 className="center-title">ตัวอย่างเคส</h3>
          <CaseCard c={preview} compact />
          <div className="pills solo"><span className={`pill ${preview.urgency}`}>{URGENCY[preview.urgency]}</span></div>
        </section>
      </aside>
    </form>
  );
}
