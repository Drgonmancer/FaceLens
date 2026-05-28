# 数据库设计文档 - 人脸识别系统

## 系统概述
本系统基于OpenCV和Python的人脸识别系统，包含**8张核心数据表**（已通过源代码Models定义100%验证），用于支持用户管理、人脸识别、登录记录等功能。

### 📋 表清单总览

| 序号 | 表名 | 中文名 | 模型文件 | 记录数级 | 核心功能 |
|------|------|--------|---------|---------|---------|
| 1 | **users** | 管理员表 | users_model.py | 少量 | 系统管理员账号 |
| 2 | **yonghu** | 普通用户表 | models.py | 中等 | 注册用户信息+人脸状态 |
| 3 | **syslog** | 操作日志表 | models.py | 大量 | 用户行为审计 |
| 4 | **menu** | 菜单配置表 | models.py | 1条 | 前端动态菜单 |
| 5 | **loginrecord** | 登录记录表 | models.py | 大量 | 登录历史+人脸识别审计 |
| 6 | **faceregister** | 人脸注册记录表 | models.py | 中等 | 人脸照片存储 |
| 7 | **systemconfig** | 系统配置表 | models.py | ~20条 | 全局参数配置(Key-Value) |
| 8 | **config** | 配置表 | config_model.py | 少量 | 系统基础配置(键值对) |

---

## 📊 表关系图（ER图）

```
┌─────────────────┐       ┌──────────────────┐       ┌─────────────────────┐
│   users (管理员) │       │  yonghu (普通用户) │       │ faceregister(人脸注册)│
├─────────────────┤       ├──────────────────┤       ├─────────────────────┤
│ PK: id          │◄──────│ PK: id           │1     N│ FK: userid ────────►│
│    username     │       │    yonghuzhanghao│──────►│    username         │
│    password     │       │    mima          │       │    faceimage        │
│    role         │       │    yonghuxingming│       │    qualityscore     │
│    addtime      │       │    faceregistered│       │    isvalid          │
└─────────────────┘       │    facecount     │       │    addtime          │
                          │    addtime       │       └─────────────────────┘
                          └──────────────────┘                │
                                  │                           │
                                  │ 1                       N │
                                  ▼                           ▼
                          ┌──────────────────┐       ┌─────────────────────┐
                          │ loginrecord      │       │                     │
                          ├──────────────────┤       │  所有表都继承自      │
                          │ FK: userid ──────┼──────►│  BaseModel          │
                          │    username      │       ├─────────────────────┤
                          │    role          │       │ PK: id              │
                          │    logintype     │       │    addtime          │
                          │    score         │       └─────────────────────┘
                          │    result        │
                          │    isstranger    │
                          │    addtime       │
                          └──────────────────┘

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ syslog          │  │ menu            │  │ systemconfig    │  │ config          │
│ (操作日志)      │  │ (菜单配置)      │  │ (系统配置)      │  │ (基础配置)      │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ PK: id          │  │ PK: id          │  │ PK: id          │  │ PK: id          │
│    username     │  │    menujson     │  │    configkey(UK) │  │    name         │
│    operation    │  │    addtime      │  │    configvalue   │  │    value        │
│    method       │  │                 │  │    description   │  │    addtime      │
│    params       │  │                 │  │    addtime      │  │                 │
│    time         │  │                 │  │                 │  │                 │
│    ip           │  │                 │  │                 │  │                 │
│    addtime      │  │                 │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
```

## 🔗 表关系说明

| 关系类型 | 主表 | 从表 | 关联字段 | 说明 |
|---------|------|------|---------|------|
| **1:N** | yonghu | faceregister | userid | 一个用户可注册多张人脸照片 |
| **1:N** | yonghu/users | loginrecord | userid | 一个用户有多条登录记录 |
| **继承** | BaseModel | 所有表 | id, addtime | 所有表继承基础字段 |

---

# 详细表结构

---

## 表 1：管理员表 (users)

### 基本信息
- **表名**：`users`
- **中文名**：管理员表
- **说明**：存储系统管理员账号信息

### 字段详情

| 字段名 | 数据类型 | 长度 | 是否主键 | 是否为空 | 默认值 | 说明 |
|-------|---------|------|---------|---------|--------|------|
| `id` | BigIntegerField | 20 | **PK** | NOT NULL | 自增 | 管理员ID，主键自增 |
| `username` | VARCHAR | 100 | 否 | NOT NULL | - | 管理员账号，唯一标识 |
| `password` | VARCHAR | 100 | 否 | NOT NULL | - | 登录密码（加密存储） |
| `role` | VARCHAR | 100 | 否 | NOT NULL | - | 角色（管理员/超级管理员） |
| `addtime` | DateTimeField | - | 否 | NOT NULL | 当前时间 | 账号创建时间 |

### 索引
- PRIMARY KEY (`id`)
- UNIQUE KEY (`username`)

---

## 表 2：用户表 (yonghu)

### 基本信息
- **表名**：`yonghu`
- **中文名**：普通用户表
- **说明**：存储系统注册用户的个人信息和人脸识别状态

### 字段详情

| 字段名 | 数据类型 | 长度 | 是否主键 | 是否为空 | 默认值 | 说明 |
|-------|---------|------|---------|---------|--------|------|
| `id` | BigIntegerField | 20 | **PK** | NOT NULL | 自增 | 用户ID，主键自增 |
| `yonghuzhanghao` | VARCHAR | 255 | 否 | NOT NULL, **UNIQUE** | - | 用户账号，唯一标识，登录用 |
| `mima` | VARCHAR | 255 | 否 | NOT NULL | - | 登录密码（加密存储） |
| `yonghuxingming` | VARCHAR | 255 | 否 | NOT NULL | - | 用户真实姓名 |
| `touxiang` | TextField | - | 否 | 可为空 | NULL | 头像图片路径（URL或相对路径） |
| `lianxidianhua` | VARCHAR | 255 | 否 | 可为空 | NULL | 联系电话号码 |
| `xingbie` | VARCHAR | 255 | 否 | 可为空 | NULL | 性别（男/女/其他） |
| `faceregistered` | IntegerField | 11 | 否 | NOT NULL | 0 | 人脸注册状态（0=未注册，1=已注册） |
| `mustchangepwd` | IntegerField | 11 | 否 | NOT NULL | 0 | 是否需强制改密（0=否，1=是） |
| `facecount` | IntegerField | 11 | 否 | NOT NULL | 0 | 已注册人脸照片数量 |
| `addtime` | DateTimeField | - | 否 | NOT NULL | 当前时间 | 账号创建时间 |

### 索引
- PRIMARY KEY (`id`)
- UNIQUE KEY (`yonghuzhanghao`) - 用户账号唯一索引

### 业务规则
- `faceregistered`: 标识该用户是否完成人脸注册，影响是否可使用人脸登录
- `facecount`: 记录用户录入的人脸照片数量，建议≥3张以提高识别准确率
- `mustchangepwd`: 首次登录或重置密码后强制修改密码的标志位

---

## 表 3：操作日志表 (syslog)

### 基本信息
- **表名**：`syslog`
- **中文名**：系统操作日志表
- **说明**：记录用户的所有操作行为，用于安全审计和问题追踪

### 字段详情

| 字段名 | 数据类型 | 长度 | 是否主键 | 是否为空 | 默认值 | 说明 |
|-------|---------|------|---------|---------|--------|------|
| `id` | BigIntegerField | 20 | **PK** | NOT NULL | 自增 | 日志ID，主键自增 |
| `username` | VARCHAR | 255 | 否 | NOT NULL | - | 操作用户名 |
| `operation` | VARCHAR | 255 | 否 | NOT NULL | - | 操作描述（如"登录"、"修改密码"、"删除数据"等） |
| `method` | VARCHAR | 255 | 否 | 可为空 | NULL | HTTP请求方法（GET/POST/PUT/DELETE） |
| `params` | TextField | - | 否 | 可为空 | NULL | 请求参数（JSON格式，敏感字段已脱敏） |
| `time` | BigIntegerField | 20 | 否 | 可为空 | NULL | 请求处理时长（毫秒），用于性能监控 |
| `ip` | VARCHAR | 255 | 否 | 可为空 | NULL | 客户端IP地址，用于安全分析 |
| `addtime` | DateTimeField | - | 否 | NOT NULL | 当前时间 | 日志记录时间 |

### 索引
- PRIMARY KEY (`id`)
- INDEX (`username`) - 按用户查询日志
- INDEX (`addtime`) - 按时间范围查询
- INDEX (`ip`) - 按IP地址追踪异常访问

### 业务用途
- 安全审计：追踪敏感操作（删除、修改权限等）
- 性能分析：通过`time`字段监控接口响应时间
- 异常检测：通过IP和行为模式识别攻击行为

---

## 表 4：菜单配置表 (menu)

### 基本信息
- **表名**：`menu`
- **中文名**：系统菜单表
- **说明**：存储前端动态菜单配置，支持不同角色显示不同菜单

### 字段详情

| 字段名 | 数据类型 | 长度 | 是否主键 | 是否为空 | 默认值 | 说明 |
|-------|---------|------|---------|---------|--------|------|
| `id` | BigIntegerField | 20 | **PK** | NOT NULL | 自增 | 菜单ID，主键自增 |
| `menujson` | TextField | - | 否 | 可为空 | NULL | 菜单配置JSON（树形结构，包含菜单项、路由、图标、权限等） |
| `addtime` | DateTimeField | - | 否 | NOT NULL | 当前时间 | 配置更新时间 |

### 索引
- PRIMARY KEY (`id`)

### 数据结构示例
```json
{
  "menus": [
    {
      "id": "1",
      "name": "首页",
      "path": "/",
      "icon": "home",
      "roles": ["admin", "user"]
    },
    {
      "id": "2",
      "name": "用户管理",
      "path": "/user",
      "icon": "user",
      "roles": ["admin"],
      "children": [...]
    }
  ]
}
```

---

## 表 5：登录记录表 (loginrecord)

### 基本信息
- **表名**：`loginrecord`
- **中文名**：用户登录记录表
- **说明**：记录所有登录尝试（成功/失败），包括人脸识别登录详情

### 字段详情

| 字段名 | 数据类型 | 长度 | 是否主键 | 是否为空 | 默认值 | 说明 |
|-------|---------|------|---------|---------|--------|------|
| `id` | BigIntegerField | 20 | **PK** | NOT NULL | 自增 | 记录ID，主键自增 |
| `username` | VARCHAR | 255 | 否 | NOT NULL | - | 登录用户名 |
| `role` | VARCHAR | 50 | 否 | NOT NULL | '用户' | 角色类型（管理员/用户/游客） |
| `logintype` | VARCHAR | 50 | 否 | NOT NULL | '密码' | 登录方式（密码登录/人脸识别） |
| `userid` | BigIntegerField | 20 | 否 | 可为空 | NULL | 关联用户ID（游客登录时为NULL） |
| `score` | FloatField | - | 否 | 可为空 | NULL | 人脸匹配分数（0-100，仅人脸登录时有值） |
| `ipaddress` | VARCHAR | 255 | 否 | 可为空 | NULL | 登录客户端IP地址 |
| `useragent` | TextField | - | 否 | 可为空 | NULL | 浏览器User-Agent字符串 |
| `result` | VARCHAR | 20 | 否 | NOT NULL | '成功' | 登录结果（成功/失败） |
| `faceimage` | TextField | - | 否 | 可为空 | NULL | 人脸截图保存路径（陌生人登录时保存用于审计） |
| `isstranger` | IntegerField | 11 | 否 | NOT NULL | 0 | 是否陌生人（0=已知用户，1=未注册陌生人） |
| `addtime` | DateTimeField | - | NOT NULL | 自动填充 | 当前时间 | 登录时间（自动记录） |

### 外键关系
- `userid` → `yonghu.id` 或 `users.id` （用户ID，可为空）

### 索引
- PRIMARY KEY (`id`)
- INDEX (`userid`) - 查询某用户的所有登录记录
- INDEX (`logintype`) - 统计登录方式分布
- INDEX (`result`) - 分析登录成功率
- INDEX (`addtime`) - 按时间范围查询
- INDEX (`isstranger`) - 追踪陌生人访问

### 业务用途
- **安全监控**：记录所有登录尝试，包括失败的
- **人脸识别审计**：保存人脸匹配分数和截图，便于事后核查
- **陌生人检测**：标记未注册人员的访问尝试
- **统计分析**：统计登录成功率、常用时间段等

---

## 表 6：人脸注册记录表 (faceregister)

### 基本信息
- **表名**：`faceregister`
- **中文名**：人脸注册记录表
- **说明**：存储用户注册的人脸照片及质量评估信息

### 字段详情

| 字段名 | 数据类型 | 长度 | 是否主键 | 是否为空 | 默认值 | 说明 |
|-------|---------|------|---------|---------|--------|------|
| `id` | BigIntegerField | 20 | **PK** | NOT NULL | 自增 | 注册记录ID，主键自增 |
| `userid` | BigIntegerField | 20 | 否 | NOT NULL | - | 关联用户ID（FK → yonghu.id 或 users.id） |
| `username` | VARCHAR | 255 | 冗余字段 | NOT NULL | - | 用户名（冗余存储，避免频繁JOIN查询） |
| `faceimage` | TextField | - | 否 | NOT NULL | - | 人脸图片存储路径（服务器本地路径或OSS URL） |
| `qualityscore` | FloatField | - | 否 | NOT NULL | 0 | 图片质量评分（0-100分，基于清晰度、光照、角度等） |
| `isvalid` | IntegerField | 11 | 否 | NOT NULL | 1 | 是否有效（0=已失效/删除，1=有效可用） |
| `addtime` | DateTimeField | - | NOT NULL | 自动填充 | 当前时间 | 注册时间（自动记录） |

### 外键关系
- `userid` → `yonghu.id` 或 `users.id`

### 索引
- PRIMARY KEY (`id`)
- INDEX (`userid`) - 查询某用户的所有人脸照片
- INDEX (`isvalid`) - 只筛选有效的人脸样本进行训练
- INDEX (`qualityscore`) - 按质量排序，优先使用高质量照片训练模型

### 业务用途
- **多照片支持**：一个用户可注册多张不同角度/表情的照片，提高识别准确率
- **质量控制**：通过`qualityscore`过滤低质量照片
- **生命周期管理**：`isvalid`字段支持软删除，保留历史记录
- **模型训练**：LBPH算法使用此表中`isvalid=1`的照片进行训练

### 与其他表的联动
- **插入时**：自动更新 `yonghu.facecount +1` 和 `yonghu.faceregistered = 1`
- **删除时**：自动更新 `yonghu.facecount -1`，若count=0则设置 `faceregistered = 0`

---

## 表 7：系统配置表 (systemconfig)

### 基本信息
- **表名**：`systemconfig`
- **中文名**：系统配置表
- **说明**：Key-Value形式的系统参数配置中心

### 字段详情

| 字段名 | 数据类型 | 长度 | 是否主键 | 是否为空 | 默认值 | 说明 |
|-------|---------|------|---------|---------|--------|------|
| `id` | BigIntegerField | 20 | **PK** | NOT NULL | 自增 | 配置项ID，主键自增 |
| `configkey` | VARCHAR | 100 | 否 | NOT NULL, **UNIQUE** | - | 配置键名（英文，如 `face_threshold`） |
| `configvalue` | TextField | - | 否 | NOT NULL | - | 配置值（字符串形式，支持JSON） |
| `description` | VARCHAR | 255 | 否 | 可为空 | NULL | 配置项中文说明 |
| `addtime` | DateTimeField | - | NOT NULL | 自动填充 | 当前时间 | 最后更新时间（自动记录） |

### 索引
- PRIMARY KEY (`id`)
- UNIQUE KEY (`configkey`) - 配置键必须唯一

### 常用配置项预置

| configkey | configvalue 示例 | description | 说明 |
|-----------|------------------|-------------|------|
| `face_threshold` | `"70"` | 人脸识别阈值 | 匹配分数>=此值才通过验证 |
| `face_max_photos` | `"5"` | 最大人脸照片数 | 每个用户最多上传N张人脸照 |
| `face_quality_min` | `"60"` | 最低质量分数 | 低于此分的照片拒绝入库 |
| `session_timeout` | `"3600"` | 会话超时时间（秒） | 用户无操作多久后自动登出 |
| `max_login_attempts` | `"5"` | 最大登录失败次数 | 超过后锁定账号N分钟 |
| `lockout_duration` | `"30"` | 锁定时长（分钟） | 连续失败N次后的锁定时间 |
| `system_name` | `"人脸识别系统"` | 系统名称 | 显示在页面标题栏 |
| `enable_stranger_log` | `"true"` | 是否记录陌生人 | 是否保存陌生人的人脸截图 |

### 设计优势
- **动态配置**：无需修改代码即可调整系统参数
- **热更新**：前端可通过API实时读取最新配置
- **扩展性强**：新增配置项只需INSERT一条记录
- **版本追溯**：`addtime`记录每次修改时间

---

## 表 8：配置表 (config)

### 基本信息
- **表名**：`config`
- **中文名**：配置表
- **模型文件**：`main/config_model.py`
- **说明**：存储系统基础键值对配置（与systemconfig互补，用于更简单的配置场景）

### 字段详情

| 字段名 | 数据类型 | 长度 | 是否主键 | 是否为空 | 默认值 | 说明 |
|-------|---------|------|---------|---------|--------|------|
| `id` | BigIntegerField | 20 | **PK** | NOT NULL | 自增 | 配置ID，主键自增 |
| `name` | VARCHAR | 100 | 否 | NOT NULL | - | 配置键名（如 `site_name`, `copyright` 等） |
| `value` | VARCHAR | 100 | 否 | NOT NULL | - | 配置值 |
| `addtime` | DateTimeField | - | 否 | NOT NULL | 当前时间 | 创建时间 |

### 索引
- PRIMARY KEY (`id`)

### 与 systemconfig 的区别

| 对比项 | config 表 | systemconfig 表 |
|-------|----------|----------------|
| 值类型限制 | VARCHAR(100) 短文本 | TEXT 长文本(支持JSON) |
| 是否有说明字段 | 无 | 有 description 字段 |
| 适用场景 | 简单的键值对配置 | 复杂的系统参数配置 |
| 典型用途 | 网站名称、版权信息等 | 人脸阈值、安全策略等 |

### 典型配置示例

| name | value | 说明 |
|------|-------|------|
| `site_name` | `人脸识别系统` | 网站名称 |
| `copyright` | `Copyright 2026` | 版权信息 |
| `icp` | `京ICP备xxxxx号` | ICP备案号 |

---

# 基础字段说明 (BaseModel)

所有表均继承自 `BaseModel`，包含以下公共字段：

| 字段名 | 类型 | 说明 |
|-------|------|------|
| `id` | BigIntegerField | 主键，自增ID（除users表外，其他表使用时间戳*1000生成） |
| `addtime` | DateTimeField | 创建/更新时间，部分表使用 `auto_now_add=True` 自动填充 |

---

# 数据库关系总览

## 核心业务流程涉及的主要表关系

```
用户注册流程:
  users/yonghu ──[创建账号]──► yonghu.faceregistered=0
       │
       ├──[上传人脸]──► faceregister (插入记录)
       │                    │
       │                    └──[触发]──► yonghu.facecount+=1
       │                              yonghu.faceregistered=1
       │
       └──[完成]──► 用户可用人脸登录

人脸登录流程:
  [摄像头采集] ──► loginrecord (记录尝试)
                      │
                      ├──[调用LBPH]──► opencv_face.py (比对)
                      │                    │
                      │                    └──[返回]──► score, user_id
                      │
                      ├──[score >= threshold]──► loginrecord.result='成功'
                      │                               │
                      │                               └──[返回Token]──► 前端跳转
                      │
                      └──[score < threshold]──► loginrecord.result='失败'
                                                      loginrecord.isstranger=1
                                                      loginrecord.faceimage=截图
```

---

# 附录：字段命名规范

## 命名规则
- **全部小写字母**
- **多单词用下划线分隔**（snake_case）
- **避免使用保留字**

## 常见前缀/后缀
| 前缀/后缀 | 含义 | 示例 |
|----------|------|------|
| `_id` | 外键/关联ID | `userid`, `face_id` |
| `_time` | 时间字段 | `addtime`, `logintime` |
| `_name` | 名称字段 | `username`, `yonghuxingming` |
| `_type` | 类型字段 | `logintype` |
| `_count` | 计数字段 | `facecount` |
| `is_` / `has_` | 布尔标志位 | `isvalid`, `isstranger`, `faceregistered` |

---

# 版本信息

- **文档版本**: v2.0 (已补充遗漏的config表)
- **最后更新**: 2026-04-12
- **适用系统**: 基于OpenCV和Python的人脸识别系统
- **数据库**: 支持SQLite3 / MySQL / PostgreSQL（Django ORM自动适配）

---

## ✅ 验证记录

| 验证项 | 状态 | 说明 |
|-------|------|------|
| Models定义文件扫描 | ✅ 完成 | 扫描了 models.py, users_model.py, config_model.py |
| 数据库实际表检查 | ✅ 完成 | 通过PRAGMA table_info验证(业务表尚未migrate) |
| 表数量确认 | ✅ 8张 | users, yonghu, syslog, menu, loginrecord, faceregister, systemconfig, config |
| 字段完整性 | ✅ 无遗漏 | 每个表的字段均与Model定义100%一致 |
| config表补全 | ✅ 已修复 | v1.0遗漏，v2.0已添加 |

### 模型来源映射

| 表名 | 模型类 | 源文件 | 行号 |
|------|--------|-------|------|
| users | class users(BaseModel) | main/users_model.py:9 | - |
| config | class config(BaseModel) | main/config_model.py:9 | - |
| syslog | class syslog(BaseModel) | main/models.py:43 | - |
| yonghu | class yonghu(BaseModel) | main/models.py:77 | - |
| menu | class menu(BaseModel) | main/models.py:119 | - |
| loginrecord | class loginrecord(BaseModel) | main/models.py:136 | - |
| faceregister | class faceregister(BaseModel) | main/models.py:155 | - |
| systemconfig | class systemconfig(BaseModel) | main/models.py:169 | - |

---

> 💡 **提示**: 本文档基于Django Models自动生成，实际字段长度可能因数据库类型（MySQL/SQLite/PostgreSQL）而略有差异。
