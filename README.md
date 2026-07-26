# 医护/陪护上门预约小程序（护理版）
1
当前实现用户下单、员工 Web 接单与用户评价闭环：

- 管理端维护医院单位数据
- 小程序获取医院单位、服务项目
- 小程序获取用户定位并显示到医院单位的距离
- 用户填写预约信息并提交订单
- 后台维护员工档案，员工通过 Web 工作台接单
- 用户可在服务完成后对订单评分和评论
- 后端使用 FastAPI + MySQL 保存医院、服务项目和订单

## 后端启动

1. 创建 MySQL 数据库：

```sql
CREATE DATABASE IF NOT EXISTS care_booking
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

2. 安装依赖并启动：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

如果 MySQL 账号密码不是默认值，修改 `backend/.env` 里的 `DATABASE_URL`。
如果 `backend/.env` 已经配置过真实密码和高德密钥，不要再次执行 `cp .env.example .env`，否则会被示例占位值覆盖。
后端启动时会自动创建 `care_booking` 数据库和初始表。
定位地址解析由后端代理高德 Web 服务，配置 `backend/.env`：

```bash
AMAP_KEY=你的高德Web服务Key
AMAP_PRIVATE_KEY=你的高德Web服务安全密钥
STAFF_TOKEN_SECRET=生产环境随机密钥
```

## 管理端

后端启动后访问：

```text
http://127.0.0.1:8000/admin/
```

可以新增、编辑、停用医院单位和员工，也可以查看最近订单与接单员工。小程序首页会从 `/api/hospitals` 获取这些单位。
管理端支持用高德检索医院单位：

- 点击“定位搜附近30km”会使用浏览器定位，搜索当前位置周边医院
- 输入医院名称后点击“按名称搜索”可检索医院
- 点击搜索结果里的“填入”会把名称、地址、坐标、电话填到单位表单

## 员工 Web 工作台

后端启动后，员工访问：

```text
http://127.0.0.1:8000/staff/
```

员工登录账号默认为员工姓名，初始密码为 `123456`。登录后可查看待接订单、领取订单；接单后自动切换到“已接订单”，开始工作后自动切换到“工作中”，并可手动结束工作进入“已完成”。管理员新增员工时会自动创建同样的默认账号和密码。

管理端的订单列表支持为待接或已接订单指定员工，也支持手动结束或停止尚未结束的订单。

## 小程序端

用微信开发者工具打开项目根目录。默认接口地址在 `app.js`：

```js
apiBaseUrl: 'http://127.0.0.1:8000'
```

本地开发时如果请求被拦截，需要在微信开发者工具里关闭“校验合法域名、web-view、TLS 版本以及 HTTPS 证书”。

小程序不会直接请求高德，正式环境只需要把你的后端 HTTPS 域名配置为微信小程序 `request` 合法域名。

## 用户预约与评价

小程序首页可提交预约并在“我的预约”查看本机创建的订单。服务人员完成工作后，用户可以提交一次 1 至 5 分评分和评价内容；后台订单列表会展示该评价。
