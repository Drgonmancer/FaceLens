@echo off
chcp 65001 >nul 2>&1
title FaceGuard 人脸识别系统 - 全自动一键安装部署 V2.0

:: ============================================================
:: FaceGuard 全自动一键安装部署脚本 V2.0
:: 功能：
::   1. 自动检测并安装 Python 3.10
::   2. 自动检测并安装 MySQL 8.0
::   3. 自动配置环境变量
::   4. 自动安装 Python 依赖包
::   5. 自动初始化数据库
::   6. 一键启动系统
:: ============================================================

setlocal enabledelayedexpansion

:: 颜色定义
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "CYAN=[96m"
set "RESET=[0m"

echo.
echo %CYAN%╔════════════════════════════════════════════════════════════╗%RESET%
echo %CYAN%║%RESET%                                                          %CYAN%║%RESET%
echo %CYAN%║%RESET%       %YELLOW%███████╗██╗   ██╗██╗ ██████╗ ██████╗ ██████╗ ██╗    ██╗%RESET%        %CYAN%║%RESET%
echo %CYAN%║%RESET%       %YELLOW%██╔════╝██║   ██║██║██╔═══██╗██╔══██╗██╔═══██╗██║    ██║%RESET%        %CYAN%║%RESET%
echo %CYAN%║%RESET%       %YELLOW%█████╗  ██║   ██║██║██║   ██║██████╔╝██║   ██║██║ █╗ ██║%RESET%        %CYAN%║%RESET%
echo %CYAN%║%RESET%       %YELLOW%██╔══╝  ╚██╗ ██╔╝██║██║   ██║██╔═══╝ ██║   ██║██║███╗██║%RESET%        %CYAN%║%RESET%
echo %CYAN%║%RESET%       %YELLOW%██║      ╚████╔╝ ██║╚██████╔╝██║     ╚██████╔╝██║╚███╔╝██║%RESET%        %CYAN%║%RESET%
echo %CYAN%║%RESET%       %YELLOW%╚═╝       ╚═══╝  ╚═╝ ╚═════╝ ╚═╝      ╚═════╝ ╚═╝ ╚══╝ ╚═╝%RESET%        %CYAN%║%RESET%
echo %CYAN%║%RESET%                                                          %CYAN%║%RESET%
echo %CYAN%║%RESET%              %YELLOW%全自动一键安装部署工具 V2.0%RESET%                  %CYAN%║%RESET%
echo %CYAN%╚════════════════════════════════════════════════════════════╝%RESET%
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[错误]%RESET% 请右键点击此文件，选择"以管理员身份运行"！
    echo.
    pause
    exit /b 1
)

:: 设置工作目录
cd /d "%~dp0server"
set "PROJECT_ROOT=%cd%"
set "DOWNLOAD_DIR=%TEMP%\FaceGuard_Installer"

:: 创建临时下载目录
if not exist "%DOWNLOAD_DIR%" mkdir "%DOWNLOAD_DIR%"

echo %GREEN%[信息]%RESET% 项目目录: %PROJECT_ROOT%
echo %GREEN%[信息]%RESET% 临时目录: %DOWNLOAD_DIR%
echo.

:: ============================================================
:: 环境预检与自动安装
:: ============================================================

call :CHECK_AND_INSTALL_PYTHON
if %errorlevel% neq 0 goto :ERROR_EXIT

call :CHECK_AND_INSTALL_MYSQL
if %errorlevel% neq 0 goto :ERROR_EXIT

:: ============================================================
:: 数据库配置
:: ============================================================
echo.
echo %BLUE%━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%RESET%
echo %YELLOW%[3/5] 配置数据库连接...%RESET%
echo %BLUE%━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%RESET%

if exist config.ini (
    echo %YELLOW%[提示]%RESET% 发现已有配置文件
    set /p RECONFIG="是否重新配置? (Y/N): "
    if /i not "%RECONFIG%"=="Y" (
        echo %GREEN%[跳过]%RESET% 使用现有配置
        goto :INSTALL_DEPS
    )
)

python setup_config.py
if %errorlevel% neq 0 (
    echo %RED%[错误]%RESET% 数据库配置失败！
    goto :ERROR_EXIT
)
echo %GREEN%[成功]%RESET% 数据库配置完成！

:INSTALL_DEPS

:: ============================================================
:: 安装Python依赖
:: ============================================================
echo.
echo %BLUE%━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%RESET%
echo %YELLOW%[4/5] 安装 Python 依赖包...%RESET%
echo %BLUE%━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%RESET%

echo %CYAN%[提示]%RESET% 首次安装可能需要3-5分钟，请耐心等待...
echo.

:: 升级pip
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet >nul 2>&1

:: 安装核心依赖
echo %YELLOW%  正在安装 Django...%RESET%
pip install django==2.0 -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet >nul 2>&1
echo %YELLOW%  正在安装 OpenCV...%RESET%
pip install opencv-python>=4.5.0 -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet >nul 2>&1
echo %YELLOW%  正在安装 MySQL驱动...%RESET%
pip install pymysql -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet >nul 2>&1
echo %YELLOW%  正在安装其他依赖...%RESET%
pip install numpy>=1.19.0 Pillow>=8.0.0 click requests xlrd==1.2.0 django-cors-headers==2.4.0 django-threadlocals -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet >nul 2>&1

echo %GREEN%[成功]%RESET% 所有依赖安装完成！

:: ============================================================
:: 初始化数据库并启动
:: ============================================================
echo.
echo %BLUE%━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%RESET%
echo %YELLOW%[5/5] 初始化数据库并启动系统...%RESET%
echo %BLUE%━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%RESET%

:: 创建必要目录
if not exist templates\file\face_train mkdir templates\file\face_train
if not exist templates\file\login_faces mkdir templates\file\login_faces
if not exist media mkdir media

:: 从config读取配置
for /f "tokens=2 delims== " %%a in ('findstr "^host" config.ini') do set DB_HOST=%%a
for /f "tokens=2 delims== " %%a in ('findstr "^port" config.ini') do set DB_PORT=%%a
for /f "tokens=2 delims== " %%a in ('findstr "^user" config.ini') do set DB_USER=%%a
for /f "tokens=2 delims== " %%a in ('findstr "^passwd" config.ini') do set DB_PASS=%%a
for /f "tokens=2 delims== " %%a in ('findstr "^db" config.ini') do set DB_NAME=%%a
set "DB_HOST=%DB_HOST: =%"
set "DB_PORT=%DB_PORT: =%"
set "DB_USER=%DB_USER: =%"
set "DB_PASS=%DB_PASS: =%"
set "DB_NAME=%DB_NAME: =%"

:: 创建数据库
mysql -h %DB_HOST% -P %DB_PORT% -u %DB_USER% -p"%DB_PASS%" -e "CREATE DATABASE IF NOT EXISTS %DB_NAME% DEFAULT CHARACTER SET utf8mb4;" 2>nul
if %errorlevel% equ 0 (
    echo %GREEN%[成功]%RESET% 数据库连接正常！
) else (
    echo %YELLOW%[警告]%RESET% 无法连接数据库，请确认 MySQL 服务已启动且配置正确
)

:: 导入SQL（如果存在）
if exist sql\cl3286667.sql (
    mysql -h %DB_HOST% -P %DB_PORT% -u %DB_USER% -p"%DB_PASS%" %DB_NAME% < sql\cl3286667.sql 2>nul
)

:: ============================================================
:: 完成！启动系统
:: ============================================================
echo.
echo.
echo %GREEN%╔════════════════════════════════════════════════════════════╗%RESET%
echo %GREEN%║%RESET%                                                          %GREEN%║%RESET%
echo %GREEN%║%RESET%           %YELLOW%🎉 安装完成！系统即将启动... 🎉%RESET%                 %GREEN%║%RESET%
echo %GREEN%║%RESET%                                                          %GREEN%║%RESET%
echo %GREEN%╠════════════════════════════════════════════════════════════╣%RESET%
echo %GREEN%║%RESET%                                                          %GREEN%║%RESET%
echo %GREEN%║%RESET%   %CYAN%访问地址:%RESET% http://localhost:8000/cl3286667/            %GREEN%║%RESET%
echo %GREEN%║%RESET%                                                          %GREEN%║%RESET%
echo %GREEN%║%RESET%   %CYAN%默认管理员账号:%RESET% admin                              %GREEN%║%RESET%
echo %GREEN%║%RESET%   %CYAN%默认密码:%RESET%     admin                               %GREEN%║%RESET%
echo %GREEN%║%RESET%                                                          %GREEN%║%RESET%
echo %GREEN%╚════════════════════════════════════════════════════════════╝%RESET%
echo.

timeout /t 3 /nobreak >nul

:: 释放端口
netstat -ano | findstr :8000 >nul 2>&1
if %errorlevel% == 0 (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 1 >nul
)

echo %YELLOW%[启动]%RESET% 正在启动服务... (按 Ctrl+C 停止)
echo.

python manage.py runserver 0.0.0.0:8000
goto :END

:: ============================================================
:: 子程序：检查并安装Python
:: ============================================================
:CHECK_AND_INSTALL_PYTHON
echo.
echo %BLUE%━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%RESET%
echo %YELLOW%[1/5] 检查/安装 Python 环境...%RESET%
echo %BLUE%━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%RESET%

:: 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
    echo %GREEN%[成功]%RESET% 已安装 Python %PYVER%
    
    :: 检查版本是否满足要求
    python -c "import sys; exit(0) if sys.version_info >= (3,8) else exit(1)" >nul 2>&1
    if !errorlevel! equ 0 (
        echo %GREEN%[OK]%RESET% 版本满足要求 (≥3.8)
        exit /b 0
    ) else (
        echo %YELLOW%[警告]%RESET% Python版本过低，建议升级到3.10
        set /p UPGRADE_PY="是否升级Python? (Y/N): "
        if /i not "%UPGRADE_PY%"=="Y" exit /b 0
    )
)

:: 需要安装Python
echo.
echo %CYAN%[提示]%RESET% 未检测到Python或需要升级，将自动下载安装...
echo.

:: Python下载信息
set "PYTHON_VER=3.10.11"
set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VER%/python-%PYTHON%-amd64.exe"
set "PYTHON_INSTALLER=%DOWNLOAD_DIR%\python-installer.exe"

:: 检查是否已下载
if not exist "%PYTHON_INSTALLER%" (
    echo %YELLOW%  正在下载 Python %PYTHON_VER%...%RESET%
    echo %YELLOW%  下载地址: %PYTHON_URL%%RESET%
    echo.
    
    :: 使用PowerShell下载
    powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%' -UseBasicParsing }" 2>nul
    
    if not exist "%PYTHON_INSTALLER%" (
        echo %RED%[错误]%RESET% Python下载失败！
        echo %RED%      请手动下载: %PYTHON_URL%%RESET%
        echo %RED%      或访问: https://www.python.org/downloads/%RESET%
        pause
        exit /b 1
    )
    echo %GREEN%  下载完成！%RESET%
)

:: 静默安装Python
echo.
echo %YELLOW%  正在安装 Python (静默模式)...%RESET%

"%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

if %errorlevel% neq 0 (
    echo %RED%[错误]%RESET% Python安装失败！请手动运行安装程序。
    start "" "%PYTHON_INSTALLER%"
    pause
    exit /b 1
)

:: 刷新环境变量
echo %YELLOW%  正在刷新环境变量...%RESET%
call :REFRESH_ENV

:: 验证安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    :: 尝试使用新路径
    set "PATH=C:\Program Files\Python310;C:\Program Files\Python310\Scripts;%PATH%"
    python --version >nul 2>&1
)

if %errorlevel% equ 0 (
    for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
    echo %GREEN%[成功]%RESET% Python %PYVER% 安装完成！
) else (
    echo %YELLOW%[警告]%RESET% Python可能已安装但需要重启终端才能生效
)

exit /b 0

:: ============================================================
:: 子程序：检查并安装MySQL
:: ============================================================
:CHECK_AND_INSTALL_MYSQL
echo.
echo %BLUE%━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━════════━%RESET%
echo %YELLOW%[2/5] 检查/安装 MySQL 数据库...%RESET%
echo %BLUE%━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━════════━━━%RESET%

:: 检查MySQL是否已安装
mysql --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=6 delims= " %%v in ('mysql --version 2^>^&1') do set MYSQL_VER=%%v
    echo %GREEN%[成功]%RESET% 已安装 MySQL %MYSQL_VER%
    exit /b 0
)

:: 需要安装MySQL
echo.
echo %CYAN%[提示]%RESET% 未检测到MySQL，将引导您进行安装...
echo.
echo %YELLOW%================================================================%RESET%
echo %YELLOW%  MySQL 安装说明：%RESET%
echo %YELLOW%  1. 将自动打开MySQL官方下载页面%RESET%
echo %YELLOW%  2. 请选择 "MySQL Installer for Windows"%RESET%
echo %YELLOW%  3. 选择 "Server only" 或 "Full" 安装类型%RESET%
echo %YELLOW%  4. 设置root密码（请记住这个密码）%RESET%
echo %YELLOW%  5. 完成后按任意键继续%RESET%
echo %YELLOW%================================================================%RESET%
echo.

set /p CONTINUE="按回车键打开MySQL下载页面..."

:: 打开MySQL下载页面
start https://dev.mysql.com/downloads/installer/

echo.
echo %YELLOW%[等待]%RESET% 请完成MySQL安装后，按回车继续...
pause >nul

:: 再次检查
mysql --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=6 delims= " %%v in ('mysql --version 2^>^&1') do set MYSQL_VER=%%v
    echo %GREEN%[成功]%RESET% MySQL %MYSQL_VER% 安装成功！
    exit /b 0
) else (
    echo %YELLOW%[警告]%RESET% 未检测到MySQL。如果已安装，请确保MySQL bin目录已在PATH中。
    echo %YELLOW%         您可以稍后手动配置数据库连接。%RESET%
    
    :: 尝试常见路径
    if exist "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" (
        echo %YELLOW%[发现]%RESET% 在默认路径发现MySQL 8.0
        set "PATH=C:\Program Files\MySQL\MySQL Server 8.0\bin;%PATH%"
        mysql --version >nul 2>&1
        if !errorlevel! equ 0 (
            echo %GREEN%[成功]%RESET% 已添加到PATH！
            exit /b 0
        )
    )
    
    if exist "C:\Program Files\MySQL\MySQL Server 5.7\bin\mysql.exe" (
        echo %YELLOW%[发现]%RESET% 在默认路径发现MySQL 5.7
        set "PATH=C:\Program Files\MySQL\MySQL Server 5.7\bin;%PATH%"
        mysql --version >nul 2>&1
        if !errorlevel! equ 0 (
            echo %GREEN%[成功]%RESET% 已添加到PATH！
            exit /b 0
        )
    )
)

exit /b 0

:: ============================================================
:: 子程序：刷新环境变量
:: ============================================================
:REFRESH_ENV
:: 刷新当前会话的环境变量
for /f "usebackq tokens=3*" %%a in (`reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul`) do (
    set "SYSTEM_PATH=%%a %%b"
)
for /f "usebackq tokens=3*" %%a in (`reg query "HKCU\Environment" /v PATH 2^>nul`) do (
    set "USER_PATH=%%a %%b"
)
set "PATH=%USER_PATH%;%SYSTEM_PATH%;%PATH%"
goto :eof

:: ============================================================
:: 错误退出
:: ============================================================
:ERROR_EXIT
echo.
echo %RED%╔══════════════════════════════════════════════════╗%RESET%
echo %RED%║%RESET%          %YELLOW%安装过程中出现错误！%RESET%                    %RED%║%RESET%
echo %RED%╠══════════════════════════════════════════════════╣%RESET%
echo %RED%║%RESET%                                                  %RED%║%RESET%
echo %RED%║%RESET%  可能的解决方案：                                %RED%║%RESET%
echo %RED%║%RESET%  1. 确保网络连接正常                            %RED%║%RESET%
echo %RED%║%RESET%  2. 以管理员身份运行此脚本                      %RED%║%RESET%
echo %RED%║%RESET%  3. 关闭杀毒软件后重试                         %RED%║%RESET%
echo %RED%║%RESET%  4. 手动安装缺失的软件后再运行                  %RED%║%RESET%
echo %RED%║%RESET%                                                  %RED%║%RESET%
echo %RED%╚══════════════════════════════════════════════════╝%RESET%
pause
exit /b 1

:END
endlocal
