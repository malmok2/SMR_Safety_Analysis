#!/usr/bin/env bash
# src/*.html 을 순서대로 이어 붙여 docs/index.html 을 만든다.
# 파일 순서 = 파일명 사전순 = 슬라이드 순서. 그래서 번호 접두사를 쓴다.
set -e
cd "$(dirname "$0")"
OUT=docs/index.html
cat src/*.html > "$OUT"
N=$(grep -o 'S({' "$OUT" | wc -l | tr -d ' ')
echo "built $OUT  ($N slides, $(wc -c < "$OUT") bytes)"
