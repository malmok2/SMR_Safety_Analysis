# git-save.ps1 — THINK Lab 문서 저장소 커밋·푸시 헬퍼
# 사용법:  cd C:\Claude\Documents ;  .\git-save.ps1 "변경 설명"
param([string]$msg = "update documents")

$ErrorActionPreference = "Stop"
Set-Location "C:\Claude\Documents"

# 저장소가 아직 초기화되지 않았으면 안내하고 중단
git rev-parse --is-inside-work-tree 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "이 폴더는 아직 git 저장소가 아닙니다. 아래를 한 번만 실행하세요:" -ForegroundColor Yellow
    Write-Host "  git init" -ForegroundColor Cyan
    Write-Host "  git branch -M main" -ForegroundColor Cyan
    Write-Host "  git remote add origin https://github.com/malmok2/Documents.git" -ForegroundColor Cyan
    Write-Host "  git add -A ; git commit -m `"초기 커밋`" ; git push -u origin main" -ForegroundColor Cyan
    exit 1
}

git add -A
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m $msg
    git push
    Write-Host "완료: 커밋·푸시됨 -> https://github.com/malmok2/Documents" -ForegroundColor Green
} else {
    Write-Host "변경 사항 없음 — 커밋할 것이 없습니다." -ForegroundColor Yellow
}
