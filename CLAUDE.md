# cardnews — 사연 판결형 카드뉴스 파이프라인 (댓글판사 + 잘잘못연구소)

> 인스타그램 카드뉴스 계정용 콘텐츠 제작 파이프라인. 세렌디피티(threads-bot)와 별개 프로젝트지만 같은 사용자.
> 작업 방식이 바뀌면 이 문서도 업데이트할 것.

## 🚀 새 컴퓨터에서 시작하는 법

Claude Code에 아래 한 문장만 입력하면 됩니다:

```
깃허브 pdrliveofficial-lang/cardnews 클론해서 CLAUDE.md 읽고 이어서 작업해줘
```

- 필요한 것: `gh` CLI 로그인(`gh auth login`), Python 3.12 + `pip install requests`, 카드 렌더 시 Google Chrome(경로 자동 감지, 필요하면 `CHROME_BIN` 환경변수로 지정), 릴스 제작 시 ffmpeg.
- **토큰·시크릿은 저장소에 없다** — 전부 GitHub repo secrets에 있고 발행은 GitHub Actions에서 실행되므로, 새 컴퓨터에 토큰을 세팅할 필요가 없다. 로컬은 콘텐츠 작성·렌더 전용.
- **발행 트리거도 외부(cron-job.org)에 있다** — 로컬 컴퓨터를 꺼도 발행은 계속된다. 즉석 발행이 필요하면 `gh workflow run <워크플로>.yml`.
- 작업 후에는 반드시 커밋·푸시 (GitHub 저장소가 운영 원본이자 이미지 호스팅이다).

## 개요

- **콘셉트**: "댓글로 판결하는 재판" — 사연(AITA 스타일)을 사건번호 붙여 카드 7장으로 풀고, 마지막 장에서 A/B 판결 투표로 댓글 유도.
- **투 트랙 운영** (2026-07-25부터):
  - **댓글판사** @comment.judgee — 재판 콘셉트(레드), 돈·경조사 갈등 사연. stories/case-*.json, state.json, 매일 12:00 KST 발행.
  - **잘잘못연구소** — 보라(#5C4BC4) 스토리형 디자인 **(최종 확정 2026-07-25, 사용자가 claude.ai 디자인 핸드오프로 전달)**. 전용 템플릿 `template-lab.html` (render.py가 lab-* slug면 자동 선택). 인스타 스토리 문법: 진행바 7세그 + 프로필 행(jaljalmot_lab) + 흰 카드 회전 + VS 배지 + A/B 투표카드 + 답장바. 100% CSS(사진 불필요 → 힉스필드 크레딧 0), Pretendard CDN 웹폰트(virtual-time-budget 8000). 디자인 스펙 원본: 사용자 바탕화면 design_handoff_jaljalmot_cardnews/README.md. 일상·관계 논쟁 사연, stories/lab-*.json (cover에 `emoji` 필드), state-lab.json, 매일 19:00 KST 발행(publish-lab.yml). **계정: @jaljalmot.lap (연결 완료 2026-07-27)** — IG_USER_ID_LAB=17841445123080452, IG_TOKEN_LAB은 2026-07-27 발급(60일, ~9/24 만료). lab-001은 7/27 수동 테스트 발행 완료, lab-002부터 자동.
- **콘텐츠 재고 (2026-08-07 충전)**: 카드뉴스 case-001~028 · lab-001~023 (양쪽 **~8/21** 소진 예정), 스레드풀 judge 40편 · lab 38편 (**~8/21**). 재고는 `state.json`/`state-lab.json`의 `next_case`와 `threads_pool_*.json`의 `next`로 확인.
- **웹툰 릴스 (2026-08-04 구축, 카드 릴스 대체 실험)**: 사연을 웹툰 상황컷 8~10컷 + 말풍선 티키타카로 재구성한 릴스. 사용자 지시: "상황을 보여주고 티키타카 형식, 대사도, 웹툰처럼".
  - 파이프라인: ①nano_banana_pro로 컷 생성(등장인물 묘사 고정으로 일관성 유지, 이미지 속 글자 금지) ②`assets/<slug>/toon/dialogue.json`에 컷 순서·자막·말풍선 대사 정의 ③`make_reel_toon2.py <slug>`가 PIL로 말풍선(흰 박스+꼬리+화자 배지) 직접 합성 → ffmpeg 줌인+크로스페이드+BGM → `output/<slug>/reel-toon.mp4`.
  - 컷 공식: 상황 2~3(자막) → 대화 4(말풍선 A↔B) → 반전/증거 1 → 판결컷(공유: 판사=법봉 `assets/case-012/toon/06.png`, 연구소=돋보기, 각 toon 폴더에 99.png로 복사).
  - **publish-reel.yml이 `reel-toon.mp4` 우선 사용** (reel.mp4 없을 때 복사 후 발행) — 재고: case-012~016, lab-008~012 커밋됨(~8/8까지 웹툰판으로 나감). 소스 PNG는 용량 문제로 .gitignore (로컬 D:에만 보관).
  - ⚠️ ffmpeg 함정: PNG 입력에 `-framerate 30` 명시 필수 — 기본 25fps가 zoompan(fps=30)과 어긋나면 세그먼트가 짧아져 xfade 체인이 무너지고 영상이 3초에서 얼어붙음(2026-08-04 실사고).
  - 정시 발행: Windows 작업 `cardnews-reel-judge`(18:00) / `cardnews-reel-lab`(21:10) → `%USERPROFILE%\.cardnews\reel-*.cmd` dispatch.
- **릴스 자동화 (2026-08-04 구축)**: 낮 캐러셀과 같은 사연을 저녁에 릴스로 재발행해 비팔로워 도달 확보 (정적 카드는 비팔로워에게 안 뿌려지는 문제의 처방 ①).
  - `make_reel.py`: output/<slug>/ 카드 PNG → 9:16 mp4 (블러 배경+중앙 카드+표지 줌인+0.4s 페이드, 카드 7장≈17초). ffmpeg 필요 (Actions에서 apt 설치).
  - BGM: `assets/bgm/judge.m4a`(재판 긴장 로파이)·`lab.m4a`(마림바) — 힉스필드 sonilo_music 생성, 저작권 프리.
  - `upload_instagram_reel.py`: REELS API 발행. 커버=01.png, share_to_feed=false(그리드 중복 방지). 가드: last_published==오늘(캐러셀 후속 원칙) + last_reel 중복 방지.
  - `publish-reel.yml`: 판사 18:00·연구소 21:00 KST. mp4는 Actions에서 생성 후 저장소 커밋(raw URL 호스팅). dispatch `slug=case-011` 입력 시 미리보기 생성만(발행 안 함).
  - ~~GitHub cron 미작동 이슈~~ → **2026-08-07 해결: GitHub 자체 schedule 전면 제거, cron-job.org 외부 트리거 단일 체제로 전환** (아래 표 참조).

- **⏰ 발행 트리거 = cron-job.org 전담 (2026-08-07 전환)**: GitHub 무료 요금제 cron이 수 시간씩 지연되거나 아예 안 오는 문제로, 모든 워크플로에서 `on: schedule`을 삭제하고 `workflow_dispatch`만 남겼다. 외부에서 GitHub API를 때려 깨우는 방식(threads-bot과 동일).
  - 계정: cron-job.org / pdrlive.official@gmail.com. 인증은 fine-grained PAT **"cron-trigger"**(threads-bot + cardnews 접근 권한, 만료 없음)가 cron-job.org에 저장돼 있음.
  - 등록된 트리거 (KST): **08:05 스레드 아침글**(threads-extra) · **12:03 판사 캐러셀**(publish) · **18:03 판사 릴스**(publish-reel) · **19:03 연구소 캐러셀**(publish-lab) · **21:02 스레드 저녁글**(threads-extra) · **21:08 연구소 릴스**(publish-reel) · **답글봇 2시간마다**(reply, 09~23시 홀수시 05분)
  - ⚠️ **워크플로에 `on: schedule`을 다시 추가하지 말 것.** 지연 도착한 cron이 claim(선점 잠금)만 해놓고 죽으면 그날 발행이 통째로 결측된다 (2026-08-06 연구소 실사고).
  - 새 트리거 추가 방법: cron-job.org 콘솔에서 기존 잡을 **Clone** → URL의 워크플로 파일명과 crontab만 수정 → Enable job → Save (토큰이 그대로 복제돼 재입력 불필요).
- **노출 인사이트 (2026-07-28 실측)**: 판사 도달 14~24/게시물(팔로워 665의 3% — 재활용 계정의 휴면 팔로워가 원인 추정), 저장·공유 0. 처방 우선순위: ①릴스 자동화(카드→슬라이드 영상) ②마지막 카드 저장 유도 문구 ③댓글 씨딩·고정 운영 ④스레드 교차 홍보. insights.yml workflow_dispatch로 재조회 가능.
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

## 💬 답글 봇 (reply_bot.py) — 2026-08-08 대수술

- **⚠️ 페이지네이션 버그 (8/8 발견·수정)**: 댓글 API는 커서 페이지네이션인데 첫 페이지만 읽고 있어서, 글마다 앞쪽 20~30개만 보고 "다 처리했다"고 판단했다. 연구소 카풀 글은 댓글 1,031개 중 대부분이 방치됨(미답변 2,184건). `fetch_all()`로 커서를 끝까지 따라가도록 수정.
- **스레드 API 한도 (실측)**: 게시글 **250/24h**, 답글은 **별도 1,000/24h**. `GET /me/threads_publishing_limit?fields=quota_usage,config,reply_quota_usage,reply_config`로 확인. 답글이 게시글 쿼터를 쓴다고 착각하지 말 것 — 답글 200건 달아도 게시글 쿼터는 2였다.
- **A안 = 최근 N일 집중 (사용자 결정 8/8)**: `--days=3` 기본값. 노출이 끝난 옛 글에 자원을 쓰지 않고 살아있는 글에 몰아준다. 정기 실행은 cap=40·threads=20·days=3.
- **CLI 플래그**: `python reply_bot.py <judge|lab> [--audit] [--cap=N] [--threads=N] [--days=N]`. `--audit`은 미답변 건수만 원글별로 집계(게시 안 함). 워크플로 `reply.yml`에 같은 입력값이 있음(`only`로 계정 지정).
- **시점 규칙 (8/8 사용자 지시)**: 사연은 **제보받은 남의 이야기**다. 1인칭("저도 그 부분이 걸렸어요")으로 쓰면 계정 주인 경험담으로 읽혀 비난이 운영자에게 꽂힌다 → PERSONA/GUIDE에 3자 시점을 못박고 사연 당사자는 '제보자님'으로 호칭. 좋은 예: "제보자님도 그래서 답답하셨나 봐요".
- **팔로우 유도 CTA (8/8)**: `CTA_EVERY=4` — 4개 답글마다 1번만, 계정별 4종 문구를 순환해 붙인다. 매번 붙이면 매크로 티가 나고 스팸 필터 위험.
- **매크로 폴백 금지 (8/6 사용자 지시)**: AI 실패 시 준비된 문구로 때우지 않는다. 답 안 달고 다음 실행에서 재시도. Gemini 429(쿼터)면 `gemini-flash-lite-latest`로 즉시 폴백.
- **⚠️ 전환 실패 교훈 (8/8)**: 연구소는 누적 조회 50만인데 스레드 팔로워 45명·인스타 0명(전환율 0.009%). 카풀 글이 9.9시간에 조회 36,635·좋아요 1,005·댓글 1,031을 찍었지만 ①답글 못 담(페이지네이션 버그) ②CTA 없음 ③프로필에 볼 것 없음으로 전부 흘려보냈다. **터진 글에는 즉시 답글 총력 + 고정 댓글로 팔로우 유도할 것.**

## 컨펌 규칙 (중요)

**업로드 전 반드시 사용자 컨펌.** 흐름: 사연 작성 → PNG 생성 → 사용자에게 보여주기 → OK 받으면 업로드. 컨펌 없이 게시 금지.

## 🤖 자동 발행 (가동 중, 2026-07-25 시작)

- **계정**: @comment.judgee ("댓글판사", 프로페셔널/크리에이터, 팔로워 ~667)
- **구조**: GitHub 저장소 `pdrliveofficial-lang/cardnews` (공개 — raw URL이 이미지 호스팅) + GitHub Actions `publish.yml`이 `upload_instagram.py` 실행 → state.json의 next_case를 캐러셀 발행 후 +1 커밋.
- **⚠️ 스케줄 방식 (2026-07-28 최종)**: GitHub 무료 cron은 6~10시간 지연됨(다중 트리거로도 해결 안 됨). **정시 발행은 사용자 PC의 Windows 작업 스케줄러가 담당**: 작업 `cardnews-judge-publish`(12:00)·`cardnews-lab-publish`(19:00)가 `%USERPROFILE%\.cardnews\publish-*.cmd` 실행 → gh workflow_dispatch (수 초 내 실행됨). 인증은 `%USERPROFILE%\.cardnews\gh-token.txt`(사용자 전용 ACL, 레포 밖) — **gh 재로그인 시 이 파일도 `gh auth token`으로 갱신할 것.** PC가 꺼져 있으면: ①작업 스케줄러 StartWhenAvailable로 부팅 후 즉시 실행 ②GitHub cron 다중 트리거가 백업(지연 발행) ③`last_published` 가드가 중복 방지. 로그: `%USERPROFILE%\.cardnews\*.log`.
- **⚠️ 중복 발행 사고 (2026-07-29)**: 지연된 GitHub cron과 정시 dispatch가 34초 차이로 동시 실행 → 가드가 둘 다 통과 → 판사 No.006 2회 발행. **수정: 발행 전 `claim.py`로 state에 claimed=오늘 커밋·푸시(선점 잠금), 푸시 실패 시 스킵.** 경합 시 한 실행만 발행됨. 중복 게시물은 API로 삭제 불가 — 앱에서 수동 삭제.
- **API**: Instagram API with Instagram Login (페이스북 페이지 불필요). Meta 앱 **cardnews-bot** (앱 ID 1013526951312622), Instagram 앱 ID 2450710675398072. comment.judgee는 앱의 Instagram 테스터로 등록·수락됨.
- **Secrets** (repo secrets): `IG_TOKEN` (장기 토큰, **2026-07-25 발급 → 60일 후 2026-09-22경 만료**), `IG_USER_ID` (17841455934440668).
- **토큰 갱신**: 만료 전 `GET graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=<현재토큰>` 호출 후 `gh secret set IG_TOKEN --body "<새토큰>"`. (재발급이 필요하면 인증 링크 방식: 리디렉션 URI는 https://github.com/pdrliveofficial-lang/cardnews, 스코프에 instagram_business_content_publish 필수. 시크릿은 Meta 콘솔 > cardnews-bot > Instagram > API 설정에서 표시.)
- **수동 발행**: `python upload_instagram.py` (env IG_TOKEN/IG_USER_ID 필요) 또는 GitHub Actions workflow_dispatch.
- 발행 이력: case-001 (2026-07-25 수동 테스트, media 17971311825093729). state.json next_case=2.

## 🎯 다음 작업 (2026-07-30 사용자 결정)

1. ~~댓글판사 연애 전환~~ **실행됨 (2026-08-02)**: case-010, 013~020(9건)을 연애·결혼 갈등 사연으로 교체(전여친 축하, 남사친 1박, 반반결혼, 읽씹+스토리, 월급공개, 커플템 선물, 친구모임 동행, 이별정산, 신혼집 비번). 011(사회 노쇼페이)·012(곗돈 이자)는 유지. 소재는 네이트판·더쿠 등 커뮤니티 논쟁 축(이성친구/돈/시댁/SNS/성의)을 리서치해 **창작 각색**(원문 복사 금지). **가드레일**: 성별 대결 프레임 금지(성별 뒤집어도 성립), 불륜 직접 소재는 노출 제한·신고 리스크로 보류 — 반응 데이터 보고 순화된 형태로 검토. 운영 방침: 반응 데이터(insights.yml) 보며 톤·소재 고도화.
2. ~~스레드 교차 발행~~ **완료 (2026-08-01)**: `post_threads.py`가 인스타 발행 직후 실행되어 표지 이미지 + 훅(제목·A/B·유도문)을 @comment.judgee 스레드에 게시. 시크릿 `THREADS_TOKEN_JUDGE`(2026-08-01 발급, 60일) / `THREADS_USER_ID_JUDGE`=28773528748904550, threads-bot 앱(1714194796572628) 사용. story JSON에 `threads` 필드를 넣으면 그 문구를 그대로 사용. 스레드 단계는 continue-on-error라 실패해도 인스타 발행엔 영향 없음. **연구소도 연결 완료 (2026-08-02)**: @jaljalmot.lap, `THREADS_TOKEN_LAB`(60일, ~10/1 만료) / `THREADS_USER_ID_LAB`=27690702580540105. post_threads.py가 slug로 판사/연구소 자동 구분. lab-006~020 스레드 원고 작성 완료.
- **스레드 글 원칙 (2026-08-02 사용자 피드백 반영)**: ①본문에서 기승전결 완결 — "링크로 오라"는 유도 금지 ②1인칭 극대노/황당 톤, 구체적 상황+어이없는 대사+되묻기 마무리 ③이미지 첨부 금지(홍보물처럼 보여 이탈) ④A/B 객관식 금지 ⑤**셀프 답글(홍보 댓글) 금지** — 사용자가 "그냥 안 하는 게 낫다"고 결정. 참고 벤치마크: @he.uiui (59만 조회, 시리즈물+고정댓글 제품 언급).
- **⚠️ 판사 계정 예외 (2026-08-06 사용자 피드백)**: 1인칭 빙의체는 **계정 주인 실화로 읽혀 비난 댓글이 운영자에게 꽂힘** → 판사는 **"[사연 접수] 제보 프레임"**(3인칭 소개 + "판결은 댓글로" + 마지막 줄 예/아니요 질문)으로 전환. **예/아니요 설문**(threads poll, 24h 자동 종료) 첨부: 풀 아이템은 `{"text","poll":{"a","b"}}` dict, 사연은 `threads_poll` 필드. post_threads.py가 `poll_attachment` 파라미터로 게시하고 실패 시 설문 없이 폴백(다음 실행 로그에서 "poll attach failed" 확인할 것). 풀 8~19 + case-014~020 적용 완료. **연구소도 2026-08-08 전환 완료** (pool 12~37 + lab-011~023, 26+13편) — 판사만 바꿔놓고 연구소를 1인칭으로 남겼더니 사용자가 "왜 또 내가 올린 것처럼 해놨어"라고 지적. **앞으로 프레임·시점 변경은 두 계정에 동시 적용할 것.** 기존 표기(폐기)=(불만 제기 없음 + 일상 소재라 리스크 낮음 — 같은 문제 보이면 동일 전환).
3. **스레드 하루 3편 체제 (2026-08-02 완료)**: 계정당 아침(08:00)·낮(카드뉴스 발행 시각: 판사 12:00 / 연구소 19:00)·저녁(21:00) 총 3편.
   - 낮 = `post_threads.py <slug>` (카드뉴스 사연 원고, publish 워크플로 내부에서 실행).
   - 아침/저녁 = `post_threads.py --pool <judge|lab> <morning|evening>` — `threads_pool_judge.json` / `threads_pool_lab.json`(각 20편, 스레드 전용 썰)에서 `next` 순서대로 1편. **slot별 하루 1회 가드 + 게시 전 선점 기록**으로 중복 트리거 방지.
   - 워크플로 `threads-extra.yml` (cron 다중 트리거 + workflow_dispatch inputs.slot), 정시 실행은 Windows 작업 `cardnews-threads-morning`(08:00) / `cardnews-threads-evening`(21:00) → `%USERPROFILE%\.cardnews\threads-*.cmd`.
   - **⚠️ 아침 슬롯 미발행 사고 (8/3~8/4)**: PC 꺼져 있어 윈도우 작업 못 돌고, 백업 GitHub cron은 지연 실행되며 slot 판정(UTC 23/00시=morning)에 안 걸려 evening으로 오분류 → 아침 이틀 결번. **수정: slot을 KST 시각(05~15시=morning)으로 판정** — cron이 몇 시간 지연돼도 슬롯 유지됨. 8/4 21:53 백필 완료.
   - 풀 소진 시점: 20편 ÷ 2슬롯 = **약 10일치 (~2026-08-12)**. 소진되면 "pool exhausted" 로그만 남고 조용히 스킵되므로 사전 충전 필요.
4. **스레드 흥행 공식 (2026-08-02, 9,024뷰 글에서 역산)**: 판사 "집들이 선물 위시리스트" 글이 11.5h만에 조회 9,024·좋아요 60·댓글 29 기록. 댓글이 "휴지는 성의없다" vs "돈 쓰는 사람 맘"으로 **갈린 것**이 핵심 동력. 공식: ①구어체 훅+구체적 숫자(15만원, 6명 중 하나) ②상대 대사 직접 인용 ③내 감정 한 줄 ④**상대 입장도 일리 있게 한 줄** ⑤마무리는 "나만 이런가/요즘은 다 이런가" 형 기준 비교 질문 — **조언 요청형("어떻게 하세요?") 금지**. 소재 조건: **명백한 가해자가 있으면 탈락**(도둑·무단침입·갑질 등은 논쟁이 안 되어 댓글이 안 붙음). 최고 반응 축 = **경조사·돈 문화**(축의금/청첩장/정산/집들이).
   - **연구소 풀 전면 재작성 (2026-08-02)**: 기존 20편 중 8편(40%)이 가해자 명백 소재(탕비실 도둑·택배 발로 밀기·임산부석·아이디어 가로채기·밤11시 청소기·무단외박·충전기·스피커폰)여서 폐기. 위 공식으로 20편 신규 작성, 경조사·돈 소재를 앞쪽에 배치. `next=0`으로 리셋(전편 신규라 중복 없음).
   - **⚠️ 표본 주의**: 게시물 조회는 시간이 지나며 붙으므로 **age_h를 맞춰 비교**할 것. 신선한 글(0.6h)과 성숙한 글(11.5h)을 비교하면 왜곡됨. `threads_insights.py`는 24h+ 글만 성숙 표본으로 집계한다.
5. **데이터 축적 (2026-08-02 구축)**: `stats.yml`이 매일 KST 02:00에 `threads_insights.py --save` 실행 → `stats/threads_stats.jsonl`에 게시물별 (조회·좋아요·댓글·age_h) 스냅샷 누적 커밋. 며칠 쌓이면 소재축·시간대별 비교가 가능해진다. 수동 조회는 `insights.yml` workflow_dispatch.
   - **미해결 이상치**: 연구소 "대리 승진" 글이 10.1h 시점 조회 0인데 답글은 1개 — API 지표 지연으로 추정(노출은 실제로 있었음). 다음 스냅샷에서 재확인 필요.
6. **스레드 글 포맷 v2 (2026-08-07 사장님 지시)**: "[사연 접수]" 제보 프레임 제거 — 1인칭으로 바로 시작. 설문은 두 계정 모두 예/아니요 통일(마무리 질문을 예/아니요로 답할 수 있게 쓸 것). **가장 궁금한 대목은 `||...||`로 감싸면 발행 시 탭해서 보는 블라인드(스포일러)로 변환**됨 (post_threads.py parse_spoilers → text_entities API, UTF-16 오프셋, 글당 최대 10개, 거부 시 자동 폴백 — 폰 실기기 렌더링 검증 완료 2026-08-07). 신규 풀 작성 시 이 포맷 준수. **마지막 줄엔 팔로우 유도문구** (사장님 확정 2026-08-07, 친근체+"스치니들" 호칭): "오늘 판결 재밌었으면 팔로우·좋아요·리포스트~ 스치니들, 내일 사연은 더 골때려" 톤의 3종 로테이션 (판사/연구소 각각 pool 항목에 반영돼 있음 — 같은 문구 연속 반복 금지).
6. **소개글 (2026-08-02)**: 두 계정 bio를 각 컨셉·발행시각에 맞춰 작성. 연구소는 수집/사건파일 어휘, 판사는 재판 어휘(판결/개정)로 차별화.
   - 연구소 @jaljalmot.lap — 스레드·인스타 **양쪽 완료**: "일상 속 애매한 사건들을 수집합니다 🔍 / 누가 잘못했는지, 판정은 댓글로 / 매일 저녁 7시 새 사건 파일 공개"
   - 판사 @comment.judgee — **인스타는 제보 프레임으로 갱신 완료 (2026-08-06)**: "제보로 들어온 사건들을 전달해드립니다 ⚖️ / 판결은 여러분의 댓글로 / 매일 낮 12시 개정 · 사연 제보는 DM (2026-08-06 "전달자" 포지션으로 재수정)". **스레드 bio도 동일 문구로 갱신 완료 (2026-08-06)** — 스레드 로그아웃 후 로그인 화면의 "Instagram으로 계속하기" SSO 버튼을 쓰면 인스타 세션(계정 전환 가능)을 타고 비밀번호 없이 원하는 계정으로 스레드 로그인 가능. 셀프 홍보 답글은 이미 삭제 확인됨. ⚠️ 현재 스레드 세션은 판사 — 연구소 스레드 작업 시 같은 방법으로 전환할 것.
   - ⚠️ **스레드 bio는 인스타에서 동기화되지 않는다**(별도 필드). ~~판사 스레드 bio 비어 있음~~ → 2026-08-04 입력 완료.
   - ⚠️ **스레드 웹에는 계정 전환·추가가 없다**(로그아웃뿐). 반면 **인스타 웹에는 계정 전환이 있고**(햄버거 > 계정 전환) jaljalmot.lap / comment.judgee / serendi_pity_ / carrot_matketer 세션이 저장돼 있어 비밀번호 없이 전환 가능 — 인스타 쪽 작업은 이 경로를 쓸 것.
   - 판사 스레드 잔여 작업: ~~①bio 입력~~ ~~②위시리스트 글 셀프 홍보 답글 삭제~~ (모두 8/4 완료). bio에 4번째 줄 "문의 및 1:1상담은 메세지로" 추가(사장님 지시 8/4). 참고: 8/4부터 맥 크롬 스레드 웹 세션은 comment.judgee (세렌디스트는 인스타 세션 경유로 재로그인 가능, 게시는 API 큐라 무관).

## 세션 기록 2026-08-03 (맥)

- **맥 클론 확인**: `/Users/2026_유훈희/개인자료/_Ai/Main_treads/cardnews` — Windows PC 없이도 GitHub 중심으로 전 작업 가능 확인.
- reply.yml 수동 dispatch → 새 답글 4건 (판사 위시리스트 글 댓글들), 누적 판사 21/연구소 1. GitHub cron 지연 시 이렇게 수동 트리거하면 즉시 처리됨.
- 노션 프로젝트 대시보드에 cardnews 페이지·현황 행 추가됨.
- **reply-bot 429 버그 수정 (8/3)**: 사용자가 "대댓글이 제대로 안 되는 것 같다" 신고 → 원인 = Gemini 무료 쿼터 429인데 재시도 간격(5~15s)이 분당 쿼터 리셋(60s)보다 짧아 전부 skip. 수정: ①429 재시도 40/80s 대기 ②AI 연속 3회 실패부터 FALLBACK 템플릿 답글(무응답 방치 방지) ③SKIP 판정은 replied 기록해 영구 제외. ⚠️ 같은 GEMINI_API_KEY를 threads-bot(결혼봇+꽃언니, 30분 주기)과 공유하므로 쿼터 경쟁 있음 — 429 잦아지면 cardnews용 별도 키 발급 검토.
- 참고: 같은 날 양재꽃언니(@serendist.log, threads-bot/flower_actions) 가동 시작 — 계정군이 3개(결혼봇·꽃언니·판사/연구소)가 됨. 토큰 만료 캘린더: 9/18 결혼봇 · 9/22 IG판사 · 9/25 IG연구소 · 10/1 스레드판사/연구소 · 10/2 꽃언니.

## 대기/진행 중 (2026-08-02 기준 — 다음 세션 시작점)

**재고 (소진일)**
| 항목 | 다음 번호 | 마지막 | 소진 예정 |
|---|---|---|---|
| 판사 카드뉴스 | case-010 | case-020 | **~8/13** |
| 연구소 카드뉴스 | lab-007 | lab-020 | **~8/16** |
| 판사 스레드 풀 | next=1 | 20편 | **~8/12** (2편/일) |
| 연구소 스레드 풀 | next=0 | 20편 | **~8/12** (2편/일) |

**토큰 만료** — IG_TOKEN ~9/22, IG_TOKEN_LAB ~9/25, THREADS_TOKEN_JUDGE/LAB ~10/1. 갱신법은 위 자동 발행 절 참조.

**막힌 것 / 사용자 액션 필요**
1. **판사 스레드 로그인** — bio 입력 + 셀프 홍보 답글 삭제 2건이 여기 묶여 있음. 스레드 웹은 로그아웃 외 전환 수단이 없어 대신 처리 불가.
2. **연구소 팔로잉 0** — 스레드가 빈 계정으로 인식하는 신호. 관련 계정 10~20개 수동 팔로우 권장(봇 팔로우는 스팸 판정 위험으로 하지 말 것).

**다음 세션 우선순위**
1. `stats/threads_stats.jsonl` 읽어 24h+ 성숙 표본 비교 — 재작성한 연구소 풀이 실제로 먹히는지, 소재축(경조사·돈 vs 나머지)·시간대(08시/12·19시/21시) 중 뭐가 유효한지 판정. **이게 나머지 결정의 입력값이다.**
2. 위 판정 결과를 반영해 재고 충전 (카드뉴스 + 스레드 풀). 8/12~8/13 동시 소진이라 그 전에.
3. 연구소 "대리 승진" 글 조회 0 이상치 재확인 — 지표 지연이었는지, 계정 노출 문제인지.
4. 판사 풀도 연구소와 같은 기준으로 감사(가해자 명백 소재 걸러내기) — 아직 안 함.

**보류**
- 댓글 고정 운영("가장 공감받은 판결 고정")은 수동 — 추후 반자동화 검토.
- 수익 계정 1호 설계 — 사용자 답변 대기(실제 쓰는 제품 카테고리 / 하루에 낼 수 있는 댓글 응대 시간).

## 작업 규칙

- 한글 인코딩: PowerShell 인라인 한글 금지, 파일은 UTF-8. (threads-bot과 동일)
- 사건번호는 이어서 증가 (case-001 다음 case-002...).
- caption.txt 는 게시 캡션 원본 — 해시태그 10개 내외 유지.
