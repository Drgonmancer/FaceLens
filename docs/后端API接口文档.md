# FaceGuard 后端 API 接口文档

> **版本**：V1.1 · **更新**：2026-05-28  
> **基础路径**：`http://<host>:<port>/cl3286667/`  
> **示例根地址**：`http://localhost:8000/cl3286667/`

---

## 1. 通用约定

### 1.1 请求格式

| 项目 | 说明 |
|------|------|
| 协议 | HTTP/HTTPS |
| 编码 | UTF-8 |
| Content-Type | `application/json` 或 `application/x-www-form-urlencoded` |
| 方法 | 多数接口同时支持 `GET`、`POST` |

JSON 请求示例：

```http
POST /cl3286667/face/qualityCheck HTTP/1.1
Content-Type: application/json
Token: eyJ...

{"face":"data:image/jpeg;base64,/9j/4AAQ..."}
```

### 1.2 统一响应结构

```json
{
  "code": 0,
  "msg": "操作成功",
  "data": {}
}
```

| code | 含义 |
|------|------|
| `0` | 成功（`normal_code`） |
| `400` | 业务参数错误（部分接口自定义） |
| `401` | 未携带或无效 Token |
| `10028` | 密码错误等人脸登录失败 |
| `20001`～`20003` | Token 相关错误 |
| 其他 | 见 `server/util/codes.py` |

登录成功时额外返回：

```json
{
  "code": 0,
  "msg": "success",
  "token": "Base64字符串",
  "id": 1,
  "data": { "id": 1 }
}
```

### 1.3 认证方式

登录后获取 `token`，后续请求在 Header 中携带：

```http
Token: <token>
```

或：

```http
Authorization: Bearer <token>
```

**免认证接口**（POST）：路径含 `register`、`login`、`faceLogin`、`qualityCheck` 等（见 `xmiddleware/xauth.py`）。

### 1.4 图片字段

人脸相关字段均为 **Base64** 字符串，可带 Data URL 前缀：

```
data:image/jpeg;base64,/9j/4AAQSkZJRg...
```

服务端会自动剥离 `data:*;base64,` 前缀。

---

## 2. 人脸识别核心接口

### 2.1 人脸质量检测

**`POST /face/qualityCheck`** · 免认证

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| face / image | string | 是 | Base64 图片 |

**响应 data 示例：**

```json
{
  "score": 72.5,
  "details": {
    "clarity": 68.2,
    "brightness": "正常",
    "size": "合适",
    "count": "1张人脸"
  }
}
```

未检测到人脸时 `score` 为 0，`details` 含 `error` 说明。

---

### 2.2 人脸注册 / 采集

**`POST /face/register`**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| userid | int | 是 | 用户 ID（`yonghu.id` 或管理员 `users.id`） |
| face | string | 是* | Base64 图片（`action=register` 时必填） |
| action | string | 否 | `register`（默认）/ `delete_all` / `check` |
| _isAdmin | bool | 否 | 是否为管理员账号 |

**action=register 成功：**

```json
{
  "code": 0,
  "msg": "人脸注册成功(质量:78分)",
  "data": { "faceCount": 3, "quality": 78 }
}
```

- 样本保存至 `templates/file/face_train/{userid}/`
- 自动触发 LBPH 全量重训
- 写入表 `faceregister`，更新 `yonghu.faceregistered`、`facecount`

**action=delete_all**：清除该用户全部人脸文件与注册标记。

**action=check**：返回当前样本数量与注册状态。

---

### 2.3 刷脸登录

**`POST /yonghu/faceLogin`** · 免认证

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| face | string | 是 | Base64 人脸图 |

**成功**（匹配且分数 ≥ 阈值）：

```json
{
  "code": 0,
  "msg": "success",
  "token": "...",
  "id": 1,
  "data": { "id": 1 }
}
```

**失败**：`code` 非 0，`msg` 说明原因；同时写入 `loginrecord`（含 IP、UA、截图路径）。

识别逻辑：`OpenCVFace.recognize_face_login()` → LBPH `predict` → 分数 `(100-confidence)*1.5` 与 `face_threshold` 比较。

---

### 2.4 双图比对

**`POST /face/match`**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| face1 / faceA | string | 是 | 第一张脸 |
| face2 / faceB | string | 是 | 第二张脸 |

**响应 data：**

```json
{
  "score": 81.2,
  "threshold": 70,
  "match": true,
  "time_ms": 45.3,
  "level": "匹配"
}
```

---

### 2.5 人脸检测演示

**`POST /face/detectDemo`**

| 参数 | 说明 |
|------|------|
| face / image | Base64 图片 |

**响应 data：**

```json
{
  "detected": true,
  "faceCount": 1,
  "faces": [{ "x": 120, "y": 80, "w": 150, "h": 150 }],
  "imageSize": { "width": 640, "height": 480 },
  "detectTimeMs": 12.5
}
```

---

### 2.6 陌生人识别

**`POST /face/recognizeStranger`**

| 参数 | 说明 |
|------|------|
| face | Base64 图片 |

**响应 data：**

```json
{
  "isStranger": true,
  "bestScore": 42.1,
  "threshold": 70,
  "bestMatch": { "userId": 2, "username": "zhangsan", "score": 42.1 },
  "allScores": [{ "userId": 2, "username": "zhangsan", "score": 42.1, "match": false }],
  "scannedCount": 5
}
```

若判定为陌生人且无匹配用户，会写入 `loginrecord`（`result=陌生人`，`isstranger=1`）。

---

## 3. 登录记录与统计

### 3.1 登录记录分页

**`GET|POST /face/loginRecord`**

| 参数 | 说明 |
|------|------|
| page | 页码，默认 1 |
| limit | 每页条数，默认 10 |
| username | 用户名模糊筛选 |
| role | 角色：管理员 / 用户 / 游客 |
| logintype | 密码 / 人脸 |
| result | 成功 / 失败 / 陌生人 |
| startDate / endDate | 日期范围 |

**响应 data：**

```json
{
  "list": [{
    "id": 1,
    "addtime": "2026-05-28 10:00:00",
    "username": "zhangsan",
    "role": "用户",
    "logintype": "人脸",
    "userid": 1,
    "score": 85.2,
    "ipaddress": "127.0.0.1",
    "useragent": "Mozilla/5.0...",
    "result": "成功",
    "faceimage": "/file/login_faces/login_abc_123.jpg",
    "isstranger": 0
  }],
  "currPage": 1,
  "totalPage": 5,
  "total": 48,
  "pageSize": 10
}
```

---

### 3.2 登录统计

**`GET|POST /face/loginStats`**

**响应 data 字段：**

| 字段 | 说明 |
|------|------|
| total | 总记录数 |
| todayCount | 今日登录数 |
| successCount / failCount | 成功/失败 |
| faceCount / pwdCount | 人脸/密码登录次数 |
| strangerCount | 陌生人次数 |
| avgScore | 成功登录平均匹配分 |

---

### 3.3 删除登录记录

| 接口 | 说明 |
|------|------|
| `POST /face/deleteRecord` | 单条删除，参数 `id` |
| `POST /face/batchDeleteRecords` | 批量，参数 `ids`（逗号分隔） |

---

### 3.4 陌生人告警列表

**`GET|POST /face/strangerAlertList`**

筛选 `isstranger=1` 的记录，参数同登录记录分页。

| 接口 | 说明 |
|------|------|
| `POST /face/deleteStrangerRecord` | 删除单条告警 |
| `POST /face/batchDeleteStrangerRecords` | 批量删除 |

---

## 4. 系统配置与仪表盘

### 4.1 获取全部配置

**`GET|POST /system/config/get`**

```json
{
  "code": 0,
  "data": [
    { "id": 1, "configkey": "face_threshold", "configvalue": "70", "description": "人脸识别阈值" }
  ]
}
```

### 4.2 设置配置项

**`POST /system/config/set`**

| 参数 | 说明 |
|------|------|
| configkey | 配置键 |
| configvalue | 配置值 |

### 4.3 保存识别阈值

**`POST /face/saveThreshold`**

| 参数 | 说明 |
|------|------|
| threshold | 40～100 整数 |

同步更新数据库与 `OpenCVFace` 内存阈值。

### 4.4 仪表盘数据

**`GET|POST /dashboard/data`**

聚合：用户总数、已注册人脸人数、样本总数、登录统计、近期登录、陌生人告警数、`faceStats`（模型训练状态等）。

---

## 5. 用户与账号接口

### 5.1 普通用户（yonghu）

| 接口 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/yonghu/register` | POST | 否 | 注册 |
| `/yonghu/login` | POST | 否 | 密码登录 |
| `/yonghu/faceLogin` | POST | 否 | 刷脸登录 |
| `/yonghu/logout` | POST | 是 | 退出 |
| `/yonghu/session` | GET | 是 | 当前会话 |
| `/yonghu/page` | GET | 是 | 分页列表 |
| `/yonghu/info/<id>` | GET | 是 | 详情 |
| `/yonghu/update` | POST | 部分免认证 | 更新资料 |
| `/yonghu/delete` | POST | 是 | 删除 |

**注册常用字段：**

```json
{
  "yonghuzhanghao": "user01",
  "mima": "123456",
  "yonghuxingming": "张三",
  "xingbie": "男"
}
```

**密码登录：**

```json
{
  "yonghuzhanghao": "user01",
  "mima": "123456"
}
```

### 5.2 管理员（users）

| 接口 | 说明 |
|------|------|
| `/users/login` | 管理员密码登录 |
| `/users/register` | 管理员注册 |
| `/users/page` | 管理员列表 |

### 5.3 个人资料

| 接口 | 说明 |
|------|------|
| `POST /user/profile` | 获取资料，参数 `userid` |
| `POST /user/updateProfile` | 更新姓名、电话等 |
| `POST /user/updateAvatar` | 更新头像 Base64 |
| `POST /user/changePassword` | `oldPassword`、`newPassword`、`userid` |

### 5.4 账号管理（管理员）

| 接口 | 说明 |
|------|------|
| `GET|POST /face/allAccounts` | 全部账号及人脸注册状态 |
| `POST /face/updateAccountName` | 修改账号名 |
| `POST /face/deleteAccount` | 删除账号，`id`、可选 `_isAdmin` |
| `POST /face/batchDeleteAccounts` | `ids` 格式：`1,2\|1`（id\|是否管理员） |

---

## 6. 通用业务接口

由 `main/urls.py` 按表名自动生成，每张业务表（如 `syslog`、`menu`）均包含：

| 路径模式 | 说明 |
|----------|------|
| `/{table}/page` | 后台分页 |
| `/{table}/list` | 列表 |
| `/{table}/save` | 新增 |
| `/{table}/update` | 更新 |
| `/{table}/delete` | 删除 |
| `/{table}/info/<id>` | 详情 |

### 6.1 文件上传

**`POST /file/upload`**

multipart 上传，返回文件访问路径（用于头像等非人脸场景）。

### 6.2 文件访问

**`GET /file/<path>`**

示例：`GET /cl3286667/file/face_train/1/display.jpg`

---

## 7. 操作日志（syslog）

| 接口 | 说明 |
|------|------|
| `GET /syslog/page` | 操作日志分页 |
| `GET /syslog/list` | 列表 |

字段：`username`、`operation`、`method`、`params`、`time`（毫秒）、`ip`。

---

## 8. 人脸注册记录

**`GET|POST /face/regList`**

查询表 `faceregister`：用户 ID、用户名、图片路径、质量分、是否有效。

---

## 9. 错误码速查

| code | 常量 | 说明 |
|------|------|------|
| 0 | normal_code | 成功 |
| 401 | - | Header 无 Token |
| 10028 | password_error_code | 认证失败 |
| 10026 | id_notexist_code | 用户不存在 |
| 10025 | id_exist_code | 用户已存在 |
| 20003 | non_authorized_code | 无权限 |

完整定义：`server/util/codes.py`。

---

## 10. 调用示例（curl）

```bash
# 质量检测
curl -X POST http://localhost:8000/cl3286667/face/qualityCheck \
  -H "Content-Type: application/json" \
  -d "{\"face\":\"<base64>\"}"

# 密码登录
curl -X POST http://localhost:8000/cl3286667/yonghu/login \
  -H "Content-Type: application/json" \
  -d "{\"yonghuzhanghao\":\"user01\",\"mima\":\"123456\"}"

# 带 Token 查询登录记录
curl -X POST http://localhost:8000/cl3286667/face/loginRecord \
  -H "Content-Type: application/json" \
  -H "Token: <your_token>" \
  -d "{\"page\":1,\"limit\":10}"
```

---

## 11. 相关文档

- [人工配置文档](./人工配置文档.md)
- [快速启动文档](./快速启动文档.md)
- [技术实现方案](./技术实现方案.md)
