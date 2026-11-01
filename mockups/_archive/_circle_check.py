# -*- coding: utf-8 -*-
"""模拟首页陪护师的圆形头像裁切效果，输出一张检查图（不影响线上图片）"""
import os
from PIL import Image, ImageDraw

SRC = r'D:\yxy\wx_project1\assets\images\nurses'
OUT = r'D:\yxy\wx_project1\mockups\_circle_check.png'
ORDER = [u'肖雯遥', u'王一茜', u'彭彦博', u'方嘉倩', u'胡冰冰', u'谢远杰']

D = 190          # 圆形内容区直径（对应真机 190rpx）
COLS = 3
PAD = 22
LABEL_H = 30
FRAME = 6        # 白边厚度

rows = (len(ORDER) + COLS - 1) // COLS
cell_w = D + PAD * 2
cell_h = D + PAD * 2 + LABEL_H

canvas = Image.new('RGB', (cell_w * COLS, cell_h * rows), (247, 247, 250))
draw = ImageDraw.Draw(canvas)

# 圆形遮罩（4 倍超采样，获得平滑边缘）
big = Image.new('L', (D * 4, D * 4), 0)
ImageDraw.Draw(big).ellipse((0, 0, D * 4 - 1, D * 4 - 1), fill=255)
MASK = big.resize((D, D), Image.LANCZOS)

for i, name in enumerate(ORDER):
    im = Image.open(os.path.join(SRC, name + '.jpg')).convert('RGB')
    w, h = im.size
    # 复刻真机 mode="widthFix"：按宽度撑满，高度等比，顶部对齐后裁掉下方
    nh = int(round(h * D / float(w)))
    im = im.resize((D, nh), Image.LANCZOS)
    im = im.crop((0, 0, D, D)) if nh >= D else im

    cx = (i % COLS) * cell_w + PAD
    cy = (i // COLS) * cell_h + PAD

    # 白色相框
    draw.ellipse((cx - FRAME, cy - FRAME, cx + D + FRAME - 1, cy + D + FRAME - 1),
                 fill=(255, 255, 255), outline=(240, 234, 245))
    canvas.paste(im, (cx, cy), MASK)

canvas.save(OUT, 'PNG')
print('saved %s  %s' % (OUT, canvas.size))
