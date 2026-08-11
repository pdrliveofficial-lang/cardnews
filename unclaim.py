# -*- coding: utf-8 -*-
"""발행 실패 시 선점(claim) 롤백 — 그날 재시도가 가능하게 한다.

claim.py가 발행 전에 오늘 날짜를 선점하는 이유는 동시 실행 경합 방지인데,
발행이 실패하면 그 하루가 통째로 날아간다 (2026-08-09~11 연구소 3일 결측 사고).
이 스크립트를 워크플로의 failure() 스텝에서 호출해 claimed를 되돌린다.

usage: python unclaim.py state-lab.json
"""
import datetime
import json
import sys

KST = datetime.timezone(datetime.timedelta(hours=9))
path = sys.argv[1] if len(sys.argv) > 1 else "state.json"
today = datetime.datetime.now(KST).strftime("%Y-%m-%d")
s = json.load(open(path, encoding="utf-8"))

if s.get("last_published") == today:
    print("KEEP")  # 실제로 발행됐다면 롤백하지 않는다 (후속 스텝만 실패한 경우)
    sys.exit(0)
if s.get("claimed") != today:
    print("NOOP")
    sys.exit(0)

s.pop("claimed", None)
json.dump(s, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("UNCLAIMED")
