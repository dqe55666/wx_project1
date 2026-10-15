# -*- coding: utf-8 -*-
"""渲染首页「本期优秀陪护师」区块的最终效果图
方案 A：细白框 + 柔和投影（对应 pages/index/index.wxss 当前实现）
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC = r'D:\yxy\wx_project1\assets\images\nurses'
OUT = r'D:\yxy\wx_project1\mockups\_nurse_final_mock.png'
ORDER = [u'肖雯遥', u'王一茜', u'彭彦博', u'方嘉倩', u'胡冰冰', u'谢远杰']

S = 2
D = 194 * S            # 圆形照片直径
FRAME = 6 * S          # 白色相框
BORDER = 2 * S         # 极浅描边
GAP = 22 * S
PAD = 30 * S
COLS = 3
HEAD_H = 96 * S
LABEL_H = 56 * S
V_GAP = 22 * S

FONT_T = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 32 * S)
FONT_HD = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 34 * S)


def circle(d):
    big = Image.new('L', (d * 4, d * 4), 0)
    ImageDraw.Draw(big).ellipse((0, 0, d * 4 - 1, d * 4 - 1), fill=255)
    return big.resize((d, d), Image.LANCZOS)


def annulus(outer, thick):
    big = Image.new('L', (outer * 4,) * 2, 0)
    d = ImageDraw.Draw(big)
    d.ellipse((0, 0, outer * 4 - 1, outer * 4 - 1), fill=255)
    t = thick * 4
    d.ellipse((t, t, outer * 4 - 1 - t, outer * 4 - 1 - t), fill=0)
    return big.resize((outer, outer), Image.LANCZOS)


OUTER = D + FRAME * 2
MASK = circle(D)
FRAME_MASK = circle(OUTER)
BORDER_MASK = annulus(OUTER, BORDER)

_sh = Image.new('RGBA', (OUTER + 60, OUTER + 60), (0, 0, 0, 0))
ImageDraw.Draw(_sh).ellipse((30, 36, 30 + OUTER - 1, 36 + OUTER - 1), fill=(60, 30, 80, 34))
SHADOW = _sh.filter(ImageFilter.GaussianBlur(9))

row_w = PAD * 2 + D * COLS + GAP * (COLS - 1)
ROW_H = HEAD_H + (D + LABEL_H + V_GAP) * 2
canvas = Image.new('RGB', (row_w, ROW_H + 60 * S), (247, 247, 250))
draw = ImageDraw.Draw(canvas)

draw.rounded_rectangle((0, 30 * S, row_w - 1, ROW_H + 29 * S), radius=20 * S, fill=(255, 255, 255))

ty = 60 * S
draw.text((PAD, ty), u'\U0001F497', font=FONT_HD, fill=(255, 77, 141))
draw.text((PAD + 46 * S, ty + 2), u'本期优秀陪护师', font=FONT_HD, fill=(35, 32, 42))
more = u'查看更多 ›'
bb = draw.textbbox((0, 0), more, font=FONT_T)
draw.text((row_w - PAD - (bb[2] - bb[0]), ty + 6), more, font=FONT_T, fill=(126, 118, 137))

base = 30 * S + HEAD_H
for i, name in enumerate(ORDER):
    im = Image.open(os.path.join(SRC, name + '.jpg')).convert('RGB').resize((D, D), Image.LANCZOS)
    cx = PAD + i % COLS * (D + GAP)
    cy = base + i // COLS * (D + LABEL_H + V_GAP)
    canvas.paste(SHADOW.convert('RGB'), (cx - FRAME - 30, cy - FRAME - 30), SHADOW.split()[3])
    canvas.paste(Image.new('RGB', (OUTER, OUTER), (255, 255, 255)),
                 (cx - FRAME, cy - FRAME), FRAME_MASK)
    canvas.paste(Image.new('RGB', (OUTER, OUTER), (241, 234, 245)),
                 (cx - FRAME, cy - FRAME), BORDER_MASK)
    canvas.paste(im, (cx, cy), MASK)
    b = draw.textbbox((0, 0), name, font=FONT_T)
    draw.text((cx + D // 2 - (b[2] - b[0]) // 2, cy + D + 16 * S), name,
              font=FONT_T, fill=(35, 32, 42))

canvas.save(OUT, 'PNG')
print('saved %s %s' % (OUT, canvas.size))
