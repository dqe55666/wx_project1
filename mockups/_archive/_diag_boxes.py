# -*- coding: utf-8 -*-
"""把检测到的框画在原图上，肉眼确认到底框住了什么"""
import os
from PIL import Image, ImageDraw

SRC = r'D:\yxy\wx_project1\mockups\_nurses_3x4'
OUT = r'D:\yxy\wx_project1\mockups\_diag_boxes.png'
ORDER = [u'肖雯遥', u'王一茜', u'彭彦博', u'方嘉倩', u'胡冰冰', u'谢远杰']


def is_skin(r, g, b):
    mx, mn = max(r, g, b), min(r, g, b)
    return (r > 95 and g > 40 and b > 20 and mx - mn > 15
            and abs(r - g) > 15 and r > g and r > b)


def subject_bbox(im, ratio=0.62):
    w, h = im.size
    px = im.load()
    band = int(h * ratio)
    minx, miny, maxx, maxy = w, band, -1, -1
    for y in range(0, band, 2):
        for x in range(0, w, 2):
            r, g, b = px[x, y]
            if not (r > 150 and (r - g) > 90 and (r - b) > 90):
                minx = min(minx, x); maxx = max(maxx, x)
                miny = min(miny, y); maxy = max(maxy, y)
    return minx, miny, maxx, maxy


def face_bbox(im, ratio=0.50):
    w, h = im.size
    px = im.load()
    band = int(h * ratio)
    minx, miny, maxx, maxy = w, band, -1, -1
    for y in range(0, band):
        for x in range(0, w):
            r, g, b = px[x, y]
            if is_skin(r, g, b):
                minx = min(minx, x); maxx = max(maxx, x)
                miny = min(miny, y); maxy = max(maxy, y)
    return minx, miny, maxx, maxy


th = 520
cols, pad = 3, 12
cells = []
for name in ORDER:
    im = Image.open(os.path.join(SRC, name + '.jpg')).convert('RGB')
    s = th / float(im.size[1])
    im = im.resize((int(im.size[0] * s), th), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    sx0, sy0, sx1, sy1 = subject_bbox(Image.open(os.path.join(SRC, name + '.jpg')).convert('RGB'))
    fx0, fy0, fx1, fy1 = face_bbox(Image.open(os.path.join(SRC, name + '.jpg')).convert('RGB'))
    d.rectangle((sx0 * s, sy0 * s, sx1 * s, sy1 * s), outline=(0, 255, 0), width=3)
    d.rectangle((fx0 * s, fy0 * s, fx1 * s, fy1 * s), outline=(0, 140, 255), width=3)
    cells.append((name, im))

cw = max(c[1].size[0] for c in cells)
canvas = Image.new('RGB', ((cw + pad) * cols + pad, (th + 34) * 2 + pad), (247, 247, 250))
dd = ImageDraw.Draw(canvas)
try:
    from PIL import ImageFont
    font = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 22)
except Exception:
    font = None
for i, (name, im) in enumerate(cells):
    x = pad + (i % cols) * (cw + pad)
    y = pad + (i // cols) * (th + 34)
    canvas.paste(im, (x, y))
    dd.text((x, y + th + 5), name, fill=(35, 32, 42), font=font)
canvas.save(OUT, 'PNG')
print(u'saved %s  绿框=非红主体(0.62h)  蓝框=肤色(0.50h)' % OUT)
