# -*- coding: utf-8 -*-
"""스레드 댓글 자동 답글 — 판사/연구소 계정.

usage: python reply_bot.py judge   |   python reply_bot.py lab
env: THREADS_TOKEN_*, THREADS_USER_ID_*, GEMINI_API_KEY(선택)
"""
import json
import os
import pathlib
import random
import sys
import time

import requests

API = "https://graph.threads.net/v1.0"
ROOT = pathlib.Path(__file__).parent
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

PERSONA = {
    "judge": (
        "너는 인스타/스레드 사연 계정 '댓글판사'의 운영자다. 사람들이 올린 사연에 "
        "판결을 내리는 콘셉트. 댓글에 다는 답글을 쓴다."
    ),
    "lab": (
        "너는 스레드 사연 계정 '잘잘못연구소'의 운영자다. 일상 갈등을 놓고 누가 "
        "잘못했는지 함께 따져보는 콘셉트. 댓글에 다는 답글을 쓴다."
    ),
}

GUIDE = """규칙:
- 반말체 금지, 친근한 해요체. 1~2문장, 40자 내외로 짧게.
- 댓글 내용에 실제로 반응할 것. 복붙 느낌 금지.
- 이모지는 최대 1개. 해시태그·링크·홍보 금지.
- 상대 의견에 맞장구치거나 가볍게 되묻기. 판결을 단정하지 말 것.
- 욕설/비방/정치 댓글이면 답글 대신 정확히 SKIP 이라고만 출력."""

FALLBACK = [
    "이 사연은 진짜 반응이 갈리네요 ㅋㅋ",
    "오 그 관점은 생각 못 했어요!",
    "댓글 보니 저도 다시 고민되네요 🤔",
    "그쵸... 저도 그 부분이 제일 걸렸어요.",
]


def api_get(token, path, params=None):
    p = dict(params or {})
    p["access_token"] = token
    r = requests.get(f"{API}{path}", params=p, timeout=30)
    if not r.ok:
        print(f"GET {path} failed: {r.text[:200]}")
        return None
    return r.json()


def gen_reply(post_text, comment_text, username, kind):
    if not GEMINI_KEY:
        return None
    prompt = (
        f"{PERSONA[kind]}\n\n{GUIDE}\n\n"
        f"[사연 원글]\n{post_text[:400]}\n\n"
        f"[{username}님의 댓글]\n{comment_text[:300]}\n\n답글:"
    )
    # 503(일시적 과부하)은 흔하므로 지수 백오프로 재시도한다.
    for attempt in range(3):
        try:
            r = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/"
                "gemini-flash-latest:generateContent",
                params={"key": GEMINI_KEY},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=40,
            )
            if not r.ok:
                print(f"gemini failed ({r.status_code}, try {attempt + 1}): {r.text[:150]}")
                if r.status_code in (429, 500, 503) and attempt < 2:
                    time.sleep(5 * (attempt + 1))
                    continue
                return None
            txt = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            txt = txt.strip('"').strip()
            if not txt or "SKIP" in txt.upper():
                return None
            return txt[:180]
        except Exception as e:
            print(f"gemini error (try {attempt + 1}): {e}")
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            return None
    return None


def publish_reply(token, user_id, text, reply_to):
    r = requests.post(f"{API}/{user_id}/threads", params={
        "media_type": "TEXT", "text": text, "reply_to_id": reply_to,
        "access_token": token}, timeout=60)
    if not r.ok:
        print(f"create reply failed: {r.text[:200]}")
        return None
    cid = r.json()["id"]
    time.sleep(8)
    p = requests.post(f"{API}/{user_id}/threads_publish", params={
        "creation_id": cid, "access_token": token}, timeout=60)
    if not p.ok:
        print(f"publish reply failed: {p.text[:200]}")
        return None
    return p.json()["id"]


def main(kind):
    suffix = "LAB" if kind == "lab" else "JUDGE"
    token = os.environ.get(f"THREADS_TOKEN_{suffix}", "")
    user_id = os.environ.get(f"THREADS_USER_ID_{suffix}", "")
    if not token or not user_id:
        print(f"{suffix} token not set — skip")
        return

    me = api_get(token, "/me", {"fields": "username"}) or {}
    my_username = me.get("username", "")

    state_path = ROOT / f"replied_{kind}.json"
    replied = set(json.loads(state_path.read_text(encoding="utf-8"))
                  if state_path.exists() else [])
    before = len(replied)

    threads = api_get(token, "/me/threads", {"fields": "id,text", "limit": 8})
    if not threads or "data" not in threads:
        print("no threads")
        return

    done = 0
    for th in threads["data"]:
        replies = api_get(token, f"/{th['id']}/replies",
                          {"fields": "id,text,username"})
        if not replies or "data" not in replies:
            continue
        for rep in replies["data"]:
            rid = rep["id"]
            if rid in replied:
                continue
            if rep.get("username", "") == my_username:
                replied.add(rid)
                continue
            text = gen_reply(th.get("text", ""), rep.get("text", "") or "",
                             rep.get("username", ""), kind)
            if not text:
                # AI 없거나 스킵 판정 → 이번엔 넘기고 다음 실행에 재시도
                print(f"skip {rid} (no ai reply)")
                continue
            mid = publish_reply(token, user_id, text, rid)
            print(f"reply to @{rep.get('username')} -> {mid}: {text}")
            replied.add(rid)
            done += 1
            time.sleep(6)
            if done >= 25:      # 한 번 실행에 25개 상한 (스팸 방지)
                break
        if done >= 25:
            break

    if len(replied) != before:
        state_path.write_text(json.dumps(sorted(replied), ensure_ascii=False, indent=1),
                              encoding="utf-8")
    print(f"replied {done} comments")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "judge")
