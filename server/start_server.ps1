# FaceGuard 启动脚本
# 右键 -> 使用 PowerShell 运行

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "FaceGuard - 端口8000"

Set-Location $PSScriptRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   FaceGuard 人脸识别系统 - 启动中..." -ForegroundColor Green
Write-Host "   访问: http://localhost:8000/cl3286667/" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$portInUse = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "[警告] 8000 端口已被占用，正在尝试释放..." -ForegroundColor Yellow
    $portInUse | ForEach-Object {
        Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
}

python manage.py runserver 0.0.0.0:8000
