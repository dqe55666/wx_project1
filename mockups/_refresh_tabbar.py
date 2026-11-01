# -*- coding: utf-8 -*-
"""把预览页底部的假 tabBar（emoji）换成真实图标（base64 内联）。可重复执行。"""
import base64
import io
import os
import re

PROJ = r'D:\yxy\wx_project1'
HTML = os.path.join(PROJ, 'mockups', 'index-live-preview.html')
ICONDIR = os.path.join(PROJ, 'assets', 'images', 'tabbar')

ORDER = [
    ('home', True),      # 预览里首页是选中态
    ('care', False),
    ('voice', False),
    ('message', False),
    ('mine', False),
]

NEW_CSS = u'  .tab .dot { width:22px; height:22px; display:block; }\r\n'


def uri(key, active):
    p = os.path.join(ICONDIR, key + ('-active' if active else '') + '.png')
    with open(p, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode('ascii')


raw = io.open(HTML, encoding='utf-8', newline='').read()

# 1) 样式：.tab .dot 改成图片尺寸
css_pat = re.compile(r'  \.tab \.dot \{[^\r\n]*\}\r?\n')
raw, n_css = css_pat.subn(NEW_CSS, raw, count=1)

# 2) 图标：按顺序把 <span class="dot">…</span> 换成 <img>
i = 0


def repl(m):
    global i
    key, active = ORDER[i]
    i += 1
    return u'<img class="dot" src="%s" alt="">' % uri(key, active)


raw, n_img = re.subn(r'<span class="dot">[^<]*</span>', repl, raw,
                     count=len(ORDER))

io.open(HTML, 'w', encoding='utf-8', newline='').write(raw)
print(u'CSS %d 处；图标 %d 个；文件 %dKB' % (n_css, n_img, os.path.getsize(HTML) // 1024))
