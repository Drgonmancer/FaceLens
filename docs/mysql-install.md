# MySQL 8.0 详细安装教程

> 本教程适用于 Windows 10/11 系统，详细讲解 MySQL 8.0 的下载、安装、配置全过程。

---

## 目录

- [一、下载 MySQL](#一下载-mysql)
- [二、安装 MySQL](#二安装-mysql)
- [三、配置环境变量](#三配置环境变量)
- [四、验证安装](#四验证安装)
- [五、常见问题](#五常见问题)

---

## 一、下载 MySQL

### 步骤 1：访问 MySQL 官网

打开浏览器，访问 MySQL 官方下载页面：

```
https://dev.mysql.com/downloads/installer/
```

**页面截图位置**：页面顶部标题为 "MySQL Installer for Windows"

---

### 步骤 2：选择安装包

在页面中找到以下内容：

| 选项 | 说明 |
|------|------|
| **MySQL Installer for Windows** | Windows 安装程序 |

点击下方的 **"Download"** 按钮

**页面截图位置**：在 "MySQL Installer for Windows" 标题下方，蓝色 "Download" 按钮

---

### 步骤 3：登录或跳过登录

会弹出登录页面，有两个选项：

1. **Sign Up**：注册 MySQL 账号（需要邮箱验证）
2. **No thanks, just start my download**：直接下载（推荐）

**点击 "No thanks, just start my download."** 链接

**页面截图位置**：页面中间，灰色文字链接

---

### 步骤 4：下载安装包

浏览器会自动下载文件，文件名类似：

```
mysql-installer-community-8.0.36.0.msi
```

文件大小约 **450MB**，下载时间取决于网络速度。

**截图位置**：浏览器下载进度条

---

## 二、安装 MySQL

### 步骤 5：运行安装程序

下载完成后，双击运行下载的 `.msi` 文件

**截图位置**：文件所在文件夹，双击 `mysql-installer-community-8.0.36.0.msi`

---

### 步骤 6：选择安装类型

安装程序启动后，会显示以下选项：

| 选项 | 说明 | 推荐度 |
|------|------|--------|
| **Developer Default** | 开发者默认（包含所有开发工具） | ⭐⭐⭐⭐⭐ |
| **Server only** | 仅服务器（只安装 MySQL Server） | ⭐⭐⭐ |
| **Client only** | 仅客户端（只安装客户端工具） | ⭐ |
| **Full** | 完整安装（所有组件） | ⭐⭐⭐⭐ |
| **Custom** | 自定义安装（手动选择组件） | ⭐⭐⭐ |

**选择 "Developer Default"**（推荐新手）

**截图位置**：安装向导第一页，5个选项的圆形图标

---

### 步骤 7：检查安装要求

点击 "Next" 后，会显示安装要求检查：

| 检查项 | 状态 |
|--------|------|
| Microsoft .NET Framework 4.5.2 | ✅ Required（必须安装） |

如果显示 "Required"，点击 **"Execute"** 按钮安装 .NET Framework

**截图位置**：列表中显示 "Required" 的项目，右侧 "Execute" 按钮

---

### 步骤 8：安装 .NET Framework（如需要）

如果上一步需要安装 .NET Framework：

1. 点击 "Execute" 后会打开 .NET Framework 下载页面
2. 下载并安装 .NET Framework 4.5.2
3. 安装完成后，回到 MySQL 安装向导
4. 点击 "Next" 继续

**截图位置**：.NET Framework 安装向导

---

### 步骤 9：确认安装组件

点击 "Next" 后，会显示将要安装的组件列表：

| 组件 | 说明 |
|------|------|
| MySQL Server 8.0.xx | MySQL 数据库服务器 |
| MySQL Workbench 8.0.xx | MySQL 图形化管理工具 |
| MySQL Shell 8.0.xx | MySQL 命令行工具 |
| MySQL Router 8.0.xx | MySQL 路由器 |
| MySQL for Visual Studio | Visual Studio 插件 |
| Connector/ODBC | ODBC 驱动 |
| Connector/Python | Python 驱动 |

**确认无误后，点击 "Next"**

**截图位置**：组件列表，每个组件前面有复选框

---

### 步骤 10：开始安装

点击 "Execute" 开始安装所有组件

**截图位置**：右下角 "Execute" 按钮

安装过程需要 **3-5 分钟**，会显示进度条。

**截图位置**：安装进度条，百分比数字

---

### 步骤 11：配置 MySQL Server

所有组件安装完成后，会自动进入配置向导。

**点击 "Next"**

**截图位置**：配置向导第一页，"Next" 按钮

---

### 步骤 12：选择配置类型

选择配置类型：

| 选项 | 说明 | 推荐度 |
|------|------|--------|
| **Development Computer** | 开发电脑（占用资源少） | ⭐⭐⭐⭐⭐ |
| **Server Computer** | 服务器电脑（占用资源多） | ⭐⭐⭐ |
| **Dedicated Computer** | 专用服务器（最大性能） | ⭐⭐ |

**选择 "Development Computer"**

**截图位置**：3个选项的圆形图标

---

### 步骤 13：配置网络

配置网络设置：

| 选项 | 说明 | 推荐值 |
|------|------|--------|
| **Config Type** | 配置类型 | Development Computer |
| **Port** | 端口号 | 3306（默认） |
| **Open Windows Firewall port for network access** | 开放防火墙端口 | ✅ 勾选 |

**保持默认设置，点击 "Next"**

**截图位置**：端口号输入框，防火墙复选框

---

### 步骤 14：设置认证方式

选择认证方式：

| 选项 | 说明 | 推荐度 |
|------|------|--------|
| **Use Strong Password Encryption (Recommended)** | 强密码加密（推荐） | ⭐⭐⭐⭐⭐ |
| **Use Legacy Authentication Method** | 传统认证方式 | ⭐ |

**选择 "Use Strong Password Encryption (Recommended)"**

**截图位置**：两个选项的单选按钮

---

### 步骤 15：设置 root 密码 ⚠️ 重要！

设置 MySQL 管理员账号（root）的密码：

| 字段 | 说明 | 要求 |
|------|------|------|
| **MySQL Root Password** | root 密码 | 至少 8 个字符，包含字母和数字 |
| **Repeat Password** | 确认密码 | 必须与上面一致 |

**⚠️ 重要提示：请务必记住这个密码！后续配置数据库时需要用到！**

示例密码：`MySql@1234`（请自行设置）

**截图位置**：两个密码输入框

**输入完成后，点击 "Next"**

---

### 步骤 16：配置 Windows 服务

配置 MySQL 作为 Windows 服务：

| 选项 | 说明 | 推荐值 |
|------|------|--------|
| **Configure MySQL Server as a Windows Service** | 配置为 Windows 服务 | ✅ 勾选 |
| **Windows Service Name** | 服务名称 | MySQL80（默认） |
| **Start the MySQL Server at System Startup** | 系统启动时自动启动 | ✅ 勾选 |
| **Run Windows Service as...** | 服务运行账号 | Standard System Account（默认） |

**保持默认设置，点击 "Next"**

**截图位置**：服务名称输入框，复选框

---

### 步骤 17：应用配置

点击 **"Execute"** 应用所有配置

**截图位置**：右下角 "Execute" 按钮

配置过程需要 **30 秒 - 1 分钟**。

**截图位置**：配置进度条

---

### 步骤 18：完成配置

配置完成后，点击 **"Finish"**

**截图位置**：右下角 "Finish" 按钮

---

### 步骤 19：完成安装

所有配置完成后，会显示安装完成页面。

**点击 "Finish"** 完成整个安装过程

**截图位置**：右下角 "Finish" 按钮

---

## 三、配置环境变量

### 步骤 20：打开系统环境变量

1. 按 `Win + R` 键，打开"运行"对话框
2. 输入 `sysdm.cpl`，按回车

**截图位置**："运行"对话框，输入框

---

### 步骤 21：打开环境变量设置

在"系统属性"窗口中：

1. 点击 **"高级"** 选项卡
2. 点击 **"环境变量"** 按钮

**截图位置**：窗口底部 "环境变量" 按钮

---

### 步骤 22：编辑系统变量

在"环境变量"窗口中：

1. 在 **"系统变量"** 区域（下方）
2. 找到 **"Path"** 变量
3. 选中 "Path"，点击 **"编辑"**

**截图位置**：系统变量区域，"Path" 变量，"编辑" 按钮

---

### 步骤 23：添加 MySQL 路径

在"编辑环境变量"窗口中：

1. 点击右侧 **"新建"** 按钮
2. 输入 MySQL 的 bin 目录路径：

```
C:\Program Files\MySQL\MySQL Server 8.0\bin
```

**⚠️ 注意：如果你的 MySQL 安装在其他位置，请修改为实际路径**

**截图位置**：新建的输入框

3. 点击 **"确定"** 保存

**截图位置**：右下角 "确定" 按钮

---

### 步骤 24：确认保存

依次点击所有窗口的 **"确定"** 按钮关闭

**截图位置**：每个窗口的 "确定" 按钮

---

## 四、验证安装

### 步骤 25：打开命令提示符

按 `Win + R`，输入 `cmd`，按回车

**截图位置**："运行"对话框，输入 `cmd`

---

### 步骤 26：验证 MySQL 版本

在命令提示符中输入：

```bash
mysql --version
```

**按回车**

如果安装成功，会显示类似：

```
mysql  Ver 8.0.36 for Win64 on x86_64 (MySQL Community Server - GPL)
```

**截图位置**：命令提示符窗口，显示版本信息

---

### 步骤 27：登录 MySQL

在命令提示符中输入：

```bash
mysql -u root -p
```

**按回车**

会提示输入密码，输入你在步骤 15 中设置的 root 密码

**按回车**

如果登录成功，会显示：

```
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 8
Server version: 8.0.36 MySQL Community Server - GPL

Copyright (c) 2000, 2024, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input.

mysql>
```

**截图位置**：命令提示符窗口，显示 MySQL 提示符 `mysql>`

---

### 步骤 28：退出 MySQL

输入：

```bash
exit
```

**按回车**

退出 MySQL 命令行

---

## 五、常见问题

### Q1: 安装时提示 "无法访问网络"

**解决方案**：

1. 检查网络连接是否正常
2. 关闭防火墙或杀毒软件后重试
3. 如果仍然失败，尝试离线安装包

---

### Q2: 安装后命令提示符中无法运行 mysql 命令

**解决方案**：

1. 确认已正确配置环境变量（步骤 20-24）
2. 重启命令提示符窗口
3. 如果仍然失败，重启电脑

---

### Q3: 忘记 root 密码怎么办？

**解决方案**：

1. 停止 MySQL 服务
   - 按 `Win + R`，输入 `services.msc`
   - 找到 "MySQL80" 服务，右键 → 停止

2. 以安全模式启动 MySQL
   ```bash
   mysqld --skip-grant-tables
   ```

3. 新开命令提示符，重置密码
   ```bash
   mysql -u root
   USE mysql;
   UPDATE user SET authentication_string=PASSWORD('新密码') WHERE User='root';
   FLUSH PRIVILEGES;
   exit;
   ```

4. 重启 MySQL 服务

---

### Q4: MySQL 服务无法启动

**解决方案**：

1. 检查端口 3306 是否被占用
   ```bash
   netstat -ano | findstr :3306
   ```

2. 如果被占用，停止占用该端口的程序

3. 或修改 MySQL 配置文件中的端口号
   - 打开 `C:\ProgramData\MySQL\MySQL Server 8.0\my.ini`
   - 修改 `port=3306` 为其他端口

---

### Q5: 卸载 MySQL

**卸载步骤**：

1. 停止 MySQL 服务
   - 按 `Win + R`，输入 `services.msc`
   - 找到 "MySQL80" 服务，右键 → 停止

2. 卸载 MySQL
   - 控制面板 → 程序和功能
   - 找到 "MySQL Server 8.0"
   - 右键 → 卸载

3. 删除残留文件
   - `C:\Program Files\MySQL`
   - `C:\ProgramData\MySQL`
   - `C:\Users\你的用户名\AppData\Roaming\MySQL`

4. 删除注册表项（可选）
   - 按 `Win + R`，输入 `regedit`
   - 找到 `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\MySQL80`
   - 删除该键

---

## 安装完成！

恭喜！MySQL 8.0 已成功安装并配置。

现在你可以：

1. 运行 FaceGuard 项目的 `install.bat` 脚本
2. 在配置向导中输入你的 MySQL root 密码
3. 开始使用人脸识别系统！

---

**如有问题，请参考：**

- MySQL 官方文档：https://dev.mysql.com/doc/
- 提交 Issue：https://github.com/your-repo/issues
