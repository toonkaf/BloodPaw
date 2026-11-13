const LEFT = [["/", "หน้าหลัก"], ["/cases", "เคสด่วน"], ["/hero", "ลงทะเบียนฮีโร่"]];

export default function Navbar({ path, user, go }) {
  const active = (p) => (p === "/" ? path === "/" : path === p || path.startsWith(p + "/"));
  return (
    <nav className="nav container" aria-label="เมนูหลัก">
      {LEFT.map(([p, label]) => (
        <button key={p} className={`nav-item ${active(p) ? "active" : ""}`} onClick={() => go(p)}>{label}</button>
      ))}
      <div className="spacer" />
      <button className={`nav-item ${["/login", "/register", "/profile"].includes(path) ? "active" : ""}`}
              onClick={() => go(user ? "/profile" : "/login")}>
        {user ? "โปรไฟล์" : "เข้าสู่ระบบ"}
      </button>
      <button className={`nav-item cta ${path === "/cases/new" ? "active" : ""}`} onClick={() => go("/cases/new")}>+ ประกาศเคสด่วน</button>
    </nav>
  );
}
