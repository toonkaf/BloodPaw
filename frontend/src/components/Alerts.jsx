/** แสดงข้อผิดพลาดหลายข้อพร้อมกัน (สิ่งที่ไม่ผ่านเกณฑ์/ลืมกรอก) */
export function ErrorList({ messages }) {
  if (!messages || messages.length === 0) return null;
  return (
    <div className="alert" role="alert">
      {messages.length === 1 ? messages[0] : (
        <>
          <b>กรุณาแก้ไขก่อนบันทึก</b>
          <ul>{messages.map((m) => <li key={m}>{m}</li>)}</ul>
        </>
      )}
    </div>
  );
}
export const Notice = ({ children }) => (children ? <div className="alert ok">{children}</div> : null);
