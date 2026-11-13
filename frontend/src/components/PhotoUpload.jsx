import { useRef, useState } from "react";
import { api } from "../api/client.js";

const OK = ["image/jpeg", "image/png", "image/webp"];

export default function PhotoUpload({ value, onChange, tone = "mint" }) {
  const ref = useRef(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  async function pick(e) {
    const file = e.target.files[0];
    e.target.value = "";
    if (!file) return;
    if (!OK.includes(file.type)) return setErr("รองรับเฉพาะไฟล์ JPG, PNG หรือ WEBP");
    if (file.size > 2 * 1024 * 1024) return setErr("ไฟล์รูปต้องไม่เกิน 2 MB");
    setErr("");
    setBusy(true);
    try {
      onChange((await api.upload(file)).url);
    } catch (ex) {
      setErr(ex.message);
    }
    setBusy(false);
  }

  return (
    <div className="photo-upload">
      {value && <img src={value} alt="รูปที่อัปโหลด" />}
      <button type="button" className={`upload-btn ${tone}`} disabled={busy} onClick={() => ref.current.click()}>
        {busy ? "กำลังอัปโหลด..." : value ? "เปลี่ยนรูป" : "อัปโหลดรูป"}
      </button>
      <input ref={ref} type="file" accept="image/jpeg,image/png,image/webp" hidden onChange={pick} />
      {err && <span className="field-hint err">{err}</span>}
    </div>
  );
}
