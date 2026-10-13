# -*- coding: utf-8 -*-
"""把首页预览 HTML 的陪护师区块替换为真实头像（base64 内联，保证预览服务下也能显示）"""
import base64
import io
import os

PROJ = r'D:\yxy\wx_project1'
HTML = os.path.join(PROJ, 'mockups', 'index-live-preview.html')
IMGDIR = os.path.join(PROJ, 'assets', 'images', 'nurses')

# 展示顺序（第一位 = 最左）
ORDER = [u'肖雯遥', u'王一茜', u'彭彦博', u'方嘉倩', u'胡冰冰', u'谢远杰']


def data_uri(name):
    with open(os.path.join(IMGDIR, name + '.jpg'), 'rb') as f:
        return 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode('ascii')


raw = io.open(HTML, encoding='utf-8', newline='').read()
nl = u'\r\n' if u'\r\n' in raw else u'\n'

OLD_CSS = nl.join([
    u'  .avatar { width:100%; height:104px; border-radius:14px;',
    u'    background:linear-gradient(145deg,#f8f3fb,#ece3f3); border:1px solid #efe8f5; box-sizing:border-box; }',
])

NEW_CSS = nl.join([
    u'  .avatar { width:100%; height:104px; border-radius:14px; overflow:hidden;',
    u'    background:linear-gradient(145deg,#f8f3fb,#ece3f3); border:1px solid #efe8f5; box-sizing:border-box; }',
    u'  .avatar img { display:block; width:100%; }',
])

OLD_BLOCK = nl.join(
    [u'          <div class="nurses">']
    + [u'            <div class="nurse"><div class="avatar"></div></div>'] * 6
    + [u'          </div>']
)

NEW_BLOCK = nl.join(
    [u'          <div class="nurses">']
    + [u'            <div class="nurse"><div class="avatar"><img src="%s" alt=""></div></div>' % data_uri(n)
       for n in ORDER]
    + [u'          </div>']
)

html = raw
hit_css = OLD_CSS in html
hit_block = OLD_BLOCK in html

if hit_css:
    html = html.replace(OLD_CSS, NEW_CSS, 1)
if hit_block:
    html = html.replace(OLD_BLOCK, NEW_BLOCK, 1)

io.open(HTML, 'w', encoding='utf-8', newline='').write(html)

print(u'CSS 锚点: %s' % (u'已替换' if hit_css else u'未找到（可能已更新过）'))
print(u'陪护师区块: %s' % (u'已替换为真实头像' if hit_block else u'未找到（可能已更新过）'))
print(u'写入完成: %s  (%dKB)' % (HTML, os.path.getsize(HTML) // 1024))
