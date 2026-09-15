#!/usr/bin/env bash
# src/*.html 을 순서대로 이어 붙여 docs/index.html 을 만든다.
# 파일 순서 = 파일명 사전순 = 슬라이드 순서. 그래서 번호 접두사를 쓴다.
set -e
cd "$(dirname "$0")"
OUT=docs/index.html
cat src/*.html > "$OUT"
N=$(grep -o 'S({' "$OUT" | wc -l | tr -d ' ')
echo "built $OUT  ($N slides, $(wc -c < "$OUT") bytes)"

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
