import { useState } from "react";
import { api, setToken } from "../api/client.js";
import Field from "../components/Field.jsx";

export function LoginView({ onAuthed, go, notice }) {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      const { access_token } = await api.login(form);
      setToken(access_token);
      await onAuthed();
    } catch (err) { setError(err.message); }
  }

  return (
    <form className="form" onSubmit={submit}>
      <h2>เข้าสู่ระบบ</h2>
      {notice && <div className="alert ok">{notice}</div>}
      {error && <div className="alert" role="alert">{error}</div>}
      <Field label="อีเมล"><input type="email" placeholder="@gmail.com" value={form.email} onChange={set("email")} required /></Field>
      <Field label="รหัสผ่าน"><input type="password" placeholder="รหัสผ่านขั้นต่ำ 8 ตัวอักษร" value={form.password} onChange={set("password")} required /></Field>
      <p className="hint">*ยังไม่เคยมีบัญชี <a onClick={() => go("/register")}>สมัครสมาชิก</a></p>
      <div className="center"><button className="btn wide" type="submit">ยืนยัน</button></div>
    </form>
  );
}

export function RegisterView({ onAuthed, go }) {
  const [form, setForm] = useState({ full_name: "", email: "", password: "", confirm: "" });
  const [error, setError] = useState("");
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setError("");
    if (form.password.length < 8) return setError("รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร");
    if (form.password !== form.confirm) return setError("รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน");
    try {
      await api.register({ full_name: form.full_name, email: form.email, password: form.password });
      const { access_token } = await api.login({ email: form.email, password: form.password });
      setToken(access_token);
      await onAuthed();
    } catch (err) { setError(err.message); }
  }

  return (
    <form className="form" onSubmit={submit}>
      <h2>สมัครสมาชิก</h2>
      {error && <div className="alert" role="alert">{error}</div>}
      <Field label="ชื่อ"><input placeholder="ชื่อ" value={form.full_name} onChange={set("full_name")} required /></Field>
      <Field label="อีเมล"><input type="email" placeholder="@gmail.com" value={form.email} onChange={set("email")} required /></Field>
      <div className="row2">
        <Field label="รหัสผ่าน"><input type="password" placeholder="รหัสผ่านขั้นต่ำ 8 ตัวอักษร" value={form.password} onChange={set("password")} required /></Field>
        <Field label="ยืนยันรหัสผ่าน"><input type="password" value={form.confirm} onChange={set("confirm")} required /></Field>
      </div>
      <p className="hint">*มีบัญชีแล้ว <a onClick={() => go("/login")}>เข้าสู่ระบบ</a></p>
      <div className="center"><button className="btn wide" type="submit">ยืนยัน</button></div>
    </form>
  );
}
