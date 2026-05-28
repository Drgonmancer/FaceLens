# FaceLens（FaceGuard）

> GitHub 仓库名：**FaceLens** · 基于 OpenCV + Django 的人脸识别身份管理平台

<p align="center">
  <strong>基于 OpenCV + Django 的 B/S 人脸识别身份管理平台</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Django-2.0-green.svg" alt="Django">
  <img src="https://img.shields.io/badge/OpenCV-4.x-orange.svg" alt="OpenCV">
  <img src="https://img.shields.io/badge/MySQL-8.0-red.svg" alt="MySQL">
  <img src="https://img.shields.io/badge/License-MIT-lightgrey.svg" alt="License">
</p>

FaceGuard 是一套可私有化部署的人脸识别身份管理平台：浏览器完成注册、人脸采集与刷脸登录；管理员可审计登录记录并处理陌生人告警。核心链路为 **Haar 人脸检测 + LBPH 识别**，无需 GPU。

---

## 项目结构

```
FaceGuard/
├── client/          # Vue 3 管理端（可选，Element Plus）
├── server/          # Django 后端 + 用户端页面（templates/client）
├── docs/            # 技术文档
├── install.bat      # Windows 一键安装
├── install.sh       # Linux/macOS 安装
└── README.md
```

---

## 快速开始

### 一键安装（推荐）

```text
右键 install.bat → 以管理员身份运行
```

安装完成后访问：**http://localhost:8000/cl3286667/**

### 手动启动

```bash
cd server
copy config.ini.example config.ini   # 编辑 MySQL 密码
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8000
```

| 角色 | 账号 | 密码 |
|------|------|------|
| 管理员 | admin | admin |
| 普通用户 | 注册创建 | 自行设置 |

---

## 功能特性

- 人脸识别登录 / 账号密码登录
- 浏览器摄像头采集、质量检测、自动训练 LBPH 模型
- 用户管理、登录审计、陌生人告警
- 识别阈值可配置（40～100）

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python、Django 2.0、PyMySQL |
| 视觉 | OpenCV（Haar + LBPH）、NumPy、Pillow |
| 数据库 | MySQL 8.0 |
| 用户端 | HTML5 / JS（`server/templates/client`） |
| 管理端 | Vue 3、Element Plus（`client/`） |

---

## 文档

| 文档 | 链接 |
|------|------|
| 快速启动 | [docs/快速启动文档.md](./docs/快速启动文档.md) |
| 人工配置 | [docs/人工配置文档.md](./docs/人工配置文档.md) |
| API 接口 | [docs/后端API接口文档.md](./docs/后端API接口文档.md) |
| 需求说明 | [docs/需求规格说明书.md](./docs/需求规格说明书.md) |
| 技术方案 | [docs/技术实现方案.md](./docs/技术实现方案.md) |

---

## 许可证

MIT License
