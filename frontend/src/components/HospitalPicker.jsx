import { useState } from "react";

/** เลือกโรงพยาบาลได้หลายแห่ง: พิมพ์/เลือกจากรายการแล้วกดเพิ่ม */
export default function HospitalPicker({ value, onChange, options }) {
  const [text, setText] = useState("");
  const add = () => {
    const name = text.trim().replace(/\s+/g, " ");
    if (name && !value.some((v) => v.toLowerCase() === name.toLowerCase())) onChange([...value, name]);
    setText("");
  };
  return (
    <div className="hospital-picker">
      <div className="hospital-row">
        <input list="hospital-options" value={text} placeholder="พิมพ์หรือเลือกโรงพยาบาล" onChange={(e) => setText(e.target.value)}
               onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); add(); } }} />
        <button type="button" className="btn small" onClick={add}>เพิ่ม</button>
      </div>
      <datalist id="hospital-options">{options.map((o) => <option key={o} value={o} />)}</datalist>
      <div className="chips">
        {value.map((h) => (
          <span className="chip on" key={h}>{h}
            <button type="button" aria-label={`ลบ ${h}`} onClick={() => onChange(value.filter((x) => x !== h))}>✕</button>
          </span>
        ))}
      </div>
    </div>
  );
}
