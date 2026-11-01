# -*- coding: utf-8 -*-
"""诊断：在不同纵向波段里，主体（非红底）的横向范围分别是多少。
用来找出「只包含头部、不包含肩膀」的波段。
"""
import os
from PIL import Image

SRC = r'D:\yxy\wx_project1\mockups\_nurses_3x4'
ORDER = [u'肖雯遥', u'王一茜', u'彭彦博', u'方嘉倩', u'胡冰冰', u'谢远杰']
BANDS = [0.30, 0.38, 0.45, 0.52, 0.60]


def extent(im, band_ratio):
    w, h = im.size
    px = im.load()
    band = int(h * band_ratio)
    minx, maxx, miny = w, -1, band
    for y in range(0, band):
        row_has = False
        for x in range(w):
            r, g, b = px[x, y]
            if not (r > 150 and (r - g) > 90 and (r - b) > 90):
                row_has = True
                if x < minx: minx = x
                if x > maxx: maxx = x
        if row_has and y < miny:
            miny = y
    return minx, miny, maxx


print('%-8s %-6s | %s' % (u'姓名', u'尺寸', u'   '.join(
    [u'<%.2fh 宽/占比' % b for b in BANDS])))
for name in ORDER:
    im = Image.open(os.path.join(SRC, name + '.jpg')).convert('RGB')
    w, h = im.size
    cells = []
    for b in BANDS:
        x0, y0, x1 = extent(im, b)
        ww = max(0, x1 - x0 + 1)
        cells.append(u'%3d/%4.1f%%' % (ww, 100.0 * ww / w))
    print('%-8s %4dx%-4d | %s' % (name, w, h, u'  '.join(cells)))
