import { useState } from "react";
import { api, setToken } from "../api/client.js";
import { ErrorList, Notice } from "../components/Alerts.jsx";
import Field from "../components/Field.jsx";

export function LoginView({ onAuthed, go, notice }) {
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [errors, setErrors] = useState([]);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setErrors([]);
    try {
      setToken((await api.login(form)).access_token);
      await onAuthed();
    } catch (err) { setErrors(err.messages); }
  }

  return (
    <form className="form narrow" onSubmit={submit}>
      <h2>เข้าสู่ระบบ</h2>
      <Notice>{notice}</Notice>
      <ErrorList messages={errors} />
      <Field label="ชื่อ"><input placeholder="ชื่อ" value={form.full_name} onChange={set("full_name")} required /></Field>
      <Field label="อีเมล"><input type="email" placeholder="@gmail.com" value={form.email} onChange={set("email")} required /></Field>
      <Field label="รหัสผ่าน"><input type="password" placeholder="รหัสผ่านขั้นต่ำ 8 ตัวอักษร" value={form.password} onChange={set("password")} required /></Field>
      <p className="hint">*ยังไม่เคยมีบัญชี <a onClick={() => go("/register")}>สมัครสมาชิก</a></p>
      <div className="center"><button className="btn wide" type="submit">ยืนยัน</button></div>
    </form>
  );
}

export function RegisterView({ onAuthed, go }) {
  const [form, setForm] = useState({ full_name: "", email: "", password: "", confirm: "" });
  const [errors, setErrors] = useState([]);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setErrors([]);
    if (form.password !== form.confirm) return setErrors(["รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน"]);
    try {
      const { full_name, email, password } = form;
      await api.register({ full_name, email, password });
      setToken((await api.login({ full_name, email, password })).access_token); // สมัครเสร็จ = เข้าสู่ระบบเลย
      await onAuthed();
    } catch (err) { setErrors(err.messages); }
  }

  return (
    <form className="form narrow" onSubmit={submit}>
      <h2>สมัครสมาชิก</h2>
      <ErrorList messages={errors} />
      <Field label="ชื่อ"><input placeholder="ชื่อ" value={form.full_name} onChange={set("full_name")} required /></Field>
      <Field label="อีเมล"><input type="email" placeholder="@gmail.com" value={form.email} onChange={set("email")} required /></Field>
      <div className="row2">
        <Field label="รหัสผ่าน"><input type="password" placeholder="รหัสผ่านขั้นต่ำ 8 ตัวอักษร" value={form.password} onChange={set("password")} required /></Field>
        <Field label="ยืนยันรหัสผ่าน"><input type="password" value={form.confirm} onChange={set("confirm")} required /></Field>
      </div>
      <p className="hint">*มีบัญชีแล้ว <a onClick={() => go("/login")}>เข้าสู่ระบบ</a> · รหัสผ่านต้องมีทั้งตัวอักษรและตัวเลข</p>
      <div className="center"><button className="btn wide" type="submit">ยืนยัน</button></div>
    </form>
  );
}
