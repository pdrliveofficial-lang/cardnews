# -*- coding: utf-8 -*-
"""카드뉴스 발행과 함께 스레드에 훅 글 게시 (인스타 유입 유도).

usage: python post_threads.py <slug>   예: python post_threads.py case-007
env: THREADS_TOKEN_JUDGE (없으면 조용히 스킵)
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


def build_text(story):
    """story JSON의 threads 필드 우선, 없으면 표지·투표 카드로 훅 생성."""
    if story.get("threads"):
        return story["threads"]
    cover = story["cards"][0]
    verdict = next((c for c in story["cards"] if c["type"] == "verdict"), None)
    title = strip_tags(cover["title"].replace("<br>", " "))
    lines = [title, ""]
    if verdict:
        lines += [f"🅰️ {verdict['a']}", f"🅱️ {verdict['b']}", ""]
    lines.append("당신의 판결은? 댓글로 남겨주세요 ⚖️")
    lines.append("전체 사연은 프로필 링크(인스타)에서 👉 @comment.judgee")
    return "\n".join(lines)


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
    text = build_text(story)
    image = f"{RAW_BASE}/output/{slug}/01.png"

    create = requests.post(f"{API}/{user_id}/threads", params={
        "media_type": "IMAGE", "image_url": image, "text": text,
        "access_token": token,
    }, timeout=60)
    if not create.ok:
        print(f"threads create failed: {create.text[:300]}")
        return
    cid = create.json()["id"]
    time.sleep(30)  # 컨테이너 처리 대기 (공식 권장)

    pub = requests.post(f"{API}/{user_id}/threads_publish", params={
        "creation_id": cid, "access_token": token,
    }, timeout=60)
    if pub.ok:
        print(f"threads published {slug}: {pub.json()}")
    else:
        print(f"threads publish failed: {pub.text[:300]}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
