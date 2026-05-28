#!/bin/bash
# FaceGuard 人脸识别系统 - Linux/Mac 启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}     ${YELLOW}FaceGuard 人脸识别系统${NC}                    ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}          ${YELLOW}一键安装部署工具 V1.0 (Linux)${YELLOW}          ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/server"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[错误] 未检测到 Python！请先安装 Python 3.8+${NC}"
    exit 1
fi

echo -e "${GREEN}[成功] Python 版本: $(python3 --version)${NC}"

# 检查MySQL
if ! command -v mysql &> /dev/null; then
    echo -e "${RED}[错误] 未检测到 MySQL！请先安装 MySQL 5.7+/8.0${NC}"
    exit 1
fi

echo -e "${GREEN}[成功] MySQL 已安装: $(mysql --version | awk '{print $5}')${NC}"

# 配置向导
if [ ! -f "config.ini" ]; then
    echo -e "${YELLOW}[提示] 首次运行，启动配置向导...${NC}"
    python3 setup_config.py
fi

# 安装依赖
echo ""
echo -e "${YELLOW}[提示] 正在安装 Python 依赖...${NC}"
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ || {
    echo -e "${RED}[错误] 依赖安装失败！${NC}"
    exit 1
}

# 创建目录
mkdir -p templates/file/face_train
mkdir -p templates/file/login_faces
mkdir -p media

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}         ${YELLOW}安装完成！${NC}                               ${GREEN}║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║${NC}   访问地址: http://localhost:8000/cl3286667/       ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}   默认账号: admin / admin                       ${GREEN}║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# 启动服务
echo -e "${YELLOW}[启动] 正在启动 Django 服务...${NC}"
python3 manage.py runserver 0.0.0.0:8000
