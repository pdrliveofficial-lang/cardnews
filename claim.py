# -*- coding: utf-8 -*-
"""오늘 발행 슬롯 선점 — 동시 실행 경합 방지용. usage: python claim.py state.json"""
import datetime
import json
import sys

KST = datetime.timezone(datetime.timedelta(hours=9))
path = sys.argv[1]
today = datetime.datetime.now(KST).strftime("%Y-%m-%d")
s = json.load(open(path, encoding="utf-8"))
if s.get("last_published") == today or s.get("claimed") == today:
    print("SKIP")
    sys.exit(0)
s["claimed"] = today
json.dump(s, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("CLAIMED")
