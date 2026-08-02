# -*- coding: utf-8 -*-
"""스레드 네이티브 '썰' 게시 — 본문에서 기승전결 완결, 인스타 유도는 셀프 답글로.

usage: python post_threads.py <slug>   예: python post_threads.py case-007
env: THREADS_TOKEN_JUDGE / THREADS_USER_ID_JUDGE (없으면 조용히 스킵)
"""
import json
import os
import pathlib
import re
import sys
import time

import requests

API = "https://graph.threads.net/v1.0"
ROOT = pathlib.Path(__file__).parent
RAW_BASE = os.environ.get(
    "RAW_BASE",
    "https://raw.githubusercontent.com/pdrliveofficial-lang/cardnews/main",
)


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s).replace("&nbsp;", " ").strip()


def fallback_text(story):
    """threads 필드가 없을 때만 쓰는 최소 버전 — 1인칭 썰 톤."""
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


def create_and_publish(user_id, token, text, image=None, reply_to=None):
    params = {"text": text, "access_token": token}
    if image:
        params["media_type"] = "IMAGE"
        params["image_url"] = image
    else:
        params["media_type"] = "TEXT"
    if reply_to:
        params["reply_to_id"] = reply_to
    r = requests.post(f"{API}/{user_id}/threads", params=params, timeout=60)
    if not r.ok:
        print(f"create failed: {r.text[:300]}")
        return None
    cid = r.json()["id"]
    time.sleep(30 if image else 10)
    p = requests.post(f"{API}/{user_id}/threads_publish", params={
        "creation_id": cid, "access_token": token}, timeout=60)
    if not p.ok:
        print(f"publish failed: {p.text[:300]}")
        return None
    return p.json()["id"]


def main(slug):
    token = os.environ.get("THREADS_TOKEN_JUDGE", "")
    user_id = os.environ.get("THREADS_USER_ID_JUDGE", "")
    if not token or not user_id:
        print("THREADS_TOKEN_JUDGE not set — skip threads post")
        return

    story_path = ROOT / "stories" / f"{slug}.json"
    if not story_path.exists():
        print(f"no story for {slug}")
        return
    story = json.loads(story_path.read_text(encoding="utf-8"))

    text = story.get("threads") or fallback_text(story)
    # 본문은 텍스트 온리 — 스레드에서 이미지는 '홍보물' 느낌을 주고 이탈을 부른다.
    root_id = create_and_publish(user_id, token, text)
    if not root_id:
        return
    print(f"threads published {slug}: {root_id}")

    # 인스타 유도는 본문이 아니라 셀프 답글로. 문구도 자연스럽게.
    reply = story.get("threads_reply") or (
        "이 사연 카드뉴스로도 정리해뒀어요. 다른 판결 사연 궁금하면 인스타 @comment.judgee 🙏"
    )
    time.sleep(3)
    rid = create_and_publish(user_id, token, reply, reply_to=root_id)
    print(f"self-reply: {rid}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
