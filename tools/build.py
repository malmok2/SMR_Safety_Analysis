#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""덱을 굽고 목차 페이지를 만든다.

    python3 tools/build.py            전부
    python3 tools/build.py <슬러그>    그 덱만

구조
    src/common/        모든 덱이 공유하는 머리·엔진·부트
    src/decks/<슬러그>/  deck.conf + 슬라이드 소스(파일명 사전순 = 슬라이드 순서)
    src/course.conf    과목 정보 — 목차 페이지가 쓴다
    src/index.tpl.html 목차 페이지 틀
    src/fonts.b64.css  심는 글꼴 (tools/fonts.py 가 만든다)

한 덱은 이렇게 만들어진다
    common/00_head + common/01_engine + decks/<슬러그>/*.html + common/99_boot
    → /*@FONTS@*/ 자리에 글꼴, <!--DECK--> 자리에 덱 정보를 꽂는다
    → docs/<슬러그>.html (한국어로 열림) · docs/<슬러그>.en.html (영어로 열림)
"""
import glob, io, json, os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, DOCS = os.path.join(ROOT, 'src'), os.path.join(ROOT, 'docs')

def conf(path):
    """key = value 한 줄씩. # 은 주석."""
    d = {}
    for line in io.open(path, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        d[k.strip()] = v.strip()
    return d

def read(*p):
    return io.open(os.path.join(*p), encoding='utf-8').read()

def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))

def build_deck(slug, fonts):
    d = os.path.join(SRC, 'decks', slug)
    cfg = conf(os.path.join(d, 'deck.conf'))
    parts = [read(SRC, 'common', '00_head.html'), read(SRC, 'common', '01_engine.html')]
    slides = sorted(f for f in glob.glob(os.path.join(d, '*.html')))
    parts += [io.open(f, encoding='utf-8').read() for f in slides]
    parts.append(read(SRC, 'common', '99_boot.html'))
    html = ''.join(parts)

    n = html.count('S({')
    deck = {'slug': slug, 'titleKo': cfg['title_ko'], 'titleEn': cfg['title_en']}
    # 첫 번째 하나만 바꾼다 — 소스 주석에 같은 글자가 들어 있어도 망가지지 않게
    html = html.replace('/*@FONTS@*/', fonts, 1)
    html = html.replace('<!--DECK-->',
                        '<script>window.DECK=%s</script>' % json.dumps(deck, ensure_ascii=False), 1)

    ko = os.path.join(DOCS, slug + '.html')
    io.open(ko, 'w', encoding='utf-8').write(html)
    en = os.path.join(DOCS, slug + '.en.html')
    io.open(en, 'w', encoding='utf-8').write(
        html.replace('<!--LANGDEF-->', '<script>window.SMR_LANG="en"</script>', 1))
    print('  %-42s %2d장  %6.0f KB' % (slug, n, os.path.getsize(ko) / 1024))
    cfg.update(slug=slug, slides=n)
    return cfg

def build_index(decks, fonts):
    tpl = read(SRC, 'index.tpl.html')
    course = conf(os.path.join(SRC, 'course.conf'))
    tokens = re.search(r'/\*@TOKENS-START@\*/([\s\S]*?)/\*@TOKENS-END@\*/',
                       read(SRC, 'common', '00_head.html'))
    cards = []
    for c in decks:
        cards.append(
            '  <div class="card">\n'
            '    <div class="wk">%s주차</div>\n'
            '    <div class="body">\n'
            '      <div class="t">%s</div>\n'
            '      <div class="te">%s</div>\n'
            '      <div class="lead">%s</div>\n'
            '      <div class="links">\n'
            '        <a class="go" href="%s.html">슬라이드 열기</a>\n'
            '        <a href="%s.en.html">Slides (English)</a>\n'
            '        <a href="%s.pdf">PDF</a>\n'
            '        <a href="%s.en.pdf">PDF (English)</a>\n'
            '      </div>\n'
            '      <div class="n">%d장 · %s</div>\n'
            '    </div>\n'
            '  </div>'
            % (esc(c.get('week', '')), esc(c['title_ko']), esc(c['title_en']),
               esc(c.get('lead_ko', '')), c['slug'], c['slug'], c['slug'], c['slug'],
               c['slides'], esc(c.get('date', ''))))
    out = tpl.replace('/*@FONTS@*/', fonts, 1).replace('/*@TOKENS@*/', tokens.group(1).strip(), 1)
    out = out.replace('<!--CARDS-->', '\n'.join(cards), 1)
    course['built'] = datetime.date.today().isoformat()
    for k, v in course.items():
        out = out.replace('{{%s}}' % k, esc(v))
    p = os.path.join(DOCS, 'index.html')
    io.open(p, 'w', encoding='utf-8').write(out)
    print('  %-42s 덱 %d개 %6.0f KB' % ('index.html (목차)', len(decks), os.path.getsize(p) / 1024))

def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    fonts = read(SRC, 'fonts.b64.css')
    os.makedirs(DOCS, exist_ok=True)
    slugs = sorted(os.path.basename(d.rstrip('/'))
                   for d in glob.glob(os.path.join(SRC, 'decks', '*'))
                   if os.path.isdir(d))
    if not slugs:
        sys.exit('src/decks 가 비어 있다')
    built = [build_deck(s, fonts) for s in slugs if not only or s == only]
    if only and not built:
        sys.exit('그런 덱이 없다: ' + only)
    if not only:
        build_index(built, fonts)
    print('  검증:  cd tools && node check.js        PDF 굽기:  cd tools && node pdf.js')

if __name__ == '__main__':
    main()
