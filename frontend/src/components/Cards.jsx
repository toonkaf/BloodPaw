import { CASE_STATUS, SPECIES, URGENCY, joinHospitals, thaiDate } from "../lib/format.js";

const Thumb = ({ url, alt }) => (
  <div className="thumb">{url ? <img src={url} alt={alt} /> : <span aria-hidden="true">🐾</span>}</div>
);

/** การ์ดเคสด่วน: compact = แบบหน้าหลัก, ปกติ = แบบรายการ/โปรไฟล์ */
export function CaseCard({ c, compact = false, showStatus = true, children }) {
  return (
    <article className={`pet-card ${compact ? "compact" : ""}`}>
      <Thumb url={c.photo_url} alt={c.pet_name} />
      <div className="pet-info">
        <div className="row3">
          <b>ชนิด : {SPECIES[c.species]}</b>
          <span>สายพันธุ์ : {c.breed}</span>
          <span>ชื่อ : {c.pet_name}</span>
        </div>
        <div className={compact ? "" : "row3 two"}>
          <span>อาการ : {c.symptom}</span>
          {!compact && <span>สาเหตุ : {c.cause}</span>}
        </div>
        <div className="pink">กรุ๊ปเลือดที่ต้องการ : {c.blood_type}</div>
        <div className="purple">โรงพยาบาล : {c.hospital}</div>
      </div>
      {!compact && (
        <div className="pills">
          <span className={`pill ${c.urgency}`}>{URGENCY[c.urgency]}</span>
          {showStatus && <span className={`pill status ${c.status}`}>{CASE_STATUS[c.status]}</span>}
        </div>
      )}
      {children}
    </article>
  );
}

/** การ์ดฮีโร่ */
export function HeroCard({ h, children, truncate = false }) {
  return (
    <article className="pet-card hero">
      <Thumb url={h.photo_url} alt={h.name} />
      <div className="pet-info">
        <div className="row3">
          <b>ชนิด : {SPECIES[h.species]}</b>
          <span>สายพันธุ์ : {h.breed}</span>
          <span>ชื่อ : {h.name}</span>
        </div>
        <div className="row3 two">
          <span>วันเกิด : {thaiDate(h.birth_date)}</span>
          <span>น้ำหนัก : {h.weight_kg} กก.</span>
        </div>
        <div className="pink">กรุ๊ปเลือด : {h.blood_type}</div>
        <div className={`purple ${truncate ? "clip" : ""}`}>โรงพยาบาล : {joinHospitals(h.hospitals)}</div>
      </div>
      {children}
    </article>
  );
}
