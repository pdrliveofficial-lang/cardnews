# -*- coding: utf-8 -*-
"""Edge TTS 나레이션 (무료·무제한) — Gemini TTS 일일 쿼터 소진 시 대체용.

계정은 '제보 전달자'이므로 나레이터 목소리는 사연 주인공 성별과 무관하게 하나로 통일한다.
인용 대사(상대방 말)만 다른 목소리로 대비를 준다.
Gemini 쿼터가 회복되면 narrate.py로 같은 파일명을 덮어쓰고 조립만 다시 하면 된다.
Usage: python narrate_edge.py [--force]
"""
import asyncio
import io
import pathlib
import sys

import edge_tts

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT))
from reel_specs import SPECS  # noqa: E402

NARRATOR = ("ko-KR-SunHiNeural", "-6%", "-15Hz")          # 차분한 전달자 톤
QUOTED = ("ko-KR-HyunsuMultilingualNeural", "+10%", "+15Hz")  # 인용 대사 — 가볍고 뻔뻔하게
OTHER_IDX = {"case-017": [3], "case-018": [3], "case-019": [3],
             "lab-011": [2, 4], "lab-012": [2, 4], "lab-013": [4]}


async def main():
    force = "--force" in sys.argv
    made = 0
    for slug, sp in SPECS.items():
        d = ROOT / "assets" / slug / "narr"
        d.mkdir(parents=True, exist_ok=True)
        lines = [(f"narr{i + 1}", s["narr"], i in OTHER_IDX.get(slug, []))
                 for i, s in enumerate(sp["scenes"])]
        lines.append(("narr6", sp["verdict_narr"], False))
        for name, text, quoted in lines:
            out = d / f"{name}.mp3"
            if out.exists() and not force:
                continue
            voice, rate, pitch = QUOTED if quoted else NARRATOR
            # Edge TTS는 간헐적으로 빈 응답을 준다(파라미터 문제가 아니라 일시 오류) → 재시도
            for attempt in range(4):
                try:
                    await edge_tts.Communicate(text, voice, rate=rate,
                                               pitch=pitch).save(str(out))
                    break
                except Exception as e:
                    if attempt == 3:
                        print(f"{slug} {name} FAIL {type(e).__name__}")
                        break
                    await asyncio.sleep(2 + attempt * 2)
            else:
                continue
            if out.exists():
                made += 1
                print(f"{slug} {name} ok")
    print(f"생성 {made}건 완료")


asyncio.run(main())
