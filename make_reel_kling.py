# -*- coding: utf-8 -*-
"""클링 스타트/엔드 프레임 영상 클립 -> 릴스 조립 (2026-08-09 실험, lab-024).

assets/<slug>/clips/scene1..5.mp4 (5s Kling 클립) + 판정컷 스틸을 이어붙인다:
- 클립을 720x1280 30fps로 정규화 + 하단 자막(drawtext, 맑은고딕)
- 0.4s 크로스페이드, 마지막에 판정컷 스틸 3.5s
- BGM assets/bgm/lab.m4a, 총 30초 이내
Usage: python make_reel_kling.py lab-024
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).parent
FPS = 30
XFADE = 0.4
FONT_B = "C\\:/Windows/Fonts/malgunbd.ttf"
FONT_R = "C\\:/Windows/Fonts/malgun.ttf"

CAPTIONS = [
    "결혼식 끝나고 축의금 정리를 하는데",
    "친구 이름이 적힌 봉투가 비어 있었습니다",
    "며칠 고민하다 조심스럽게 물었어요",
    "\"아 깜빡했나봐ㅋㅋ 나중에 줄게~\"",
    "그 나중이... 6개월째입니다",
]
VERDICT_TOP = "빈 봉투, 실수라기엔 좀 길죠?"
VERDICT_SUB = "판정은 댓글로 · 스하리 남겨주면 다 갈게요"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-1500:])
        raise SystemExit("ffmpeg failed")


def esc(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\\\\\'").replace("%", "\\%").replace('"', '\\"')


def main(slug):
    base = ROOT / "assets" / slug
    clips = [base / "clips" / f"scene{i}.mp4" for i in range(1, 6)]
    for c in clips:
        if not c.exists():
            raise SystemExit(f"missing {c}")
    verdict_img = ROOT / "assets" / "lab-008" / "toon" / "99.png"  # 공유 돋보기 판정컷

    tmp = ROOT / "build" / f"kling-{slug}"
    tmp.mkdir(parents=True, exist_ok=True)
    segs, durs = [], []

    for i, (clip, cap) in enumerate(zip(clips, CAPTIONS)):
        seg = tmp / f"seg{i}.mp4"
        filt = (
            f"scale=720:1280:force_original_aspect_ratio=increase,"
            f"crop=720:1280,fps={FPS},"
            f"drawtext=fontfile='{FONT_B}':text='{esc(cap)}':fontsize=40:"
            "fontcolor=white:borderw=3:bordercolor=black@0.85:"
            "box=1:boxcolor=black@0.42:boxborderw=16:"
            "x=(w-text_w)/2:y=h-260,format=yuv420p"
        )
        run(["ffmpeg", "-y", "-i", str(clip), "-vf", filt, "-an",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", str(seg)])
        # 실제 길이 측정
        p = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "format=duration", "-of", "csv=p=0", str(seg)],
                           capture_output=True, text=True)
        durs.append(float(p.stdout.strip()))
        segs.append(seg)
        print(f"seg{i + 1} {durs[-1]:.2f}s")

    # 판정컷 스틸 3.5s
    vd = 3.5
    vseg = tmp / "seg_v.mp4"
    vfilt = (
        f"crop=iw:ih*0.86:0:0,scale=720:1280:force_original_aspect_ratio=increase,"
        f"crop=720:1280,fps={FPS},"
        f"drawtext=fontfile='{FONT_B}':text='{esc(VERDICT_TOP)}':fontsize=44:"
        "fontcolor=white:borderw=3:bordercolor=black@0.85:"
        "box=1:boxcolor=black@0.45:boxborderw=18:x=(w-text_w)/2:y=h-300,"
        f"drawtext=fontfile='{FONT_R}':text='{esc(VERDICT_SUB)}':fontsize=30:"
        "fontcolor=white:borderw=2:bordercolor=black@0.85:"
        "box=1:boxcolor=black@0.45:boxborderw=14:x=(w-text_w)/2:y=h-215,"
        "format=yuv420p"
    )
    run(["ffmpeg", "-y", "-framerate", str(FPS), "-loop", "1", "-t", str(vd),
         "-i", str(verdict_img), "-vf", vfilt, "-an",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", str(vseg)])
    segs.append(vseg)
    durs.append(vd)

    inputs = []
    for s in segs:
        inputs += ["-i", str(s)]
    total = sum(durs) - XFADE * (len(segs) - 1)
    chain, prev, offset = [], "[0:v]", 0.0
    for i in range(1, len(segs)):
        offset += durs[i - 1] - XFADE
        label = "[v]" if i == len(segs) - 1 else f"[x{i}]"
        chain.append(f"{prev}[{i}:v]xfade=transition=fade:duration={XFADE}:offset={offset:.2f}{label}")
        prev = f"[x{i}]"
    bgm = ROOT / "assets" / "bgm" / "lab.m4a"
    afade = max(total - 1.2, 0)
    filt = ";".join(chain) + f";[{len(segs)}:a]volume=0.85,afade=t=out:st={afade:.2f}:d=1.2[a]"

    out = ROOT / "output" / slug
    out.mkdir(parents=True, exist_ok=True)
    final = out / "reel-kling.mp4"
    run(["ffmpeg", "-y", *inputs, "-i", str(bgm), "-filter_complex", filt,
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
         "-pix_fmt", "yuv420p", str(final)])
    print(f"done -> {final} ({total:.1f}s, {final.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "lab-024")
