# -*- coding: utf-8 -*-
"""계정/게시물 인사이트 리포트 — GitHub Actions에서 실행, 로그로 출력."""
import os
import requests

API = "https://graph.instagram.com/v23.0"


def report(token, user_id, label):
    if not token or not user_id:
        print(f"== {label}: token not set, skip ==")
        return
    me = requests.get(f"{API}/me", params={
        "fields": "username,followers_count,media_count", "access_token": token
    }, timeout=30).json()
    print(f"== {label} == {me}")
    media = requests.get(f"{API}/{user_id}/media", params={
        "fields": "id,timestamp,like_count,comments_count,caption",
        "limit": 15, "access_token": token
    }, timeout=30).json()
    for m in media.get("data", []):
        vals = {}
        try:
            ins = requests.get(f"{API}/{m['id']}/insights", params={
                "metric": "reach,views,saved,shares,total_interactions",
                "access_token": token
            }, timeout=30).json()
            for d in ins.get("data", []):
                v = None
                if d.get("total_value"):
                    v = d["total_value"].get("value")
                elif d.get("values"):
                    v = d["values"][0].get("value")
                vals[d["name"]] = v
            if "error" in ins:
                vals = {"err": ins["error"].get("message", "?")[:60]}
        except Exception as e:
            vals = {"err": str(e)[:60]}
        cap = (m.get("caption") or "")[:28].replace("\n", " ")
        print(f"{m['timestamp']} likes={m.get('like_count')} com={m.get('comments_count')} {vals} | {cap}")


report(os.environ.get("IG_TOKEN"), os.environ.get("IG_USER_ID"), "JUDGE")
report(os.environ.get("IG_TOKEN_LAB"), os.environ.get("IG_USER_ID_LAB"), "LAB")
