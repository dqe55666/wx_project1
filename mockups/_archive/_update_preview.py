# -*- coding: utf-8 -*-
"""同步首页预览：陪护师显示姓名 + 字号调整 + 轻缩放按下反馈"""
import io
import os
import re

PROJ = r'D:\yxy\wx_project1'
HTML = os.path.join(PROJ, 'mockups', 'index-live-preview.html')

ORDER = [u'肖雯遥', u'王一茜', u'彭彦博', u'方嘉倩', u'胡冰冰', u'谢远杰']

raw = io.open(HTML, encoding='utf-8', newline='').read()
nl = u'\r\n' if u'\r\n' in raw else u'\n'

OLD_CSS = nl.join([
    u'  .nurse { flex:0 0 calc((100% - 22px) / 3); min-width:0; cursor:pointer; transition:transform .12s ease, opacity .12s ease; }',
    u'  .nurse:active { transform:scale(.9); opacity:.82; }',
])

NEW_CSS = nl.join([
    u'  .nurse { flex:0 0 calc((100% - 22px) / 3); min-width:0; cursor:pointer; transition:transform .12s ease, opacity .12s ease;',
    u'    display:flex; flex-direction:column; align-items:center; gap:8px; }',
    u'  .nurse:active { transform:scale(.94); filter:brightness(.94); }',
    u'  .nurse-name { max-width:100%; font-size:15px; font-weight:700; color:#23202a; text-align:center;',
    u'    overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }',
])

# 给每个陪护师格子补上姓名
pat = re.compile(u'(<div class="nurse"><div class="avatar"><img src="[^"]*" alt=""></div>)(</div>)')
counter = [0]


def _add(m):
    i = counter[0]
    counter[0] += 1
    name = ORDER[i] if i < len(ORDER) else u'陪护师'
    return u'%s<text class="nurse-name">%s</text>%s' % (m.group(1), name, m.group(2))


html, n = pat.subn(_add, raw)

if OLD_CSS in html:
    html = html.replace(OLD_CSS, NEW_CSS, 1)
    print(u'CSS 已更新')
else:
    print(u'CSS 锚点未找到（可能已更新过）')

io.open(HTML, 'w', encoding='utf-8', newline='').write(html)
print(u'补充姓名: %d 处' % n)
print(u'写入完成: %dKB' % (os.path.getsize(HTML) // 1024))
