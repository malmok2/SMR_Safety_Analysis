# src\*.html 을 순서대로 이어 붙여 docs\index.html 을 만든다 (build.sh 의 윈도우판).
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$out = 'docs\index.html'
Get-ChildItem src\*.html | Sort-Object Name | Get-Content -Raw -Encoding UTF8 |
    Set-Content $out -Encoding UTF8 -NoNewline
$n = ([regex]::Matches((Get-Content $out -Raw -Encoding UTF8), 'S\(\{')).Count
Write-Host "built $out  ($n slides, $((Get-Item $out).Length) bytes)"
