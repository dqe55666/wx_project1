# -*- coding: utf-8 -*-
"""定位每张图的「发顶 y」与「下巴 y」，作为统一定标的基准"""
import os
from PIL import Image

SRC = r'D:\yxy\wx_project1\mockups\_nurses_3x4'
ORDER = [u'肖雯遥', u'王一茜', u'彭彦博', u'方嘉倩', u'胡冰冰', u'谢远杰']


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
    hair_top = None
    for y in range(band):
        for x in range(w):
            if not is_red(*px[x, y]):
                hair_top = y
                break
        if hair_top is not None:
            break
    # 脸列范围（肤色列剖面）
    col = [0] * w
    for y in range(int(h * 0.55)):
        for x in range(w):
            if is_skin(*px[x, y]):
                col[x] += 1
    thr = max(4, int(h * 0.55 * 0.10))
    xs = [x for x in range(w) if col[x] >= thr]
    if not xs:
        return hair_top, None, None, None, None
    fx0, fx1 = xs[0], xs[-1]
    # 行剖面
    rows = []
    for y in range(band):
        c = sum(1 for x in range(fx0, fx1 + 1) if is_skin(*px[x, y]))
        rows.append(c)
    fw = fx1 - fx0 + 1
    peak = max(rows) if rows else 0
    # 下巴：从峰值往下，第一次低于 62% 脸宽的位置
    pi = rows.index(peak)
    chin = None
    for y in range(pi, band):
        if rows[y] < fw * 0.62:
            chin = y
            break
    if chin is None:
        chin = band
    return hair_top, chin, fx0, fx1, fw


print('%-8s %-9s %s' % (u'姓名', u'尺寸', u'发顶y  下巴y  头高  头高/图高   脸x范围  中心x%'))
for name in ORDER:
    im = Image.open(os.path.join(SRC, name + '.jpg')).convert('RGB')
    w, h = im.size
    ht, chin, fx0, fx1, fw = analyze(im)
    if chin is None:
        print('%-8s %4dx%-4d 未检出' % (name, w, h))
        continue
    print('%-8s %4dx%-4d %4d  %4d  %4d   %5.1f%%     %3d~%3d  %5.1f%%'
          % (name, w, h, ht, chin, chin - ht, 100.0 * (chin - ht) / h, fx0, fx1,
             100.0 * (fx0 + fx1) / 2 / w))
