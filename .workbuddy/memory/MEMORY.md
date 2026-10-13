# 项目长期约定 · wx_project1（医伴心途 · 陪诊小程序）

## UI 主题
- 主色 `#ff4d8d`；渐变 `#ff5f9e → #ff74ab`；浅底 `#fff0f6` / `#ffd9e8` / `#ffe3ef`
- 页面背景 `#ffffff` 或 `#f7f7fa`；正文 `#23202a`；次要文字 `#7e7689`；描边 `#f1eaf5`
- 全局 CSS 变量在 `app.wxss`；公共组件样式在 `assets/common.wxss`（26 个页面 import）
- **颜色同步必须同时覆盖 `.wxss`、wxml 内联 `style`、switch 组件的 `color` 属性**（已漏过两次）

## 交互规范（面向老年人）
- **禁止 `wx.vibrateShort` 震动**（用户明确：会吓到人）
- 按下反馈一律视觉化，三种类各司其职：
  - `.tap`：`scale(.96)` + `brightness(.93)` + `inset box-shadow` —— **只用于有背景的卡片**
  - `.tap-soft`：`scale(.94)` + `brightness(.94)` —— **用于透明容器**（用 `.tap` 会凭空显出方框）
  - `.tap-dim`：`opacity(.55~.6)` —— 用于纯文字按钮
- 可点区域不小于 88rpx；正文类字号 ≥ 28rpx（主流 30~34rpx），标题 40rpx+

## 图片素材
- 陪护师头像放 `assets/images/nurses/`，保留中文人名文件名（用户要求）
- 压缩规格：最长边 ≤ 480px + 质量 82 + progressive + **剥离 EXIF**；单张 < 30KB
- 原图备份在 `mockups/_nurses_originals/`（`mockups` 已被 `packOptions.ignore` 排除，不打包）
- **WXSS 与内联样式的 `background-image` 不支持本地路径**，只能用 `<image>` 标签
- 竖构图证件照用 `overflow:hidden` + `mode="widthFix"` 做**顶部对齐裁切**，避免居中裁切切掉额头

## 工具脚本（都在 `mockups/` 下，不参与打包，可复用）
- `_compress_nurses.py`：批量压缩陪护师头像（备份 + 缩放 + 剥离 EXIF）
- `_refresh_preview_nurses.py`：把预览 HTML 的陪护师区替换为真实头像（base64 内联）
- `_alt_bg_nurses.py`：红底 → 主题粉底备选方案（用户已决定不改，仅存档）
- `_update_preview.py`：同步预览中的姓名与新字号

## 环境与校验习惯
- Python venv（已装 Pillow 12.3）：`C:\Users\hhh\.workbuddy\binaries\python\envs\default`
- Node（校验 JS）：`C:\Users\hhh\.workbuddy\binaries\node\versions\22.22.2-6\node.exe`
- 校验方式：JS 用 `node --check`；wxss 查花括号配对；wxml 查 `<view>`/`</view>` 配对；json 用 `json.loads`

## 架构要点
- 后端 FastAPI + SQLAlchemy + MySQL（UI 改造全程未动后端）
- 高德 Web 服务经后端代理：`/api/location/regeo`、`/api/amap/hospitals`
- 首页 `pages/index` 是门户页（`navigationStyle: custom` 自定义导航栏）；下单表单在 `pages/visit/create`
- tabBar 5 项：主页 / 陪诊中 / 语音识别 / 消息 / 我的（纯文字无图标）
- `pages/booking/booking` 有样式但不在 app.json 页面列表，疑似废弃页
