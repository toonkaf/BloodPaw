export const SPECIES = { dog: "สุนัข", cat: "แมว" };
export const URGENCY = { advance: "ล่วงหน้า", urgent: "ด่วน", critical: "ด่วนมาก" };
export const CASE_STATUS = { searching: "กำลังตามหา", found: "พบฮีโร่", success: "สำเร็จ" };

/** 2026-05-25 -> 25/05/2569 (พ.ศ.) ตามแบบหน้าจอ */
export function thaiDate(iso) {
  if (!iso) return "-";
  const [y, m, d] = iso.split("-");
  return `${d}/${m}/${Number(y) + 543}`;
}

export function thaiTime(iso) {
  const d = new Date(/[zZ]|[+-]\d\d:?\d\d$/.test(iso) ? iso : iso + "Z");
  return d.toLocaleTimeString("th-TH", { hour: "2-digit", minute: "2-digit" });
}

export const joinHospitals = (list) => (list || []).join(", ");
