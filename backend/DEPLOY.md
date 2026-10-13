# Docker 服务器部署

以下命令在服务器项目的 `backend` 目录执行。服务器需要 Docker Engine 与 Docker Compose 插件。本方案只将 API 放进 Docker，使用 Linux 宿主机已有的 MySQL（`127.0.0.1:3306`）。

## 首次部署

1. 创建生产配置，并替换所有示例值：

```bash
cp .env.example .env
openssl rand -hex 32
```

将生成的随机值填入 `STAFF_TOKEN_SECRET` 和 `ADMIN_TOKEN_SECRET`。`DATABASE_URL` 使用服务器现有的 root 用户、root 密码和 `127.0.0.1:3306`；密码请使用 URL 安全字符（字母、数字、`-`、`_`），同时修改 `ADMIN_PASSWORD`，并按需配置高德密钥。

`.env` 中预置了 `PYTHON_IMAGE` 与 `PIP_INDEX_URL`，分别使用 DaoCloud Docker Hub 代理和清华 PyPI 镜像。若某一镜像暂时不可用，可改回官方源：

```env
PYTHON_IMAGE=python:3.13-slim
PIP_INDEX_URL=https://pypi.org/simple
```

容器经 Docker 默认网桥连接 MySQL，`172.17.%` 是 Docker 容器的来源网段；MySQL 不需要也不应暴露到公网。

2. 构建并启动：

```bash
docker compose up -d --build
docker compose ps
curl http://127.0.0.1:8000/api/health
```

首次启动会自动创建 `care_booking` 数据库、表结构和初始数据。管理端、员工端和客服端分别位于 `/admin/`、`/staff/`、`/support/`。

## 更新与排查

```bash
docker compose up -d --build
docker compose logs -f api
```

数据库由宝塔 MySQL 服务管理，请使用宝塔数据库备份功能或宿主机上的 `mysqldump` 备份。不要使用 `docker compose down -v` 试图清理数据库；本方案没有 Docker 数据库卷。

## 公网访问

API 监听服务器 `8000` 端口，MySQL 仍使用宿主机 `3306`。正式环境应使用 Nginx、Caddy 或云负载均衡为域名配置 HTTPS，并将请求反向代理到 `127.0.0.1:8000`。微信小程序和员工工作台的定位功能都需要 HTTPS；将该 HTTPS 域名加入微信小程序的 `request` 合法域名后，再把小程序的 `apiBaseUrl` 改为该域名。
