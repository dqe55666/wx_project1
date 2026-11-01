# -*- coding: utf-8 -*-
"""把证件照红底替换为主题浅粉底，生成对比预览（不修改线上使用的图片）"""
import base64
import io
import os
from PIL import Image, ImageDraw, ImageFilter

PROJ = r'D:\yxy\wx_project1'
SRC = os.path.join(PROJ, 'assets', 'images', 'nurses')
BAK = os.path.join(PROJ, 'mockups', '_nurses_originals')
OUT = os.path.join(PROJ, 'mockups', '_pink_bg')
HTML = os.path.join(PROJ, 'mockups', 'avatar-bg-compare.html')

ORDER = [u'肖雯遥', u'王一茜', u'彭彦博', u'方嘉倩', u'胡冰冰', u'谢远杰']
TARGET = (255, 227, 239)   # #ffe3ef 主题浅粉
MAX_EDGE = 480
MARK = (0, 255, 0)

os.makedirs(OUT, exist_ok=True)


def build(name):
    """从原图生成 480px 的粉底版"""
    src = os.path.join(BAK, name + '.jpg')
    if not os.path.exists(src):
        src = os.path.join(SRC, name + '.jpg')
    im = Image.open(src).convert('RGB')
    w0, h0 = im.size
    scale = min(1.0, MAX_EDGE / float(max(w0, h0)))
    if scale < 1.0:
        im = im.resize((max(1, int(round(w0 * scale))), max(1, int(round(h0 * scale)))),
                       Image.LANCZOS)

    w, h = im.size
    pi = im.load()

    # 思路：先用「颜色」筛出所有纯红像素，再用「连通性」排除人物身上的红衣物。
    # 关键差别——发丝永远不满足「红色」条件，所以从原理上就不可能被吃掉，
    # 不会像单靠泛洪那样顺着发丝间的红色透光一路蔓延。
    cand = Image.new('RGB', (w, h), (0, 0, 0))
    pc = cand.load()
    for y in range(h):
        for x in range(w):
            r, g, b = pi[x, y]
            if r > 150 and (r - g) > 90 and (r - b) > 90:
                pc[x, y] = (255, 255, 255)

    # 只保留与画面四边连通的候选区域（红毛衣被身体隔开、不连通，因而自动排除）
    for seed in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        try:
            if cand.getpixel(seed) == (255, 255, 255):
                ImageDraw.floodfill(cand, seed, MARK, thresh=10)
        except Exception:
            pass

    pc = cand.load()
    mask = Image.new('L', (w, h), 0)
    pm = mask.load()
    for y in range(h):
        for x in range(w):
            if pc[x, y] == MARK:
                pm[x, y] = 255

    # 轻微膨胀（吃掉轮廓上的红色光晕）+ 羽化（让过渡自然）
    mask = mask.filter(ImageFilter.MaxFilter(3))
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))

    out = Image.composite(Image.new('RGB', (w, h), TARGET), im, mask)
    dst = os.path.join(OUT, name + '.jpg')
    out.save(dst, 'JPEG', quality=88, optimize=True, progressive=True)
    return dst


def data_uri(path):
    with open(path, 'rb') as f:
        return 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode('ascii')


rows = []
for n in ORDER:
    pink = build(n)
    rows.append((n, data_uri(os.path.join(SRC, n + '.jpg')), data_uri(pink)))

html = [u"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>陪护师头像底色对比</title>
<style>
  body{margin:0;padding:28px 22px 60px;background:#fff;color:#23202a;
       font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;}
  h1{font-size:19px;margin:0 0 8px;}
  p.sub{font-size:13px;color:#8f8699;margin:0 0 22px;line-height:1.7;}
  .head{display:flex;gap:14px;font-size:13px;font-weight:700;color:#8f8699;margin-bottom:8px;}
  .head span{flex:1;text-align:center;}
  table{width:100%;border-collapse:collapse;}
  td{width:50%;padding:6px;vertical-align:top;}
  .cap{font-size:11.5px;color:#b7b0c2;text-align:center;padding-top:5px;}
  img{width:100%;display:block;border-radius:12px;border:1px solid #f1eaf5;box-sizing:border-box;}
  .wrap{max-width:560px;margin:0 auto;}
</style></head><body><div class="wrap">
<h1>陪护师头像底色对比</h1>
<p class="sub">左：当前红底证件照　／　右：换成页面主题浅粉底（#ffe3ef）。<br>
只替换了与四角连通的背景区域，人物的头发、衣服、肤色均未改动。</p>
<div class="head"><span>当前（红底）</span><span>建议（主题粉底）</span></div>
<table>"""]

for n, a, b in rows:
    html.append(
        u'<tr><td><img src="%s"><div class="cap">%s</div></td>'
        u'<td><img src="%s"><div class="cap">%s</div></td></tr>' % (a, n, b, n)
    )

html.append(u'</table></div></body></html>')

io.open(HTML, 'w', encoding='utf-8').write(u'\n'.join(html))
print(u'对比页: %s (%dKB)' % (HTML, os.path.getsize(HTML) // 1024))
print(u'粉底版目录: %s' % OUT)
for f in sorted(os.listdir(OUT)):
    print(u'  %s  %dKB' % (f, os.path.getsize(os.path.join(OUT, f)) // 1024))
