import { useCallback, useEffect, useState } from "react";
import { api, hasToken } from "./api/client.js";
import Navbar from "./components/Navbar.jsx";
import HomeView from "./views/HomeView.jsx";
import CasesView from "./views/CasesView.jsx";
import CaseFormView from "./views/CaseFormView.jsx";
import HeroFormView from "./views/HeroFormView.jsx";
import ProfileView from "./views/ProfileView.jsx";
import { LoginView, RegisterView } from "./views/AuthViews.jsx";

const PROTECTED = ["/cases/new", "/hero", "/profile"];
const currentPath = () => window.location.hash.replace(/^#/, "") || "/";

export default function App() {
  const [path, setPath] = useState(currentPath());
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(!hasToken());

  const go = useCallback((p) => { window.location.hash = p; }, []);
  const refreshUser = useCallback(async () => {
    try { setUser(await api.me()); } catch { setUser(null); }
    setReady(true);
  }, []);

  useEffect(() => {
    const onHash = () => setPath(currentPath());
    window.addEventListener("hashchange", onHash);
    if (hasToken()) refreshUser();
    return () => window.removeEventListener("hashchange", onHash);
  }, [refreshUser]);

  if (!ready) return null;

  const needLogin = PROTECTED.includes(path) && !user;
  const afterAuth = async () => { await refreshUser(); go("/"); };

  let view;
  if (needLogin) view = <LoginView onAuthed={afterAuth} go={go} notice="กรุณาเข้าสู่ระบบก่อนใช้งานส่วนนี้" />;
  else if (path === "/login") view = <LoginView onAuthed={afterAuth} go={go} />;
  else if (path === "/register") view = <RegisterView onAuthed={afterAuth} go={go} />;
  else if (path === "/cases") view = <CasesView user={user} />;
  else if (path === "/cases/new") view = <CaseFormView go={go} />;
  else if (path === "/hero") view = <HeroFormView go={go} />;
  else if (path === "/profile") view = <ProfileView user={user} onLogout={() => { setUser(null); go("/"); }} />;
  else view = <HomeView user={user} go={go} />;

  return (
    <div className="page">
      <Navbar path={path} user={user} go={go} />
      <main className="container">{view}</main>
      <footer className="footer">SOFTWARE DEVELOPMENT TOOLS AND ENVIRONMENTS (1/2569) : ค่ายสุดท้าย</footer>
    </div>
  );
}
