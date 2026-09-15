/* 슬라이드 렌더 검증.
 *   node shot.js ../docs/index.html            전수 캡처
 *   node shot.js ../docs/index.html 0,16,23    번호 지정(0부터)
 * 브라우저: 환경변수 CHROME_PATH 가 있으면 그것, 없으면 설치된 Chrome(channel).
 * 출력: shot_NN.png + 콘솔 오류 목록.
 *   Google Fonts 의 ERR_CONNECTION_RESET 1건은 오프라인일 때 정상이다.
 */
const path = require('path');
const { chromium } = require('playwright-core');
const { findChromium } = require('./browser');

(async () => {
  const file = path.resolve(process.argv[2] || '../docs/index.html');
  const only = process.argv[3] ? process.argv[3].split(',').map(Number) : null;

  const b = await chromium.launch(findChromium());
  const p = await b.newPage({ viewport: { width: 1440, height: 810 } });

  const errs = [];
  p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  p.on('pageerror', e => errs.push('PAGEERROR: ' + e.message));

  await p.goto('file://' + file);
  await p.waitForTimeout(1500);

  const n = await p.evaluate(() => D.length);
  console.log('slides:', n);

  for (let i = 0; i < n; i++) {
    if (only && !only.includes(i)) continue;
    await p.evaluate(i => go(i), i);
    await p.waitForTimeout(1600);
    await p.screenshot({ path: 'shot_' + String(i).padStart(2, '0') + '.png' });
  }

  console.log('ERRORS:', errs.length);
  errs.slice(0, 15).forEach(e => console.log(' -', e));
  await b.close();
})();
