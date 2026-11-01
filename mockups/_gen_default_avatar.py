# -*- coding: utf-8 -*-
"""生成登录页/我的页共用的默认头像（主题粉 + 人形剪影）。
可重复执行，输出 assets/images/avatar-default.png（200x200）"""
import os
from PIL import Image, ImageDraw

OUT = r'D:\yxy\wx_project1\assets\images\avatar-default.png'
BG = (255, 217, 232)        # #ffd9e8 浅粉底
FG = (255, 95, 158)         # #ff5f9e 主题粉
S = 4                       # 4 倍超采样
N = 200 * S

im = Image.new('RGBA', (N, N), (0, 0, 0, 0))
d = ImageDraw.Draw(im)

# 底圆
d.ellipse([0, 0, N - 1, N - 1], fill=BG + (255,))

# 头（圆）+ 肩（半椭圆），居中偏上
head_r = int(N * 0.155)
cx = N // 2
head_cy = int(N * 0.375)
d.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r], fill=FG + (255,))

shoulder_w = int(N * 0.29)
shoulder_h = int(N * 0.21)
shoulder_top = int(N * 0.575)
# 用圆形裁剪兜底：先在临时层画肩，再按底圆裁
layer = Image.new('RGBA', (N, N), (0, 0, 0, 0))
dl = ImageDraw.Draw(layer)
dl.ellipse([cx - shoulder_w, shoulder_top, cx + shoulder_w, shoulder_top + shoulder_h * 2],
           fill=FG + (255,))
# 裁回底圆内
mask = Image.new('L', (N, N), 0)
ImageDraw.Draw(mask).ellipse([0, 0, N - 1, N - 1], fill=255)
im.paste(layer, (0, 0), Image.composite(layer.split()[3], Image.new('L', (N, N), 0),
                                        mask))

im = im.resize((200, 200), Image.LANCZOS)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
im.save(OUT, 'PNG', optimize=True)
print('OK', OUT, os.path.getsize(OUT), 'bytes')
