#!/usr/bin/env bash
# src/*.html 을 순서대로 이어 붙여 docs/index.html 을 만들고,
# 같은 내용에 기본 언어만 영어로 박은 docs/index_en.html 을 함께 굽는다.
# 파일 순서 = 파일명 사전순 = 슬라이드 순서. 그래서 번호 접두사를 쓴다.
set -e
cd "$(dirname "$0")"
OUT=docs/index.html
OUT_EN=docs/index_en.html
cat src/*.html > "$OUT.tmp"
# 심어 둔 글꼴을 /*@FONTS@*/ 자리에 끼운다 (src/fonts.b64.css · tools/fonts.py 가 만든다)
sed -e '/\/\*@FONTS@\*\//r src/fonts.b64.css' -e '/\/\*@FONTS@\*\//d' "$OUT.tmp" > "$OUT"
rm -f "$OUT.tmp"
sed 's|<!--LANGDEF-->|<script>window.SMR_LANG="en"</script>|' "$OUT" > "$OUT_EN"
N=$(grep -o 'S({' "$OUT" | wc -l | tr -d ' ')
echo "built $OUT  ($N slides, $(wc -c < "$OUT") bytes)"
echo "built $OUT_EN  (기본 언어 영어)"

# 한/영 토큰 [[한국어||English]] 개수 — 렌더 결과 검증은 tools/check.js 가 한다
if command -v python3 >/dev/null 2>&1; then
  python3 - "$OUT" <<'TOKCHK'
import re, sys
s = open(sys.argv[1], encoding='utf-8').read()
n = len([m for m in re.finditer(r'\[\[([\s\S]*?)\|\|([\s\S]*?)\]\]', s)
         if re.search(r'[가-힣]', m.group(1))])
print('  한/영 토큰 %d개' % n)
TOKCHK
fi
echo "  검증:  cd tools && node check.js        PDF 굽기:  cd tools && node pdf.js"
