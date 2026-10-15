# -*- coding: utf-8 -*-
"""同步首页预览 HTML 的陪护师区 = 细白框圆形头像（正方形新图）。可重复执行。"""
import base64
import io
import os
import re

PROJ = r'D:\yxy\wx_project1'
HTML = os.path.join(PROJ, 'mockups', 'index-live-preview.html')
IMGDIR = os.path.join(PROJ, 'assets', 'images', 'nurses')
ORDER = [u'肖雯遥', u'王一茜', u'彭彦博', u'方嘉倩', u'胡冰冰', u'谢远杰']

NEW_CSS = (
    u'  .avatar { width:105px; height:105px; margin:0 auto; border-radius:50%; padding:3px;\r\n'
    u'    background:#fff; border:1px solid #f1eaf5; box-sizing:border-box;\r\n'
    u'    box-shadow:0 3px 9px rgba(60,30,80,.12); }\r\n'
    u'  .avatar-inner { width:100%; height:100%; border-radius:50%; overflow:hidden; }\r\n'
    u'  .avatar img { display:block; width:100%; border-radius:50%; }\r\n'
)


def data_uri(name):
    with open(os.path.join(IMGDIR, name + '.jpg'), 'rb') as f:
        return 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode('ascii')


raw = io.open(HTML, encoding='utf-8', newline='').read()
css_pat = re.compile(r'  \.avatar \{.*?\.avatar img \{.*?\}\r?\n', re.S)
raw, n_css = css_pat.subn(NEW_CSS, raw, count=1)

start = raw.find('<div class="nurses">')
end = raw.find('</div>\r\n        </div>', start)
if end == -1:
    end = raw.find('</div>\n        </div>', start)
block = raw[start:end]


def repl(m):
    name = ORDER[repl.i]
    repl.i += 1
    return (u'<div class="avatar"><div class="avatar-inner"><img src="%s" alt="">'
            u'</div></div>' % data_uri(name))


repl.i = 0
new_block, n_img = re.subn(r'<div class="avatar"><div class="avatar-inner"><img src="[^"]*" alt=""></div></div>',
                           repl, block)
raw = raw[:start] + new_block + raw[end:]
io.open(HTML, 'w', encoding='utf-8', newline='').write(raw)
print(u'CSS %d 处；头像 %d 张；%dKB' % (n_css, n_img, os.path.getsize(HTML) // 1024))
