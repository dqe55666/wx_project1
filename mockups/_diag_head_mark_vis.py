# -*- coding: utf-8 -*-
"""在图上画出检测到的 发顶线 / 下巴线 / 脸中心线，肉眼验证基准是否准确"""
import os
from PIL import Image, ImageDraw, ImageFont

SRC = r'D:\yxy\wx_project1\mockups\_nurses_3x4'
OUT = r'D:\yxy\wx_project1\mockups\_diag_head_mark.png'
ORDER = [u'肖雯遥', u'王一茜', u'彭彦博', u'方嘉倩', u'胡冰冰', u'谢远杰']
MANUAL_CHIN = {}          # 若自动下巴不准，可在此手动覆盖


def is_red(r, g, b):
    return r > 150 and (r - g) > 90 and (r - b) > 90


def is_skin(r, g, b):
    mx, mn = max(r, g, b), min(r, g, b)
    if mx - mn < 25:
        return False
    return (r > 110 and g > 45 and b > 25 and r > g and r > b
            and (r - g) >= 22 and (g - b) >= -10 and (r - b) >= 30)


def analyze(im):
    w, h = im.size
    px = im.load()
    band = int(h * 0.80)
    hair_top = next((y for y in range(band) if any(not is_red(*px[x, y]) for x in range(w))), 0)
    col = [0] * w
    for y in range(int(h * 0.55)):
        for x in range(w):
            if is_skin(*px[x, y]):
                col[x] += 1
    thr = max(4, int(h * 0.55 * 0.10))
    xs = [x for x in range(w) if col[x] >= thr]
    fx0, fx1 = xs[0], xs[-1]
    fw = fx1 - fx0 + 1
    rows = [sum(1 for x in range(fx0, fx1 + 1) if is_skin(*px[x, y])) for y in range(band)]
    pi = rows.index(max(rows))
    chin = next((y for y in range(pi, band) if rows[y] < fw * 0.62), band)
    return hair_top, chin, fx0, fx1


th = 520
pad = 12
cols = 3
cells = []
font = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 20)
for name in ORDER:
    src = Image.open(os.path.join(SRC, name + '.jpg')).convert('RGB')
    w, h = src.size
    ht, chin, fx0, fx1 = analyze(src)
    chin = MANUAL_CHIN.get(name, chin)
    s = th / float(h)
    im = src.resize((int(w * s), th), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    d.line((0, ht * s, im.size[0], ht * s), fill=(0, 220, 90), width=3)      # 发顶
    d.line((0, chin * s, im.size[0], chin * s), fill=(255, 200, 0), width=3)  # 下巴
    d.line(((fx0 + fx1) / 2 * s, 0, (fx0 + fx1) / 2 * s, th), fill=(0, 160, 255), width=2)
    cells.append((name, im, chin - ht))
cw = max(c[1].size[0] for c in cells)
canvas = Image.new('RGB', ((cw + pad) * cols + pad, (th + 34) * 2 + pad), (247, 247, 250))
dd = ImageDraw.Draw(canvas)
for i, (name, im, hh) in enumerate(cells):
    x = pad + (i % cols) * (cw + pad)
    y = pad + (i // cols) * (th + 34)
    canvas.paste(im, (x, y))
    dd.text((x, y + th + 4), u'%s  头高 %dpx' % (name, hh), fill=(35, 32, 42), font=font)
canvas.save(OUT, 'PNG')
print(u'saved %s   绿=发顶  黄=下巴  蓝=脸中心' % OUT)
