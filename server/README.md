# server

Django 后端与用户端页面。

## 启动

```bash
pip install -r requirements.txt
python setup_config.py          # 首次：配置 config.ini
python manage.py runserver 0.0.0.0:8000
```

或双击 `start_server.bat`。

## 目录说明

| 目录/文件 | 说明 |
|-----------|------|
| `main/` | 业务模型与 API（`face_v.py`、`Yonghu_v.py`） |
| `util/opencv_face.py` | Haar + LBPH 识别核心 |
| `templates/client/` | 用户端单页应用 |
| `templates/file/face_train/` | 人脸样本与模型（运行时生成） |
| `sql/` | 数据库初始化脚本 |

文档见 [../docs/](../docs/)
