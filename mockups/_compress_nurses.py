# -*- coding: utf-8 -*-
"""批量压缩陪护师头像：备份原图 -> 按 EXIF 修正方向 -> 等比缩放 -> 剥离 EXIF -> 覆盖写回"""
import os
import shutil
from PIL import Image, ImageOps

SRC = r'D:\yxy\wx_project1\assets\images\nurses'
BAK = r'D:\yxy\wx_project1\mockups\_nurses_originals'
MAX_EDGE = 480      # 最长边上限（首页头像约 214rpx，480px 足够 2~3 倍屏）
QUALITY = 82

os.makedirs(BAK, exist_ok=True)

names = [f for f in os.listdir(SRC)
         if os.path.isfile(os.path.join(SRC, f))
         and f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]

total_before = 0
total_after = 0

for f in names:
    src = os.path.join(SRC, f)
    bak = os.path.join(BAK, f)
    size_before = os.path.getsize(src)
    total_before += size_before

    # 1) 备份原图（只备份一次，不覆盖已有备份）
    if not os.path.exists(bak):
        shutil.copy2(src, bak)

    # 2) 打开并按 EXIF 修正方向（手机竖拍照片常见问题）
    im = Image.open(src)
    im = ImageOps.exif_transpose(im)
    w0, h0 = im.size

    # 3) 等比缩放，不放大
    scale = min(1.0, MAX_EDGE / float(max(w0, h0)))
    if scale < 1.0:
        im = im.resize(
            (max(1, int(round(w0 * scale))), max(1, int(round(h0 * scale)))),
            Image.LANCZOS
        )

    # 4) 统一转 RGB（透明底填白）
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA')
        bg = Image.new('RGB', im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        im = bg
    elif im.mode != 'RGB':
        im = im.convert('RGB')

    # 5) 写出：剥离 EXIF（去掉拍摄设备 / GPS 等隐私信息），progressive + optimize 进一步减小体积
    im.save(src, 'JPEG', quality=QUALITY, optimize=True, progressive=True)
    size_after = os.path.getsize(src)
    total_after += size_after

    print(u'%s  %dx%d -> %dx%d  %dKB -> %dKB' % (
        f, w0, h0, im.size[0], im.size[1], size_before // 1024, size_after // 1024))

print(u'---')
print(u'合计: %dKB -> %dKB' % (total_before // 1024, total_after // 1024))
print(u'原图备份在: %s' % BAK)
