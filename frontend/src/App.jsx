import { useCallback, useEffect, useState } from "react";
import { api, hasToken } from "./api/client.js";
import Navbar from "./components/Navbar.jsx";
import { LoginView, RegisterView } from "./views/AuthViews.jsx";
import CaseFormView from "./views/CaseFormView.jsx";
import CasesView from "./views/CasesView.jsx";
import HeroFormView from "./views/HeroFormView.jsx";
import HomeView from "./views/HomeView.jsx";
import MatchView from "./views/MatchView.jsx";
import ProfileView from "./views/ProfileView.jsx";

const currentPath = () => window.location.hash.replace(/^#/, "") || "/";
// หน้าที่ต้องเข้าสู่ระบบก่อน (ตาม User Flow)
const NEEDS_LOGIN = [/^\/cases\/new$/, /^\/hero(\/\d+\/edit)?$/, /^\/profile$/, /^\/matches\/\d+$/];

export default function App() {
  const [path, setPath] = useState(currentPath());
  const [user, setUser] = useState(null);
  const [meta, setMeta] = useState(null);
  const [ready, setReady] = useState(!hasToken());

  const go = useCallback((p) => { window.location.hash = p; }, []);
  const refreshUser = useCallback(async () => {
    try { setUser(await api.me()); } catch { setUser(null); }
    setReady(true);
  }, []);

  useEffect(() => {
    const onHash = () => { setPath(currentPath()); window.scrollTo(0, 0); };
    const onExpired = () => { setUser(null); go("/login"); };
    window.addEventListener("hashchange", onHash);
    window.addEventListener("auth-expired", onExpired);
    if (hasToken()) refreshUser();
    return () => { window.removeEventListener("hashchange", onHash); window.removeEventListener("auth-expired", onExpired); };
  }, [refreshUser, go]);

  useEffect(() => { api.meta().then(setMeta).catch(() => {}); }, [path]); // รายการโรงพยาบาลอัปเดตตามข้อมูลล่าสุด

  if (!ready) return null;

  const needLogin = NEEDS_LOGIN.some((re) => re.test(path)) && !user;
  if (needLogin) sessionStorage.setItem("next", path);
  const afterAuth = async () => {
    await refreshUser();
    const next = sessionStorage.getItem("next") || "/";
    sessionStorage.removeItem("next");
    go(next);
  };

  let view;
  let m;
  if (needLogin) view = <LoginView onAuthed={afterAuth} go={go} notice="กรุณาเข้าสู่ระบบก่อนใช้งานส่วนนี้" />;
  else if (path === "/login") view = <LoginView onAuthed={afterAuth} go={go} />;
  else if (path === "/register") view = <RegisterView onAuthed={afterAuth} go={go} />;
  else if (path === "/cases") view = <CasesView meta={meta} />;
  else if (path === "/cases/new") view = <CaseFormView go={go} meta={meta} />;
  else if (path === "/hero") view = <HeroFormView key="new" go={go} meta={meta} />;
  else if ((m = path.match(/^\/hero\/(\d+)\/edit$/))) view = <HeroFormView key={m[1]} go={go} meta={meta} heroId={m[1]} />;
  else if (path === "/profile") view = <ProfileView user={user} go={go} onLogout={() => { setUser(null); go("/"); }} />;
  else if ((m = path.match(/^\/matches\/(\d+)$/))) view = <MatchView key={m[1]} id={m[1]} go={go} />;
  else view = <HomeView go={go} />;

  return (
    <div className="page">
      <Navbar path={path} user={user} go={go} />
      <main className="container">{view}</main>
      <footer className="footer">SOFTWARE DEVELOPMENT TOOLS AND ENVIRONMENTS (1/2569) : ค่ายสุดท้าย</footer>
    </div>
  );
}
