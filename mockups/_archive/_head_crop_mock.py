# -*- coding: utf-8 -*-
"""按“头部占比”重新裁切陪护师证件照，让圆形头像里脸更饱满、红底面积更小。
只输出对照图，不覆盖线上图片。
"""
import os
from PIL import Image, ImageDraw, ImageFont

SRC = r'D:\yxy\wx_project1\assets\images\nurses'
OUT = r'D:\yxy\wx_project1\mockups\_head_crop_mock.png'
ORDER = [u'肖雯遥', u'王一茜', u'彭彦博', u'方嘉倩', u'胡冰冰', u'谢远杰']


def subject_bbox(im):
    """纯红底以外的主体（头发/脸/衣服）外接框，只看上半部分避开衣服"""
    w, h = im.size
    px = im.load()
    band = int(h * 0.62)
    minx, miny, maxx, maxy = w, band, -1, -1
    step = 2
    for y in range(0, band, step):
        for x in range(0, w, step):
            r, g, b = px[x, y]
            if not (r > 150 and (r - g) > 90 and (r - b) > 90):
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
    return minx, miny, maxx, maxy


def head_crop(im, zoom=1.0):
    """以头部为中心的正方形裁切；zoom 越大脸越大"""
    w, h = im.size
    x0, y0, x1, y1 = subject_bbox(im)
    hw = max(1, x1 - x0)
    cx = (x0 + x1) // 2
    side = int(hw * 1.58 / zoom)
    side = min(side, w, h)
    left = cx - side // 2
    left = max(0, min(left, w - side))
    top = y0 - int(side * 0.15)
    top = max(0, min(top, h - side))
    return im.crop((left, top, left + side, top + side))


SCALE = 2
D = 200 * SCALE
GAP = 24 * SCALE
PAD = 32 * SCALE
TITLE_H = 76 * SCALE
LABEL_H = 58 * SCALE
COLS = 3
FONT = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 32 * SCALE)

MASK_BIG = Image.new('L', (D * 4, D * 4), 0)
ImageDraw.Draw(MASK_BIG).ellipse((0, 0, D * 4 - 1, D * 4 - 1), fill=255)
MASK = MASK_BIG.resize((D, D), Image.LANCZOS)


def grad(d, c1, c2):
    g = Image.new('RGB', (d, d))
    px = g.load()
    for y in range(d):
        for x in range(d):
            t = (x + y) / float(2 * d - 2)
            px[x, y] = (int(c1[0] + (c2[0] - c1[0]) * t),
                        int(c1[1] + (c2[1] - c1[1]) * t),
                        int(c1[2] + (c2[2] - c1[2]) * t))
    return g


RING_T = 5 * SCALE
RING_BIG = Image.new('L', ((D + RING_T * 2) * 4,) * 2, 0)
_d = ImageDraw.Draw(RING_BIG)
_d.ellipse((0, 0, (D + RING_T * 2) * 4 - 1, (D + RING_T * 2) * 4 - 1), fill=255)
_d.ellipse((RING_T * 4, RING_T * 4, (D + RING_T * 2) * 4 - 1 - RING_T * 4,
            (D + RING_T * 2) * 4 - 1 - RING_T * 4), fill=0)
RING_MASK = RING_BIG.resize((D + RING_T * 2, D + RING_T * 2), Image.LANCZOS)
GRAD = grad(D + RING_T * 2, (255, 95, 158), (255, 116, 171))

row_w = PAD * 2 + D * COLS + GAP * (COLS - 1)
row_h = TITLE_H + D + LABEL_H
canvas = Image.new('RGB', (row_w, row_h * 2 + 40 * SCALE), (247, 247, 250))
draw = ImageDraw.Draw(canvas)


def render(y0, zoom, label):
    draw.rectangle((0, y0, row_w, y0 + row_h - 1), fill=(255, 255, 255))
    draw.text((PAD, y0 + 24 * SCALE), u'陪护师  ' + label, font=FONT, fill=(35, 32, 42))
    base = y0 + TITLE_H
    for i, name in enumerate(ORDER):
        im = Image.open(os.path.join(SRC, name + '.jpg')).convert('RGB')
        im = head_crop(im, zoom).resize((D, D), Image.LANCZOS)
        cx = PAD + i % COLS * (D + GAP)
        cy = base + i // COLS * (D + LABEL_H)
        canvas.paste(GRAD, (cx - RING_T, cy - RING_T), RING_MASK)
        white = Image.new('RGB', (D, D), (255, 255, 255))
        canvas.paste(white, (cx, cy), MASK)
        inner = int(D * 0.055)
        canvas.paste(im.resize((D - inner * 2, D - inner * 2), Image.LANCZOS),
                     (cx + inner, cy + inner),
                     MASK.resize((D - inner * 2, D - inner * 2), Image.LANCZOS))
        bb = draw.textbbox((0, 0), name, font=FONT)
        draw.text((cx + D // 2 - (bb[2] - bb[0]) // 2, cy + D + 14 * SCALE),
                  name, font=FONT, fill=(35, 32, 42))


render(0, 1.0, u'A · 现状裁切')
render(row_h + 40 * SCALE, 1.28, u'B · 头部放大')

canvas.save(OUT, 'PNG')
print('saved %s %s' % (OUT, canvas.size))
