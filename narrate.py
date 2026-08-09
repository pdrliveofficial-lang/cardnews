# -*- coding: utf-8 -*-
"""Gemini TTS 나레이션 생성 — 무료 티어는 분당 10회 제한이라 7초 간격으로 페이스 조절."""
import base64, os, pathlib, re, struct, subprocess, sys, time
import requests
from reel_specs import SPECS

KEY = os.environ.get("GEMINI_API_KEY", "").strip()   # 공개 저장소이므로 키를 코드에 두지 않는다
URL = ("https://generativelanguage.googleapis.com/v1beta/models/"
       "gemini-2.5-flash-preview-tts:generateContent")
GAP = 13.0           # 분당 10회 한도 — 재시도도 호출로 카운트되므로 여유있게 5회/분
NARRATOR = "차분하고 담담하게, 자기 이야기를 털어놓듯 사연을 읽어주는 톤으로"
OTHER = "미안한 기색 없이 해맑고 뻔뻔한 말투로, 조금 빠르게"
OTHER_IDX = {"case-017": [3], "case-018": [3], "case-019": [3],
             "lab-011": [2, 4], "lab-012": [2, 4], "lab-013": [4]}


def require_key():
    if not KEY:
        sys.exit("GEMINI_API_KEY 환경변수가 필요합니다. 예: set GEMINI_API_KEY=...")


def tts(text, style, voice, out):
    for attempt in range(4):
        r = requests.post(URL, params={"key": KEY}, timeout=180, json={
            "contents": [{"parts": [{"text": f"{style}: {text}"}]}],
            "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {
                "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}})
        if r.ok:
            pcm = base64.b64decode(
                r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
            wav = str(out).replace(".mp3", ".wav")
            with open(wav, "wb") as f:  # 24kHz 16bit mono PCM -> WAV
                f.write(b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVEfmt "
                        + struct.pack("<IHHIIHH", 16, 1, 1, 24000, 48000, 2, 16)
                        + b"data" + struct.pack("<I", len(pcm)) + pcm)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav,
                            "-b:a", "128k", str(out)], check=True)
            pathlib.Path(wav).unlink()
            return True
        if r.status_code == 429:
            m = re.search(r"retry in ([\d.]+)s", r.text)
            wait = float(m.group(1)) + 8 if m else 30
            print(f"    429 → {wait:.0f}s 대기", flush=True)
            time.sleep(wait)
            continue
        print(f"    FAIL {r.status_code} {r.text[:120]}", flush=True)
        return False
    return False


def main():
    require_key()
    todo = []
    for slug, sp in SPECS.items():
        d = pathlib.Path("assets") / slug / "narr"
        d.mkdir(parents=True, exist_ok=True)
        lines = [(f"narr{i + 1}", s["narr"], i in OTHER_IDX.get(slug, []))
                 for i, s in enumerate(sp["scenes"])]
        lines.append(("narr6", sp["verdict_narr"], False))
        for name, text, other in lines:
            out = d / f"{name}.mp3"
            if not out.exists():
                todo.append((slug, out, text, other))
    print(f"생성 대상 {len(todo)}건 (예상 {len(todo) * GAP / 60:.0f}분)", flush=True)
    ok = 0
    for i, (slug, out, text, other) in enumerate(todo):
        good = tts(text, OTHER if other else NARRATOR,
                   "Leda" if other else "Kore", out)
        ok += good
        print(f"[{i + 1}/{len(todo)}] {slug} {out.stem} {'ok' if good else 'FAIL'}", flush=True)
        if i < len(todo) - 1:
            time.sleep(GAP)
    print(f"ALL DONE ok={ok} fail={len(todo) - ok}", flush=True)


main()
