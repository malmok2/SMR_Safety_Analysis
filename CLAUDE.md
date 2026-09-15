# SMR_Safety_Analysis — 운영 지침

한양대 원자력공학과 THINK Lab(지도교수 송민섭), 대학원 과목 **NUE4067 「소형모듈원자로 안전해석」**의
발표용 HTML 슬라이드 저장소다. 교재 `THINK Lab SMR 설계요건과 공학적안전설비 (Rev1.0).docx`(60쪽)를
브라우저에서 도는 46장 애니메이션 슬라이드로 옮긴 것이며, 여기서 계속 개정한다.
본문은 **한국어와 영어를 함께** 담고 있고(`L` 키), 배경은 **어두운 판과 밝은 판**을 오갈 수 있으며(`T` 키),
46장을 그대로 **PDF로 내려받을** 수 있다.

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
docs/index.html   빌드 산출물(한국어로 열림). 직접 고치지 말 것 — 항상 src를 고치고 다시 빌드한다
docs/index_en.html               같은 내용, 영어로 열림. build.sh 가 <!--LANGDEF--> 자리에
                                 window.SMR_LANG="en" 을 꽂아 함께 굽는다
docs/NUE4067_SMR_safety_ko.pdf   미리 구운 PDF(46쪽). tools/pdf.js 가 만든다
docs/NUE4067_SMR_safety_en.pdf
tools/browser.js  크로미움 실행 파일 탐색(CHROME_PATH → PLAYWRIGHT_BROWSERS_PATH → Chrome 채널)
tools/shot.js     Playwright 스크린샷 검증 도구
tools/check.js    46장을 한/영으로 전수 점검 — 콘솔 오류 · 번역 누락 · 토큰 찌꺼기 · 레이아웃 넘침
tools/pdf.js      docs/*.pdf 를 다시 굽는다
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
| `TX(ko,en)` | 현재 언어의 문자열. **init 안에서 JS로 만드는 글자는 전부 이걸 쓴다** |
| `tr(s)` | 문자열 속 `[[한국어\|\|English]]` 토큰을 현재 언어로 치환. `go()`가 알아서 부른다 |
| `setLang('en')` | 언어 전환. 현재 슬라이드를 다시 그리고 주소·localStorage에 남긴다 |
| `setTheme('light')` | 배경 전환. CSS 토큰만 갈아끼우므로 **다시 그리지 않는다** |

조작키: `←/→` `Space` `PageUp/Down` 이동 · `Home/End` · `O` 개요 · `L` 한/영 · `T` 배경 · `P` 인쇄·PDF ·
`R` 재생 · `F` 전체화면 · `Esc`. 화면 왼쪽 28 % 클릭은 뒤로, 나머지는 앞으로.

슬라이드 등록이 끝난 뒤 `99_wrap.html` 끝에서 **`boot()`** 를 부른다. `boot()`이 언어를 읽고
평소에는 `buildOv(); go(0)`, 주소에 `?print=1` 이 있으면 `buildPrint()` 를 부른다.

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

### 그림의 가로세로비 — 죽은 띠가 생기는 자리

`.fig svg`는 `width:100%; height:auto`다. 그래서 **그려 넣을 칸의 비율보다 납작한 viewBox를 쓰면
위아래로 빈 띠가 남는다.** 폭은 이미 꽉 차 있으므로 그림을 키우는 방법은 **viewBox 높이를 키우고
내용을 다시 앉히는 것뿐**이다. 비율을 그대로 둔 채 크기만 키우는 건 아무 효과가 없다.

칸 폭은 두 가지뿐이다.

```
.body > .fig 만         → 1172 px      (전폭)
.body > .fig + .side    →  816 px      (.side 가 330 px + 여백 26)
```

**viewBox 폭을 칸 폭에 맞춘다.** 816 칸에 1120 폭 viewBox를 넣으면 0.73배로 축소되어
`.lbl` 12 px 가 화면에서 8.8 px 로 나온다. 다른 슬라이드의 12 px 라벨과 나란히 놓이면 확연히 작다.
`.side`가 있는 슬라이드는 viewBox 폭을 **780~820**으로 잡는다.

높이는 `viewBox폭 × 본문높이 / 칸폭 × 0.92` 정도가 적당하다. `tools/check.js`가 80 % 미만을 잡아 준다.

### 두 가지 배경

`:root[data-theme="light"]`가 같은 토큰을 다시 정의한다. **색은 반드시 토큰으로 쓴다** —
`#fff` 같은 값을 직접 넣으면 한쪽 배경에서 반드시 깨진다. 파생 토큰이 넷 더 있다.

```
--on-accent   강조색으로 꽉 채운 면 위에 얹는 글자 (다크 #071018 / 라이트 #FFFFFF)
--hot-2       과열 — --hot 보다 한 단계 위
--dead        무력화된 패널 (후쿠시마 모드)
--bubble      수조 기포
--act --veil  눌린 버튼 바탕 · 개요 화면 덮개
```

라이트의 강조 4색은 **흰 바탕에서 WCAG AA(4.5:1)를 넘도록** 어둡게 다시 잡았다
(`--cool #0B7FA8` · `--hot #C1440E` · `--ok #17795A` · `--amber #8A6100`).
색이 지는 의미는 두 배경에서 같다. 밝기만 뒤집었을 뿐이다.

발표는 다크가 기본, **인쇄·PDF는 라이트가 기본**이다(학생이 46쪽을 인쇄할 수 있어야 한다).

주요 클래스: `.rail` `h2.t`(제목) `ul.b`(상단 불릿) `.body`+`.fig`/`.side`(2단) `.readout`(.hi/.warn/.good)
`.ctl`(슬라이더) `.btn` `table.d` `.formula` `.div`(섹션 표지) `.cover` `.src`(출처) `.tag` `.num`

---

## 4. 한국어 · 영어

한 파일에 두 언어가 **나란히** 들어 있다. 별도 번역 파일을 만들지 않는다 — 수치를 고칠 때
양쪽이 같은 줄에 보여야 한쪽만 낡는 일이 없다.

### 파일이 둘이다

`index.html`은 한국어로, `index_en.html`은 영어로 열린다. 내용은 같고 기본 언어만 다르다 —
받는 사람이 아무것도 누르지 않아도 제 언어로 보게 하려는 것이다. 우선순위는

```
?lang=  >  window.SMR_LANG(파일의 기본값)  >  localStorage  >  ko
```

파일의 기본값이 기억된 선택보다 세다. 영문판을 건넸는데 예전에 한국어를 본 적이 있다고
한국어로 열리면 안 되기 때문이다.

### 마크업 안의 글자 — 토큰

```html
<li>[[붕괴열 <b>비율</b>은 노심 크기와 거의 무관||The decay heat <b>fraction</b> barely depends on core size]]</li>
```

`go()`가 슬라이드를 그리기 직전에 `tr()`로 치환한다. `html` · `src` · `ov` · `tag` · `SECT()` 의
문자열이 모두 이 경로를 지나므로, SVG `<text>` 안이든 표 칸 안이든 똑같이 동작한다.

- 토큰은 **문장 단위**로 건다. 태그를 사이에 두고 잘라 붙이면 영어 어순이 망가진다.
- **토큰 안에 토큰을 넣지 말 것.** 정규식이 non-greedy라 안쪽에서 끊긴다. 빌드가 개수를 세고,
  `tools/check.js`가 화면에 남은 `[[` `||` `]]` 찌꺼기를 잡는다.
- 영문에 `→ ← ① “ ”` 같은 글자를 쓸 때는 `&#8594;` `&#8592;` `&#9312;` `&#8220;` `&#8221;` 로 쓴다.
- 토큰이 태그 경계를 삼키지 않게 한다. `>[[가||A]]</span>` 가 옳고 `[[>가</span>||>A</span>]]` 는 피한다.

### init 안에서 JS로 만드는 글자 — `TX()`

`init()`이 `insertAdjacentHTML`·`textContent`로 넣는 글자는 `tr()`을 거치지 않는다. 반드시 `TX()`를 쓴다.

```js
el.querySelector('#lp-drv').textContent = TX('펌프','Pumps');
const B=[[8,16, TX('고압안전주입 (HPSI) · CMT','High-pressure injection (HPSI) · CMT'), 'var(--cool)']];
```

축 라벨처럼 **함수가 마크업을 통째로 만들어 돌려주는 경우**에는 그 함수가 `return tr(g)` 하게 하고
안에서는 토큰을 그대로 써도 된다(`20_economics.html`의 `ecAxes()`가 그 예).

`TX`라는 이름을 쓰는 이유 — 슬라이드 코드가 `T`를 온도·시간 변수로 이미 쓰고 있어서 가려진다.

### 영문 용어

NRC·IAEA 표기를 따른다. 기본안전기능 = fundamental safety function, 심층방어 = defence in depth,
단일고장기준 = single failure criterion, 정지여유도 = shutdown margin, 잔열제거 = residual heat removal,
붕괴열 = decay heat, 자연순환 = natural circulation, 공학적안전설비 = engineered safety features.

영문은 한국어보다 길어지기 쉽다. 표와 인용문이 넘치면 **문장을 줄인다** — 글자 크기를 줄이지 않는다.
넘침은 `tools/check.js`가 잡아 준다.

---

## 5. PDF · 인쇄

주소에 `?print=1` 을 붙이거나 `P` 키를 누르면 46장이 한 지면에 한 장씩 펼쳐진다(`buildPrint()`).

- 무대 대신 `.sheet` 46개를 만들고 각 슬라이드의 `init()`을 **한 번씩** 부른다.
- 이때 엔진의 `FREEZE` 가 3.4초로 설정되어 모든 `raf()`가 그 시점에 멎는다. 그래서 인쇄본은
  애니메이션이 **끝난 장면**으로 굳는다. 버튼으로 켜는 상태는 기본값으로 나온다.
- 멎으면 `<html data-print-ready>` 가 붙는다. `tools/pdf.js`는 이 신호를 기다렸다가 인쇄한다.
- 지면은 `@page{size:1280px 720px;margin:0}` — 슬라이드와 1:1이다. 배율을 건드리지 않는다.
- 인쇄 모드는 **라이트 배경이 기본**이다. 어두운 판이 필요하면 `?print=1&theme=dark`.

```bash
cd tools && node pdf.js          # ko·en 둘 다 → docs/NUE4067_SMR_safety_{ko,en}.pdf
node pdf.js ko                   # 한 언어만
```

**슬라이드를 고쳤으면 PDF를 다시 굽고 같이 커밋한다.** 안 그러면 공개 링크의 PDF가 낡는다.

---

## 6. 반드시 지킬 것

1. **Web Animations API로 SVG 기하 속성을 애니메이션하지 말 것.**
   `<g>`의 `transform`은 통째로 날아가 요소가 원점으로 튀고, `<line>`의 `x1 y1 x2 y2`는
   Chrome에서 CSS 속성이 아니라 **조용히 무시된다**(4장 300 MWe 경계선이 v1.0 내내 안 보였다).
   움직여야 하면 래퍼 `<g>`를 하나 더 두거나, `opacity`·`stroke-dashoffset`만 애니메이션한다.
   `rect`의 `width`·`height`, `circle`의 `cx cy r`은 CSS 기하 속성이라 동작한다.
2. **단일 파일을 유지한다.** 외부 이미지·JS·CSS 금지. 그림은 전부 인라인 SVG로 그린다.
   유일한 외부 자원은 Google Fonts(IBM Plex Sans KR)이고, 오프라인이면 Pretendard → 맑은 고딕으로 폴백된다.
   **강의실에 인터넷이 없어도 깨지지 않아야 한다**가 기준이다.
3. **타이머는 `raf()`로만 만든다.** `setInterval`이나 맨 `requestAnimationFrame`은 슬라이드를 떠나도 계속 돌아
   누수·중복 애니메이션을 만든다.
4. **수치는 교재와 일치시킨다.** 붕괴열·자연순환·SDM·격납 압력의 계수는 교재 본문 값이다. 임의로 바꾸지 않는다.
5. **인허가 현황은 낡는다.** `50_issues_defence.html`의 타임라인·현황은 2026-09 기준이다. 반년마다 확인한다.
6. **색은 토큰으로만 쓴다.** `#fff`·`#071018` 같은 값을 SVG에 직접 넣으면 라이트 배경에서 깨진다.
   마땅한 토큰이 없으면 `00_head.html`에 **두 배경 모두**를 정의하고 쓴다.
7. **글자를 새로 넣으면 영문도 같이 넣는다.** 한국어만 넣으면 영문판에 한글이 그대로 남는다 —
   `tools/check.js`가 잡지만, 잡히기 전에 넣는 것이 맞다.
8. **SVG 경로를 `Z`로 닫을 때 대각선이 생기는지 본다.** 유로를 그리는 `<path>`를 닫으면 끝점에서
   시작점으로 직선이 하나 그어진다. 37장에서 그 대각선이 노심 위를 가로질러 삼각형을 만들었다.
   순환 경로는 닫지 말고 양 끝을 노심 옆면에서 끝낸다.
9. **`raf()`의 경과시간은 0 아래로 내려가지 않는다.** 첫 프레임의 타임스탬프가 `t0`보다 이를 수 있어
   엔진에서 막아 두었다. `log`·`pow`를 쓰는 슬라이드가 NaN으로 깨지던 문제였다.

---

## 7. 검증

```bash
cd tools && npm install playwright-core      # 최초 1회
node check.js                                # 전수 점검 — 이것부터 돌린다
node shot.js "../docs/index.html" "1,16,23,36"   # 슬라이드 번호 지정, 생략하면 전수
```

`check.js`는 46장을 **한국어와 영어로 각각** 넘기며 네 가지를 센다. 넷 다 0이어야 한다.

```
console errors: 0          콘솔 오류(폰트 요청 실패는 걸러냈다)
영문판에 남은 한글: 0        번역 누락
화면에 남은 토큰 찌꺼기: 0    [[ || ]] 가 화면에 보이면 토큰이 깨진 것
무대 밖으로 넘친 요소: 0      1280×720 밖으로 나간 글자 — 영문이 길어질 때 잘 생긴다
제목이 두 줄로 흐른 슬라이드: 0   한 줄이 기준. 두 줄이 되면 본문이 43 px 밀린다
그림이 본문의 80 % 미만: 0      viewBox 비율이 칸보다 납작하다는 뜻(위 3절)
SVG 글자 충돌·이탈: 0        <text> 끼리 겹치거나 그림 밖으로 나간 것
index_en.html 이 영어로 열림: 예
```

마지막 항목은 인쇄 모드에서 46장을 한 번에 펼쳐 놓고 재므로 한/영 두 번에 12초면 끝난다.
**이 검사가 없던 동안 겹침 11곳이 그대로 나갔다.** HTML 요소만 재는 것으로는 부족하다.

`shot.js`는 `shot_N.png`를 남긴다.
**Google Fonts 요청 실패(`ERR_CONNECTION_RESET` · `ERR_CERT_AUTHORITY_INVALID`)는 오프라인 환경의
정상 동작이다.** 그 외 오류는 고친다.

손으로 볼 때의 최소 확인: 46장 전부 넘어가는가 · 글자가 서로 겹치지 않는가 · 슬라이더를 끝까지 밀어도
숫자가 NaN이나 음수로 깨지지 않는가 · `L`로 언어를 바꿔도 레이아웃이 버티는가.

---

## 8. 개정·커밋

- 한 커밋 = 한 가지 변경. `src/`와 `docs/index.html`을 **같이** 커밋한다(빌드 산출물도 추적한다 —
  GitHub Pages가 `docs/`를 그대로 서빙하므로, 커밋하지 않으면 공개 링크가 낡는다).
- 슬라이드 내용이 바뀌었으면 `docs/*.pdf`도 다시 굽고 같은 커밋에 넣는다.
- 커밋 메시지는 한국어로, 무엇이 왜 바뀌었는지 한 줄. 예: `SDM 요구선 라벨이 막대 뒤로 들어가 우측 여백으로 이동`
- 슬라이드를 더하거나 빼면 `CHANGELOG.md`에 한 줄 남긴다.
- 강의에 실제로 쓴 판은 태그를 단다: `git tag 2026-2-w2 && git push --tags`.
