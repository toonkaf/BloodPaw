#!/usr/bin/env bash
# ตรวจระบบหลัง Deploy แบบ end-to-end: สมัคร → ล็อกอิน → ลงทะเบียนฮีโร่ → ประกาศเคส → ตรวจ Privacy → ปิดเคส
set -euo pipefail
BASE="${BASE_URL:-http://localhost:${WEB_PORT:-8080}}/api"
EMAIL="smoke$(date +%s)@example.com"
J='Content-Type: application/json'
py() { python3 -c "import sys,json;d=json.load(sys.stdin);print($1)"; }
fail() { echo "[FAIL] $1"; exit 1; }

curl -fsS "$BASE/health" >/dev/null && echo "[ok] health"

curl -fsS -X POST "$BASE/auth/register" -H "$J" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"password123\",\"full_name\":\"Smoke\"}" >/dev/null && echo "[ok] register"
TOKEN=$(curl -fsS -X POST "$BASE/auth/login" -H "$J" -d "{\"email\":\"$EMAIL\",\"password\":\"password123\"}" | py "d['access_token']")
AUTH="Authorization: Bearer $TOKEN"; echo "[ok] login"

curl -fsS -X POST "$BASE/heroes" -H "$AUTH" -H "$J" \
  -d '{"name":"Brownie","species":"dog","blood_type":"DEA 1.1-","weight_kg":28,"province":"Bangkok","contact_phone":"0898765432"}' >/dev/null && echo "[ok] register hero"

CASE=$(curl -fsS -X POST "$BASE/cases" -H "$AUTH" -H "$J" \
  -d '{"pet_name":"Corn","species":"dog","blood_type":"DEA 1.1-","hospital":"Vet A","province":"Bangkok","urgency":"critical","contact_phone":"0812345678"}' | py "d['id']")
echo "[ok] create case $CASE"

ANON=$(curl -fsS "$BASE/cases?status=searching" | py "[c['contact_phone'] for c in d if c['id']==$CASE][0]")
[ "$ANON" = "None" ] && echo "[ok] contact hidden from anonymous" || fail "contact phone leaked to anonymous user"

SEARCHING=$(curl -fsS "$BASE/stats" | py "d['cases_searching']")
[ "$SEARCHING" -ge 1 ] && echo "[ok] dashboard counts searching=$SEARCHING" || fail "dashboard did not count the new case"

curl -fsS -X POST "$BASE/cases/$CASE/close" -H "$AUTH" >/dev/null && echo "[ok] close case"
CODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE/cases/$CASE/close" -H "$AUTH")
[ "$CODE" = "409" ] && echo "[ok] closing twice rejected (409)" || fail "expected 409, got $CODE"
echo "SMOKE TEST PASSED"
