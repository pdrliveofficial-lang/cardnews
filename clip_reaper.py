# -*- coding: utf-8 -*-
"""클링 클립 감시 → 완료 즉시 다운로드 → 힉스필드에서 삭제.

사장님 지시(2026-08-09): 힉스필드에 기록을 남기지 않는다. 다운로드와 삭제를 한 세트로,
완료되는 대로 바로 처리한다.

삭제는 브라우저 세션 토큰이 필요한 fnf API를 쓰므로, 여기서는 다운로드 + 삭제 대상
목록만 만들고 실제 DELETE는 브라우저에서 실행한다(reaper_pending.json).

프롬프트 문구로 어느 사연·몇 번째 장면인지 역매핑한다.
Usage: python clip_reaper.py [--loop]
"""
import io
import json
import pathlib
import subprocess
import sys
import time
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT))

PAYLOAD = json.loads((ROOT / "assets" / "kling_payload.json").read_text(encoding="utf-8"))
PENDING = ROOT / "build" / "reaper_pending.json"
DONE_LOG = ROOT / "build" / "reaper_done.json"


def motion_key(p):
    """프롬프트 앞부분을 키로 삼아 (slug, scene#) 매칭."""
    return (p or "").strip()[:60].lower()


INDEX = {}
for slug, arr in PAYLOAD.items():
    for i, it in enumerate(arr):
        INDEX[motion_key(it["p"])] = (slug, i + 1)


def find_url(o, key="result_url"):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key and isinstance(v, str) and v.startswith("http"):
                return v
            r = find_url(v, key)
            if r:
                return r
    if isinstance(o, list):
        for v in o:
            r = find_url(v, key)
            if r:
                return r
    return None


def list_jobs():
    r = subprocess.run("higgsfield generate list --video --size 100 --json", shell=True,
                       capture_output=True, text=True, encoding="utf-8")
    out = (r.stdout or "").strip()
    try:
        start = out.index("[") if out.startswith("[") else out.index("{")
        d = json.loads(out[start:])
        return d if isinstance(d, list) else d.get("jobs") or d.get("data") or []
    except Exception:
        return []


def sweep():
    done = json.loads(DONE_LOG.read_text()) if DONE_LOG.exists() else []
    pend = json.loads(PENDING.read_text()) if PENDING.exists() else []
    got = 0
    for j in list_jobs():
        if "kling" not in str(j.get("job_type", "")).lower():
            continue
        if j.get("status") != "completed":
            continue
        jid = j.get("id")
        if jid in done:
            continue
        prompt = (j.get("params") or {}).get("prompt") or j.get("prompt") or ""
        hit = INDEX.get(motion_key(prompt))
        if not hit:
            continue                      # 이번 배치와 무관한 잡은 건드리지 않는다
        slug, n = hit
        url = find_url(j)
        if not url:
            continue
        d = ROOT / "assets" / slug / "clips"
        d.mkdir(parents=True, exist_ok=True)
        dest = d / f"scene{n}.mp4"
        if not dest.exists():
            urllib.request.urlretrieve(url, dest)
            print(f"↓ {slug} scene{n} ({dest.stat().st_size // 1024}KB)")
            got += 1
        done.append(jid)
        if jid not in pend:
            pend.append(jid)              # 브라우저에서 삭제할 목록
    (ROOT / "build").mkdir(exist_ok=True)
    DONE_LOG.write_text(json.dumps(done))
    PENDING.write_text(json.dumps(pend))
    return got, len(done), len(pend)


def main():
    loop = "--loop" in sys.argv
    while True:
        got, total, pend = sweep()
        print(f"다운로드 누적 {total}/30 · 삭제대기 {pend}건" + (f" (이번 {got}건)" if got else ""))
        if not loop or total >= 30:
            break
        time.sleep(45)


main()
