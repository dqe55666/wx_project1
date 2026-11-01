# -*- coding: utf-8 -*-
"""把新素材导入 assets/images/：备份原图 + 缩放到合适宽度 + 压缩

用法：在 SRC_MAP 里加一行，然后执行本脚本（可重复执行，原图已备份则跳过备份）
"""
import os
import shutil
from PIL import Image, ImageOps

PROJ = r'D:\yxy\wx_project1'
BACKUP = os.path.join(PROJ, 'mockups', '_import_originals')

# 目标路径（相对 assets/images）: 源文件绝对路径
SRC_MAP = {
    r'bg\hospital.jpg': r'C:\Users\hhh\.workbuddy\clipboard-images\clipboard-2026-10-20T00-09-34-528Z-229976cd.jpg',
    r'login\care.jpg': r'C:\Users\hhh\.workbuddy\clipboard-images\clipboard-2026-10-20T00-09-34-531Z-28925602.jpg',
}

MAX_W = 1240        # 全面屏 3 倍图足够（414pt × 3 ≈ 1242）
QUALITY = 80
IMG_ROOT = os.path.join(PROJ, 'assets', 'images')


def main():
    if not os.path.isdir(BACKUP):
        os.makedirs(BACKUP)
    total = 0
    for rel, src in SRC_MAP.items():
        dst = os.path.join(IMG_ROOT, rel)
        d = os.path.dirname(dst)
        if not os.path.isdir(d):
            os.makedirs(d)

        im = Image.open(src)
        im = ImageOps.exif_transpose(im).convert('RGB')
        ow, oh = im.size

        # 备份原图（同名扁平存放）
        bak = os.path.join(BACKUP, os.path.basename(dst))
        if not os.path.exists(bak):
            shutil.copy2(src, bak)

        if ow > MAX_W:
            im = im.resize((MAX_W, int(round(oh * MAX_W / float(ow)))), Image.LANCZOS)

        im.save(dst, 'JPEG', quality=QUALITY, optimize=True, progressive=True)
        kb = os.path.getsize(dst) / 1024.0
        total += kb
        print(u'%-22s %dx%d -> %dx%d   %.0fKB' % (
            rel.replace('\\', '/'), ow, oh, im.size[0], im.size[1], kb))

    pkg = sum(os.path.getsize(os.path.join(r, f)) / 1024.0
              for r, _, fs in os.walk(IMG_ROOT) for f in fs)
    print(u'新增合计 %.0fKB    images 目录总计 %.0fKB' % (total, pkg))


if __name__ == '__main__':
    main()
