/* 덱 점검 — 46장을 한/영으로 모두 넘겨보고
 *   · 콘솔 오류
 *   · 영문판에 남은 한글(번역 누락)
 *   · 무대(1280×720) 밖으로 삐져나온 요소
 * 를 보고한다.  node check.js [../docs/index.html]
 * 폰트 요청 실패(ERR_CONNECTION_RESET / ERR_CERT)는 오프라인의 정상 동작이라 걸러낸다.
 */
const path = require('path');
const { chromium } = require('playwright-core');
const { findChromium } = require('./browser');

const HANGUL = /[가-힣]/;

/* 인쇄 모드(46장 동시 렌더 · 3.4초에 정지)에서 SVG 글자끼리 겹치는지, 그림 밖으로 나갔는지 본다.
   화면 모드로 한 장씩 보려면 46장 × 대기시간이 들지만, 인쇄 모드는 한 번에 끝난다. */
async function svgScan(page, file, lang) {
  await page.goto('file://' + file + '?print=1&lang=' + lang);
  await page.waitForSelector('html[data-print-ready]', { timeout: 90000 });
  return page.evaluate(() => {
    const eff = e => {                       // 조상까지 곱한 실효 투명도
      let o = 1, n = e;
      while (n && n !== document.body) {
        const s = getComputedStyle(n);
        o *= parseFloat(s.opacity || 1);
        if (s.display === 'none' || s.visibility === 'hidden') return 0;
        n = n.parentElement || n.parentNode;
      }
      return o;
    };
    const out = [];
    document.querySelectorAll('.sheet').forEach((sh, idx) => {
      const n = idx + 1;
      const box = [...sh.querySelectorAll('svg text')]
        .filter(t => eff(t) > 0.08)
        .map(t => ({ r: t.getBoundingClientRect(), s: (t.textContent || '').trim(),
                     v: t.ownerSVGElement.getBoundingClientRect() }))
        .filter(x => x.r.width > 0 && x.s);
      for (let i = 0; i < box.length; i++) {
        const A = box[i].r, V = box[i].v;
        if (A.right > V.right + 1 || A.left < V.left - 1 || A.bottom > V.bottom + 1 || A.top < V.top - 1)
          out.push({ n, kind: '그림 밖', a: box[i].s, b: '' });
        for (let j = i + 1; j < box.length; j++) {
          const B = box[j].r;
          const w = Math.min(A.right, B.right) - Math.max(A.left, B.left);
          const h = Math.min(A.bottom, B.bottom) - Math.max(A.top, B.top);
          if (w > 2.5 && h > 2.5) out.push({ n, kind: '겹침', a: box[i].s, b: box[j].s,
                                             w: Math.round(w), h: Math.round(h) });
        }
      }
    });
    return out;
  });
}


(async () => {
  const file = path.resolve(process.argv[2] || path.join(__dirname, '..', 'docs', 'index.html'));
  const b = await chromium.launch(findChromium());
  const p = await b.newPage({ viewport: { width: 1440, height: 810 } });

  let at = 0;
  const errs = [];
  const skip = t => /ERR_CERT|ERR_CONNECTION|ERR_NAME|ERR_TUNNEL|ERR_PROXY|fonts\.g|jsdelivr/i.test(t);
  p.on('console', m => { if (m.type() === 'error' && !skip(m.text())) errs.push([at, m.text()]); });
  p.on('pageerror', e => errs.push([at, 'PAGEERROR: ' + e.message]));

  await p.goto('file://' + file);
  await p.waitForTimeout(1000);
  const n = await p.evaluate(() => D.length);

  const left = [], over = [], junk = [];
  for (const lang of ['ko', 'en']) {
    await p.evaluate(l => setLang(l), lang);
    for (let i = 0; i < n; i++) {
      at = i + 1;
      await p.evaluate(i => { cur = -1; go(i); }, i);
      await p.waitForTimeout(260);
      const r = await p.evaluate(() => {
        const s = document.querySelector('.slide');
        const txt = [];
        const walk = document.createTreeWalker(s, NodeFilter.SHOW_TEXT);
        let t; while ((t = walk.nextNode())) { const v = t.nodeValue.trim(); if (v) txt.push(v); }
        const box = s.getBoundingClientRect();
        const spill = [];
        s.querySelectorAll('h2,li,p,td,th,.readout,.btn,.src,.formula,blockquote').forEach(e => {
          const r = e.getBoundingClientRect();
          if (r.width && (r.right > box.right + 1 || r.bottom > box.bottom + 1 || r.left < box.left - 1))
            spill.push((e.textContent || '').trim().slice(0, 40));
        });
        return { txt, spill };
      });
      if (lang === 'en') r.txt.filter(t => HANGUL.test(t)).forEach(t => left.push([i + 1, t]));
      r.txt.filter(t => /\[\[|\]\]|\|\|/.test(t)).forEach(t => junk.push([lang, i + 1, t]));
      r.spill.forEach(t => over.push([lang, i + 1, t]));
    }
  }

  const svg = [];
  for (const lang of ['ko', 'en'])
    (await svgScan(p, file, lang)).forEach(x => svg.push([lang, x]));

  console.log('slides:', n);
  console.log('console errors:', errs.length);
  errs.slice(0, 20).forEach(e => console.log('   slide', e[0], '·', e[1].slice(0, 120)));
  console.log('영문판에 남은 한글:', left.length);
  left.slice(0, 400).forEach(e => console.log('   slide', e[0], '·', e[1].slice(0, 90)));
  console.log('화면에 남은 토큰 찌꺼기:', junk.length);
  junk.slice(0, 20).forEach(e => console.log('   ' + e[0], 'slide', e[1], '·', e[2].slice(0, 90)));
  console.log('무대 밖으로 넘친 요소:', over.length);
  over.slice(0, 30).forEach(e => console.log('   ' + e[0], 'slide', e[1], '·', e[2]));
  console.log('SVG 글자 충돌·이탈:', svg.length);
  svg.slice(0, 40).forEach(([l, x]) => console.log('   ' + l, 'slide', String(x.n).padStart(2),
    x.kind, '[' + x.a.slice(0, 44) + ']', x.b ? '× [' + x.b.slice(0, 44) + ']  ' + x.w + '×' + x.h + 'px' : ''));
  await b.close();
  process.exit(errs.length || left.length || junk.length || over.length || svg.length ? 1 : 0);
})();
