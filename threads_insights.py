# -*- coding: utf-8 -*-
"""스레드 게시물별 성적 리포트 — 어떤 소재/포맷이 먹히는지 판단용."""
import os

import requests

API = "https://graph.threads.net/v1.0"
METRICS = "views,likes,replies,reposts,quotes,shares"


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

    print(f"{'date':<11} {'views':>7} {'like':>5} {'reply':>5} {'rep':>4} {'shr':>4}  hook")
    for p, v in rows:
        hook = (p.get("text") or "").split("\n")[0][:46].replace("\r", "")
        date = p["timestamp"][:10]
        print(f"{date:<11} {str(v.get('views', '-')):>7} {str(v.get('likes', '-')):>5} "
              f"{str(v.get('replies', '-')):>5} {str(v.get('reposts', '-')):>4} "
              f"{str(v.get('shares', '-')):>4}  {hook}")

    vs = [v.get("views") or 0 for _, v in rows]
    if vs:
        print(f"-- 원글 {len(vs)}건 / 조회 평균 {sum(vs) // len(vs)} / 최고 {max(vs)} / 최저 {min(vs)}")


report(os.environ.get("THREADS_TOKEN_JUDGE"), os.environ.get("THREADS_USER_ID_JUDGE"), "JUDGE")
report(os.environ.get("THREADS_TOKEN_LAB"), os.environ.get("THREADS_USER_ID_LAB"), "LAB")
