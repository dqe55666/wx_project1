# -*- coding: utf-8 -*-
"""微调头部裁切参数，三档对照（1.00 / 1.16 / 1.30），挑出最稳的一档"""
import os
from PIL import Image, ImageDraw, ImageFont

SRC = r'D:\yxy\wx_project1\assets\images\nurses'
OUT = r'D:\yxy\wx_project1\mockups\_head_crop_tune.png'
ORDER = [u'肖雯遥', u'王一茜', u'彭彦博', u'方嘉倩', u'胡冰冰', u'谢远杰']
ZOOMS = [(1.00, 0.15), (1.16, 0.17), (1.30, 0.19)]


def subject_bbox(im):
    w, h = im.size
    px = im.load()
    band = int(h * 0.62)
    minx, miny, maxx, maxy = w, band, -1, -1
    for y in range(0, band, 2):
        for x in range(0, w, 2):
            r, g, b = px[x, y]
            if not (r > 150 and (r - g) > 90 and (r - b) > 90):
                minx = min(minx, x); maxx = max(maxx, x)
                miny = min(miny, y); maxy = max(maxy, y)
    return minx, miny, maxx, maxy


def head_crop(im, zoom, top_r):
    w, h = im.size
    x0, y0, x1, y1 = subject_bbox(im)
    hw = max(1, x1 - x0)
    cx = (x0 + x1) // 2
    side = min(int(hw * 1.58 / zoom), w, h)
    left = max(0, min(cx - side // 2, w - side))
    top = max(0, min(int(y0 - side * top_r), h - side))
    return im.crop((left, top, left + side, top + side))


S, D, GAP, PAD = 2, 200 * 2, 24 * 2, 32 * 2
TITLE_H, LABEL_H, COLS = 76 * 2, 58 * 2, 3
FONT = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 32 * S)
MASK_BIG = Image.new('L', (D * 4, D * 4), 0)
ImageDraw.Draw(MASK_BIG).ellipse((0, 0, D * 4 - 1, D * 4 - 1), fill=255)
MASK = MASK_BIG.resize((D, D), Image.LANCZOS)

row_w = PAD * 2 + D * COLS + GAP * (COLS - 1)
row_h = TITLE_H + D + LABEL_H
canvas = Image.new('RGB', (row_w, row_h * len(ZOOMS) + 40 * S), (247, 247, 250))
draw = ImageDraw.Draw(canvas)

for k, (zoom, top_r) in enumerate(ZOOMS):
    y0 = k * (row_h + 40 * S)
    draw.rectangle((0, y0, row_w, y0 + row_h - 1), fill=(255, 255, 255))
    draw.text((PAD, y0 + 24 * S), u'zoom %.2f  顶部留白 %.0f%%' % (zoom, top_r * 100),
              font=FONT, fill=(35, 32, 42))
    base = y0 + TITLE_H
    for i, name in enumerate(ORDER):
        im = Image.open(os.path.join(SRC, name + '.jpg')).convert('RGB')
        im = head_crop(im, zoom, top_r).resize((D, D), Image.LANCZOS)
        cx = PAD + i % COLS * (D + GAP)
        cy = base + i // COLS * (D + LABEL_H)
        draw.ellipse((cx - 3 * S, cy - 3 * S, cx + D + 3 * S - 1, cy + D + 3 * S - 1),
                     fill=(255, 255, 255), outline=(241, 234, 245), width=2)
        canvas.paste(im, (cx, cy), MASK)
        bb = draw.textbbox((0, 0), name, font=FONT)
        draw.text((cx + D // 2 - (bb[2] - bb[0]) // 2, cy + D + 14 * S), name,
                  font=FONT, fill=(35, 32, 42))

canvas.save(OUT, 'PNG')
print('saved %s %s' % (OUT, canvas.size))
