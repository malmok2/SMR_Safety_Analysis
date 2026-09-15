/* 슬라이드 46장을 한 장 = 한 페이지짜리 PDF로 굽는다.
 *   node pdf.js                 ko·en 둘 다
 *   node pdf.js ko              한 언어만
 *   node pdf.js ko ../docs      출력 폴더 지정
 * 덱을 ?print=1&lang=… 로 열면 46장이 지면에 펼쳐지고, 애니메이션은 3.4 초 뒤
 * 멎으면서 <html data-print-ready>가 붙는다. 그 신호를 기다렸다가 인쇄한다.
 * 지면은 배포·인쇄용이라 <b>밝은 배경</b>으로 굽는다(?theme=light). 어두운 판이 필요하면 theme=dark.
 * 결과: <out>/NUE4067_SMR_safety_<lang>.pdf  — index.html 의 내려받기 링크와 같은 이름이다.
 */
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright-core');
const { findChromium } = require('./browser');

const DECK = path.resolve(__dirname, '..', 'docs', 'index.html');

(async () => {
  const langs = process.argv[2] ? [process.argv[2]] : ['ko', 'en'];
  const out = path.resolve(process.argv[3] || path.join(__dirname, '..', 'docs'));
  if (!fs.existsSync(DECK)) { console.error('덱이 없다:', DECK, '— 먼저 build.sh 를 돌릴 것'); process.exit(1); }

  const b = await chromium.launch(findChromium());
  for (const lang of langs) {
    const p = await b.newPage({ viewport: { width: 1400, height: 900 } });
    const errs = [];
    p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    p.on('pageerror', e => errs.push('PAGEERROR: ' + e.message));

    await p.goto('file://' + DECK + '?print=1&theme=light&lang=' + lang);
    await p.waitForSelector('html[data-print-ready]', { timeout: 90000 });

    const n = await p.evaluate(() => document.querySelectorAll('.sheet').length);
    const file = path.join(out, 'NUE4067_SMR_safety_' + lang + '.pdf');
    await p.pdf({ path: file, width: '1280px', height: '720px', printBackground: true,
                  margin: { top: 0, right: 0, bottom: 0, left: 0 } });

    const real = errs.filter(e => !/ERR_CERT|ERR_CONNECTION|ERR_NAME|ERR_TUNNEL|ERR_PROXY|fonts\.g|jsdelivr/i.test(e));
    console.log(`${lang}: ${n} pages → ${path.relative(process.cwd(), file)}`
              + ` (${(fs.statSync(file).size / 1048576).toFixed(1)} MB)`
              + (real.length ? `  ⚠ 오류 ${real.length}건` : ''));
    real.slice(0, 5).forEach(e => console.log('   -', e));
    await p.close();
  }
  await b.close();
})();
