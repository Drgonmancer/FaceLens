@echo off
if /i not "%~1"=="RUN" (
    cmd /k "%~f0" RUN
    exit /b
)

setlocal enabledelayedexpansion
title FaceGuard

cd /d "%~dp0"
set "ROOT=%cd%"
set "VENV=%ROOT%\.venv"
set "PYTHON=%VENV%\Scripts\python.exe"
set "PIP=%VENV%\Scripts\pip.exe"

set "FG_DB_HOST=127.0.0.1"
set "FG_DB_PORT=3306"
set "FG_DB_USER=root"
set "FG_DB_NAME=cl3286667"

echo.
echo ========================================
echo    FaceGuard - Starting...
echo    URL: http://localhost:8000/cl3286667/
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.8+
    goto :FAIL
)

if not exist "%PYTHON%" (
    echo [INFO] Creating virtual environment...
    python -m venv "%VENV%"
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        goto :FAIL
    )
)

if not exist "%VENV%\.deps_ok" (
    echo [INFO] Installing dependencies, please wait...
    "%PIP%" install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple >nul 2>&1
    "%PIP%" install -r "%ROOT%\server\requirements.txt" -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        goto :FAIL
    )
    type nul > "%VENV%\.deps_ok"
    echo [OK] Dependencies installed.
)

"%PYTHON%" -c "import cv2; assert hasattr(cv2,'face')" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing OpenCV face recognition module...
    "%PIP%" uninstall -y opencv-python opencv-contrib-python >nul 2>&1
    "%PIP%" install "opencv-contrib-python>=4.5.0" -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo [ERROR] Failed to install opencv-contrib-python.
        goto :FAIL
    )
)

if not exist "%ROOT%\server\templates\file\face_train" mkdir "%ROOT%\server\templates\file\face_train"
if not exist "%ROOT%\server\templates\file\login_faces" mkdir "%ROOT%\server\templates\file\login_faces"
if not exist "%ROOT%\server\media" mkdir "%ROOT%\server\media"

cd /d "%ROOT%\server"
"%PYTHON%" write_config.py
if errorlevel 1 goto :FAIL

"%PYTHON%" ensure_ready.py
if errorlevel 1 goto :FAIL

netstat -ano | findstr :8000 | findstr LISTENING >nul 2>&1
if not errorlevel 1 (
    echo [WARN] Port 8000 in use, releasing...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

echo.
echo [RUNNING] Press Ctrl+C to stop
echo [USER]    http://localhost:8000/cl3286667/
echo [ADMIN]   http://localhost:8000/cl3286667/manage/
echo [ACCOUNT] admin / admin
echo.

start "" "http://localhost:8000/cl3286667/"
"%PYTHON%" manage.py runserver 0.0.0.0:8000
goto :END

:FAIL
echo.
echo [FAILED] Startup aborted.
:END
echo.
pause
endlocal
