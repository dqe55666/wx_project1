# -*- coding: utf-8 -*-
"""渲染首页「陪护师」区块的高保真对照图：A=纯白边圆框(现状)  B=主题渐变环
只生成对照图，不修改任何线上资源。
"""
import os
from PIL import Image, ImageDraw, ImageFont

SRC = r'D:\yxy\wx_project1\assets\images\nurses'
OUT = r'D:\yxy\wx_project1\mockups\_nurse_ring_mock.png'
ORDER = [u'肖雯遥', u'王一茜', u'彭彦博', u'方嘉倩', u'胡冰冰', u'谢远杰']

SCALE = 2               # 2 倍渲染，便于放大看细节
D = 200 * SCALE         # 圆形内容区直径（真机 200rpx）
GAP = 24 * SCALE        # 列间距（真机 24rpx）
PAD = 32 * SCALE        # 卡片左右内边距（真机 32rpx）
TITLE_H = 76 * SCALE    # 区块标题占位
LABEL_H = 58 * SCALE    # 名字行占位
COLS = 3

BG_CARD = (255, 255, 255)
BG_PAGE = (247, 247, 250)

FONT = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 32 * SCALE)
FONT_SM = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 26 * SCALE)


def load(name, d):
    """复刻真机 mode=widthFix 顶部对齐裁切"""
    im = Image.open(os.path.join(SRC, name + '.jpg')).convert('RGB')
    w, h = im.size
    nh = int(round(h * d / float(w)))
    im = im.resize((d, nh), Image.LANCZOS)
    return im.crop((0, 0, d, d)) if nh >= d else im


def circle_mask(d):
    big = Image.new('L', (d * 4, d * 4), 0)
    ImageDraw.Draw(big).ellipse((0, 0, d * 4 - 1, d * 4 - 1), fill=255)
    return big.resize((d, d), Image.LANCZOS)


def ring_mask(d, thick):
    """环形遮罩：外圆减内圆"""
    big = Image.new('L', (d * 4, d * 4), 0)
    dr = ImageDraw.Draw(big)
    dr.ellipse((0, 0, d * 4 - 1, d * 4 - 1), fill=255)
    inner = int(thick * 4)
    dr.ellipse((inner, inner, d * 4 - 1 - inner, d * 4 - 1 - inner), fill=0)
    return big.resize((d, d), Image.LANCZOS)


def grad(d, c1, c2):
    """135度线性渐变"""
    g = Image.new('RGB', (d, d))
    px = g.load()
    for y in range(d):
        for x in range(d):
            t = (x + y) / float(2 * d - 2)
            px[x, y] = (
                int(c1[0] + (c2[0] - c1[0]) * t),
                int(c1[1] + (c2[1] - c1[1]) * t),
                int(c1[2] + (c2[2] - c1[2]) * t),
            )
    return g


MASK = circle_mask(D)
RING_T = 5 * SCALE
RING_MASK = ring_mask(D + RING_T * 2, RING_T)
GRAD = grad(D + RING_T * 2, (255, 95, 158), (255, 116, 171))

row_w = PAD * 2 + D * COLS + GAP * (COLS - 1)
row_h = TITLE_H + D + LABEL_H
canvas = Image.new('RGB', (row_w, row_h * 2 + 40 * SCALE), BG_PAGE)
draw = ImageDraw.Draw(canvas, 'RGBA')


def render(y0, mode):
    # 卡片底
    draw.rectangle((0, y0, row_w, y0 + row_h - 1), fill=BG_CARD)
    # 区块标题
    draw.text((PAD, y0 + 24 * SCALE), u'陪护师', font=FONT, fill=(35, 32, 42))
    cy = y0 + TITLE_H
    for i, name in enumerate(ORDER):
        cx = PAD + i % COLS * (D + GAP)
        cyy = cy + i // COLS * (D + LABEL_H)
        im = load(name, D)
        if mode == 'ring':
            # 先贴渐变环
            ring_box = (cx - RING_T, cyy - RING_T)
            canvas.paste(GRAD, ring_box, RING_MASK)
            # 再贴白圈（内衬）
            white = Image.new('RGB', (D, D), (255, 255, 255))
            white_d = Image.new('L', (D * 4, D * 4), 0)
            ImageDraw.Draw(white_d).ellipse((0, 0, D * 4 - 1, D * 4 - 1), fill=255)
            wm = white_d.resize((D, D), Image.LANCZOS)
            canvas.paste(white, (cx, cyy), wm)
            inner = int(D * 0.07)
            canvas.paste(im.resize((D - inner * 2, D - inner * 2), Image.LANCZOS),
                         (cx + inner, cyy + inner),
                         circle_mask(D - inner * 2))
        else:
            # 现状：白边 + 淡描边
            draw.ellipse((cx - 3 * SCALE, cyy - 3 * SCALE, cx + D + 3 * SCALE - 1, cyy + D + 3 * SCALE - 1),
                         fill=(255, 255, 255), outline=(241, 234, 245), width=2)
            canvas.paste(im, (cx, cyy), MASK)
        # 名字
        bb = draw.textbbox((0, 0), name, font=FONT)
        tw = bb[2] - bb[0]
        draw.text((cx + D // 2 - tw // 2, cyy + D + 14 * SCALE), name, font=FONT, fill=(35, 32, 42))


render(0, 'plain')
render(row_h + 40 * SCALE, 'ring')
canvas.save(OUT, 'PNG')
print('saved %s %s' % (OUT, canvas.size))
