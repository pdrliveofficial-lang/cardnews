# -*- coding: utf-8 -*-
"""카드뉴스 -> 릴스 mp4 조립 (ffmpeg 필요, GitHub Actions ubuntu에 기본 탑재).

output/<slug>/NN.png (1080x1350) 카드들을 9:16(1080x1920) 슬라이드 영상으로 조립:
- 배경: 카드 자체를 확대·블러·어둡게 (세로 여백 채움)
- 전경: 카드 원본을 중앙 배치, 표지(첫 카드)는 천천히 줌인
- 카드 간 0.4초 페이드 전환, BGM 자동 선택(판사/연구소) + 끝 페이드아웃
- 결과: output/<slug>/reel.mp4 (h264/aac, 인스타 REELS 규격)

Usage: python make_reel.py case-011
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).parent
FPS = 30
XFADE = 0.4          # 카드 간 전환 시간
DUR_COVER = 3.2      # 표지 노출
DUR_MID = 2.6        # 중간 카드
DUR_LAST = 3.2       # 마지막 카드 (투표 유도)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-2000:])
        raise SystemExit(f"ffmpeg failed: {' '.join(map(str, cmd[:6]))}...")


def build_segment(png, dur, out, zoom=False):
    """카드 1장 -> 블러 배경 + 중앙 카드 합성 세그먼트."""
    fg = "[0:v]scale=1000:-2[fg]"
    if zoom:
        # 표지: 프레임 번호(on)에 비례해 1.00 -> ~1.06 줌인
        fg = ("[0:v]scale=2000:-2,zoompan=z='1+0.0007*on':d=1"
              ":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
              f":s=1000x1250:fps={FPS}[fg]")
    filt = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,gblur=sigma=28,eq=brightness=-0.12[bg];"
        f"{fg};"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2,fps={FPS},format=yuv420p[v]"
    )
    run(["ffmpeg", "-y", "-loop", "1", "-t", f"{dur}", "-i", str(png),
         "-filter_complex", filt, "-map", "[v]",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", str(out)])


def main(slug):
    out_dir = ROOT / "output" / slug
    cards = sorted(out_dir.glob("[0-9][0-9].png"))
    if len(cards) < 2:
        raise SystemExit(f"{slug}: 카드가 부족합니다 ({len(cards)}장)")

    bgm = ROOT / "assets" / "bgm" / ("lab.m4a" if slug.startswith("lab") else "judge.m4a")
    tmp = ROOT / "build" / f"reel-{slug}"
    tmp.mkdir(parents=True, exist_ok=True)

    durs = [DUR_COVER] + [DUR_MID] * (len(cards) - 2) + [DUR_LAST]
    segs = []
    for i, (png, dur) in enumerate(zip(cards, durs)):
        seg = tmp / f"seg{i:02d}.mp4"
        build_segment(png, dur, seg, zoom=(i == 0))
        segs.append(seg)
        print(f"segment {i + 1}/{len(cards)} done")

    # xfade 체인: offset은 직전 오프셋 + 직전 길이 - 전환시간 (누적)
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
    afade_start = max(total - 1.2, 0)
    filt = ";".join(chain) + (
        f";[{len(segs)}:a]volume=0.85,afade=t=out:st={afade_start:.2f}:d=1.2[a]")

    final = out_dir / "reel.mp4"
    run(["ffmpeg", "-y", *inputs, "-i", str(bgm), "-filter_complex", filt,
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
         "-pix_fmt", "yuv420p", str(final)])
    for s in segs:
        s.unlink()
    print(f"reel done -> {final} ({total:.1f}s, {final.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "case-001")
