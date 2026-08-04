# -*- coding: utf-8 -*-
"""웹툰 상황컷 -> 릴스 mp4 조립 (기존 make_reel.py의 카드 방식과 별개 실험 트랙).

assets/<slug>/toon/NN.png (9:16 일러스트) + texts.json 자막을 풀스크린 합성:
- 장면마다 느린 줌인(Ken Burns) + 하단 1/3에 자막(제목/보조 2단)
- 장면 간 0.4초 페이드, BGM은 make_reel.py와 동일 규칙
- 결과: output/<slug>/reel-toon.mp4

texts.json 형식: [{"top": "제목줄", "sub": "보조줄(선택)", "crop_bottom": 0.15(선택)}, ...]
Usage: python make_reel_toon.py case-012
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).parent
FPS = 30
XFADE = 0.4
DUR_FIRST = 3.4
DUR_MID = 2.9
DUR_LAST = 3.6
FONT_BOLD = "C\\:/Windows/Fonts/malgunbd.ttf"
FONT_REG = "C\\:/Windows/Fonts/malgun.ttf"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-2000:])
        raise SystemExit("ffmpeg failed")


def esc(t):
    # drawtext 특수문자 이스케이프
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\\\\\'").replace("%", "\\%")


def build_segment(png, dur, out, text, first=False):
    frames = int(dur * FPS)
    crop_expr = "crop=iw:ih"
    if text.get("crop_bottom"):
        keep = 1 - float(text["crop_bottom"])
        crop_expr = f"crop=iw:ih*{keep:.2f}:0:0"
    # 줌인: 2배 스케일 후 zoompan (지터 방지용 큰 캔버스)
    z = "1.10-0.0006*on" if first else "1+0.0005*on"
    chain = (
        f"[0:v]{crop_expr},scale=2160:3840:force_original_aspect_ratio=increase,"
        f"crop=2160:3840,zoompan=z='{z}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":s=1080x1920:fps={FPS}"
    )
    top, sub = text.get("top", ""), text.get("sub", "")
    if top:
        chain += (
            f",drawtext=fontfile='{FONT_BOLD}':text='{esc(top)}':fontsize=58:"
            "fontcolor=white:borderw=3:bordercolor=black@0.85:"
            "box=1:boxcolor=black@0.40:boxborderw=20:"
            "x=(w-text_w)/2:y=h-430"
        )
    if sub:
        chain += (
            f",drawtext=fontfile='{FONT_REG}':text='{esc(sub)}':fontsize=44:"
            "fontcolor=white:borderw=3:bordercolor=black@0.85:"
            "box=1:boxcolor=black@0.40:boxborderw=16:"
            "x=(w-text_w)/2:y=h-310"
        )
    chain += ",format=yuv420p[v]"
    run(["ffmpeg", "-y", "-loop", "1", "-t", f"{dur}", "-i", str(png),
         "-filter_complex", chain, "-map", "[v]", "-frames:v", str(frames),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", str(out)])


def main(slug):
    toon = ROOT / "assets" / slug / "toon"
    scenes = sorted(p for p in toon.glob("[0-9][0-9].png"))
    texts = json.loads((toon / "texts.json").read_text(encoding="utf-8"))
    if len(scenes) != len(texts):
        raise SystemExit(f"scenes {len(scenes)} != texts {len(texts)}")

    bgm = ROOT / "assets" / "bgm" / ("lab.m4a" if slug.startswith("lab") else "judge.m4a")
    tmp = ROOT / "build" / f"reeltoon-{slug}"
    tmp.mkdir(parents=True, exist_ok=True)

    durs = [DUR_FIRST] + [DUR_MID] * (len(scenes) - 2) + [DUR_LAST]
    segs = []
    for i, (png, dur, txt) in enumerate(zip(scenes, durs, texts)):
        seg = tmp / f"seg{i:02d}.mp4"
        build_segment(png, dur, seg, txt, first=(i == 0))
        segs.append(seg)
        print(f"segment {i + 1}/{len(scenes)} done")

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
    afade = max(total - 1.2, 0)
    filt = ";".join(chain) + f";[{len(segs)}:a]volume=0.85,afade=t=out:st={afade:.2f}:d=1.2[a]"

    out_dir = ROOT / "output" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    final = out_dir / "reel-toon.mp4"
    run(["ffmpeg", "-y", *inputs, "-i", str(bgm), "-filter_complex", filt,
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
         "-pix_fmt", "yuv420p", str(final)])
    for s in segs:
        s.unlink()
    print(f"reel-toon done -> {final} ({total:.1f}s, {final.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "case-012")
