@echo off
chcp 65001 >nul
title FaceGuard - 端口8000
cd /d "%~dp0"

echo ========================================
echo    FaceGuard 人脸识别系统 - 启动中...
echo    访问: http://localhost:8000/cl3286667/
echo ========================================
echo.

netstat -ano | findstr :8000 >nul 2>&1
if %errorlevel% == 0 (
    echo [警告] 8000端口已被占用，正在尝试释放...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 >nul
)

python manage.py runserver 0.0.0.0:8000
pause
