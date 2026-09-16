/* 그림 칸에 viewBox 높이를 맞춘다.
 *   node figfit.js <슬러그> [ko|en]
 *
 * `.fig svg` 는 width:100%; height:auto 라서 viewBox 비율이 곧 그림 높이다.
 * 비율이 칸보다 납작하면 위아래에 빈 띠가 남고(check.js 가 잡는다), 반대로 너무 길면
 * flex 가 줄여 버려서 같은 12 px 라벨이 다른 장보다 작게 나온다. 둘 다 눈에 띈다.
 *
 * 그래서 인쇄 모드로 전 장을 펼쳐 놓고 칸 높이를 실제로 재서, 각 장이 써야 할
 * viewBox 높이를 계산해 준다. 권장값과 5 % 넘게 어긋난 장만 표시한다.
 */
const path = require('path');
const { chromium } = require('playwright-core');
const { findChromium } = require('./browser');

const slug = process.argv[2];
const lang = process.argv[3] || 'ko';
if (!slug) { console.log('사용법: node figfit.js <슬러그> [ko|en]'); process.exit(1); }

(async () => {
  const file = path.resolve(__dirname, '..', 'docs', slug + '.html');
  const b = await chromium.launch(findChromium());
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  await p.goto('file://' + file + '?print=1&lang=' + lang);
  await p.waitForFunction(() => document.documentElement.hasAttribute('data-print-ready'),
                          { timeout: 30000 });

  const rows = await p.evaluate(() => {
    const out = [];
    document.querySelectorAll('.sheet').forEach((sh, i) => {
      const sl = sh.querySelector('.slide'); if (!sl) return;
      const body = sl.querySelector('.body'), svg = sl.querySelector('.fig svg');
      if (!body || !svg) return;
      const bb = body.getBoundingClientRect(), sv = svg.getBoundingClientRect();
      const vb = (svg.getAttribute('viewBox') || '').split(/\s+/).map(Number);
      out.push({ n: i + 1, vbW: vb[2], vbH: vb[3], svgW: sv.width,
                 bodyH: bb.height, svgH: sv.height });
    });
    return out;
  });
  await b.close();

  console.log(`\n── ${slug} · ${lang} · 그림 ${rows.length}개`);
  let bad = 0;
  rows.forEach(r => {
    const k = r.svgW / r.vbW;                 /* 화면 px 당 viewBox 단위 */
    const want = Math.round(r.bodyH / k);     /* 칸을 꽉 채우는 viewBox 높이 */
    const off = (r.vbH - want) / want;
    const mark = Math.abs(off) <= 0.05 ? '   ' : (off < 0 ? ' ↑ ' : ' ↓ ');
    if (Math.abs(off) > 0.05) bad++;
    else return;
    console.log(`  ${String(r.n).padStart(3)}${mark}viewBox ${r.vbW}×${r.vbH}` +
                `  →  ${r.vbW}×${want}` +
                `   (칸 ${Math.round(r.bodyH)}px · 지금 ${Math.round(r.svgH)}px)`);
  });
  console.log(bad ? `\n  ${bad}개가 5 % 넘게 어긋남 — ↑ 는 키우고 ↓ 는 줄인다`
                  : '\n  전부 칸에 맞음');
})();
