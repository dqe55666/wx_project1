# -*- coding: utf-8 -*-
"""把首页预览 HTML 的「服务医院」区块换成新版列表（缩略图 + 标签 + 重点科室）

按「区块边界」整体替换，不用正则去配嵌套 div（之前那样会留下残行）。
可重复执行。
"""
import base64
import io
import os
import re

PROJ = r'D:\yxy\wx_project1'
HTML = os.path.join(PROJ, 'mockups', 'index-live-preview.html')
THUMB = os.path.join(PROJ, 'assets', 'images', 'bg', 'hospital.jpg')

HOSPITALS = [
    (u'张家界市人民医院', u'1.6km', u'三甲', u'综合医院', u'儿科、呼吸内科、妇产科'),
    (u'张家界市永定医院', u'6.0km', u'三甲', u'综合医院', u'儿科、呼吸内科、妇产科'),
    (u'张家界市中医院', u'1.2km', u'二甲', u'中医医院', u'针灸科、康复科、中医内科'),
]

# 缩略图只内联一次：用 CSS 背景图，避免 3 行各贴一份 base64
NEW_CSS = u"""  .hosp-list { display:flex; flex-direction:column; }
  .hosp { display:flex; align-items:flex-start; gap:11px; padding:13px 2px;
    border-bottom:1px solid #f4eef8; cursor:pointer; transition:transform .12s ease, filter .12s ease; }
  .hosp:last-child { border-bottom:0; padding-bottom:2px; }
  .hosp:active { transform:scale(.97); filter:brightness(.96); }
  .hosp .thumb { flex:none; width:66px; height:66px; border-radius:10px; background-color:#f4eef8;
    background-image:url(__THUMB__); background-size:cover; background-position:center; }
  .hosp .main { flex:1; min-width:0; }
  .hosp .top { display:flex; align-items:baseline; gap:8px; }
  .hosp .hn { flex:1; min-width:0; font-size:16.5px; font-weight:800; color:#23202a;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .hosp .hd { flex:none; font-size:13px; color:#9a93a4; }
  .hosp .tags { display:flex; flex-wrap:wrap; gap:5px; margin-top:6px; }
  .hosp .tags span { font-size:13px; line-height:1; padding:4px 7px; border-radius:5px;
    color:#ff5f9e; background:#fff5f9; border:1px solid #ffd0e3; }
  .hosp .ha { margin-top:6px; font-size:14px; color:#7e7689;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
"""


def data_uri(p):
    with open(p, 'rb') as f:
        return 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode('ascii')


def build_rows():
    out = []
    for name, dist, lv, tp, dept in HOSPITALS:
        out.append(
            u'          <div class="hosp">\r\n'
            u'            <div class="thumb"></div>\r\n'
            u'            <div class="main">\r\n'
            u'              <div class="top"><div class="hn">%s</div><div class="hd">距您 %s</div></div>\r\n'
            u'              <div class="tags"><span>%s</span><span>%s</span></div>\r\n'
            u'              <div class="ha">重点科室：%s</div>\r\n'
            u'            </div>\r\n'
            u'          </div>' % (name, dist, lv, tp, dept))
    return u'          <div class="hosp-list">\r\n' + u'\r\n'.join(out) + u'\r\n          </div>'


raw = io.open(HTML, encoding='utf-8', newline='').read()

# --- 1) 样式块：从 .hosp-list 到 .hosp .hd（旧）或 .hosp .ha（新）整段替换
css_pat = re.compile(r'  \.hosp-list \{.*?  \.hosp \.h[da] \{[^\r\n]*\}\r?\n', re.S)
raw, n_css = css_pat.subn(NEW_CSS.replace('__THUMB__', data_uri(THUMB)), raw, count=1)

# --- 2) 区块内容：定位 .hosp-list（或旧的 empty-state）起点，一路切到「服务医院」section 的收尾 </div>
anchor = raw.find(u'          <div class="hosp-list">')
if anchor == -1:
    anchor = raw.find(u'          <div class="empty-state">')
if anchor == -1:
    raise SystemExit(u'未找到服务医院区块，脚本未改动文件')

section_end = raw.find(u'\r\n        </div>', anchor)
if section_end == -1:
    section_end = raw.find(u'\n        </div>', anchor)
if section_end == -1:
    raise SystemExit(u'未找到区块结束标记，脚本未改动文件')

raw = raw[:anchor] + build_rows() + raw[section_end:]

io.open(HTML, 'w', encoding='utf-8', newline='').write(raw)
print(u'CSS %d 处；区块已整体替换；文件 %dKB' % (n_css, os.path.getsize(HTML) // 1024))
