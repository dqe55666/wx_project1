# -*- coding: utf-8 -*-
"""陪护师圆形头像三种边框方案对照（图片已统一为正方形头部裁切）"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC = r'D:\yxy\wx_project1\assets\images\nurses'
OUT = r'D:\yxy\wx_project1\mockups\_nurse_variants.png'
SHOW = [u'肖雯遥', u'王一茜', u'彭彦博']

S = 2
D = 190 * S
GAP = 24 * S
PAD = 30 * S
HEAD_H = 66 * S
LABEL_H = 54 * S
FONT = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 32 * S)
FONT_H = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 30 * S)


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


def grad(d, c1, c2):
    g = Image.new('RGB', (d, d))
    px = g.load()
    for y in range(d):
        for x in range(d):
            t = (x + y) / float(2 * d - 2)
            px[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    return g


def soft(outer, alpha, blur, dy):
    p = outer + 60
    layer = Image.new('RGBA', (p, p), (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse((30, 30 + dy, 30 + outer - 1, 30 + outer - 1),
                                  fill=(255, 77, 141, alpha))
    return layer.filter(ImageFilter.GaussianBlur(blur))


# 三种方案： (环厚, 白色留白厚, 阴影透明度, 模糊, 下沉)
VARIANTS = [
    (u'A · 细白框 + 柔阴影', 0, 6 * S, 70, 8, 3 * S),
    (u'B · 渐变环 5 + 白 5', 5 * S, 5 * S, 70, 8, 3 * S),
    (u'C · 极细环 3 + 白 7', 3 * S, 7 * S, 55, 7, 2 * S),
]

row_w = PAD * 2 + D * len(SHOW) + GAP * (len(SHOW) - 1)
row_h = HEAD_H + D + LABEL_H + 26 * S
canvas = Image.new('RGB', (row_w, row_h * len(VARIANTS) + 20 * S), (247, 247, 250))
draw = ImageDraw.Draw(canvas)

for vi, (title, ring, white, alpha, blur, dy) in enumerate(VARIANTS):
    y0 = vi * row_h
    draw.rectangle((0, y0, row_w, y0 + row_h - 1), fill=(255, 255, 255))
    draw.text((PAD, y0 + 22 * S), title, font=FONT_H, fill=(126, 118, 137))
    base = y0 + HEAD_H
    outer = D + (ring + white) * 2
    for i, name in enumerate(SHOW):
        im = Image.open(r'%s\%s.jpg' % (SRC, name)).convert('RGB').resize((D, D), Image.LANCZOS)
        cx = PAD + i * (D + GAP)
        cy = base
        sh = soft(outer, alpha, blur, dy)
        canvas.paste(sh.convert('RGB'), (cx - ring - white - 30, cy - ring - white - 30), sh.split()[3])
        if ring:
            canvas.paste(grad(outer, (255, 95, 158), (255, 143, 189)),
                         (cx - ring - white, cy - ring - white), annulus(outer, ring))
        else:
            canvas.paste(Image.new('RGB', (outer, outer), (255, 255, 255)),
                         (cx - white, cy - white), circle(outer))
        wd = D + white * 2
        if ring:
            canvas.paste(Image.new('RGB', (wd, wd), (255, 255, 255)),
                         (cx - white, cy - white), circle(wd))
        canvas.paste(im, (cx, cy), circle(D))
        b = draw.textbbox((0, 0), name, font=FONT)
        draw.text((cx + D // 2 - (b[2] - b[0]) // 2, cy + D + 14 * S), name,
                  font=FONT, fill=(35, 32, 42))

canvas.save(OUT, 'PNG')
print('saved %s %s' % (OUT, canvas.size))
