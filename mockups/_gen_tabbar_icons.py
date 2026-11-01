# -*- coding: utf-8 -*-
"""生成 tabBar 图标（5 组 × 常态/选中）

规格：81×81 PNG RGBA，正常态 #b3adbd，选中态 #ff4d8d（与 app.json 的 color / selectedColor 一致）
画法：在 100×100 的坐标网格上绘制，4 倍超采样后缩到 81px 获得平滑边缘
输出：assets/images/tabbar/*.png
"""
import os
from PIL import Image, ImageChops, ImageDraw, ImageFilter

PROJ = r'D:\yxy\wx_project1'
OUTDIR = os.path.join(PROJ, 'assets', 'images', 'tabbar')
CHECK = os.path.join(PROJ, 'mockups', '_tabbar_check.png')

S = 4                      # 超采样倍数
GRID = 100
N = GRID * S
SIZE = 81                  # 最终边长
NORMAL = (179, 173, 189)   # #b3adbd
ACTIVE = (255, 77, 141)    # #ff4d8d


# ---------- 绘制小工具（坐标都用 100 网格） ----------
def new_mask():
    return Image.new('L', (N, N), 0)


def circ(d, cx, cy, r, v=255):
    d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), fill=v)


def rr(d, x0, y0, x1, y1, r, v=255):
    d.rounded_rectangle((x0 * S, y0 * S, x1 * S, y1 * S), radius=r * S, fill=v)


def ell(d, x0, y0, x1, y1, v=255):
    d.ellipse((x0 * S, y0 * S, x1 * S, y1 * S), fill=v)


def poly(d, pts, v=255):
    d.polygon([(x * S, y * S) for x, y in pts], fill=v)


def arc(d, x0, y0, x1, y1, w):
    d.arc((x0 * S, y0 * S, x1 * S, y1 * S), start=0, end=180, fill=255, width=int(w * S))


def person(d, hx, hy, hr, bx0, by0, bx1, by1):
    circ(d, hx, hy, hr)
    ell(d, bx0, by0, bx1, by1)


# ---------- 5 个图标 ----------
def icon_home():
    m = new_mask()
    d = ImageDraw.Draw(m)
    poly(d, [(50, 11), (93, 52), (93, 91), (7, 91), (7, 52)])
    rr(d, 40, 62, 60, 91, 5, 0)          # 门（挖空）
    return m


def icon_care():
    """陪诊中：一大一小两个人，中间留出透明缝，避免糊成一坨"""
    front = new_mask()
    person(ImageDraw.Draw(front), 34, 30, 14, 4, 42, 64, 122)

    back = new_mask()
    person(ImageDraw.Draw(back), 71, 26, 11, 46, 36, 96, 112)

    # 用模糊+阈值近似膨胀，在两个人之间留 ~2.5 格空隙
    gap = front.filter(ImageFilter.GaussianBlur(radius=2.5 * S)).point(
        lambda v: 255 if v > 55 else 0)
    back = ImageChops.subtract(back, gap)
    return ImageChops.lighter(back, front)


def icon_voice():
    m = new_mask()
    d = ImageDraw.Draw(m)
    arc(d, 23, 20, 77, 74, 6)            # 下方的半圆
    rr(d, 37, 9, 63, 58, 13)             # 话筒
    rr(d, 47, 71, 53, 87, 3)             # 杆
    rr(d, 33, 87, 67, 94, 3)             # 底座
    return m


def icon_message():
    m = new_mask()
    d = ImageDraw.Draw(m)
    rr(d, 9, 13, 91, 72, 19)
    poly(d, [(28, 64), (28, 91), (52, 68)])   # 小尾巴
    for cx in (33, 50, 67):                    # 三个点挖空
        circ(d, cx, 42, 5, 0)
    return m


def icon_mine():
    m = new_mask()
    d = ImageDraw.Draw(m)
    person(d, 50, 28, 16, 12, 42, 88, 124)
    return m


ICONS = [
    ('home', u'主页', icon_home),
    ('care', u'陪诊中', icon_care),
    ('voice', u'语音识别', icon_voice),
    ('message', u'消息', icon_message),
    ('mine', u'我的', icon_mine),
]


def tint(mask, color):
    rgba = Image.new('RGBA', mask.size, color + (0,))
    rgba.putalpha(mask)
    return rgba


def main():
    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)

    # 对照图：上排常态 / 下排选中，附中文标签
    try:
        from PIL import ImageFont
        font = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 22)
    except Exception:
        font = None
    cell = 140
    sheet = Image.new('RGB', (cell * len(ICONS), cell * 2 + 40), (255, 255, 255))
    ds = ImageDraw.Draw(sheet)

    for i, (key, label, fn) in enumerate(ICONS):
        mask = fn()
        for row, (color, suffix) in enumerate([(NORMAL, ''), (ACTIVE, '-active')]):
            img = tint(mask, color).resize((SIZE, SIZE), Image.LANCZOS)
            path = os.path.join(OUTDIR, key + suffix + '.png')
            img.save(path, 'PNG', optimize=True)
            big = img.resize((96, 96), Image.NEAREST)
            x = i * cell + (cell - 96) // 2
            y = row * cell + 14
            sheet.paste(big, (x, y), big)
            kb = os.path.getsize(path) / 1024.0
            print(u'%-22s %5.1fKB' % (key + suffix + '.png', kb))
        x = i * cell + cell // 2
        ds.text((x - 24, cell * 2 + 6), label, fill=(35, 32, 42), font=font)

    sheet.save(CHECK, 'PNG')
    print(u'\n对照图 -> %s' % CHECK)


if __name__ == '__main__':
    main()
