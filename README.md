# SMR_Safety_Analysis

한양대 원자력공학과 **THINK Lab** · 대학원 「소형모듈원자로 안전해석」(NUE4067) 강의 자료.

**한 학기치를 주차별로 쌓아 간다.** 주차마다 브라우저에서 도는 애니메이션 슬라이드 한 벌과
인쇄용 PDF 를 만들고, 첫 화면이 그 목록이다. 한국어와 영어를 버튼 하나로 오간다.

**▶ 강의 목차: https://malmok2.github.io/SMR_Safety_Analysis/**

| 주차 | 자료 |
|---|---|
| 02~03 | SMR 설계요건과 공학적안전설비 — 46장 · [슬라이드](https://malmok2.github.io/SMR_Safety_Analysis/w02-03_smr-design-requirements.html) · [English](https://malmok2.github.io/SMR_Safety_Analysis/w02-03_smr-design-requirements.en.html) · [PDF](https://malmok2.github.io/SMR_Safety_Analysis/w02-03_smr-design-requirements.pdf) |

## 무엇이 들어 있나 (02~03주차)

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

화면 아래 **조작 막대**에 `한국어 / English` · 배경 전환 · `PDF ↓` 버튼이 늘 떠 있다.
`F` 전체화면으로 들어가면 막대가 사라지고 슬라이드가 화면을 다 쓴다.

키보드: `←` `→` `Space` 이동 · `O` 전체 개요 · `L` 한/영 · `T` 배경 · `P` 인쇄·PDF ·
`R` 애니메이션 다시재생 · `F` 전체화면 · `Esc` 닫기.
화면 왼쪽 28 %를 클릭하면 뒤로, 나머지는 앞으로.

## 한국어 · 영어

**막대의 `한국어 / English` 버튼**을 누르면 그 자리에서 바뀐다(`L` 키도 같다).
번역은 소스 안에 `[[한국어||English]]` 형태로 나란히 들어 있어 한쪽만 낡지 않는다.

파일을 그대로 건네줄 때를 위해 영어로 열리는 판도 함께 굽는다 — `<슬러그>.en.html`.

## 배경

발표는 **어두운 배경**이 기본이다. 조명을 낮춘 강의실에서 대비가 가장 크고, 이 덱은 색이
의미를 지고 있어서(냉각재 파랑 · 열 주황 · 피동 초록 · 규제 조문 노랑) 어두운 바탕이 그 구분을 살린다.
강의실이 밝으면 `T` 키로 **밝은 배경**으로 바꾼다. **인쇄와 PDF 는 밝은 배경이 기본**이다.

## PDF

주차마다 두 벌을 미리 구워 둔다 — `<슬러그>.pdf` · `<슬러그>.en.pdf`. 46쪽, 한 쪽이 슬라이드 한 장.
브라우저에서 직접 뽑으려면 `P` 키 → `Ctrl+P`.

## 빌드

```bash
./build.sh                    # 전부 (윈도우: .\build.ps1)
./build.sh <슬러그>            # 그 덱만
cd tools && npm install playwright-core   # 최초 1회
node check.js                 # 모든 덱 전수 점검 — 아홉 가지
node pdf.js                   # PDF 다시 굽기
python3 tools/fonts.py        # 새 글자를 넣었을 때 글꼴 서브셋 갱신
```

**`docs/`를 직접 고치지 말 것** — 다음 빌드에 덮인다. 항상 `src/`를 고친다.
주차 추가 방법·엔진 API·시각 규약은 [`CLAUDE.md`](CLAUDE.md)에 있다.

## 폰트

본문은 **Pretendard**, 라벨·수치의 라틴은 **IBM Plex Mono**다. 둘 다 **파일 안에 심어 두었다** —
덱에 실제로 쓰인 글자만 남긴 서브셋(389 KB)이라, 인터넷이 없어도 글꼴까지 그대로 나온다.
IBM Plex Mono에는 한글이 없으므로 모노 문맥의 한글도 Pretendard로 그린다.

글꼴 원본은 둘 다 SIL Open Font License 1.1이다.
Pretendard © 길형진(orioncactus) · IBM Plex Mono © IBM Corp.

---
지도교수 송민섭 · Hanyang University, Department of Nuclear Engineering
