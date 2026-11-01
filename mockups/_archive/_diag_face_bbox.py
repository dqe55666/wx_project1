# -*- coding: utf-8 -*-
"""诊断：用肤色检测定位人脸框，看 6 张的人脸尺寸/位置是否可比"""
import os
from PIL import Image

SRC = r'D:\yxy\wx_project1\mockups\_nurses_3x4'
ORDER = [u'肖雯遥', u'王一茜', u'彭彦博', u'方嘉倩', u'胡冰冰', u'谢远杰']


def is_skin(r, g, b):
    """常见 RGB 肤色规则（避开纯红底：红底 g、b 极低）"""
    mx, mn = max(r, g, b), min(r, g, b)
    return (r > 95 and g > 40 and b > 20 and mx - mn > 15
            and abs(r - g) > 15 and r > g and r > b)


def face_bbox(im):
    w, h = im.size
    px = im.load()
    band = int(h * 0.72)
    minx, miny, maxx, maxy, n = w, band, -1, -1, 0
    for y in range(0, band):
        for x in range(0, w):
            r, g, b = px[x, y]
            if is_skin(r, g, b):
                n += 1
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
    return minx, miny, maxx, maxy, n


def band_of(h):
    return int(h * 0.72)


print('%-8s %-10s %-22s %-22s %s' % (u'姓名', u'尺寸', u'人脸框(x0,y0,x1,y1)', u'脸宽/脸高(占图)', u'像素质%'))
for name in ORDER:
    im = Image.open(os.path.join(SRC, name + '.jpg')).convert('RGB')
    w, h = im.size
    x0, y0, x1, y1, n = face_bbox(im)
    fw, fh = x1 - x0 + 1, y1 - y0 + 1
    print('%-8s %4dx%-5d (%3d,%3d,%3d,%3d)      %3dx%-3d  %4.1f%%x%4.1f%%      %.2f%%'
          % (name, w, h, x0, y0, x1, y1, fw, fh, 100.0 * fw / w, 100.0 * fh / h,
             100.0 * n / (w * band_of(h))))
