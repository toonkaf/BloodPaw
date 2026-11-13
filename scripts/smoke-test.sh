#!/usr/bin/env bash
# ตรวจระบบหลัง Deploy แบบ end-to-end ตาม User Flow:
# สมัคร/เข้าสู่ระบบ -> ลงทะเบียนฮีโร่ (+รูป) -> ประกาศเคส -> ระบบจับคู่ -> คุยกัน/ส่งเบอร์ -> ยืนยัน -> Dashboard
set -euo pipefail
BASE="${BASE_URL:-http://localhost:${WEB_PORT:-8080}}/api"
J='Content-Type: application/json'
RUN="$(date +%s)$RANDOM"
HOSP="Smoke Hospital $RUN"     # ชื่อโรงพยาบาลไม่ซ้ำ เพื่อไม่ไปจับคู่กับข้อมูลอื่นในระบบ
py() { python3 -c "import sys,json;d=json.load(sys.stdin);print($1)"; }
fail() { echo "[FAIL] $1"; exit 1; }
ok() { echo "[ok] $1"; }

signup() { # name email -> token
  curl -fsS -X POST "$BASE/auth/register" -H "$J" -d "{\"email\":\"$2\",\"password\":\"password123\",\"full_name\":\"$1\"}" >/dev/null
  curl -fsS -X POST "$BASE/auth/login" -H "$J" -d "{\"email\":\"$2\",\"password\":\"password123\",\"full_name\":\"$1\"}" | py "d['access_token']"
}

curl -fsS "$BASE/health" >/dev/null && ok "health"
OWNER=$(signup "Owner" "owner$RUN@example.com"); DONOR=$(signup "Donor" "donor$RUN@example.com"); ok "register + login (2 users)"
A_OWNER="Authorization: Bearer $OWNER"; A_DONOR="Authorization: Bearer $DONOR"

CODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE/auth/login" -H "$J" -d "{\"email\":\"owner$RUN@example.com\",\"password\":\"wrong-pass1\",\"full_name\":\"Owner\"}")
[ "$CODE" = "401" ] && ok "wrong password rejected (401)" || fail "expected 401, got $CODE"

# อัปโหลดรูป (ไฟล์ PNG ขั้นต่ำ — Backend ตรวจจากเนื้อไฟล์จริง)
TMP=$(mktemp); printf '\x89PNG\r\n\x1a\n' > "$TMP"; head -c 64 /dev/zero >> "$TMP"
PHOTO=$(curl -fsS -X POST "$BASE/uploads" -H "$A_DONOR" -F "file=@$TMP;type=image/png" | py "d['url']"); rm -f "$TMP"
curl -fsS -o /dev/null "${BASE%/api}${PHOTO}" && ok "upload photo, downloadable without login ($PHOTO)"

BIRTH=$(python3 -c "import datetime;print(datetime.date.today()-datetime.timedelta(days=365*3+30))")
BAD=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE/heroes" -H "$A_DONOR" -H "$J" \
  -d "{\"name\":\"X\",\"species\":\"dog\",\"breed\":\"X\",\"birth_date\":\"$BIRTH\",\"weight_kg\":10,\"blood_type\":\"DEA 1.2\",\"vaccinated_ok\":true,\"no_chronic_disease\":true,\"criteria_confirmed\":true,\"hospitals\":[\"$HOSP\"],\"province\":\"X\",\"contact_phone\":\"0898765432\"}")
[ "$BAD" = "422" ] && ok "underweight hero rejected (422)" || fail "expected 422, got $BAD"

curl -fsS -X POST "$BASE/heroes" -H "$A_DONOR" -H "$J" \
  -d "{\"name\":\"Brownie\",\"species\":\"dog\",\"breed\":\"Golden\",\"birth_date\":\"$BIRTH\",\"weight_kg\":35,\"photo_url\":\"$PHOTO\",\"blood_type\":\"DEA 1.2\",\"vaccinated_ok\":true,\"no_chronic_disease\":true,\"criteria_confirmed\":true,\"hospitals\":[\"$HOSP\"],\"province\":\"Khon Kaen\",\"contact_phone\":\"0898765432\"}" >/dev/null && ok "register hero"

CASE=$(curl -fsS -X POST "$BASE/cases" -H "$A_OWNER" -H "$J" \
  -d "{\"species\":\"dog\",\"pet_name\":\"Corn\",\"breed\":\"Bangkaew\",\"symptom\":\"bleeding\",\"cause\":\"accident\",\"blood_type\":\"DEA 1.2\",\"hospital\":\"$HOSP\",\"contact_phone\":\"0812345678\",\"urgency\":\"critical\"}")
STATUS=$(echo "$CASE" | py "d['status']"); MID=$(echo "$CASE" | py "d['match_id']")
[ "$STATUS" = "found" ] && [ "$MID" != "None" ] && ok "case auto-matched (match $MID)" || fail "case was not matched (status=$STATUS)"

curl -fsS "$BASE/me/requests" -H "$A_DONOR" | py "[r['match_id'] for r in d]" | grep -q "$MID" && ok "hero received the request"

PRIV=$(curl -fsS "$BASE/cases" | py "any('contact_phone' in c for c in d)")
[ "$PRIV" = "False" ] && ok "public case list hides phone numbers" || fail "phone number leaked in public list"

curl -s -o /dev/null -w '%{http_code}' "$BASE/matches/$MID" | grep -q 401 && ok "chat requires login"

curl -fsS -X POST "$BASE/matches/$MID/messages" -H "$A_OWNER" -H "$J" -d '{"body":"hello"}' >/dev/null
curl -fsS -X POST "$BASE/matches/$MID/share-phone" -H "$A_DONOR" >/dev/null
SEEN=$(curl -fsS "$BASE/matches/$MID" -H "$A_OWNER" | py "[m['body'] for m in d['messages'] if m['kind']=='tel']")
[ "$SEEN" = "['0898765432']" ] && ok "tel button delivered the hero's phone to the case owner" || fail "tel message wrong: $SEEN"

BEFORE=$(curl -fsS "$BASE/stats" | py "d['cases_success']")
curl -fsS -X POST "$BASE/matches/$MID/confirm" -H "$A_DONOR" >/dev/null && ok "confirm"
AFTER=$(curl -fsS "$BASE/stats" | py "d['cases_success']")
[ "$AFTER" -gt "$BEFORE" ] && ok "dashboard success count $BEFORE -> $AFTER" || fail "dashboard did not change"
CODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE/matches/$MID/confirm" -H "$A_OWNER")
[ "$CODE" = "409" ] && ok "confirming twice rejected (409)" || fail "expected 409, got $CODE"
echo "SMOKE TEST PASSED"
