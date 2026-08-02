# cardnews — 사연 판결형 카드뉴스 파이프라인 (댓글판사 + 잘잘못연구소)

> 인스타그램 카드뉴스 계정용 콘텐츠 제작 파이프라인. 세렌디피티(threads-bot)와 별개 프로젝트지만 같은 사용자.
> 작업 방식이 바뀌면 이 문서도 업데이트할 것.

## 개요

- **콘셉트**: "댓글로 판결하는 재판" — 사연(AITA 스타일)을 사건번호 붙여 카드 7장으로 풀고, 마지막 장에서 A/B 판결 투표로 댓글 유도.
- **투 트랙 운영** (2026-07-25부터):
  - **댓글판사** @comment.judgee — 재판 콘셉트(레드), 돈·경조사 갈등 사연. stories/case-*.json, state.json, 매일 12:00 KST 발행.
  - **잘잘못연구소** — 보라(#5C4BC4) 스토리형 디자인 **(최종 확정 2026-07-25, 사용자가 claude.ai 디자인 핸드오프로 전달)**. 전용 템플릿 `template-lab.html` (render.py가 lab-* slug면 자동 선택). 인스타 스토리 문법: 진행바 7세그 + 프로필 행(jaljalmot_lab) + 흰 카드 회전 + VS 배지 + A/B 투표카드 + 답장바. 100% CSS(사진 불필요 → 힉스필드 크레딧 0), Pretendard CDN 웹폰트(virtual-time-budget 8000). 디자인 스펙 원본: 사용자 바탕화면 design_handoff_jaljalmot_cardnews/README.md. 일상·관계 논쟁 사연, stories/lab-*.json (cover에 `emoji` 필드), state-lab.json, 매일 19:00 KST 발행(publish-lab.yml). **계정: @jaljalmot.lap (연결 완료 2026-07-27)** — IG_USER_ID_LAB=17841445123080452, IG_TOKEN_LAB은 2026-07-27 발급(60일, ~9/24 만료). lab-001은 7/27 수동 테스트 발행 완료, lab-002부터 자동.
- **콘텐츠 재고**: case-001~020 + lab-001~020 (2026-07-28 20세트 충전, 각 ~8/12·8/14 소진 예정).
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
3. **스레드 하루 3편 체제 (2026-08-02 완료)**: 계정당 아침(08:00)·낮(카드뉴스 발행 시각: 판사 12:00 / 연구소 19:00)·저녁(21:00) 총 3편.
   - 낮 = `post_threads.py <slug>` (카드뉴스 사연 원고, publish 워크플로 내부에서 실행).
   - 아침/저녁 = `post_threads.py --pool <judge|lab> <morning|evening>` — `threads_pool_judge.json` / `threads_pool_lab.json`(각 20편, 스레드 전용 썰)에서 `next` 순서대로 1편. **slot별 하루 1회 가드 + 게시 전 선점 기록**으로 중복 트리거 방지.
   - 워크플로 `threads-extra.yml` (cron 다중 트리거 + workflow_dispatch inputs.slot), 정시 실행은 Windows 작업 `cardnews-threads-morning`(08:00) / `cardnews-threads-evening`(21:00) → `%USERPROFILE%\.cardnews\threads-*.cmd`.
   - 풀 소진 시점: 20편 ÷ 2슬롯 = **약 10일치 (~2026-08-12)**. 소진되면 "pool exhausted" 로그만 남고 조용히 스킵되므로 사전 충전 필요.
4. **스레드 흥행 공식 (2026-08-02, 9,024뷰 글에서 역산)**: 판사 "집들이 선물 위시리스트" 글이 11.5h만에 조회 9,024·좋아요 60·댓글 29 기록. 댓글이 "휴지는 성의없다" vs "돈 쓰는 사람 맘"으로 **갈린 것**이 핵심 동력. 공식: ①구어체 훅+구체적 숫자(15만원, 6명 중 하나) ②상대 대사 직접 인용 ③내 감정 한 줄 ④**상대 입장도 일리 있게 한 줄** ⑤마무리는 "나만 이런가/요즘은 다 이런가" 형 기준 비교 질문 — **조언 요청형("어떻게 하세요?") 금지**. 소재 조건: **명백한 가해자가 있으면 탈락**(도둑·무단침입·갑질 등은 논쟁이 안 되어 댓글이 안 붙음). 최고 반응 축 = **경조사·돈 문화**(축의금/청첩장/정산/집들이).
   - **연구소 풀 전면 재작성 (2026-08-02)**: 기존 20편 중 8편(40%)이 가해자 명백 소재(탕비실 도둑·택배 발로 밀기·임산부석·아이디어 가로채기·밤11시 청소기·무단외박·충전기·스피커폰)여서 폐기. 위 공식으로 20편 신규 작성, 경조사·돈 소재를 앞쪽에 배치. `next=0`으로 리셋(전편 신규라 중복 없음).
   - **⚠️ 표본 주의**: 게시물 조회는 시간이 지나며 붙으므로 **age_h를 맞춰 비교**할 것. 신선한 글(0.6h)과 성숙한 글(11.5h)을 비교하면 왜곡됨. `threads_insights.py`는 24h+ 글만 성숙 표본으로 집계한다.
5. **데이터 축적 (2026-08-02 구축)**: `stats.yml`이 매일 KST 02:00에 `threads_insights.py --save` 실행 → `stats/threads_stats.jsonl`에 게시물별 (조회·좋아요·댓글·age_h) 스냅샷 누적 커밋. 며칠 쌓이면 소재축·시간대별 비교가 가능해진다. 수동 조회는 `insights.yml` workflow_dispatch.
   - **미해결 이상치**: 연구소 "대리 승진" 글이 10.1h 시점 조회 0인데 답글은 1개 — API 지표 지연으로 추정(노출은 실제로 있었음). 다음 스냅샷에서 재확인 필요.
6. **소개글 (2026-08-02)**: 두 계정 bio를 각 컨셉·발행시각에 맞춰 작성. 연구소는 수집/사건파일 어휘, 판사는 재판 어휘(판결/개정)로 차별화.
   - 연구소 @jaljalmot.lap — 스레드·인스타 **양쪽 완료**: "일상 속 애매한 사건들을 수집합니다 🔍 / 누가 잘못했는지, 판정은 댓글로 / 매일 저녁 7시 새 사건 파일 공개"
   - 판사 @comment.judgee — **인스타만 완료**(기존 "당신의 선택은?" 8자를 교체): "연애하다 생긴 애매한 싸움을 판결합니다 ⚖️ / 오늘의 잘잘못, 판정은 댓글로 / 매일 낮 12시 개정"
   - ⚠️ **스레드 bio는 인스타에서 동기화되지 않는다**(별도 필드). 판사 스레드 bio는 여전히 비어 있음.
   - ⚠️ **스레드 웹에는 계정 전환·추가가 없다**(로그아웃뿐). 반면 **인스타 웹에는 계정 전환이 있고**(햄버거 > 계정 전환) jaljalmot.lap / comment.judgee / serendi_pity_ / carrot_matketer 세션이 저장돼 있어 비밀번호 없이 전환 가능 — 인스타 쪽 작업은 이 경로를 쓸 것.
   - **판사 스레드 로그인 시 한 번에 처리할 잔여 작업 2건**: ①bio 입력(위 문구) ②위시리스트 글에 남은 셀프 홍보 답글 삭제.

## 대기/진행 중

1. **사연 소재 뱅크**: case-002~010 재고 있음 (~8/3까지). 소진 전 신규 사연 제작 필요.
2. **프로필 세팅**: 프로필 사진(로고)·소개문구 미완 — 다음 세션에서 시안 제작 추천.
3. **댓글 고정 운영**: "가장 공감받은 판결 고정"은 수동 운영 필요 — 추후 반자동화 검토.

## 작업 규칙

- 한글 인코딩: PowerShell 인라인 한글 금지, 파일은 UTF-8. (threads-bot과 동일)
- 사건번호는 이어서 증가 (case-001 다음 case-002...).
- caption.txt 는 게시 캡션 원본 — 해시태그 10개 내외 유지.
