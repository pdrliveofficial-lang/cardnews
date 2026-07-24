# cardnews — 사연 판결형 카드뉴스 파이프라인 ("댓글판사")

> 인스타그램 카드뉴스 계정용 콘텐츠 제작 파이프라인. 세렌디피티(threads-bot)와 별개 프로젝트지만 같은 사용자.
> 작업 방식이 바뀌면 이 문서도 업데이트할 것.

## 개요

- **콘셉트**: "댓글로 판결하는 재판" — 사연(AITA 스타일)을 사건번호 붙여 카드 7장으로 풀고, 마지막 장에서 A/B 판결 투표로 댓글 유도.
- **계정**: **댓글판사 (확정)** — @comment.judge 예정, 아직 미개설
- **콘텐츠 재고**: 사건 No.001~010 (output/case-001~010, 각 7장 + caption.txt) — 10회분 업로드 준비 완료. 3안 잘잘못연구소 시안은 폐기(댓글판사로 통일).
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

## 대기/진행 중

1. **인스타 계정 개설**: 사용자가 직접 개설 필요 (계정 생성은 Claude가 대행 불가). 이름 1안 "댓글판사".
2. **업로드 방식 미정**: Graph API 자동화(비즈니스 계정+FB페이지 필요) vs 브라우저 반자동 vs 수동. 계정 개설 후 결정.
3. **사연 소재 뱅크**: 아직 없음. 추후 stories/ 에 축적.

## 작업 규칙

- 한글 인코딩: PowerShell 인라인 한글 금지, 파일은 UTF-8. (threads-bot과 동일)
- 사건번호는 이어서 증가 (case-001 다음 case-002...).
- caption.txt 는 게시 캡션 원본 — 해시태그 10개 내외 유지.
