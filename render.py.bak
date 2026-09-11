# -*- coding: utf-8 -*-
"""cardnews render: stories/<slug>.json -> output/<slug>/NN.png (1080x1350)

Usage: python render.py stories/case-001.json
"""
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).parent

# 크롬 실행 파일 — 맥/윈도우 겸용 (환경변수 CHROME_BIN으로 강제 지정 가능)
_CANDIDATES = [
    os.environ.get("CHROME_BIN", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/usr/bin/google-chrome",
]
CHROME = next((c for c in _CANDIDATES if c and pathlib.Path(c).exists()), _CANDIDATES[2])


def main(story_path):
    story_file = pathlib.Path(story_path)
    story = json.loads(story_file.read_text(encoding="utf-8"))
    slug = story.get("slug", story_file.stem)

    tpl_name = "template-lab.html" if slug.startswith("lab") else "template.html"
    template = (ROOT / tpl_name).read_text(encoding="utf-8")
    built = template.replace(
        "/*__DATA__*/null", json.dumps(story, ensure_ascii=False)
    )
    build_path = ROOT / "build" / f"{slug}.html"
    build_path.write_text(built, encoding="utf-8")

    out_dir = ROOT / "output" / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    n = len(story["cards"])
    for i in range(n):
        png = out_dir / f"{i + 1:02d}.png"
        url = build_path.as_uri() + f"?card={i}"
        cmd = [
            CHROME, "--headless=new", "--disable-gpu",
            "--force-device-scale-factor=1", "--hide-scrollbars",
            "--window-size=1080,1350", "--virtual-time-budget=8000",
            f"--screenshot={png}", url,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"[{i + 1}/{n}] {png.name} done")

    caption_path = out_dir / "caption.txt"
    caption_path.write_text(story.get("caption", ""), encoding="utf-8")
    print(f"caption.txt done -> {out_dir}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "stories/case-001.json")
