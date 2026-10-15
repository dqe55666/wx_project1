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
- `_compress_nurses.py`：批量压缩陪护师头像（备份 + 缩放 + 剥离 EXIF）
- `_crop_nurses_square.py`：**当前头像由它产出**——按「头高/0.62」统一定标裁 400×400，源图取 `_nurses_3x4/`
- `_diag_head_mark_vis.py`：把检测到的发顶/下巴/脸中心线**画回原图**目视复核（改裁切算法后必跑）
- `_diag_head_width.py` / `_diag_face_profile.py` / `_diag_boxes.py`：诊断用（宽度剖面、肤色检测、检测框可视化）
- `_head_crop_tune.py` / `_head_crop_mock.py`：裁切参数对照
- `_nurse_variants.py`：头像边框方案对照（白框 / 粉环 / 细环）
- `_nurse_final_mock.py`：陪护师区块最终效果图（纯 PIL 渲染，无需浏览器）
- `_refresh_nurse_ring.py`：同步 `index-live-preview.html` 的陪护师区（base64 内联，可重复执行）
- `_refresh_preview_nurses.py` / `_update_preview.py`：早期预览同步脚本
- `_alt_bg_nurses.py`：红底 → 主题粉底备选方案（用户已决定不改，仅存档）
- `_circle_check.py`：圆形裁切校验图

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
