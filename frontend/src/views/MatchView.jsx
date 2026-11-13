import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../api/client.js";
import { ErrorList } from "../components/Alerts.jsx";
import { CaseCard, HeroCard } from "../components/Cards.jsx";
import { thaiTime } from "../lib/format.js";

const ENDED = { declined: "การติดต่อนี้ถูกปฏิเสธแล้ว", cancelled: "การจับคู่นี้ถูกยกเลิกแล้ว", confirmed: "เคสนี้สำเร็จแล้ว" };

/** หน้าติดต่อ: เจ้าของฮีโร่เห็น "ติดต่อเคสด่วน", เจ้าของเคสเห็น "ติดต่อฮีโร่" */
export default function MatchView({ id, go }) {
  const [m, setM] = useState(null);
  const [text, setText] = useState("");
  const [errors, setErrors] = useState([]);
  const box = useRef(null);
  const lastCount = useRef(0);

  const load = useCallback(() => api.match(id).then(setM).catch((e) => setErrors(e.messages)), [id]);
  useEffect(() => {
    load();
    const t = setInterval(load, 3000); // โพลข้อความใหม่ทุก 3 วินาที
    return () => clearInterval(t);
  }, [load]);

  useEffect(() => {
    if (m && m.messages.length !== lastCount.current) {
      lastCount.current = m.messages.length;
      box.current?.scrollTo({ top: box.current.scrollHeight });
    }
  }, [m]);

  if (!m) return errors.length ? <ErrorList messages={errors} /> : <div className="empty">กำลังโหลด...</div>;
  const pending = m.status === "pending";
  const act = (fn, ask, after) => async () => {
    if (ask && !window.confirm(ask)) return;
    try { await fn(); after ? after() : load(); } catch (e) { setErrors(e.messages); }
  };
  const send = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    try { await api.sendMessage(id, text); setText(""); load(); } catch (err) { setErrors(err.messages); }
  };

  return (
    <>
      <h2 className="page-title">{m.role === "hero_owner" ? "ติดต่อเคสด่วน" : "ติดต่อฮีโร่"}</h2>
      <ErrorList messages={errors} />
      {!pending && <div className="alert ok">{ENDED[m.status]} — ดูย้อนหลังได้แต่ส่งข้อความเพิ่มไม่ได้</div>}
      <div className="match-layout">
        <div>
          {m.role === "hero_owner" ? <CaseCard c={m.case} showStatus={false} /> : <HeroCard h={m.hero} />}
          <div className="match-actions">
            <button className="pill-btn red" disabled={!pending}
              onClick={act(() => api.decline(id), "ปฏิเสธการจับคู่นี้? ระบบจะนำเคสไปจับคู่ใหม่", () => go("/profile"))}>ปฏิเสธ</button>
            <button className="pill-btn green" disabled={!pending}
              onClick={act(() => api.confirm(id), "ยืนยันว่าสำเร็จแล้ว? เคสจะถูกปิดและย้อนกลับไม่ได้", () => go("/profile"))}>ยืนยัน/สำเร็จ</button>
          </div>
        </div>

        <section className="chat">
          <div className="chat-box" ref={box} aria-live="polite">
            {m.messages.length === 0 && <div className="empty">ยังไม่มีข้อความ ลองทักทายหรือกด tel เพื่อส่งเบอร์โทรของคุณ</div>}
            {m.messages.map((x) => (
              <div key={x.id} className={`bubble ${x.mine ? "mine" : "theirs"} ${x.kind}`}>
                {x.kind === "tel" ? <>📞 เบอร์โทร: <b>{x.body}</b></> : x.body}
                <time>{thaiTime(x.created_at)}</time>
              </div>
            ))}
          </div>
          <form className="chat-input" onSubmit={send}>
            <button type="button" className="tel-btn" disabled={!pending} onClick={act(() => api.sharePhone(id), "ส่งเบอร์โทรของคุณให้อีกฝ่าย?")}>tel.</button>
            <input value={text} onChange={(e) => setText(e.target.value)} maxLength={1000} disabled={!pending} placeholder="พิมพ์ข้อความ" aria-label="พิมพ์ข้อความ" />
            <button type="submit" className="send-btn" disabled={!pending || !text.trim()}>ส่ง</button>
          </form>
        </section>
      </div>
    </>
  );
}
