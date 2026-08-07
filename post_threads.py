# -*- coding: utf-8 -*-
"""스레드 네이티브 '썰' 게시 — 본문에서 기승전결 완결. 홍보 답글 없음.

usage:
  python post_threads.py <slug>        # 카드뉴스 사연 1편 게시 (발행 워크플로에서 호출)
  python post_threads.py --pool judge  # 스레드 전용 썰 풀에서 1편 게시 (아침/저녁 슬롯)
env: THREADS_TOKEN_JUDGE/LAB, THREADS_USER_ID_JUDGE/LAB
"""
import datetime
import json
import os
import pathlib
import re
import sys
import time

import requests

API = "https://graph.threads.net/v1.0"
ROOT = pathlib.Path(__file__).parent
KST = datetime.timezone(datetime.timedelta(hours=9))


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s).replace("&nbsp;", " ").strip()


def fallback_text(story):
    cards = story["cards"]
    body = []
    for c in cards:
        if c["type"] == "story":
            body += [strip_tags(p) for p in c["paras"]]
        elif c["type"] == "quote":
            body += [strip_tags(q) for q in c["quotes"]]
    verdict = next((c for c in cards if c["type"] == "verdict"), None)
    lines = body[:5]
    if verdict:
        lines.append(f"이거 {strip_tags(verdict['a'])} vs {strip_tags(verdict['b'])}, 어느 쪽이에요?")
    return "\n".join(lines)


def creds(lab):
    suffix = "LAB" if lab else "JUDGE"
    return (os.environ.get(f"THREADS_TOKEN_{suffix}", ""),
            os.environ.get(f"THREADS_USER_ID_{suffix}", ""))


def parse_spoilers(text):
    """본문 속 ||블라인드|| 구간을 스포일러 엔티티로 변환.
    offset/length는 UTF-16 코드 유닛 기준(메타 API 엔티티 관례) — 2026-08-07 실발행으로 검증됨.
    반환: (마커 제거된 본문, text_entities 리스트[최대 10개])"""
    entities = []
    out = []
    u16 = lambda s: len(s.encode("utf-16-le")) // 2
    pos = 0
    while True:
        a = text.find("||", pos)
        b = text.find("||", a + 2) if a != -1 else -1
        if a == -1 or b == -1:
            out.append(text[pos:])
            break
        out.append(text[pos:a])
        hidden = text[a + 2:b]
        entities.append({"entity_type": "SPOILER",
                         "offset": u16("".join(out)), "length": u16(hidden)})
        out.append(hidden)
        pos = b + 2
    return "".join(out), entities[:10]


def publish(user_id, token, text, poll=None):
    """poll={"a":"예","b":"아니요"} 형태면 스레드 설문(24시간 자동 종료) 첨부.
    본문에 ||...|| 가 있으면 해당 구간을 탭해서 보는 블라인드(스포일러)로 변환."""
    text, entities = parse_spoilers(text)
    params = {"media_type": "TEXT", "text": text, "access_token": token}
    if entities:
        params["text_entities"] = json.dumps(entities, ensure_ascii=False)
    if poll:
        params["poll_attachment"] = json.dumps(
            {"option_a": poll["a"], "option_b": poll["b"]}, ensure_ascii=False)
    r = requests.post(f"{API}/{user_id}/threads", params=params, timeout=60)
    # 부가 기능(스포일러/설문)이 거부되면 하나씩 떼고 본문만이라도 나가게 한다
    for extra in ("text_entities", "poll_attachment"):
        if r.ok or extra not in params:
            continue
        print(f"{extra} attach failed: {r.text[:200]} — retry without it")
        params.pop(extra)
        r = requests.post(f"{API}/{user_id}/threads", params=params, timeout=60)
    if not r.ok:
        print(f"create failed: {r.text[:300]}")
        return None
    cid = r.json()["id"]
    time.sleep(10)
    p = requests.post(f"{API}/{user_id}/threads_publish", params={
        "creation_id": cid, "access_token": token}, timeout=60)
    if not p.ok:
        print(f"publish failed: {p.text[:300]}")
        return None
    return p.json()["id"]


def post_from_pool(kind, slot):
    """threads_pool_<kind>.json 에서 다음 썰 1편 게시. slot별 하루 1회 가드."""
    lab = kind == "lab"
    token, user_id = creds(lab)
    if not token or not user_id:
        print("threads token not set — skip")
        return
    pool_path = ROOT / f"threads_pool_{kind}.json"
    if not pool_path.exists():
        print(f"no pool file for {kind}")
        return
    pool = json.loads(pool_path.read_text(encoding="utf-8"))
    today = datetime.datetime.now(KST).strftime("%Y-%m-%d")
    posted = pool.setdefault("posted", {})
    if posted.get(slot) == today and not FORCE:
        print(f"{kind}/{slot} already posted today — skip")
        return
    items = pool.get("items", [])
    idx = pool.get("next", 0)
    if idx >= len(items):
        print(f"pool exhausted ({kind}) — 신규 썰 충전 필요")
        return
    # 선점: 게시 전에 먼저 기록해 중복 트리거를 막는다
    posted[slot] = today
    pool["next"] = idx + 1
    pool_path.write_text(json.dumps(pool, ensure_ascii=False, indent=2), encoding="utf-8")
    item = items[idx]
    if isinstance(item, dict):  # {"text":..., "poll":{"a","b"}} 형태 (제보 프레임 + 설문)
        mid = publish(user_id, token, item["text"], item.get("poll"))
    else:
        mid = publish(user_id, token, item)
    print(f"pool post {kind}/{slot} #{idx}: {mid}")


def post_from_story(slug):
    lab = slug.startswith("lab")
    token, user_id = creds(lab)
    if not token or not user_id:
        print("threads token not set — skip threads post")
        return
    story_path = ROOT / "stories" / f"{slug}.json"
    if not story_path.exists():
        print(f"no story for {slug}")
        return
    story = json.loads(story_path.read_text(encoding="utf-8"))
    text = story.get("threads") or fallback_text(story)
    mid = publish(user_id, token, text, story.get("threads_poll"))
    if mid:
        print(f"threads published {slug}: {mid}")


FORCE = False

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--force" in args:
        FORCE = True
        args.remove("--force")
    if args and args[0] == "--pool":
        post_from_pool(args[1] if len(args) > 1 else "judge",
                       args[2] if len(args) > 2 else "extra")
    else:
        post_from_story(args[0] if args else "")
