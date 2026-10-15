# -*- coding: utf-8 -*-
"""陪护师头像统一定标裁切（最终版）

原理：
  1. 自动定位「发顶 y」「下巴 y」→ 得到头部高度 head_h
  2. 统一目标：头部高度 = 裁切边长的 62%  →  side = head_h / 0.62
  3. 人头在画面里本来就偏大的（王一茜/彭彦博），side 会超过原图宽度，
     此时用**背景红做边缘复制延展**（不是纯色填充，保留原有渐变），
     保证 6 张的头部占比完全一致
  4. 底色不变：延展用的就是原图最外侧像素的颜色

输入：mockups/_nurses_3x4/  （原始 3:4 压缩图，未被裁过）
输出：assets/images/nurses/*.jpg  （400x400, q82, progressive, 剥离 EXIF）
"""
import os
from PIL import Image

PROJ = r'D:\yxy\wx_project1'
SRC = os.path.join(PROJ, 'mockups', '_nurses_3x4')
DST = os.path.join(PROJ, 'assets', 'images', 'nurses')
ORDER = [u'肖雯遥', u'王一茜', u'彭彦博', u'方嘉倩', u'胡冰冰', u'谢远杰']

TARGET_HEAD = 0.62      # 头部高度 / 裁切边长
HAIR_TOP_POS = 0.16     # 发顶在裁切框内的纵向位置
OUT_SIDE = 400
QUALITY = 82

# 自动检测不准时的手动覆盖（像素坐标，基于 3:4 原图）
MANUAL_CHIN = {u'王一茜': 250}


def is_red(r, g, b):
    return r > 150 and (r - g) > 90 and (r - b) > 90


def is_skin(r, g, b):
    mx, mn = max(r, g, b), min(r, g, b)
    if mx - mn < 25:
        return False
    return (r > 110 and g > 45 and b > 25 and r > g and r > b
            and (r - g) >= 22 and (g - b) >= -10 and (r - b) >= 30)


def analyze(im):
    """返回 (发顶y, 下巴y, 脸中心x)"""
    w, h = im.size
    px = im.load()
    band = int(h * 0.80)
    hair_top = next((y for y in range(band)
                     if any(not is_red(*px[x, y]) for x in range(w))), 0)
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
    return hair_top, chin, (fx0 + fx1) / 2.0


def expand_replicate(im, left, top, right, bottom):
    """用最外侧像素复制延展画布（背景是纯色，延展后无缝）"""
    w, h = im.size
    nw, nh = w + left + right, h + top + bottom
    out = Image.new('RGB', (nw, nh))
    out.paste(im, (left, top))
    if left:
        strip = im.crop((0, 0, 1, h))
        out.paste(strip.resize((left, h)), (0, top))
    if right:
        strip = im.crop((w - 1, 0, w, h))
        out.paste(strip.resize((right, h)), (left + w, top))
    if top:
        band = out.crop((0, top, nw, top + 1))
        out.paste(band.resize((nw, top)), (0, 0))
    if bottom:
        band = out.crop((0, top + h - 1, nw, top + h))
        out.paste(band.resize((nw, bottom)), (0, top + h))
    return out


def build(name):
    src = Image.open(os.path.join(SRC, name + '.jpg')).convert('RGB')
    w, h = src.size
    ht, chin, cx = analyze(src)
    chin = MANUAL_CHIN.get(name, chin)
    head_h = chin - ht

    side = int(round(head_h / TARGET_HEAD))
    side = min(side, h)                       # 纵向不能超过原图高度
    top = int(round(ht - side * HAIR_TOP_POS))
    left = int(round(cx - side / 2.0))

    pad_l = max(0, -left)
    pad_t = max(0, -top)
    pad_r = max(0, left + side - w)
    pad_b = max(0, top + side - h)
    canvas = expand_replicate(src, pad_l, pad_t, pad_r, pad_b)
    left += pad_l
    top += pad_t

    sq = canvas.crop((left, top, left + side, top + side))
    sq = sq.resize((OUT_SIDE, OUT_SIDE), Image.LANCZOS)
    out = os.path.join(DST, name + '.jpg')
    sq.save(out, 'JPEG', quality=QUALITY, optimize=True, progressive=True)
    return head_h, side, pad_l, pad_t, pad_r, pad_b, os.path.getsize(out) / 1024.0


def main():
    total = 0
    print('%-8s %-7s %-7s %-22s %s' % (u'姓名', u'头高', u'裁切边长', u'延展(左/上/右/下)', u'大小'))
    for name in ORDER:
        hh, side, pl, pt, pr, pb, kb = build(name)
        total += kb
        print('%-8s %5dpx  %5dpx   %3d/%-3d/%-3d/%-3d        %.1fKB'
              % (name, hh, side, pl, pt, pr, pb, kb))
    print(u'合计 %.1fKB    头部占比统一为 %.0f%%' % (total, TARGET_HEAD * 100))


if __name__ == '__main__':
    main()
