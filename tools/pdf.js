/* 덱마다 46장을 한 장 = 한 페이지짜리 PDF로 굽는다.
 *   node pdf.js                      모든 덱, ko·en 둘 다
 *   node pdf.js <슬러그>              그 덱만
 *   node pdf.js <슬러그> ko           한 언어만
 * 덱을 ?print=1&theme=light&lang=… 로 열면 46장이 지면에 펼쳐지고, 애니메이션은 3.4 초 뒤
 * 멎으면서 <html data-print-ready>가 붙는다. 그 신호를 기다렸다가 인쇄한다.
 * 지면은 배포·인쇄용이라 밝은 배경으로 굽는다. 어두운 판이 필요하면 theme=dark.
 * 결과: docs/<슬러그>.pdf · docs/<슬러그>.en.pdf — 목차 페이지의 링크와 같은 이름이다.
 */
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright-core');
const { spawnSync } = require('child_process');
const { findChromium } = require('./browser');

const ROOT = path.resolve(__dirname, '..');
const DOCS = path.join(ROOT, 'docs');

(async () => {
  const only = process.argv[2];
  const langs = process.argv[3] ? [process.argv[3]] : ['ko', 'en'];
  const slugs = fs.readdirSync(path.join(ROOT, 'src', 'decks'))
    .filter(s => fs.statSync(path.join(ROOT, 'src', 'decks', s)).isDirectory())
    .filter(s => !only || s === only).sort();
  if (!slugs.length) { console.error('그런 덱이 없다:', only); process.exit(1); }

  const made = [];

  const b = await chromium.launch(findChromium());
  for (const slug of slugs) {
    const deck = path.join(DOCS, slug + '.html');
    if (!fs.existsSync(deck)) { console.error(slug, '— 먼저 build.sh 를 돌릴 것'); continue; }
    for (const lang of langs) {
      const p = await b.newPage({ viewport: { width: 1400, height: 900 } });
      const errs = [];
      p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
      p.on('pageerror', e => errs.push('PAGEERROR: ' + e.message));

      await p.goto('file://' + deck + '?print=1&theme=light&lang=' + lang);
      await p.waitForSelector('html[data-print-ready]', { timeout: 90000 });

      const n = await p.evaluate(() => document.querySelectorAll('.sheet').length);
      const file = path.join(DOCS, slug + (lang === 'en' ? '.en' : '') + '.pdf');
      await p.pdf({ path: file, width: '1280px', height: '720px', printBackground: true,
                    margin: { top: 0, right: 0, bottom: 0, left: 0 } });

      const real = errs.filter(e => !/ERR_CERT|ERR_CONNECTION|ERR_NAME|ERR_TUNNEL|ERR_PROXY|fonts\.g|jsdelivr/i.test(e));
      console.log(`  ${path.basename(file).padEnd(46)} ${n}쪽  ${(fs.statSync(file).size / 1048576).toFixed(1)} MB`
                + (real.length ? `  ⚠ 오류 ${real.length}건` : ''));
      real.slice(0, 5).forEach(e => console.log('     -', e));
      made.push(file);
      await p.close();
    }
  }
  await b.close();

  /* 크로미움은 그림을 2배 해상도로 키워 무압축에 가깝게 넣는다. 사진이 있는 덱은 PDF 가
     스무 배로 불어나므로 곧바로 다시 눌러 준다. 사진이 없으면 아무 일도 일어나지 않는다. */
  if (made.length) {
    const r = spawnSync('python3', [path.join(__dirname, 'pdfshrink.py'), ...made],
                        { encoding: 'utf8' });
    if (r.status === 0) process.stdout.write(r.stdout);
    else console.log('  (pdfshrink 를 건너뜀 — pip install pikepdf Pillow 하면 PDF 가 작아진다)');
  }
})();
