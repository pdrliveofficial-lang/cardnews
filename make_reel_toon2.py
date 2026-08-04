# -*- coding: utf-8 -*-
"""웹툰 티키타카 릴스 v2 — 말풍선 대사를 PIL로 직접 합성 (AI 이미지 속 글자 깨짐 회피).

assets/<slug>/toon/NN.png + dialogue.json -> output/<slug>/reel-toon.mp4

dialogue.json 컷 형식:
  {"img": "07", "dur": 2.8, "crop_bottom": 0.2,
   "caption": ["윗줄", "아랫줄"],                       # 하단 자막형
   "bubbles": [{"who": "사연자", "text": "대사", "xy": [0.5, 0.13],
                "tail": [0.52, 0.30], "accent": "#C8372D"}]}  # 말풍선형
xy/tail은 0~1 비율 좌표 (1080x1920 기준), who 배지는 말풍선 위에 붙음.
Usage: python make_reel_toon2.py case-012
"""
import json
import pathlib
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).parent
W, H = 1080, 1920
FPS = 30
XFADE = 0.4
FONT_B = "C:/Windows/Fonts/malgunbd.ttf"
FONT_R = "C:/Windows/Fonts/malgun.ttf"


def wrap(text, font, max_w, draw):
    """공백 기준 단어 줄바꿈."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_cover(im):
    """1080x1920 꽉 채우기 (중앙 크롭)."""
    r = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


def draw_bubble(im, b):
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT_B, 46)
    badge_f = ImageFont.truetype(FONT_B, 34)
    max_w = int(W * 0.72)
    lines = wrap(b["text"], font, max_w, d)
    line_h = 62
    tw = max(d.textlength(ln, font=font) for ln in lines)
    bw, bh = tw + 90, len(lines) * line_h + 70
    cx, cy = b["xy"][0] * W, b["xy"][1] * H
    x0, y0 = cx - bw / 2, cy - bh / 2
    x0 = min(max(x0, 30), W - bw - 30)  # 화면 밖 방지
    x1, y1 = x0 + bw, y0 + bh
    # 꼬리 (말풍선 -> 화자 머리)
    tx, ty = b["tail"][0] * W, b["tail"][1] * H
    base_x = min(max(tx, x0 + 70), x1 - 70)
    d.polygon([(base_x - 34, y1 - 6), (base_x + 34, y1 - 6), (tx, ty)],
              fill="white", outline="black")
    # 본체
    d.rounded_rectangle([x0, y0, x1, y1], radius=44, fill="white",
                        outline="black", width=6)
    d.polygon([(base_x - 30, y1 - 7), (base_x + 30, y1 - 7), (tx, ty)], fill="white")
    ty_text = y0 + 34
    for ln in lines:
        d.text(((x0 + x1) / 2, ty_text), ln, font=font, fill="#111111", anchor="ma")
        ty_text += line_h
    # 화자 배지
    who = b.get("who")
    if who:
        bx = x0 + 20
        wl = d.textlength(who, font=badge_f)
        d.rounded_rectangle([bx, y0 - 46, bx + wl + 44, y0 + 6], radius=22,
                            fill=b.get("accent", "#C8372D"), outline="black", width=4)
        d.text((bx + 22 + wl / 2, y0 - 40), who, font=badge_f, fill="white", anchor="ma")


def draw_caption(im, lines_txt):
    d = ImageDraw.Draw(im)
    fonts = [ImageFont.truetype(FONT_B, 58), ImageFont.truetype(FONT_R, 44)]
    y = H - 430
    for i, ln in enumerate(lines_txt):
        f = fonts[min(i, 1)]
        tw = d.textlength(ln, font=f)
        pad = 20 if i == 0 else 16
        x0 = (W - tw) / 2 - pad
        box_h = (f.size + 2 * pad * 0.8)
        overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rectangle([x0, y, x0 + tw + 2 * pad, y + box_h], fill=(0, 0, 0, 105))
        im.alpha_composite(overlay)
        d.text((W / 2, y + pad * 0.8), ln, font=f, fill="white", anchor="ma",
               stroke_width=3, stroke_fill="black")
        y += box_h + 18
    return im


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-1500:])
        raise SystemExit("ffmpeg failed")


def main(slug):
    toon = ROOT / "assets" / slug / "toon"
    cuts = json.loads((toon / "dialogue.json").read_text(encoding="utf-8"))
    comp = toon / "composed"
    comp.mkdir(exist_ok=True)
    tmp = ROOT / "build" / f"reeltoon2-{slug}"
    tmp.mkdir(parents=True, exist_ok=True)

    frames = []
    for i, c in enumerate(cuts):
        im = Image.open(toon / f"{c['img']}.png").convert("RGBA")
        if c.get("crop_bottom"):
            im = im.crop((0, 0, im.width, round(im.height * (1 - c["crop_bottom"]))))
        im = fit_cover(im)
        for b in c.get("bubbles", []):
            draw_bubble(im, b)
        if c.get("caption"):
            im = draw_caption(im, c["caption"])
        f = comp / f"{i:02d}.png"
        im.convert("RGB").save(f, quality=95)
        frames.append(f)
        print(f"composed {i + 1}/{len(cuts)}")

    segs = []
    for i, (f, c) in enumerate(zip(frames, cuts)):
        dur = c.get("dur", 2.8)
        z = "1.08-0.0005*on" if i == 0 else "1+0.0004*on"
        filt = (f"[0:v]scale=2160:3840,zoompan=z='{z}':d=1:"
                "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"s=1080x1920:fps={FPS},format=yuv420p[v]")
        seg = tmp / f"seg{i:02d}.mp4"
        # -framerate 명시 필수: 기본 25fps 입력이 zoompan(fps=30)을 통과하면
        # 프레임 수가 모자라 세그먼트가 짧아지고 xfade 체인 전체가 무너진다.
        run(["ffmpeg", "-y", "-framerate", str(FPS), "-loop", "1",
             "-t", str(dur), "-i", str(f),
             "-filter_complex", filt, "-map", "[v]",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", str(seg)])
        segs.append((seg, dur))
        print(f"segment {i + 1}/{len(frames)}")

    inputs = []
    for s, _ in segs:
        inputs += ["-i", str(s)]
    durs = [d for _, d in segs]
    total = sum(durs) - XFADE * (len(segs) - 1)
    chain, prev, offset = [], "[0:v]", 0.0
    for i in range(1, len(segs)):
        offset += durs[i - 1] - XFADE
        label = "[v]" if i == len(segs) - 1 else f"[x{i}]"
        chain.append(f"{prev}[{i}:v]xfade=transition=fade:duration={XFADE}:offset={offset:.2f}{label}")
        prev = f"[x{i}]"
    bgm = ROOT / "assets" / "bgm" / ("lab.m4a" if slug.startswith("lab") else "judge.m4a")
    afade = max(total - 1.2, 0)
    filt = ";".join(chain) + f";[{len(segs)}:a]volume=0.85,afade=t=out:st={afade:.2f}:d=1.2[a]"

    final = ROOT / "output" / slug / "reel-toon.mp4"
    final.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", *inputs, "-i", str(bgm), "-filter_complex", filt,
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
         "-pix_fmt", "yuv420p", str(final)])
    for s, _ in segs:
        s.unlink()
    print(f"done -> {final} ({total:.1f}s, {final.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "case-012")
