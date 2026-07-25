# cardnews — 사연 판결형 카드뉴스 파이프라인 (댓글판사 + 잘잘못연구소)

> 인스타그램 카드뉴스 계정용 콘텐츠 제작 파이프라인. 세렌디피티(threads-bot)와 별개 프로젝트지만 같은 사용자.
> 작업 방식이 바뀌면 이 문서도 업데이트할 것.

## 개요

- **콘셉트**: "댓글로 판결하는 재판" — 사연(AITA 스타일)을 사건번호 붙여 카드 7장으로 풀고, 마지막 장에서 A/B 판결 투표로 댓글 유도.
- **투 트랙 운영** (2026-07-25부터):
  - **댓글판사** @comment.judgee — 재판 콘셉트(레드), 돈·경조사 갈등 사연. stories/case-*.json, state.json, 매일 12:00 KST 발행.
  - **잘잘못연구소** — 보라(#5C4BC4) 스토리형 디자인 **(최종 확정 2026-07-25, 사용자가 claude.ai 디자인 핸드오프로 전달)**. 전용 템플릿 `template-lab.html` (render.py가 lab-* slug면 자동 선택). 인스타 스토리 문법: 진행바 7세그 + 프로필 행(jaljalmot_lab) + 흰 카드 회전 + VS 배지 + A/B 투표카드 + 답장바. 100% CSS(사진 불필요 → 힉스필드 크레딧 0), Pretendard CDN 웹폰트(virtual-time-budget 8000). 디자인 스펙 원본: 사용자 바탕화면 design_handoff_jaljalmot_cardnews/README.md. 일상·관계 논쟁 사연, stories/lab-*.json (cover에 `emoji` 필드), state-lab.json, 매일 19:00 KST 발행(publish-lab.yml). **계정 미개설 — 개설 후 IG_TOKEN_LAB/IG_USER_ID_LAB secrets 등록 필요. secrets 없으면 워크플로는 조용히 스킵.**
- **콘텐츠 재고**: case-001~010 (댓글판사 10회분) + lab-001~010 (연구소 10회분).
- **이미지 생성**: 표지는 nano_banana_pro. ⚠️ **CLI 생성은 무료가 아님** — 거래내역 확인 결과 건당 2크레딧 차감 (2026-07-25 확인). 웹 UI의 Unlimited 모드와 달리 CLI/API 생성은 크레딧을 소모함. 장당 2크레딧이라 부담은 작지만 사용자에게 소모량 보고할 것.
- **전략**: 결혼/축의금 사연 30% 믹스 → 장기적으로 세렌디피티 DVD 사업과 연결.
- **사연 원칙**: 정치·젠더갈등·특정인 저격 금지. 의견이 갈리는 사연만. 창작/각색 사연 사용(실존 인물 특정 불가하게).

## 파이프라인

```
stories/case-NNN.json  →  python render.py stories/case-NNN.json  →  output/case-NNN/01~07.png + caption.txt
```

- `template.html`: 1080×1350 카드 렌더러. `?card=N` 쿼리로 N번째 카드 표시. 데이터는 `/*__DATA__*/null` 자리에 JSON 주입.
- `render.py`: 템플릿에 JSON 주입 → `build/` 에 HTML 생성 → Chrome headless로 장당 스크린샷.
- 카드 타입: `cover`(표지) / `story`(본문, paras[]) / `quote`(인용, quotes[]) / `vs`(양측 주장 a/b) / `verdict`(A/B 투표). 텍스트에 `<b>`(강조 흰색), `<em>`(강조 빨강), `<br>` 사용 가능.
- 브랜딩 옵션(JSON 최상위): `brand`(로고), `no_label`(기본 "사건" — 잘잘못연구소 버전은 "연구"), `swipe_text`(표지 하단 문구). case-001=댓글판사 시안, case-002=잘잘못연구소 시안. 계정명 확정 시 통일할 것.
- 본문이 길면 자동으로 글자 크기를 줄여 카드 안에 맞춤(템플릿 내 auto-shrink). 본문 카드는 세로 중앙배치.
- 폰트: Malgun Gothic(본문) + Batang(명조 포인트) — 시스템 폰트라 별도 설치 불요.

### 표지 썸네일 사진 (cover.image)

- cover 카드에 `"image": "../assets/case-NNN/cover.png"` 넣으면 사진 배경 + 어두운 스크림 + "AI 연출 이미지" 고지가 자동 적용됨. 경로는 build/ 기준 상대경로.
- 사진 생성: Higgsfield CLI 직접 호출 (계정 로그인돼 있음). 사연의 핵심 소품/장면을 무드샷으로:
  ```
  higgsfield generate create nano_banana_pro --prompt "<영문 프롬프트>" --aspect_ratio "4:5" --resolution 2k --json   # → job_id
  higgsfield generate wait <job_id> --json   # → result_url 다운로드 → assets/case-NNN/cover.png
  ```
- 프롬프트 팁: "moody cinematic low-key lighting, dark navy background tones, photorealistic editorial photography" 톤이 카드 잉크색과 어울림. **봉투·간판 등에 글자가 생기면 어색한 한자가 나오므로 "plain/blank, no text or writing" 명시할 것** (case-001에서 배운 것).
- **⚠️ 필수: 힉스필드 생성 사용 시 다운로드 → 사용 → 계정 이력 삭제까지가 한 세트.** 요청 없어도 같은 턴에 반드시 삭제 (회사 공용 계정, Today 통삭제 금지 — 우리 job만 골라 삭제. 절차는 메모리 higgsfield-cleanup-routine 참조).

## 컨펌 규칙 (중요)

**업로드 전 반드시 사용자 컨펌.** 흐름: 사연 작성 → PNG 생성 → 사용자에게 보여주기 → OK 받으면 업로드. 컨펌 없이 게시 금지.

## 🤖 자동 발행 (가동 중, 2026-07-25 시작)

- **계정**: @comment.judgee ("댓글판사", 프로페셔널/크리에이터, 팔로워 ~667)
- **구조**: GitHub 저장소 `pdrliveofficial-lang/cardnews` (공개 — raw URL이 이미지 호스팅) + GitHub Actions `publish.yml`이 **매일 12:00 KST** `upload_instagram.py` 실행 → state.json의 next_case를 캐러셀 발행 후 +1 커밋.
- **API**: Instagram API with Instagram Login (페이스북 페이지 불필요). Meta 앱 **cardnews-bot** (앱 ID 1013526951312622), Instagram 앱 ID 2450710675398072. comment.judgee는 앱의 Instagram 테스터로 등록·수락됨.
- **Secrets** (repo secrets): `IG_TOKEN` (장기 토큰, **2026-07-25 발급 → 60일 후 2026-09-22경 만료**), `IG_USER_ID` (17841455934440668).
- **토큰 갱신**: 만료 전 `GET graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=<현재토큰>` 호출 후 `gh secret set IG_TOKEN --body "<새토큰>"`. (재발급이 필요하면 인증 링크 방식: 리디렉션 URI는 https://github.com/pdrliveofficial-lang/cardnews, 스코프에 instagram_business_content_publish 필수. 시크릿은 Meta 콘솔 > cardnews-bot > Instagram > API 설정에서 표시.)
- **수동 발행**: `python upload_instagram.py` (env IG_TOKEN/IG_USER_ID 필요) 또는 GitHub Actions workflow_dispatch.
- 발행 이력: case-001 (2026-07-25 수동 테스트, media 17971311825093729). state.json next_case=2.

## 대기/진행 중

1. **사연 소재 뱅크**: case-002~010 재고 있음 (~8/3까지). 소진 전 신규 사연 제작 필요.
2. **프로필 세팅**: 프로필 사진(로고)·소개문구 미완 — 다음 세션에서 시안 제작 추천.
3. **댓글 고정 운영**: "가장 공감받은 판결 고정"은 수동 운영 필요 — 추후 반자동화 검토.

## 작업 규칙

- 한글 인코딩: PowerShell 인라인 한글 금지, 파일은 UTF-8. (threads-bot과 동일)
- 사건번호는 이어서 증가 (case-001 다음 case-002...).
- caption.txt 는 게시 캡션 원본 — 해시태그 10개 내외 유지.
