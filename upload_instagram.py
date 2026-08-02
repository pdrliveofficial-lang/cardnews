# -*- coding: utf-8 -*-
"""Instagram carousel auto-publisher for cardnews (공식 Instagram Graph API 사용).

state.json의 next_case 번호를 읽어 output/case-NNN/ 의 카드 7장을
캐러셀로 발행하고 next_case를 +1 한다.

env:
  IG_TOKEN    : Instagram API long-lived token (instagram_business_content_publish)
  IG_USER_ID  : Instagram professional account user id
  RAW_BASE    : (optional) raw image URL base
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


def wait_ready(container_id, timeout=180):
    for _ in range(timeout // 5):
        st = api("GET", container_id, fields="status_code")
        code = st.get("status_code")
        if code == "FINISHED":
            return
        if code == "ERROR":
            raise RuntimeError(f"container {container_id} failed: {st}")
        time.sleep(5)
    raise TimeoutError(f"container {container_id} not ready")


def main():
    if not TOKEN or not IG_USER:
        print("IG_TOKEN / IG_USER_ID not set — skipping publish")
        return
    state_path = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "state.json")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    today = datetime.datetime.now(KST).strftime("%Y-%m-%d")
    if state.get("last_published") == today:
        print(f"already published today ({today}) — skipping")
        return
    n = state["next_case"]
    prefix = state.get("prefix", "case")
    slug = f"{prefix}-{n:03d}"
    out_dir = ROOT / "output" / slug
    if not out_dir.exists():
        print(f"no content for {slug} — nothing to publish")
        return

    caption = (out_dir / "caption.txt").read_text(encoding="utf-8").strip()
    images = sorted(p.name for p in out_dir.glob("*.png"))
    print(f"publishing {slug}: {len(images)} cards")

    children = []
    for name in images:
        url = f"{RAW_BASE}/output/{slug}/{name}"
        res = api("POST", f"{IG_USER}/media", image_url=url, is_carousel_item="true")
        children.append(res["id"])
        print(f"  container {name} -> {res['id']}")

    for cid in children:
        wait_ready(cid)

    carousel = api(
        "POST", f"{IG_USER}/media",
        media_type="CAROUSEL", children=",".join(children), caption=caption,
    )
    wait_ready(carousel["id"])
    published = api("POST", f"{IG_USER}/media_publish", creation_id=carousel["id"])
    print(f"published {slug}: media id {published['id']}")

    pathlib.Path(ROOT / "last_slug.txt").write_text(slug, encoding="utf-8")
    state["next_case"] = n + 1
    state["last_published"] = today
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
