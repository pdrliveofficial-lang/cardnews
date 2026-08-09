# -*- coding: utf-8 -*-
"""클링 영상 클립 -> 릴스 조립 v2 (자막 2줄 랩핑 + TTS 나레이션, 2026-08-09).

v1 문제: ①한 줄 자막이 720px 프레임을 벗어남 → 수동 2줄 랩핑 + 폰트 축소
        ②나레이션 없음 → edge-tts(ko-KR-SunHiNeural, 무료)로 장면별 낭독을 깔았다.
입력: assets/<slug>/clips/scene1..5.mp4, assets/<slug>/narr/narr1..6.mp3
Usage: python make_reel_kling.py lab-024
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).parent
FPS = 30
XFADE = 0.4
CLIP_T = 4.9          # 클립 5초 중 4.9초 사용 (총 길이 30초 이내로)
VERDICT_T = 6.8       # 판정컷 — 나레이션(6.4s)이 다 들어가는 길이
FONT_B = "C\\:/Windows/Fonts/malgunbd.ttf"
FONT_R = "C\\:/Windows/Fonts/malgun.ttf"

# 자막: 수동 2줄 랩핑 (drawtext는 자동 줄바꿈이 없다 — 13자 안팎에서 끊을 것)
CAPTIONS = [
    ("결혼식 끝나고", "축의금 정리를 하는데"),
    ("친구 이름이 적힌 봉투가", "비어 있었습니다"),
    ("며칠 고민하다", "조심스럽게 물었어요"),
    ("\"아 깜빡했나봐ㅋㅋ", "나중에 줄게~\""),
    ("그 나중이...", "6개월째입니다"),
]
VERDICT_TOP = ("빈 봉투,", "실수라기엔 좀 길죠?")
VERDICT_SUB = "판정은 댓글로 · 스하리 남겨주면 다 갈게요"
NARR_OFFSET = 0.25    # 장면 시작 후 나레이션 지연


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-1500:])
        raise SystemExit("ffmpeg failed")


def esc(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\\\\\'").replace("%", "\\%").replace('"', '\\"')


def two_lines(l1, l2, size=36, y1=-320, y2=-262, font=FONT_B):
    parts = []
    for txt, y in ((l1, y1), (l2, y2)):
        if not txt:
            continue
        parts.append(
            f"drawtext=fontfile='{font}':text='{esc(txt)}':fontsize={size}:"
            "fontcolor=white:borderw=3:bordercolor=black@0.85:"
            "box=1:boxcolor=black@0.42:boxborderw=14:"
            f"x=(w-text_w)/2:y=h{y}"
        )
    return ",".join(parts)


def main(slug):
    base = ROOT / "assets" / slug
    clips = [base / "clips" / f"scene{i}.mp4" for i in range(1, 6)]
    narrs = [base / "narr" / f"narr{i}.mp3" for i in range(1, 7)]
    for f in clips + narrs:
        if not f.exists():
            raise SystemExit(f"missing {f}")
    verdict_img = ROOT / "assets" / "lab-008" / "toon" / "99.png"

    tmp = ROOT / "build" / f"kling-{slug}"
    tmp.mkdir(parents=True, exist_ok=True)
    segs, durs = [], []

    for i, (clip, (l1, l2)) in enumerate(zip(clips, CAPTIONS)):
        seg = tmp / f"seg{i}.mp4"
        filt = (
            f"scale=720:1280:force_original_aspect_ratio=increase,"
            f"crop=720:1280,fps={FPS},{two_lines(l1, l2)},format=yuv420p"
        )
        run(["ffmpeg", "-y", "-t", str(CLIP_T), "-i", str(clip), "-vf", filt,
             "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", str(seg)])
        segs.append(seg)
        durs.append(CLIP_T)
        print(f"seg{i + 1} ok")

    vseg = tmp / "seg_v.mp4"
    vfilt = (
        f"crop=iw:ih*0.86:0:0,scale=720:1280:force_original_aspect_ratio=increase,"
        f"crop=720:1280,fps={FPS},"
        + two_lines(VERDICT_TOP[0], VERDICT_TOP[1], size=42, y1=-340, y2=-276)
        + ","
        + two_lines(VERDICT_SUB, "", size=28, y1=-205, font=FONT_R)
        + ",format=yuv420p"
    )
    run(["ffmpeg", "-y", "-framerate", str(FPS), "-loop", "1", "-t", str(VERDICT_T),
         "-i", str(verdict_img), "-vf", vfilt, "-an",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", str(vseg)])
    segs.append(vseg)
    durs.append(VERDICT_T)

    # ---- 합성: 영상 xfade 체인 + (BGM + 나레이션 adelay) 믹스 ----
    inputs = []
    for s in segs:
        inputs += ["-i", str(s)]
    n_video = len(segs)
    bgm = ROOT / "assets" / "bgm" / "lab.m4a"
    inputs += ["-i", str(bgm)]
    for nr in narrs:
        inputs += ["-i", str(nr)]

    total = sum(durs) - XFADE * (n_video - 1)
    chain, prev, offset = [], "[0:v]", 0.0
    starts = [0.0]
    for i in range(1, n_video):
        offset += durs[i - 1] - XFADE
        starts.append(offset)
        label = "[v]" if i == n_video - 1 else f"[x{i}]"
        chain.append(f"{prev}[{i}:v]xfade=transition=fade:duration={XFADE}:offset={offset:.2f}{label}")
        prev = f"[x{i}]"

    afade = max(total - 1.2, 0)
    aparts = [f"[{n_video}:a]volume=0.18,afade=t=out:st={afade:.2f}:d=1.2[bg]"]
    mix_ins = "[bg]"
    for k in range(6):
        delay_ms = int((starts[k] + NARR_OFFSET) * 1000)
        aparts.append(f"[{n_video + 1 + k}:a]adelay={delay_ms}|{delay_ms},volume=1.0[n{k}]")
        mix_ins += f"[n{k}]"
    aparts.append(f"{mix_ins}amix=inputs=7:duration=first:normalize=0[a]")
    filt = ";".join(chain) + ";" + ";".join(aparts)

    out = ROOT / "output" / slug
    out.mkdir(parents=True, exist_ok=True)
    final = out / "reel-kling.mp4"
    run(["ffmpeg", "-y", *inputs, "-filter_complex", filt,
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
         "-pix_fmt", "yuv420p", str(final)])
    print(f"done -> {final} ({total:.1f}s, {final.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "lab-024")
