# -*- coding: utf-8 -*-
"""릴스 제작 진행률 스냅샷 — 클링 클립 / 나레이션 / 조립 단계를 한 화면에 보여준다."""
import io
import json
import pathlib
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from reel_specs import SPECS  # noqa: E402

ROOT = pathlib.Path(__file__).parent
SLUGS = list(SPECS)
N_CLIP, N_NARR, N_REEL = 30, 36, 6


def kling_status():
    r = subprocess.run("higgsfield generate list --video --size 100 --json", shell=True,
                       capture_output=True, text=True, encoding="utf-8")
    out = (r.stdout or "").strip()
    try:
        start = out.index("[") if out.startswith("[") else out.index("{")
        d = json.loads(out[start:])
        items = d if isinstance(d, list) else d.get("jobs") or d.get("data") or []
    except Exception:
        return 0, 0
    kl = [j for j in items if "kling" in str(j.get("job_type", "")).lower()][:N_CLIP + 2]
    return (sum(1 for j in kl if j.get("status") == "completed"),
            sum(1 for j in kl if j.get("status") in ("failed", "canceled")))


def count(slug, sub, pat):
    d = ROOT / "assets" / slug / sub
    return len(list(d.glob(pat))) if d.exists() else 0


def bar(n, t, w=24):
    filled = int(w * n / t) if t else 0
    return "█" * filled + "░" * (w - filled)


def main():
    # 힉스필드에서 다운로드 즉시 삭제하므로 목록 조회로는 진행률을 못 센다.
    # 로컬에 내려받은 클립 파일 수를 진실의 원천으로 삼는다.
    _, clip_fail = kling_status()
    narr = {s: min(count(s, "narr", "narr*.mp3"), 6) for s in SLUGS}
    clips = {s: count(s, "clips", "scene*.mp4") for s in SLUGS}
    clip_done = sum(clips.values())
    reels = {s: (ROOT / "output" / s / "reel-kling.mp4").exists() for s in SLUGS}

    narr_done, reel_done = sum(narr.values()), sum(reels.values())
    total = N_CLIP + N_NARR + N_REEL
    done = clip_done + narr_done + reel_done
    pct = round(done / total * 100)

    log = ""
    p = pathlib.Path("/tmp/narr2.log")
    if p.exists():
        lines = [l.strip() for l in p.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip()]
        log = lines[-1] if lines else ""

    print(f"\n{'=' * 48}")
    print(f"  릴스 6편 제작 진행률    {pct}%    ({done}/{total})")
    print(f"{'=' * 48}")
    print(f"  클링 클립   {bar(clip_done, N_CLIP)} {clip_done:2d}/{N_CLIP}"
          + (f"   실패 {clip_fail}" if clip_fail else ""))
    print(f"  나레이션    {bar(narr_done, N_NARR)} {narr_done:2d}/{N_NARR}")
    print(f"  영상 조립   {bar(reel_done, N_REEL)} {reel_done:2d}/{N_REEL}")
    print("\n  사연별 상태")
    for s in SLUGS:
        mark = "완료" if reels[s] else ("조립대기" if clips[s] == 5 else "생성중")
        print(f"   [{mark:4s}] {s:9s}  나레이션 {narr[s]}/6 · 클립 {clips[s]}/5")
    if log:
        print(f"\n  나레이션 로그: {log}")
    print()

    (ROOT / "build").mkdir(exist_ok=True)
    json.dump({"pct": pct, "clip_done": clip_done, "narr_done": narr_done,
               "reel_done": reel_done, "log": log},
              open(ROOT / "build" / "progress.json", "w"), ensure_ascii=False)


main()
