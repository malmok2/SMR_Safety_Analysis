# 덱을 굽고 목차 페이지를 만든다. 실제 일은 tools\build.py 가 한다.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python3 -ErrorAction SilentlyContinue }
if (-not $py) { Write-Error "python 이 없다. https://www.python.org 에서 설치할 것"; exit 1 }
& $py.Source tools\build.py @args
