# src\*.html 을 순서대로 이어 붙여 docs\index.html 을 만든다.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$out = 'docs\index.html'
$outEn = 'docs\index_en.html'
Get-ChildItem src\*.html | Sort-Object Name | Get-Content -Raw | Set-Content -Encoding UTF8 $out
# 심어 둔 글꼴을 /*@FONTS@*/ 자리에 끼운다
$text = (Get-Content -Raw $out).Replace('/*@FONTS@*/', (Get-Content -Raw 'src\fonts.b64.css'))
$text | Set-Content -Encoding UTF8 $out
# 같은 내용에 기본 언어만 영어로 박은 판
$text.Replace('<!--LANGDEF-->', '<script>window.SMR_LANG="en"</script>') |
  Set-Content -Encoding UTF8 $outEn
Write-Host "built $outEn  (기본 언어 영어)"
$n = ([regex]::Matches($text, 'S\(\{')).Count
Write-Host "built $out  ($n slides, $((Get-Item $out).Length) bytes)"

# 한/영 토큰 [[한국어||English]] 개수 - 렌더 결과 검증은 tools\check.js 가 한다
$hits = [regex]::Matches($text, '(?s)\[\[(.*?)\|\|(.*?)\]\]') |
        Where-Object { $_.Groups[1].Value -match '[\uAC00-\uD7A3]' }
Write-Host "  한/영 토큰 $($hits.Count)개"
Write-Host "  검증:  cd tools; node check.js        PDF 굽기:  cd tools; node pdf.js"
