# -*- coding: utf-8 -*-
"""스레드 게시물별 성적 리포트 — 어떤 소재/포맷이 먹히는지 판단용.

--save 를 주면 stats/threads_stats.jsonl 에 스냅샷을 누적한다.
게시물은 시간이 지나며 조회가 붙으므로, 신선도를 맞춰 비교하려면
age_h(게시 후 경과시간)를 함께 기록해야 한다.
"""
import datetime
import json
import os
import pathlib
import sys

import requests

API = "https://graph.threads.net/v1.0"
METRICS = "views,likes,replies,reposts,quotes,shares"
SAVE = "--save" in sys.argv
STATS = pathlib.Path(__file__).parent / "stats" / "threads_stats.jsonl"
NOW = datetime.datetime.now(datetime.timezone.utc)
snapshots = []


def age_hours(ts):
    try:
        t = datetime.datetime.fromisoformat(ts.replace("+0000", "+00:00"))
        return round((NOW - t).total_seconds() / 3600, 1)
    except Exception:
        return None


def report(token, user_id, label):
    if not token or not user_id:
        print(f"== {label}: token not set, skip ==")
        return
    me = requests.get(f"{API}/me", params={
        "fields": "username,threads_profile_picture_url", "access_token": token
    }, timeout=30).json()
    print(f"\n===== {label} ({me.get('username', '?')}) =====")
    posts = requests.get(f"{API}/{user_id}/threads", params={
        "fields": "id,timestamp,text,media_type,is_reply,permalink",
        "limit": 40, "access_token": token
    }, timeout=30).json()
    rows = []
    for p in posts.get("data", []):
        if p.get("is_reply"):
            continue  # 답글은 제외 — 원글 성적만 본다
        vals = {}
        try:
            ins = requests.get(f"{API}/{p['id']}/insights", params={
                "metric": METRICS, "access_token": token}, timeout=30).json()
            for d in ins.get("data", []):
                vals[d["name"]] = d.get("values", [{}])[0].get("value")
            if "error" in ins:
                vals = {"err": ins["error"].get("message", "?")[:50]}
        except Exception as e:
            vals = {"err": str(e)[:50]}
        rows.append((p, vals))

    print(f"{'date':<11} {'age_h':>6} {'views':>7} {'like':>5} {'reply':>5} {'rep':>4} {'shr':>4}  hook")
    for p, v in rows:
        hook = (p.get("text") or "").split("\n")[0][:46].replace("\r", "")
        age = age_hours(p["timestamp"])
        print(f"{p['timestamp'][:10]:<11} {str(age):>6} {str(v.get('views', '-')):>7} "
              f"{str(v.get('likes', '-')):>5} {str(v.get('replies', '-')):>5} "
              f"{str(v.get('reposts', '-')):>4} {str(v.get('shares', '-')):>4}  {hook}")
        snapshots.append({
            "at": NOW.isoformat(timespec="seconds"), "account": label, "id": p["id"],
            "posted": p["timestamp"], "age_h": age, "hook": hook,
            "views": v.get("views"), "likes": v.get("likes"), "replies": v.get("replies"),
            "reposts": v.get("reposts"), "shares": v.get("shares"),
        })

    # 24h 이상 지난 글만 성숙 표본으로 본다 — 신선한 글과 섞으면 비교가 왜곡된다.
    mature = [v.get("views") or 0 for p, v in rows if (age_hours(p["timestamp"]) or 0) >= 24]
    if mature:
        print(f"-- 24h+ 성숙 원글 {len(mature)}건 / 조회 평균 {sum(mature) // len(mature)} "
              f"/ 최고 {max(mature)} / 최저 {min(mature)}")
    else:
        print(f"-- 24h+ 성숙 원글 0건 (총 {len(rows)}건) — 비교 가능한 표본 아직 없음")


report(os.environ.get("THREADS_TOKEN_JUDGE"), os.environ.get("THREADS_USER_ID_JUDGE"), "JUDGE")
report(os.environ.get("THREADS_TOKEN_LAB"), os.environ.get("THREADS_USER_ID_LAB"), "LAB")

if SAVE and snapshots:
    STATS.parent.mkdir(exist_ok=True)
    with STATS.open("a", encoding="utf-8") as f:
        for s in snapshots:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"\nsaved {len(snapshots)} snapshots -> {STATS.name}")
