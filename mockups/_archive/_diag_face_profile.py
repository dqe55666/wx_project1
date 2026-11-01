# -*- coding: utf-8 -*-
"""用「肤色列剖面 + 行剖面」稳健定位人脸（排除白衬衫、深色外套、红底的干扰）"""
import os
from PIL import Image

SRC = r'D:\yxy\wx_project1\mockups\_nurses_3x4'
ORDER = [u'肖雯遥', u'王一茜', u'彭彦博', u'方嘉倩', u'胡冰冰', u'谢远杰']
BAND = 0.55


def is_skin(r, g, b):
    mx, mn = max(r, g, b), min(r, g, b)
    if mx - mn < 25:          # 灰/白（含白衬衫、红底高光）直接排除
        return False
    return (r > 110 and g > 45 and b > 25 and r > g and r > b
            and (r - g) >= 22 and (g - b) >= -10 and (r - b) >= 30)


def face_box(im):
    w, h = im.size
    band = int(h * BAND)
    px = im.load()
    col_cnt = [0] * w
    for y in range(band):
        for x in range(w):
            r, g, b = px[x, y]
            if is_skin(r, g, b):
                col_cnt[x] += 1
    # 纵向肤色够多的列 = 脸部所在列（先取阈值，再做「找最长的连续段」）
    thr = max(4, int(band * 0.10))
    cols = [x for x in range(w) if col_cnt[x] >= thr]
    if not cols:
        return None
    # 找最长连续段（滤掉零散噪点）
    best = cur = (cols[0], cols[0])
    for x in cols[1:]:
        if x - cur[1] <= 6:
            cur = (cur[0], x)
        else:
            if cur[1] - cur[0] > best[1] - best[0]:
                best = cur
            cur = (x, x)
    if cur[1] - cur[0] > best[1] - best[0]:
        best = cur
    x0, x1 = best
    # 行剖面（只看脸列范围）
    row_cnt = []
    for y in range(band):
        c = 0
        for x in range(x0, x1 + 1):
            r, g, b = px[x, y]
            if is_skin(r, g, b):
                c += 1
        row_cnt.append(c)
    rthr = max(3, int((x1 - x0 + 1) * 0.18))
    rows = [y for y in range(band) if row_cnt[y] >= rthr]
    y0, y1 = rows[0], rows[-1]
    return x0, y0, x1, y1, (x1 - x0 + 1), (y1 - y0 + 1)


print('%-8s %-9s %-24s %-14s %s' % (u'姓名', u'尺寸', u'脸框(x0,y0,x1,y1)', u'脸宽x脸高', u'中心x/图宽  脸高/图高'))
for name in ORDER:
    im = Image.open(os.path.join(SRC, name + '.jpg')).convert('RGB')
    w, h = im.size
    r = face_box(im)
    if not r:
        print(name, u'未检出')
        continue
    x0, y0, x1, y1, fw, fh = r
    print('%-8s %4dx%-4d (%3d,%3d,%3d,%3d)  %4dx%-4d  %5.1f%%      %4.1f%%'
          % (name, w, h, x0, y0, x1, y1, fw, fh, 100.0 * (x0 + x1) / 2 / w, 100.0 * fh / h))
