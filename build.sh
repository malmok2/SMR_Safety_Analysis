#!/usr/bin/env bash
# 덱을 굽고 목차 페이지를 만든다. 실제 일은 tools/build.py 가 한다
# (덱이 여럿이라 bash·PowerShell 에 같은 로직을 두 벌 두지 않는다).
set -e
cd "$(dirname "$0")"
exec python3 tools/build.py "$@"
