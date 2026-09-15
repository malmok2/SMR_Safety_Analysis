# SMR_Safety_Analysis — 운영 지침

한양대 원자력공학과 THINK Lab(지도교수 송민섭), 대학원 과목 **NUE4067 「소형모듈원자로 안전해석」**의
발표용 HTML 슬라이드 저장소다. 교재 `THINK Lab SMR 설계요건과 공학적안전설비 (Rev1.0).docx`(60쪽)를
브라우저에서 도는 46장 애니메이션 슬라이드로 옮긴 것이며, 여기서 계속 개정한다.

교재 원본과 그림 소스는 이 저장소에 없다. `C:\Claude\Documents\THINK Lab SMR 설계요건과 공학적안전설비 Rev1.0`
(별도 저장소 `malmok2/Documents`)에 있다. 수치를 바꿔야 하면 **교재가 기준**이고, 양쪽을 같이 고친다.

---

## 1. 구조

```
src/          슬라이드 소스 12개. 파일명 사전순 = 슬라이드 순서
  00_head.html              <head> · CSS 토큰 · 컴포넌트 클래스
  01_engine.html            덱 엔진(슬라이드 등록·내비·애니메이션 프리미티브)
  10_cover_roadmap.html     표지 · 로드맵 · §01 도입
  20_economics.html         규모의 경제 · 4대 저감인자
  30_loop_integral.html     루프형 vs 일체형
  40_decayheat_natcirc.html §02 붕괴열 · 자연순환 · 열관성
  50_issues_defence.html    §03 쟁점·인허가 · §04 심층방어
  60_esf_categories.html    §05 단일고장 · GDC · Category A~D
  70_shutdown.html          §06 제어봉 · SDM
  80_rhr.html               §07 잔열제거
  90_eccs_containment.html  §08 안전주입 · §09 격납
  99_wrap.html              §10 정리 (끝에 buildOv(); go(0); 호출)
docs/index.html   빌드 산출물. 직접 고치지 말 것 — 항상 src를 고치고 다시 빌드한다
tools/shot.js     Playwright 스크린샷 검증 도구
build.sh / build.ps1
```

**빌드는 단순 연결이다.** `cat src/*.html > docs/index.html`. 그래서:

- 슬라이드를 **추가**하려면 새 `S({...})` 블록을 해당 절의 src 파일 안, 원하는 위치에 넣는다.
- 절 하나를 **통째로** 넣으려면 새 파일을 만들되 번호 접두사로 순서를 맞춘다(예: `45_something.html`).
- `docs/index.html`을 고치면 다음 빌드에 덮여 사라진다.

```bash
./build.sh          # 또는 윈도우: .\build.ps1
```
빌드가 끝나면 슬라이드 수를 출력한다. **46장이 기준값이다.** 숫자가 예상과 다르면 `S({` 를 빠뜨렸거나 중복한 것이다.

---

## 2. 엔진 API (`src/01_engine.html`)

```js
SECT('05 · 공학적안전설비')     // 여기부터 새 섹션. 개요 화면(O)과 레일 표시에 쓰인다
S({ html:`...`, init(el){ ... } })   // 슬라이드 하나. init은 이 슬라이드가 켜질 때마다 호출
```

`S()`의 `html`은 **슬라이드 본문만** 쓴다. 좌측 레일(섹션명·번호)과 하단 푸터는 `go()`가 붙인다.
`init(el)`의 `el`은 그 슬라이드의 DOM 루트다. **`document.querySelector`를 쓰지 말고 `el.querySelector`를 쓴다.**
슬라이드는 전환할 때마다 `innerHTML`로 새로 그려지므로, 전역에서 찾으면 죽은 노드를 잡는다.

프리미티브:

| 함수 | 하는 일 |
|---|---|
| `raf(fn)` | `fn(경과초, 타임스탬프)`를 매 프레임 호출. **슬라이드를 떠나면 자동으로 멈춘다**(CLEAN 등록). 타이머는 반드시 이걸로 만든다 |
| `flow(path, {n, color, r, speed})` | SVG `<path>` 위로 입자를 흘린다. 반환 객체의 `.speed`·`.on`·`.dir`을 바꾸면 실시간 반응 |
| `track(obj, key, get, k)` | 값을 목표치로 부드럽게 따라가게 한다(1차 지연) |
| `poly(pts)` | `[[x,y],…]` → `points` 문자열 |
| `decay(t)` | Way–Wigner 붕괴열 비율. `0.0622(t^-0.2 − (t+10^8)^-0.2)` |
| `rhoW(T)` | 물 밀도 `1006.0 − 0.2646T − 0.002424T²` (kg/m³, T는 °C) |
| `clamp` `lerp` `fmt` | 수치 유틸 |

조작키: `←/→` `Space` `PageUp/Down` 이동 · `Home/End` · `O` 개요 · `R` 재생 · `F` 전체화면 · `Esc`.
화면 왼쪽 28 % 클릭은 뒤로, 나머지는 앞으로.

---

## 3. 시각 규약 (`src/00_head.html`)

```
--ground #070E18   바탕(근흑 네이비)      --cool  #4CC9F0  강조 = 냉각재
--panel  #0E1B2C   패널면                 --hot   #FF7A45  열·노심·위험
--rule   #1E3450   미믹 라인              --ok    #5DD39E  피동·성공
--ink    #FFFFFF   본문                   --amber #FFC55C  규제 조문
--ink-2  #C9D9EC   보조 텍스트            --ink-3 #8FA8C6  라벨(캡션·단위) 전용
```

- **회색 글씨 금지.** 강의실 프로젝터에서 안 보인다. 보조 텍스트도 `--ink-2`(청백색)까지만.
  `--ink-3`은 축 라벨·단위·출처에만 쓴다.
- 색은 **의미**를 진다. 차가운 것은 `--cool`, 뜨거운 것은 `--hot`, 피동·성공은 `--ok`, 규제 조문은 `--amber`.
  장식으로 색을 쓰지 않는다.
- 본문은 **개조식**(~했음 / ~임 / ~됨). "~하였다 / ~한다" 종결형은 쓰지 않는다.
- 슬라이드마다 하단에 **출처·조건**을 단다(`.src`). 수치가 있으면 어디서 왔는지 반드시 밝힌다.
- 무대는 1280×720 고정이고 `transform: scale()`로 뷰포트에 맞춘다. **px로 배치해도 안전하다.**

주요 클래스: `.rail` `h2.t`(제목) `ul.b`(상단 불릿) `.body`+`.fig`/`.side`(2단) `.readout`(.hi/.warn/.good)
`.ctl`(슬라이더) `.btn` `table.d` `.formula` `.div`(섹션 표지) `.cover` `.src`(출처) `.tag` `.num`

---

## 4. 반드시 지킬 것

1. **Web Animations API로 SVG `<g>`의 `transform`을 애니메이션하지 말 것.**
   `transform` 속성이 통째로 날아가 요소가 원점으로 튄다(이 덱에서 실제로 겪었다).
   움직여야 하면 래퍼 `<g>`를 하나 더 두거나, `opacity`만 애니메이션한다.
2. **단일 파일을 유지한다.** 외부 이미지·JS·CSS 금지. 그림은 전부 인라인 SVG로 그린다.
   유일한 외부 자원은 Google Fonts(IBM Plex Sans KR)이고, 오프라인이면 Pretendard → 맑은 고딕으로 폴백된다.
   **강의실에 인터넷이 없어도 깨지지 않아야 한다**가 기준이다.
3. **타이머는 `raf()`로만 만든다.** `setInterval`이나 맨 `requestAnimationFrame`은 슬라이드를 떠나도 계속 돌아
   누수·중복 애니메이션을 만든다.
4. **수치는 교재와 일치시킨다.** 붕괴열·자연순환·SDM·격납 압력의 계수는 교재 본문 값이다. 임의로 바꾸지 않는다.
5. **인허가 현황은 낡는다.** `50_issues_defence.html`의 타임라인·현황은 2026-09 기준이다. 반년마다 확인한다.

---

## 5. 검증

```bash
cd tools && npm install playwright-core      # 최초 1회
node shot.js "../docs/index.html" "1,16,23,36"   # 슬라이드 번호 지정, 생략하면 전수
```
콘솔 오류와 슬라이드 수를 출력하고 `shot_N.png`를 남긴다.
**Google Fonts 요청 실패(`ERR_CONNECTION_RESET`) 1건은 오프라인 환경의 정상 동작이다.** 그 외 오류는 고친다.

손으로 볼 때의 최소 확인: 46장 전부 넘어가는가 · 글자가 서로 겹치지 않는가 · 슬라이더를 끝까지 밀어도
숫자가 NaN이나 음수로 깨지지 않는가.

---

## 6. 개정·커밋

- 한 커밋 = 한 가지 변경. `src/`와 `docs/index.html`을 **같이** 커밋한다(빌드 산출물도 추적한다 —
  GitHub Pages가 `docs/`를 그대로 서빙하므로, 커밋하지 않으면 공개 링크가 낡는다).
- 커밋 메시지는 한국어로, 무엇이 왜 바뀌었는지 한 줄. 예: `SDM 요구선 라벨이 막대 뒤로 들어가 우측 여백으로 이동`
- 슬라이드를 더하거나 빼면 `CHANGELOG.md`에 한 줄 남긴다.
- 강의에 실제로 쓴 판은 태그를 단다: `git tag 2026-2-w2 && git push --tags`.
