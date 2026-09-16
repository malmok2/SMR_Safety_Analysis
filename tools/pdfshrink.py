#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""구운 PDF 안의 사진을 다시 눌러 파일을 줄인다.

    python3 tools/pdfshrink.py docs/*.pdf

크로미움은 인쇄할 때 그림을 2배 해상도로 키워 무압축에 가깝게 넣는다. 덱에 심은 WebP 가
2 MB 인데 PDF 는 25 MB 가 되는 이유다. 학생이 받아 갈 파일이므로 그대로 두면 안 된다.

사진에 drop-shadow 를 쓰기 때문에 크로미움이 그림을 <본체 + 투명도 마스크> 두 장으로 넣는다.
둘 다 줄이고 본체는 JPEG 로, 마스크는 회색 JPEG 로 다시 넣는다. 글자와 벡터(인라인 SVG 도해)는
건드리지 않으므로 슬라이드의 선과 글씨는 그대로 벡터로 남는다.
"""
import io, os, sys
import pikepdf
from PIL import Image

MAXPX  = 1600     # 한 변의 상한. 지면이 1280 px 이므로 이 정도면 충분하다
Q_BASE = 80       # 화면 캡처의 글자가 뭉개지지 않는 선
Q_MASK = 88       # 그림자 마스크. 가장자리가 지저분해지지 않게 조금 높인다
MINPX  = 40000    # 이보다 작은 그림은 손대 봐야 의미가 없다


def _pixels(obj, w, h):
    """마스크를 합치지 않고 본체 픽셀만 읽는다."""
    cs = str(obj.get('/ColorSpace') or '')
    mode = 'L' if 'Gray' in cs else ('RGB' if 'RGB' in cs else None)
    if mode is None:
        return None
    data = obj.read_bytes()
    if len(data) != w * h * (1 if mode == 'L' else 3):
        return None
    return Image.frombytes(mode, (w, h), data)


def shrink(path):
    before = os.path.getsize(path)
    pdf = pikepdf.open(path, allow_overwriting_input=True)
    done = 0
    for obj in pdf.objects:
        try:
            if obj.get('/Subtype') != '/Image':
                continue
            w, h = int(obj.Width), int(obj.Height)
        except Exception:
            continue
        if w * h < MINPX:
            continue
        im = _pixels(obj, w, h)
        if im is None:
            continue
        if max(im.size) > MAXPX:
            k = MAXPX / max(im.size)
            im = im.resize((max(1, round(w * k)), max(1, round(h * k))), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=(Q_MASK if im.mode == 'L' else Q_BASE),
                optimize=True, progressive=True)
        new = buf.getvalue()
        if len(new) >= len(obj.read_raw_bytes()):
            continue
        obj.write(new, filter=pikepdf.Name('/DCTDecode'))
        obj.Width, obj.Height = im.size
        obj.ColorSpace = pikepdf.Name('/DeviceGray' if im.mode == 'L' else '/DeviceRGB')
        obj.BitsPerComponent = 8
        for k in ('/DecodeParms', '/Decode'):
            if k in obj:
                del obj[k]
        done += 1
    pdf.save(path, linearize=True, compress_streams=True,
             object_stream_mode=pikepdf.ObjectStreamMode.generate)
    after = os.path.getsize(path)
    print('  %-46s %5.1f MB → %4.1f MB   (그림 %d개)'
          % (os.path.basename(path), before / 1e6, after / 1e6, done))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for f in sys.argv[1:]:
        shrink(f)
