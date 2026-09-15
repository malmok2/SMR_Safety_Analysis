#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""덱에 심을 글꼴 서브셋을 다시 만든다 → src/fonts.b64.css

   python3 tools/fonts.py

필요한 것
  pip install fonttools brotli        (brotli 가 없으면 woff2_compress 명령을 찾는다)
  인터넷 — Pretendard 와 IBM Plex Mono 원본을 GitHub 릴리스에서 받는다

무엇을 하나
  src/*.html 에 실제로 쓰인 글자만 남겨 굵기별로 서브셋하고 base64 로 박아 넣는다.
  그래서 강의실에 인터넷이 없어도 글꼴이 그대로 나온다.
  새 글자를 넣었는데 모양이 달라 보이면 서브셋에 없는 것이다 — 이 스크립트를 다시 돌린다.
  tools/check.js 가 서브셋에 없는 글자를 일러 준다.
"""
import base64, glob, io, os, shutil, subprocess, sys, tempfile, urllib.request, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRETENDARD = 'https://github.com/orioncactus/pretendard/releases/download/v1.3.9/Pretendard-1.3.9.zip'
PLEX = 'https://github.com/IBM/plex/releases/download/%40ibm%2Fplex-mono%401.1.0/ibm-plex-mono.zip'
SANS = [('Light', 300), ('Regular', 400), ('Medium', 500), ('SemiBold', 600), ('Bold', 700)]
MONO = [('Regular', 400), ('Medium', 500), ('SemiBold', 600), ('Bold', 700)]

def charset():
    ch = set()
    for f in sorted(glob.glob(os.path.join(ROOT, 'src', '*.html'))):
        ch |= set(io.open(f, encoding='utf-8').read())
    ch |= set('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    ch |= set(' .,:;·…—–-()[]{}<>/\\|!?\'"“”‘’%°±×÷≈≤≥→←↑↓∙*+=_#&@~^$')
    ch |= set('①②③④⑤⑥⑦⑧⑨⑩§¶†‡')
    ch |= set('ΔΣΩαβγδεθλμνπρστφχψω')
    return ''.join(sorted(c for c in ch if ord(c) >= 0x20))

def fetch(url, into):
    z = os.path.join(into, os.path.basename(url).split('?')[0] or 'f.zip')
    print('  받는 중', url.rsplit('/', 1)[-1])
    urllib.request.urlretrieve(url, z)
    with zipfile.ZipFile(z) as f:
        f.extractall(os.path.join(into, 'x'))
    return os.path.join(into, 'x')

def subset(src, out_base, text_file):
    """woff2 를 만들어 경로를 돌려준다. brotli 가 있으면 한 번에, 없으면 woff2_compress 로."""
    try:
        import brotli  # noqa: F401
        out = out_base + '.woff2'
        subprocess.run([sys.executable, '-m', 'fontTools.subset', src, '--text-file=' + text_file,
                        '--output-file=' + out, '--flavor=woff2', '--layout-features=*',
                        '--no-hinting'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return out
    except ImportError:
        if not shutil.which('woff2_compress'):
            sys.exit('brotli 도 woff2_compress 도 없다 — pip install brotli')
        tmp = out_base + os.path.splitext(src)[1]
        subprocess.run([sys.executable, '-m', 'fontTools.subset', src, '--text-file=' + text_file,
                        '--output-file=' + tmp, '--layout-features=*', '--no-hinting'],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['woff2_compress', tmp], check=True, stdout=subprocess.DEVNULL)
        return os.path.splitext(tmp)[0] + '.woff2'

def main():
    tmp = tempfile.mkdtemp(prefix='smrfonts-')
    txt = os.path.join(tmp, 'charset.txt')
    cs = charset()
    io.open(txt, 'w', encoding='utf-8').write(cs)
    io.open(os.path.join(ROOT, 'src', 'fonts.charset.txt'), 'w', encoding='utf-8').write(cs)
    print('서브셋 문자 %d자 (한글 %d자)'
          % (len(cs), sum(1 for c in cs if '가' <= c <= '힣')))

    pd = fetch(PRETENDARD, tmp)
    px = fetch(PLEX, tmp)
    jobs = ([('PretendardSub', w, os.path.join(pd, 'public', 'static', 'Pretendard-%s.otf' % s))
             for s, w in SANS]
          + [('PlexMonoSub', w, os.path.join(px, 'ibm-plex-mono', 'fonts', 'complete', 'ttf',
                                             'IBMPlexMono-%s.ttf' % s)) for s, w in MONO])

    head = io.open(os.path.join(ROOT, 'tools', 'fonts.head.txt'), encoding='utf-8').read() \
        if os.path.exists(os.path.join(ROOT, 'tools', 'fonts.head.txt')) else ''
    out, total = [head.rstrip()] if head else [], 0
    for fam, w, src in jobs:
        f = subset(src, os.path.join(tmp, '%s-%d' % (fam, w)), txt)
        total += os.path.getsize(f)
        b64 = base64.b64encode(io.open(f, 'rb').read()).decode()
        out.append("@font-face{font-family:'%s';font-style:normal;font-weight:%d;"
                   "src:url(data:font/woff2;base64,%s) format('woff2')}" % (fam, w, b64))
        print('  %-14s %3d → %6.1f KB' % (fam, w, os.path.getsize(f) / 1024))
    dst = os.path.join(ROOT, 'src', 'fonts.b64.css')
    io.open(dst, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print('글꼴 %d벌 · 원본 %.0f KB · %s %.0f KB'
          % (len(jobs), total / 1024, os.path.relpath(dst, ROOT), os.path.getsize(dst) / 1024))
    shutil.rmtree(tmp, ignore_errors=True)

if __name__ == '__main__':
    main()
