# -*- coding: utf-8 -*-
"""저녁 릴스 발행 — 오늘 낮에 캐러셀로 나간 사연을 릴스로 한 번 더 (비팔로워 도달용).

state 파일의 last_published가 오늘이어야 발행한다 (캐러셀 후속 원칙).
발행 대상: output/<prefix-(next_case-1)>/reel.mp4 (없으면 스킵 — 워크플로가 먼저 생성·커밋).
중복 가드: state의 last_reel == 오늘이면 스킵.

env:
  IG_TOKEN / IG_USER_ID : 계정 토큰 (판사 또는 연구소용을 워크플로에서 주입)
usage: python upload_instagram_reel.py [state.json|state-lab.json]
"""
import datetime
import json
import os
import pathlib
import sys
import time

import requests

KST = datetime.timezone(datetime.timedelta(hours=9))
API = "https://graph.instagram.com/v23.0"
ROOT = pathlib.Path(__file__).parent
RAW_BASE = os.environ.get(
    "RAW_BASE",
    "https://raw.githubusercontent.com/pdrliveofficial-lang/cardnews/main",
)
TOKEN = os.environ.get("IG_TOKEN", "")
IG_USER = os.environ.get("IG_USER_ID", "")


def api(method, path, **params):
    params["access_token"] = TOKEN
    r = requests.request(method, f"{API}/{path}", params=params, timeout=60)
    if not r.ok:
        print(f"API error {r.status_code}: {r.text}", file=sys.stderr)
        r.raise_for_status()
    return r.json()


def wait_ready(container_id, timeout=600):
    """영상 처리는 이미지보다 오래 걸린다 (통상 1~3분)."""
    for _ in range(timeout // 10):
        st = api("GET", container_id, fields="status_code")
        code = st.get("status_code")
        if code == "FINISHED":
            return
        if code == "ERROR":
            raise RuntimeError(f"container {container_id} failed: {st}")
        time.sleep(10)
    raise TimeoutError(f"container {container_id} not ready")


def main():
    if not TOKEN or not IG_USER:
        print("IG_TOKEN / IG_USER_ID not set — skipping")
        return
    state_path = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "state.json")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    today = datetime.datetime.now(KST).strftime("%Y-%m-%d")

    if state.get("last_reel") == today:
        print(f"reel already published today ({today}) — skipping")
        return
    if state.get("last_published") != today:
        print(f"carousel not published today (last: {state.get('last_published')}) — skipping reel")
        return

    prefix = state.get("prefix", "case")
    slug = f"{prefix}-{state['next_case'] - 1:03d}"
    reel = ROOT / "output" / slug / "reel.mp4"
    if not reel.exists():
        print(f"no reel.mp4 for {slug} — skipping (make_reel.py 먼저)")
        return

    caption = (ROOT / "output" / slug / "caption.txt").read_text(encoding="utf-8").strip()
    video_url = f"{RAW_BASE}/output/{slug}/reel.mp4"
    cover_url = f"{RAW_BASE}/output/{slug}/01.png"
    print(f"publishing reel {slug}: {video_url}")

    container = api(
        "POST", f"{IG_USER}/media",
        media_type="REELS", video_url=video_url, caption=caption,
        cover_url=cover_url, share_to_feed="false",
    )
    wait_ready(container["id"])
    published = api("POST", f"{IG_USER}/media_publish", creation_id=container["id"])
    print(f"published reel {slug}: media id {published['id']}")

    state["last_reel"] = today
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
