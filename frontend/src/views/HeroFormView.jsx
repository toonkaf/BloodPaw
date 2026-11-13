import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import { ErrorList } from "../components/Alerts.jsx";
import Field from "../components/Field.jsx";
import HospitalPicker from "../components/HospitalPicker.jsx";
import PhotoUpload from "../components/PhotoUpload.jsx";
import { CRITERIA } from "../lib/criteria.js";
import { SPECIES } from "../lib/format.js";

const EMPTY = { species: "dog", name: "", breed: "", birth_date: "", weight_kg: "", photo_url: null, blood_type: "ไม่ทราบ",
  vaccinated_ok: false, no_chronic_disease: false, criteria_confirmed: false, hospitals: [], province: "", contact_phone: "" };

const CriteriaList = ({ c }) => (
  <>
    <p className="crit-title">{c.title}</p>
    <ol>{c.items.map((t) => <li key={t}>{t}</li>)}</ol>
  </>
);

/** heroId มีค่า = หน้าแก้ไขข้อมูล (ดึงข้อมูลเดิมมาใส่ไว้) ไม่มี = ลงทะเบียนใหม่ */
export default function HeroFormView({ go, meta, heroId }) {
  const editing = Boolean(heroId);
  const [f, setF] = useState(EMPTY);
  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(editing);

  useEffect(() => {
    if (!editing) return;
    api.myHeroes().then((list) => {
      const h = list.find((x) => x.id === Number(heroId));
      if (!h) return setErrors(["ไม่พบฮีโร่ที่ต้องการแก้ไข"]);
      setF({ ...EMPTY, ...h, criteria_confirmed: false }); // ต้องยืนยันเกณฑ์ใหม่ทุกครั้งที่บันทึก
    }).catch((e) => setErrors(e.messages)).finally(() => setLoading(false));
  }, [heroId, editing]);

  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const check = (k) => (e) => setF({ ...f, [k]: e.target.checked });
  const bloods = meta?.hero_blood_types?.[f.species] || ["ไม่ทราบ"];

  async function submit(e) {
    e.preventDefault();
    setErrors([]);
    const payload = { name: f.name, species: f.species, breed: f.breed, birth_date: f.birth_date, weight_kg: Number(f.weight_kg),
      photo_url: f.photo_url, blood_type: f.blood_type, vaccinated_ok: f.vaccinated_ok, no_chronic_disease: f.no_chronic_disease,
      criteria_confirmed: f.criteria_confirmed, hospitals: f.hospitals, province: f.province, contact_phone: f.contact_phone };
    const missing = [];
    if (!f.birth_date) missing.push("วันเกิด: ยังไม่ได้กรอก");
    if (!f.weight_kg) missing.push("น้ำหนัก: ยังไม่ได้กรอก");
    if (f.hospitals.length === 0) missing.push("โรงพยาบาลที่สะดวกบริจาค: เพิ่มอย่างน้อย 1 แห่ง");
    if (missing.length) return setErrors(missing);
    try {
      editing ? await api.updateHero(heroId, payload) : await api.createHero(payload);
      go("/profile");
    } catch (err) { setErrors(err.messages); }
  }

  if (loading) return <div className="empty">กำลังโหลด...</div>;

  return (
    <form className="two-col" onSubmit={submit}>
      <div className="col-main">
        <h2 className="page-title">{editing ? "แก้ไขข้อมูลสัตว์เลี้ยงเป็นฮีโร่" : "ลงทะเบียนสัตว์เลี้ยงเป็นฮีโร่"}</h2>
        <ErrorList messages={errors} />

        <section className="panel">
          <h3>ข้อมูลสัตว์</h3>
          <div className="grid2">
            <Field label="ชนิด"><select value={f.species} onChange={(e) => setF({ ...f, species: e.target.value, blood_type: "ไม่ทราบ" })}>
              {Object.entries(SPECIES).map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select></Field>
            <Field label="ชื่อ"><input value={f.name} onChange={set("name")} required /></Field>
          </div>
          <div className="grid3f">
            <Field label="สายพันธุ์"><input value={f.breed} onChange={set("breed")} required /></Field>
            <Field label="วันเกิด"><input type="date" value={f.birth_date} onChange={set("birth_date")} required /></Field>
            <Field label="น้ำหนัก (กก.)"><input type="number" step="0.1" min="0" value={f.weight_kg} onChange={set("weight_kg")} required /></Field>
          </div>
          <PhotoUpload value={f.photo_url} onChange={(url) => setF({ ...f, photo_url: url })} />
        </section>

        <section className="panel">
          <h3>สุขภาพ</h3>
          <Field label="กรุ๊ปเลือด" hint="*ถ้าไม่ทราบสัตวแพทย์จะตรวจให้ก่อนบริจาค" className="half">
            <select value={f.blood_type} onChange={set("blood_type")}>{bloods.map((b) => <option key={b}>{b}</option>)}</select>
          </Field>
          <div className="checks">
            <label className="check"><input type="checkbox" checked={f.vaccinated_ok} onChange={check("vaccinated_ok")} />
              <span>ได้รับวัคซีนพื้นฐานครบ และยังไม่หมดอายุ</span></label>
            <label className="check"><input type="checkbox" checked={f.no_chronic_disease} onChange={check("no_chronic_disease")} />
              <span>ไม่มีโรคประจำตัวเรื้อรัง<small>*เช่น โรคหัวใจ โรคไต ลมชัก</small></span></label>
          </div>
          <div className="crit-box" tabIndex={0} aria-label="เกณฑ์การบริจาคเบื้องต้น">
            <p className="crit-species">เกณฑ์การบริจาคเบื้องต้น ชนิดสัตว์ : {SPECIES[f.species]}</p>
            <CriteriaList c={CRITERIA[f.species]} />
          </div>
          <p className="red-note">*ผลสุดท้ายขึ้นอยู่กับสัตวแพทย์ ซึ่งจะตรวจสุขภาพและกรุ๊ปเลือดก่อนบริจาคทุกครั้ง</p>
          <label className="confirm-pill"><input type="checkbox" checked={f.criteria_confirmed} onChange={check("criteria_confirmed")} />
            <span>ฉันอ่านเกณฑ์ข้างต้น และน้องฮีโร่ผ่านเกณฑ์</span></label>
        </section>

        <section className="panel">
          <h3>ที่อยู่ที่สะดวกบริจาค</h3>
          <Field label="โรงพยาบาล" hint="*เลือกได้หลายโรงพยาบาล">
            <HospitalPicker value={f.hospitals} onChange={(h) => setF({ ...f, hospitals: h })} options={meta?.hospitals || []} />
          </Field>
          <div className="grid2">
            <Field label="จังหวัด"><input value={f.province} onChange={set("province")} required /></Field>
            <Field label="เบอร์โทร" hint="*ไม่เปิดเผยสู่สาธารณะ จะส่งให้อีกฝ่ายเมื่อกดปุ่ม tel ในหน้าติดต่อเท่านั้น">
              <input inputMode="tel" placeholder="0898765432" value={f.contact_phone} onChange={set("contact_phone")} required /></Field>
          </div>
        </section>
      </div>

      <aside className="col-side">
        <section className="panel crit-side">
          <h3 className="center-title">เกณฑ์การบริจาคเบื้องต้น</h3>
          <CriteriaList c={CRITERIA.dog} />
          <CriteriaList c={CRITERIA.cat} />
        </section>
        <div className="actions side-actions">
          <button type="button" className="btn" onClick={() => go(editing ? "/profile" : "/")}>ยกเลิก</button>
          <button type="submit" className="btn primary">บันทึก</button>
        </div>
      </aside>
    </form>
  );
}
