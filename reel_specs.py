# -*- coding: utf-8 -*-
"""클링 릴스 제작 사양 — 사연별 장면 프롬프트·자막·나레이션을 한 곳에 모은다.

파이프라인: 프레임 생성(나노바나나) → 클링 영상(스타트 프레임만, Unlimited 무료)
          → Gemini TTS 나레이션 → make_reel_kling.py 조립
자막은 drawtext에 자동 줄바꿈이 없으므로 반드시 2줄로 끊어서 적을 것(줄당 13자 안팎).
"""

STYLE = ("Korean webtoon manhwa style digital illustration, clean bold linework, "
         "soft cel shading, expressive face, muted warm color palette, "
         "vertical 9:16 composition, high quality, "
         "no text, no letters, no writing, no watermark")

SPECS = {
 # ================= 댓글판사 (연애 갈등) =================
 "case-017": {
  "chars": {
   "M": "a Korean man in his late 20s with short black hair wearing a plain gray t-shirt",
   "W": "a Korean woman in his late 20s with long wavy dark hair wearing a light pink blouse",
  },
  "verdict_img": "assets/case-012/toon/06.png",
  "verdict": [("먼저 말했다고", "평생 입어야 하는 건 아니죠?"),
              "판결은 댓글로 · 스하리 남겨주면 다 갈게요"],
  "verdict_narr": "먼저 말했다고 평생 입어야 하는 건 아니죠? 판결은 댓글로 남겨주세요.",
  "scenes": [
   {"p": "{M} and {W} sitting close on a sofa in a cozy living room, chatting happily, "
         "he gestures while talking with a light smile, warm evening light, {S}",
    "cap": ("\"커플템 하나쯤", "있으면 좋겠다\""),
    "narr": "커플템 하나쯤 있으면 좋겠다고, 먼저 말한 건 저였습니다."},
   {"p": "{W} smiling brightly while holding out a neatly wrapped gift box with both hands, "
         "living room with small birthday decorations, warm light, {S}",
    "cap": ("제 생일에 여친이", "커플 후드티를 선물했어요"),
    "narr": "제 생일에, 여자친구가 커플 후드티를 선물했어요."},
   {"p": "close-up of {M} holding up a folded hoodie in front of himself, "
         "looking at it with an awkward strained smile, slight frown, indoor warm light, {S}",
    "cap": ("근데 받아보니", "제 취향이랑 너무 멀더라고요"),
    "narr": "그런데 막상 받아보니, 제 취향이랑 너무 멀더라고요."},
   {"p": "{W} sitting on the sofa with arms crossed, hurt and upset expression, "
         "looking away from the camera, dim living room, {S}",
    "cap": ("\"네가 먼저 하자고 했잖아", "왜 이제 와서?\""),
    "narr": "네가 먼저 하자고 했잖아. 싫으면 그때 말하지, 왜 이제 와서?"},
   {"p": "{M} sitting alone on the edge of the sofa at night, shoulders slumped, "
         "staring down at the folded hoodie on his lap with a conflicted guilty face, {S}",
    "cap": ("제 말이 시작인 건 맞아서", "말 꺼내기도 어려웠습니다"),
    "narr": "제 말이 시작인 건 맞아서, 말 꺼내기도 어려웠습니다."},
  ]},

 "case-018": {
  "chars": {
   "W": "a Korean woman in her late 20s with a neat shoulder-length bob wearing a beige cardigan",
   "M": "a Korean man in his late 20s with short neat hair wearing a navy sweatshirt",
  },
  "verdict_img": "assets/case-012/toon/06.png",
  "verdict": [("가끔은 친구끼리 보고 싶은 거,", "이상한 거 아니죠?"),
              "판결은 댓글로 · 스하리 남겨주면 다 갈게요"],
  "verdict_narr": "가끔은 친구끼리 보고 싶은 거, 이상한 거 아니죠? 판결은 댓글로 남겨주세요.",
  "scenes": [
   {"p": "four Korean friends in their late 20s laughing together around a restaurant table, "
         "{M} among them smiling and fitting in well, warm cheerful mood, {S}",
    "cap": ("친구들이 먼저", "\"남친도 데려와\" 했어요"),
    "narr": "친구들이 먼저, 남자친구도 데려오라고 했어요."},
   {"p": "{M} cheerfully putting on his jacket by the front door, ready to go out, "
         "looking back with an eager smile, apartment hallway, {S}",
    "cap": ("그 뒤로 모든 모임마다", "따라가려고 합니다"),
    "narr": "그런데 그 뒤로, 모든 모임마다 따라가려고 합니다."},
   {"p": "{W} speaking carefully with both palms slightly raised, cautious apologetic "
         "expression, living room at evening, {S}",
    "cap": ("이번엔 혼자 가고", "싶다고 말했더니"),
    "narr": "이번엔 혼자 가고 싶다고 조심스럽게 말했더니,"},
   {"p": "{M} frowning with a hurt suspicious expression, one hand raised in question, "
         "leaning forward slightly, living room, {S}",
    "cap": ("\"이제 와서 빼는 이유가 뭔데?", "뭐 숨길 거 있어?\""),
    "narr": "이제 와서 빼는 이유가 뭔데? 뭐 숨길 거 있어?"},
   {"p": "close-up of {W} with a tired frustrated expression, lips pressed together, "
         "looking down, dim room lighting, {S}",
    "cap": ("오는 게 싫은 게 아닌데", "숨기는 사람이 되네요"),
    "narr": "오는 게 싫은 게 아닌데, 저는 숨기는 사람이 되네요."},
  ]},

 "case-019": {
  "chars": {
   "W": "a Korean woman in her early 30s with straight dark hair wearing a white knit top",
   "M": "a Korean man in his early 30s with short black hair wearing a charcoal jacket",
  },
  "verdict_img": "assets/case-012/toon/06.png",
  "verdict": [("받으면 3년이 정산되는 기분,", "이해되죠?"),
              "판결은 댓글로 · 스하리 남겨주면 다 갈게요"],
  "verdict_narr": "받으면 3년이 정산되는 기분, 이해되죠? 판결은 댓글로 남겨주세요.",
  "scenes": [
   {"p": "{W} and {M} walking side by side on a city street at dusk, she is paying with a "
         "card at a small counter while he stands slightly behind, warm street lights, {S}",
    "cap": ("3년 연애 동안", "데이트비는 제가 7 정도 냈어요"),
    "narr": "3년 연애 동안, 데이트비는 제가 칠 할 정도 냈어요."},
   {"p": "{W} and {M} standing apart facing away from each other on a quiet evening street, "
         "sad heavy atmosphere, cool blue tones, {S}",
    "cap": ("헤어질 때 상대가", "미안했다는 말을 여러 번 했고"),
    "narr": "헤어질 때 상대가, 미안했다는 말을 여러 번 하더니"},
   {"p": "close-up of a woman's hands holding a smartphone showing an abstract blurred "
         "bank transfer notification, her startled face slightly out of focus behind, {S}",
    "cap": ("일주일 뒤 계좌로", "200만원이 들어왔습니다"),
    "narr": "일주일 뒤, 계좌로 200만원이 들어왔습니다."},
   {"p": "{M} sitting at a cafe table looking down with a heavy earnest expression, "
         "hands clasped together, muted lighting, {S}",
    "cap": ("\"정산이 아니라 내 마음이야", "안 그러면 못 살 것 같아\""),
    "narr": "이건 정산이 아니라 내 마음이야. 안 그러면 내가 미안해서 못 살 것 같아."},
   {"p": "{W} sitting alone on her bed at night staring at her phone with a complicated "
         "empty expression, dim bedroom, {S}",
    "cap": ("돌려받을 생각 없었는데", "3년이 숫자가 되는 기분이라"),
    "narr": "돌려받을 생각은 한 번도 없었는데, 3년이 숫자로 정리되는 기분이라서요."},
  ]},

 # ================= 잘잘못연구소 (일상 논쟁) =================
 "lab-011": {
  "chars": {
   "A": "a Korean man in his late 20s with medium-length hair wearing a plain black t-shirt",
   "B": "a Korean woman in her late 20s with a short bob and round glasses wearing a yellow cardigan",
  },
  "verdict_img": "assets/lab-008/toon/99.png",
  "verdict": [("개봉일이어도", "스포는 스포죠?"),
              "판정은 댓글로 · 스하리 남겨주면 다 갈게요"],
  "verdict_narr": "개봉일이어도 스포는 스포죠? 판정은 댓글로 남겨주세요.",
  "scenes": [
   {"p": "{A} sitting at his desk holding two paper movie tickets with an excited happy "
         "smile, a blurred movie poster frame on the wall behind, warm room light, {S}",
    "cap": ("1년 기다린 영화를", "주말에 보러 갈 예정이었어요"),
    "narr": "1년을 기다린 영화를, 주말에 보러 갈 예정이었어요."},
   {"p": "{A} standing in a subway car staring at his smartphone, completely frozen with "
         "wide shocked eyes, abstract blurred chat bubbles glowing on the screen, {S}",
    "cap": ("근데 개봉 첫날 본 친구가", "단톡방에 이럽니다"),
    "narr": "그런데 개봉 첫날 본 친구가, 단톡방에 이럽니다."},
   {"p": "{B} sitting in a movie theater seat holding a bucket of popcorn, typing on her "
         "phone with a casual carefree grin, dim cinema lighting, {S}",
    "cap": ("\"야 대박... 주인공이", "마지막에 죽는 거 실화냐?\""),
    "narr": "야 대박. 주인공이 마지막에 죽는 거 실화냐?"},
   {"p": "close-up of {A} with a devastated hollow stare, mouth slightly open in disbelief, "
         "dark circles, subway interior blurred behind, {S}",
    "cap": ("아무 경고도 없이요", "저 그 자리에서 얼어붙었습니다"),
    "narr": "아무 경고도 없이요. 저 그 자리에서 얼어붙었습니다."},
   {"p": "{B} pushing up her round glasses while speaking matter-of-factly, confident "
         "unbothered expression, cinema lobby background, {S}",
    "cap": ("\"개봉했으면 스포 아니지 않냐?", "그게 화낼 일이야?\""),
    "narr": "개봉했으면 스포 아니지 않냐? 어차피 보면 알 내용인데, 그게 그렇게 화낼 일이야?"},
  ]},

 "lab-012": {
  "chars": {
   "A": "a Korean woman in her mid 20s with a messy bun wearing pastel pink pajamas",
   "B": "a Korean woman in her mid 20s with long straight hair wearing an oversized white t-shirt",
  },
  "verdict_img": "assets/lab-008/toon/99.png",
  "verdict": [("도와준다고 해놓고", "이건 좀 그렇죠?"),
              "판정은 댓글로 · 스하리 남겨주면 다 갈게요"],
  "verdict_narr": "도와준다고 해놓고 이건 좀 그렇죠? 판정은 댓글로 남겨주세요.",
  "scenes": [
   {"p": "{A} holding a small salad bowl with a determined face while {B} beside her gives "
         "an encouraging thumbs up, bright apartment kitchen, daytime, {S}",
    "cap": ("다이어트 선언하고", "룸메한테 도와달라고 했어요"),
    "narr": "다이어트를 선언하고, 룸메이트한테 도와달라고 부탁까지 했어요."},
   {"p": "an opened box of crispy fried chicken on a living room table at night, steam "
         "rising, dramatic warm appetizing light, no people, {S}",
    "cap": ("3일 뒤 밤 10시", "거실에서 치킨 냄새가 났습니다"),
    "narr": "3일 뒤 밤 10시, 거실에서 치킨 냄새가 났습니다."},
   {"p": "{B} holding up a fried chicken drumstick toward the camera with a playful teasing "
         "grin, sitting on the living room floor at night, {S}",
    "cap": ("\"한 조각만 먹어~", "치팅데이라고 생각해ㅋㅋ\""),
    "narr": "한 조각만 먹어. 치팅데이라고 생각해."},
   {"p": "{A} covering her nose and turning her head away with an agonized tempted "
         "expression, night living room, {S}",
    "cap": ("나 도와준다며...", "하필 오늘이야?"),
    "narr": "나 도와준다며. 하필 오늘이야?"},
   {"p": "{B} pouting with an annoyed defensive expression while still holding a piece of "
         "chicken, night living room, {S}",
    "cap": ("\"네 다이어트 때문에", "내가 치킨도 못 시켜?\""),
    "narr": "네 다이어트 때문에 내가 치킨도 못 시켜? 그건 아니지."},
  ]},

 "lab-013": {
  "chars": {
   "A": "a Korean man in his late 20s with short neat hair wearing a gray hoodie, headset on",
   "B": "a Korean man in his late 20s with slightly messy hair wearing a black hoodie, headset on",
  },
  "verdict_img": "assets/lab-008/toon/99.png",
  "verdict": [("게임이라도", "욕은 욕이죠?"),
              "판정은 댓글로 · 스하리 남겨주면 다 갈게요"],
  "verdict_narr": "게임이라도 욕은 욕이죠? 판정은 댓글로 남겨주세요.",
  "scenes": [
   {"p": "{A} sitting at a gaming desk at night wearing a headset, smiling and relaxed, "
         "colorful monitor glow on his face, {S}",
    "cap": ("10년지기랑 처음", "팀 게임을 했는데"),
    "narr": "10년지기 친구랑 처음으로 팀 게임을 했는데,"},
   {"p": "close-up of {A} with a nervous apologetic expression, hands fumbling on a "
         "keyboard, monitor glow, night room, {S}",
    "cap": ("저는 그 게임이", "처음이었어요"),
    "narr": "저는 그 게임이 처음이었어요."},
   {"p": "{B} at his gaming desk shouting furiously into his headset mic, face twisted with "
         "anger, harsh red monitor glow, night, {S}",
    "cap": ("실수할 때마다 목소리가", "점점 험해지더니"),
    "narr": "제가 실수할 때마다 목소리가 점점 험해지더니,"},
   {"p": "close-up of {A} sitting frozen with a hurt stunned face, headset on, staring "
         "blankly at the monitor, dim night room, {S}",
    "cap": ("결국 마이크 너머로", "욕설이 날아왔습니다"),
    "narr": "결국 지고 나서, 마이크 너머로 욕설이 날아왔습니다."},
   {"p": "{B} sitting casually at a cafe table the next day, shrugging with a dismissive "
         "amused smirk, daylight, {S}",
    "cap": ("\"게임할 땐 원래 다 그래~", "진지충 되지 마라ㅋㅋ\""),
    "narr": "게임할 땐 원래 다 그래. 그걸 담아두냐? 진지충 되지 마라."},
  ]},
}


def prompt_of(slug, i):
    sp = SPECS[slug]
    return sp["scenes"][i]["p"].format(S=STYLE, **sp["chars"])
