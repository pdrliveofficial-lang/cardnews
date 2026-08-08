# -*- coding: utf-8 -*-
"""스레드 댓글 자동 답글 — 판사/연구소 계정.

usage: python reply_bot.py judge   |   python reply_bot.py lab
env: THREADS_TOKEN_*, THREADS_USER_ID_*, GEMINI_API_KEY(선택)
"""
import json
import os
import pathlib
import sys
import time

import requests

API = "https://graph.threads.net/v1.0"
ROOT = pathlib.Path(__file__).parent
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

# ⚠️ 핵심 (2026-08-08 사용자 지시): 원글은 **제보받은 남의 사연**이지 운영자 경험담이 아니다.
# 1인칭으로 답하면("저도 그 부분이 걸렸어요") 계정 주인이 겪은 일로 읽혀 비난이 운영자에게 꽂힌다.
# 운영자는 사연을 전달한 제3자 위치에서, 댓글 단 사람과 함께 제보자를 공감해줘야 한다.
PERSONA = {
    "judge": (
        "너는 스레드 계정 '댓글판사' 운영자다. 이 계정은 사람들에게 제보받은 연애·결혼 갈등 "
        "사연을 대신 올려주고, 잘잘못은 댓글로 판결받는 곳이다.\n"
        "원글 사연은 **제보자(남)의 이야기이지 네 경험이 아니다.** 너는 사연을 전달한 사람으로서, "
        "댓글 쓴 분과 함께 제보자 입장을 헤아리며 이야기를 나눈다. "
        "사연 속 인물은 '제보자님'이라고 부른다."
    ),
    "lab": (
        "너는 스레드 계정 '잘잘못연구소' 운영자다. 이 계정은 사람들에게 제보받은 일상 갈등 "
        "사연을 대신 올려주고, 누가 잘못했는지 댓글로 판정받는 곳이다.\n"
        "원글 사연은 **제보자(남)의 이야기이지 네 경험이 아니다.** 너는 사연을 전달한 사람으로서, "
        "댓글 쓴 분과 함께 제보자 입장을 헤아리며 이야기를 나눈다. "
        "사연 속 인물은 '제보자님'이라고 부른다."
    ),
}

# -- 팔로우 유도 (2026-08-08 사용자 지시) --
# 매 답글마다 붙이면 매크로 티가 나고 스팸으로 읽힌다 → CTA_EVERY 회마다 1번만,
# 문구를 돌려가며 붙인다. 답글 본문은 AI가 쓴 그대로 두고 CTA는 줄바꿈 후 추가.
CTA_EVERY = 4
CTA = {
    "judge": [
        "이런 사건 더 보시려면 팔로우 해두세요 ⚖️",
        "매일 낮 12시에 새 사건 올라와요, 팔로우하고 같이 판결해주세요!",
        "제보 사연 더 있어요 — 팔로우하고 보러 오세요 👀",
        "다음 재판도 궁금하시면 팔로우요!",
    ],
    "lab": [
        "이런 사연 더 보시려면 팔로우 해두세요 🔍",
        "매일 저녁 7시에 새 사건 파일 열려요, 팔로우하고 같이 판정해주세요!",
        "애매한 사건 더 모으는 중이에요 — 팔로우하고 보러 오세요 👀",
        "다음 연구도 궁금하시면 팔로우요!",
    ],
}


def add_cta(text, kind, n):
    """n번째 답글이 CTA 차례면 팔로우 유도 한 줄을 덧붙인다."""
    if n % CTA_EVERY != 0:
        return text
    lines = CTA.get(kind) or []
    if not lines:
        return text
    cta = lines[(n // CTA_EVERY - 1) % len(lines)]
    merged = f"{text}\n{cta}"
    return merged if len(merged) <= 240 else text


GUIDE = """규칙:
- 반말체 금지, 친근한 해요체. 1~2문장, 40자 내외로 짧게.
- 댓글 내용에 실제로 반응할 것. 복붙 느낌 금지.
- 이모지는 최대 1개. 해시태그·링크·홍보 금지.
- 상대 의견에 맞장구치거나 가볍게 되묻기. 판결을 단정하지 말 것.
- 욕설/비방/정치 댓글이면 답글 대신 정확히 SKIP 이라고만 출력.

⚠️ 시점 규칙 (가장 중요):
- 사연은 제보받은 남의 이야기다. **네가 겪은 일처럼 쓰지 말 것.**
  나쁜 예: "저도 그 부분이 걸렸어요" / "제가 그때 참았어야 했나 봐요" / "저희 집도 그래요"
  좋은 예: "제보자님도 그래서 답답하셨나 봐요" / "저도 이 사연 받고 좀 놀랐어요"
           "그쵸, 그 대사가 제일 얄밉더라고요" / "말씀처럼 그 부분이 핵심 같아요"
- 사연 속 당사자를 가리킬 땐 '제보자님'이라고 쓴다. 상대방은 '그분', '상대분' 정도로.
- 사연 내용을 두고 댓글 쓴 분과 **같이 이야기하는 사람**의 말투를 유지할 것."""

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
    # 429(무료 쿼터 소진)는 재시도해도 소용없다 — 즉시 쿼터가 넉넉한 보조 모델로 넘어간다.
    # 5xx(일시 과부하)만 같은 모델에서 짧게 재시도.
    for model in ("gemini-flash-latest", "gemini-flash-lite-latest"):
        for attempt in range(2):
            try:
                r = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{model}:generateContent",
                    params={"key": GEMINI_KEY},
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                    timeout=40,
                )
                if not r.ok:
                    print(f"gemini {model} failed ({r.status_code}, try {attempt + 1})")
                    if r.status_code == 429:
                        break  # 다음 모델로
                    if r.status_code in (500, 503) and attempt == 0:
                        time.sleep(6)
                        continue
                    break
                txt = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                txt = txt.strip('"').strip()
                if not txt:
                    return None
                if "SKIP" in txt.upper():
                    return "SKIP"  # 욕설/정치 등 답글 부적합 판정
                return txt[:180]
            except Exception as e:
                print(f"gemini {model} error (try {attempt + 1}): {e}")
                if attempt == 0:
                    time.sleep(6)
                    continue
                break
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


def fetch_all(token, path, params, max_pages=20):
    """커서 페이지네이션을 끝까지 따라가 전체 목록을 모은다.
    (기본 응답은 첫 페이지뿐이라, 댓글 많은 글은 대부분이 안 보였다 — 2026-08-08 발견)"""
    out, after, pages = [], None, 0
    while pages < max_pages:
        p = dict(params)
        if after:
            p["after"] = after
        d = api_get(token, path, p)
        if not d or "data" not in d:
            break
        out += d["data"]
        after = (d.get("paging") or {}).get("cursors", {}).get("after")
        if not after or not d["data"]:
            break
        pages += 1
    return out


def collect_pending(token, my_username, replied, thread_limit):
    """미답변 댓글 목록을 수집. (원글, 댓글) 튜플 리스트."""
    threads = fetch_all(token, "/me/threads",
                        {"fields": "id,text,timestamp", "limit": 100})[:thread_limit]
    pending, total = [], 0
    for th in threads:
        replies = fetch_all(token, f"/{th['id']}/replies",
                            {"fields": "id,text,username", "limit": 100})
        total += len(replies)
        for rep in replies:
            if rep["id"] in replied or rep.get("username", "") == my_username:
                continue
            pending.append((th, rep))
    return threads, total, pending


def main(kind, audit=False, cap=25, thread_limit=8):
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

    threads, total, pending = collect_pending(token, my_username, replied, thread_limit)
    print(f"[{kind}] 원글 {len(threads)}개 / 수집 댓글 {total}개 / 미답변 {len(pending)}개")

    if audit:
        by_post = {}
        for th, rep in pending:
            by_post.setdefault(th["id"], (th, []))[1].append(rep)
        for th, reps in sorted(by_post.values(), key=lambda x: -len(x[1])):
            hook = (th.get("text") or "").split("\n")[0][:40]
            print(f"  미답변 {len(reps):3d}건 | {th.get('timestamp','')[:10]} | {hook}")
        return

    done = 0
    ai_fails = 0  # 연속 AI 실패 카운터 — 5회면 쿼터 소진으로 보고 실행 종료
    for th, rep in pending:
        rid = rep["id"]
        text = gen_reply(th.get("text", ""), rep.get("text", "") or "",
                         rep.get("username", ""), kind)
        if text == "SKIP":
            # 욕설/정치 등 답글 부적합 — 기록하고 영구 제외
            print(f"skip {rid} (ai judged SKIP)")
            replied.add(rid)
            continue
        if not text:
            # AI 실패(쿼터 등) — 매크로 문구로 때우지 않는다 (2026-08-06 사용자 지시:
            # "준비된 답변만 달면 안 되지"). 다음 실행에서 진짜 답변으로 재시도.
            ai_fails += 1
            print(f"skip {rid} (no ai reply, retry next run)")
            if ai_fails >= 5:
                print("AI 연속 실패 5회 — 쿼터 소진으로 보고 이번 실행 종료")
                break
            continue
        ai_fails = 0
        text = add_cta(text, kind, done + 1)
        mid = publish_reply(token, user_id, text, rid)
        print(f"reply to @{rep.get('username')} -> {mid}: {text}")
        replied.add(rid)
        done += 1
        if done % 20 == 0:  # 진행 상황을 로그에 남겨 장시간 실행을 추적
            print(f"--- {done}/{len(pending)} 진행 중 ---")
        time.sleep(6)
        if done >= cap:
            print(f"이번 실행 상한 {cap}개 도달 — 나머지는 다음 실행에서")
            break

    if len(replied) != before:
        state_path.write_text(json.dumps(sorted(replied), ensure_ascii=False, indent=1),
                              encoding="utf-8")
    print(f"replied {done} comments (남은 미답변 약 {max(len(pending) - done, 0)}개)")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]

    def flag_val(name, default):
        for f in flags:
            if f.startswith(f"--{name}="):
                return int(f.split("=", 1)[1])
        return default

    main(args[0] if args else "judge",
         audit="--audit" in flags,
         cap=flag_val("cap", 25),
         thread_limit=flag_val("threads", 8))
