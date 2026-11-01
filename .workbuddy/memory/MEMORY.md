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
- **目录约定**（`assets/images/` 下按用途分文件夹）：
  - `nurses/` —— 陪护师头像（中文人名文件名，用户要求）
  - `bg/` —— 页面背景插画（如 `hospital.jpg` 卡通医院大楼）
  - `login/` —— 登录/引导类插画（如 `care.jpg` 暖色诊所门口）
- 大图插画规格：宽度 ≤ **1240px**（3 倍图够用）+ q80 + progressive + 剥 EXIF；单张 ≤ 200KB
- 陪护师头像放 `assets/images/nurses/`，保留中文人名文件名（用户要求）
- 压缩规格：最长边 ≤ 480px + 质量 82 + progressive + **剥离 EXIF**；单张 < 30KB
- 原图备份在 `mockups/_nurses_originals/`、`mockups/_import_originals/`（`mockups` 已被 `packOptions.ignore` 排除，不打包）
- **WXSS 与内联样式的 `background-image` 不支持本地路径**，只能用 `<image>` 标签（用 `position:absolute` + `mode="aspectFill"` 铺满，或 `widthFix` 定宽）
- **陪护师头像最终形态**：文件已裁成 **400×400 正方形**（按头部占比统一定标），页面用圆形展示
  - 定标算法：`发顶y`=首行非背景像素（稳）；`下巴y`=肤色行剖面从峰值下探首次跌破「脸宽×62%」（**必须画回原图目视复核**）；`脸中心x`=肤色列剖面最长连续段中点
  - 统一目标：`裁切边长 = 头高 / 0.62`，发顶固定放在裁切框 **16%** 处
  - 头天生占满画幅时（王一茜/彭彦博），用 **`expand_replicate`（复制最外侧一列/行）延展背景红**，比重算阈值可靠
  - 脚本 `mockups/_crop_nurses_square.py`（**源图取 `mockups/_nurses_3x4/`，可重复执行**，不会二次裁切）
  - **红底保持不变**（用户明确要求），延展用的就是原图边缘的红
  - 展示：`.avatar`(210rpx 圆, 白底, padding 6rpx, `border:2rpx solid #f1eaf5`, 柔阴影) > `.avatar-inner`(`overflow:hidden`+`border-radius:50%` 负责裁圆) > `<image mode="widthFix">`
  - 曾试过主题渐变环（`mockups/_nurse_variants.py` B/C 方案）——**结论：不加环最干净**，粉环与红底相邻反而更花
  - **踩过的坑**：不要用「非背景主体的整块 bbox 宽度」当头部宽度——蓬松头发（谢远杰）、深色外套、白衬衫都会污染，导致各图脸大小不一致

## 工具脚本（都在 `mockups/` 下，不参与打包，可复用）
**顶层只留这 5 个常用 + 3 个备份目录 + 1 个预览页**（2026-10-20 清理过，别再把一次性诊断堆在顶层）：
- `_crop_nurses_square.py`：**当前头像由它产出**——按「头高/0.62」统一定标裁 400×400，源图取 `_nurses_3x4/`
- `_import_images.py`：导入新插画（`SRC_MAP` 里加一行）+ 缩放 1240px + 压缩 + 备份原图
- `_refresh_nurse_ring.py`：同步 `index-live-preview.html` 的陪护师区（base64 内联，可重复执行）
- `_diag_head_mark_vis.py`：把检测到的发顶/下巴/脸中心线**画回原图**目视复核（改裁切算法后必跑）
- `_compress_nurses.py`：批量压缩陪护师头像（备份 + 缩放 + 剥离 EXIF）
- `index-live-preview.html`：首页实时预览
- 备份目录：`_nurses_originals/`（原始大图）、`_nurses_3x4/`（3:4 压缩版，裁切源）、`_import_originals/`（插画原图）
- `_archive/`：一次性诊断脚本与旧预览页的归档（`_diag_*`、`_head_crop_*`、`_nurse_variants`、`_pink_bg/`、旧 html 等），**确认不要了可整目录删掉**

**习惯**：一次性诊断用完就移进 `_archive/`，不要堆在顶层。

## 环境与校验习惯
- Python venv（已装 Pillow 12.3）：`C:\Users\hhh\.workbuddy\binaries\python\envs\default`
- Node（校验 JS）：`C:\Users\hhh\.workbuddy\binaries\node\versions\22.22.2-6\node.exe`
- 校验方式：JS 用 `node --check`；wxss 查花括号配对；wxml 查 `<view>`/`</view>` 配对；json 用 `json.loads`

## 架构要点
- 后端 FastAPI + SQLAlchemy + MySQL（UI 改造全程未动后端）
- **⚠️ `app.js` 的 `apiBaseUrl` 是 `http://127.0.0.1:8000`（本机）**——只有开发者本机能连上；别人手机上打开小程序拿不到数据。要让别人用，后端得部署到公网 HTTPS 域名并在小程序后台配 request 合法域名
- 高德 Web 服务经后端代理：`/api/location/regeo`、`/api/amap/hospitals`
- 首页 `pages/index` 是门户页（`navigationStyle: custom` 自定义导航栏）；下单表单在 `pages/visit/create`
- **登录页 `pages/login/login`**：整屏登录（custom 导航），上 46% 是 `assets/images/bg/hospital.jpg` 背景 + 渐变遮罩，下方白色面板内嵌 `assets/images/login/care.jpg` 主视觉；入口在 `pages/mine/index` 的登录按钮（`wx.navigateTo`），**启动不强制登录**
- tabBar 5 项：主页 / 陪诊中 / 语音识别 / 消息 / 我的，**已有图标**（`assets/images/tabbar/`，81×81 PNG，常态 `#b3adbd` / 选中 `#ff4d8d`，用 `mockups/_gen_tabbar_icons.py` 生成）
- **首页「服务医院」列表**：平铺行 + 1px 分隔线（不是卡片）；行内 = 132rpx 方形缩略图 + 医院名 + 「距您 x」+ 三甲/综合医院标签 + 重点科室
  - 后端 `hospital_units` 表只有 name/address/经纬度/电话，**等级、类型、重点科室由前端 `HOSPITAL_META_RULES` 按名称匹配**（加字段后删掉）
  - 缩略图暂时全部复用 `assets/images/bg/hospital.jpg`，换成各家实景图时改 `HOSPITAL_IMAGE` 即可
  - `formatDistance()`：1km 内显示米，否则 1 位小数
- `pages/booking/booking` 有样式但不在 app.json 页面列表，疑似废弃页
