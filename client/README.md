# client

Vue 3 + Element Plus 管理后台（可选）。

## 开发

```bash
npm install
npm run serve
```

默认开发端口见 `vue.config.js`（8081），需配置 `.env` 中后端 API 地址。

## 生产部署

```bash
npm run build
```

将 `dist` 内容复制到 `../server/templates/manage/`，通过 http://localhost:8000/cl3286667/manage/ 访问。

用户端主界面在 `server/templates/client/index.html`，由 Django 直接托管，无需构建本目录。
