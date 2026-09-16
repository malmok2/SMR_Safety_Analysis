#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""교재(docx)의 그림을 덱의 media/ 로 뽑는다.

    python3 tools/media.py <docx 경로> <슬러그>

교재의 화면 캡처와 실물 도면은 SVG 로 다시 그릴 수 없다. 그림 자체가 내용이므로
원본을 그대로 쓰되, 슬라이드에 앉히기 좋게 손을 본다.

  · 흰 여백을 잘라 낸다 — 캡처본은 바깥이 대부분 흰 종이라, 그대로 두면 칸 안에서
    그림이 작아지고 위아래에 흰 띠가 남는다.
  · 칸(최대 1172 px)의 두 배까지만 두고 그 위는 줄인다.
  · WebP 로 저장한다. 단일 파일 규칙 때문에 base64 로 심어야 하므로 용량이 곧 덱 크기다.

파일 이름은 교재의 그림 번호다 — f6_03.webp = 그림 6.3 → 슬라이드에서 PH({src:'f6_03'}).
"""
import io, os, re, sys, zipfile
from xml.etree import ElementTree as ET
from PIL import Image, ImageChops

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAXW, MAXH, Q = 1500, 1150, 84


def trim(im, thr=246):
    """가장자리의 흰 여백을 잘라 낸다. 안쪽 흰 바탕은 건드리지 않는다."""
    g = im.convert('L')
    bg = Image.new('L', g.size, 255)
    box = ImageChops.difference(g, bg).point(lambda v: 255 if v > 255 - thr else 0).getbbox()
    if not box:
        return im
    pad = 6                      # 잘라 낸 자리에 숨 쉴 틈은 남긴다
    x0, y0, x1, y1 = box
    box = (max(0, x0 - pad), max(0, y0 - pad),
           min(im.width, x1 + pad), min(im.height, y1 + pad))
    # 너무 많이 잘리면(오검출) 원본을 둔다
    if (box[2] - box[0]) * (box[3] - box[1]) < im.width * im.height * 0.15:
        return im
    return im.crop(box)


def main(docx, slug):
    out = os.path.join(ROOT, 'src', 'decks', slug, 'media')
    os.makedirs(out, exist_ok=True)
    z = zipfile.ZipFile(docx)
    rels = {c.get('Id'): c.get('Target')
            for c in ET.fromstring(z.read('word/_rels/document.xml.rels'))}
    body = ET.fromstring(z.read('word/document.xml')).find(W + 'body')
    ptext = lambda p: ''.join(t.text or '' for t in p.iter(W + 't'))

    pend, pairs = [], []
    for ch in body:
        if ch.tag != W + 'p':
            continue
        pend += [rels.get(b.get(R + 'embed') or b.get(R + 'link'))
                 for b in ch.iter(A + 'blip') if rels.get(b.get(R + 'embed') or b.get(R + 'link'))]
        txt = ptext(ch).strip()
        if txt and pend:
            pairs += [(m, txt) for m in pend]
            pend = []

    rx, seen, tot = re.compile(r'그림\s*(\d+)\.(\d+)'), {}, 0
    for m, cap in pairs:
        g = rx.search(cap)
        if not g:
            continue
        name = 'f%s_%02d' % (g.group(1), int(g.group(2)))
        while name in seen:
            name += 'b'
        seen[name] = m

    for name, m in sorted(seen.items()):
        im = Image.open(io.BytesIO(z.read('word/' + m)))
        if im.mode in ('P', 'LA'):
            im = im.convert('RGBA')
        if im.mode == 'RGBA':
            bg = Image.new('RGB', im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[-1])
            im = bg
        elif im.mode != 'RGB':
            im = im.convert('RGB')
        im = trim(im)
        if im.width > MAXW or im.height > MAXH:
            k = min(MAXW / im.width, MAXH / im.height)
            im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        p = os.path.join(out, name + '.webp')
        im.save(p, 'WEBP', quality=Q, method=6)
        kb = os.path.getsize(p) / 1024
        tot += kb
        print('  %-9s %4d x %-4d %7.1f KB' % (name, im.width, im.height, kb))
    print('  %d개 · 합계 %.0f KB (base64 로 심으면 %.0f KB)' % (len(seen), tot, tot * 4 / 3))
    print('  쓰지 않는 그림은 지울 것 — 전부 덱 파일 안에 들어간다')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
