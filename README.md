# SMR_Safety_Analysis

한양대 원자력공학과 **THINK Lab** · 대학원 「소형모듈원자로 안전해석」(NUE4067) 강의 자료.

교재 『THINK Lab SMR 설계요건과 공학적안전설비 (Rev1.0)』(60쪽)의 내용을 **브라우저에서 도는 46장
애니메이션 슬라이드**로 옮긴 것이다. 단일 HTML 파일이라 USB에 담아 가도, 링크로 열어도 똑같이 돈다.
**한국어와 영어를 한 번에 전환**할 수 있고, 배경도 **어두운 판/밝은 판**을 오갈 수 있으며,
**46장을 그대로 PDF로 내려받을** 수 있다.

**▶ 열기: https://malmok2.github.io/SMR_Safety_Analysis/**

| | |
|---|---|
| 슬라이드 (한국어) | <https://malmok2.github.io/SMR_Safety_Analysis/> |
| 슬라이드 (English) | <https://malmok2.github.io/SMR_Safety_Analysis/?lang=en> |
| PDF (한국어, 46쪽) | <https://malmok2.github.io/SMR_Safety_Analysis/NUE4067_SMR_safety_ko.pdf> |
| PDF (English, 46 p) | <https://malmok2.github.io/SMR_Safety_Analysis/NUE4067_SMR_safety_en.pdf> |

## 무엇이 들어 있나

표지·로드맵 → SMR 정의와 규모의 경제 → 루프형 vs 일체형 → 붕괴열·자연순환·열관성 →
쟁점과 인허가 현황 → 심층방어·단일고장기준·GDC → 공학적안전설비와 피동 Category A~D →
정지계통 → 잔열제거 → 안전주입 → 격납 → 요건→기능→계통 종합.

개념마다 직접 그린 인라인 SVG 애니메이션이 붙어 있다. 슬라이더를 움직이면 실제로 계산이 다시 돈다.

| 슬라이드 | 조작 |
|---|---|
| 규모의 경제 `C(P) = 4000(P/1400)^-0.49` | 출력 슬라이더 |
| 루프형 배관 파단 | 파단 버튼 — 입자가 새고 수위가 떨어진다 |
| 자연순환 `Δp = (ρ_c − ρ_h) g H` | 높이·ΔT 슬라이더 → 화면의 유속이 따라 바뀐다 |
| 심층방어 5단계 | 정상 모드 / 후쿠시마 모드 |
| 정지여유도 SDM | 슬라이더 4개, 1 % 밑으로 가면 경고 |
| 잔열제거 수조 | 용량 슬라이더 → 72 h 도달 여부 |
| 격납 압력 | 이상기체 계산 vs 포화압 클램프 |

## 조작

`←` `→` `Space` 이동 · `O` 전체 개요 · `L` 한/영 전환 · `T` 배경 전환 · `P` 인쇄·PDF 모드 ·
`R` 현재 애니메이션 재생 · `F` 전체화면 · `Esc` 닫기.
화면 왼쪽 28 %를 클릭하면 뒤로, 나머지는 앞으로. 마우스를 움직이면 오른쪽 아래에
`KO / EN / LIGHT / PDF ↓` 버튼이 나타난다.

## 배경

발표는 **어두운 배경**이 기본이다. 조명을 낮춘 강의실에서 대비가 가장 크고, 이 덱은 색이
의미를 지고 있어서(냉각재 파랑 · 열 주황 · 피동 초록 · 규제 조문 노랑) 어두운 바탕이 그 구분을 살린다.

강의실이 밝거나 프로젝터가 약하면 `T` 키로 **밝은 배경**으로 바꾼다. 색이 지는 의미는 그대로고,
흰 바탕에서 읽히도록 강조색만 어둡게 다시 잡았다(WCAG AA 4.5:1 이상).
**인쇄와 PDF는 밝은 배경이 기본**이다 — 46쪽을 흑백으로 뽑아도 읽히게.

## 한국어 · 영어

선택한 언어는 브라우저에 기억되고 주소에도 남는다(`?lang=en`). 강의 중에 `L` 키만 누르면
그 자리에서 바뀐다 — 슬라이드가 다시 그려질 뿐 위치는 그대로다.

번역은 소스 안에 `[[한국어||English]]` 형태로 **나란히** 들어 있다. 수치를 고칠 때 양쪽을
동시에 보게 되므로 한쪽만 낡는 일이 없다. 자세한 규칙은 [`CLAUDE.md`](CLAUDE.md) 4절.

## PDF

학생에게 주는 방법은 두 가지다.

1. **미리 구운 PDF** — 위 표의 링크. 46쪽, 한 쪽이 슬라이드 한 장(1280×720 가로), 밝은 배경.
2. **브라우저에서 직접** — `P` 키를 누르면 46장이 지면에 펼쳐진다. `Ctrl+P` → PDF로 저장.
   색을 살리려면 인쇄 설정에서 **배경 그래픽**을 켠다. 어두운 판이 필요하면 `?print=1&theme=dark`.

애니메이션은 3.4초 뒤 멈춘 장면으로 굳는다. 버튼으로 켜는 화면(후쿠시마 모드, stuck rod 등)은
기본 상태로 인쇄된다.

## 빌드

`src/*.html`을 파일명 순으로 이어 붙여 `docs/index.html`을 만든다.

```bash
./build.sh                       # 윈도우: .\build.ps1
cd tools && npm install playwright-core   # 최초 1회
node check.js                    # 46장을 한/영으로 넘겨보며 오류·번역누락·레이아웃 점검
node pdf.js                      # docs/NUE4067_SMR_safety_{ko,en}.pdf 다시 굽기
```

**`docs/index.html`을 직접 고치지 말 것** — 다음 빌드에 덮인다. 항상 `src/`를 고친다.
슬라이드를 고쳤으면 PDF도 다시 구워서 **같이 커밋**한다.
구조·엔진 API·시각 규약·주의사항은 [`CLAUDE.md`](CLAUDE.md)에 있다.

## 폰트

본문은 **Pretendard**(jsDelivr의 dynamic-subset), 라벨·수치는 **IBM Plex Mono**(Google Fonts)다.
받아오지 못하면 설치된 Pretendard → Apple SD Gothic Neo → 맑은 고딕 순으로 떨어진다.
글자 모양만 조금 달라질 뿐 레이아웃은 유지된다.

---
지도교수 송민섭 · Hanyang University, Department of Nuclear Engineering
