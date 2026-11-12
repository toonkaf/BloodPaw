const URGENCY = { critical: "วิกฤต", urgent: "ด่วน", normal: "ทั่วไป" };
const SPECIES = { dog: "สุนัข", cat: "แมว" };

export default function CaseCard({ c, user, onClose }) {
  const isOwner = user && user.id === c.owner_id;
  return (
    <article className="case">
      <div className="case-head">
        <h3>{c.pet_name} · {SPECIES[c.species]} · {c.blood_type}</h3>
        <span className={`badge ${c.status === "closed" ? "closed" : c.urgency}`}>
          {c.status === "closed" ? "ปิดเคสแล้ว" : URGENCY[c.urgency]}
        </span>
      </div>
      <div className="meta"><span>🏥 {c.hospital}</span><span>📍 {c.province}</span>
        <span>{new Date(c.created_at + "Z").toLocaleString("th-TH")}</span></div>
      {c.note && <div>{c.note}</div>}
      {c.status === "searching" && (
        <div className="contact">
          {c.contact_phone ? <>📞 ติดต่อ: <b>{c.contact_phone}</b></> : <a href="#/login">เข้าสู่ระบบเพื่อดูเบอร์ติดต่อ</a>}
        </div>
      )}
      {isOwner && c.status === "searching" && onClose && (
        <div><button className="btn small" onClick={() => onClose(c.id)}>ปิดเคส (ได้เลือดแล้ว)</button></div>
      )}
    </article>
  );
}
