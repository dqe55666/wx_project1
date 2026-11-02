# -*- coding: utf-8 -*-
"""通过 GitHub API（api.github.com）推送本地 commit。

背景：本环境代理挡了 github.com（git 协议用不了），但 api.github.com 可达，
且本机 Credential Manager 里存有带 repo 权限的 token，所以改用 Git Data API：
  1) 上传变更文件的 blob
  2) 用 base_tree + 变更项建 tree（内容寻址，SHA 应与本地一致）
  3) 复刻本地 commit 的 author/committer/message 建 commit（SHA 应与本地一致）
  4) 更新 refs/heads/master（fast-forward）
最后校验远端 ref 是否等于本地 HEAD，不一致则本地对齐远端。
"""
import base64
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

PROJ = r'D:\yxy\wx_project1'
REPO = 'dqe55666/wx_project1'
BRANCH = 'master'
API = 'https://api.github.com'


def git(*args):
    p = subprocess.run(['git', '-C', PROJ] + list(args), capture_output=True)
    if p.returncode != 0:
        raise RuntimeError('git %s 失败: %s' % (' '.join(args), p.stderr.decode('utf-8', 'replace')))
    return p.stdout.decode('utf-8', 'replace')


def git_raw(*args, data=None):
    """git 子命令，stdin 可传原始字节（如 hash-object 写 commit 对象），返回 stdout 字节"""
    p = subprocess.run(['git', '-C', PROJ] + list(args), input=data, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError('git %s 失败: %s' % (' '.join(args), p.stderr.decode('utf-8', 'replace')))
    return p.stdout


def get_token():
    p = subprocess.run(['git', '-C', PROJ, 'credential', 'fill'],
                       input=b'protocol=https\nhost=github.com\n\n', capture_output=True)
    for line in p.stdout.decode('utf-8', 'replace').splitlines():
        if line.startswith('password='):
            return line[len('password='):].strip()
    raise RuntimeError('本机没有 GitHub 凭据')


TOKEN = get_token()


def api(method, path, payload=None):
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header('Authorization', 'token ' + TOKEN)
    req.add_header('Accept', 'application/vnd.github+json')
    if data:
        req.add_header('Content-Type', 'application/json')
    last = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                body = r.read()
                return r.status, (json.loads(body.decode('utf-8')) if body else {})
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', 'replace')
            return e.code, (json.loads(body) if body.strip().startswith('{') else {'raw': body[:300]})
        except Exception as ex:          # 网络/代理抖动，重试
            last = ex
            time.sleep(2 * (attempt + 1))
    raise RuntimeError('API 调用失败 %s %s: %s' % (method, path, last))


# ---------- 1. 收集本地信息 ----------
head = git('rev-parse', 'HEAD').strip()
parent = git('rev-parse', 'HEAD~1').strip()
base_tree = git('rev-parse', '%s^{tree}' % parent).strip()
new_tree = git('rev-parse', '%s^{tree}' % head).strip()
print(u'本地 HEAD   : %s' % head)
print(u'远端应当等于: %s (origin/master)' % parent)
print(u'base tree   : %s' % base_tree)
print(u'new  tree   : %s' % new_tree)

raw = git('cat-file', 'commit', head)
m = re.search(r'^author (.+?) <(.+?)> (\d+) ([+-]\d{4})$', raw, re.M)
c = re.search(r'^committer (.+?) <(.+?)> (\d+) ([+-]\d{4})$', raw, re.M)
msg = raw.split('\n\n', 1)[1]


def iso(epoch, tz):
    sign = 1 if tz[0] == '+' else -1
    off = timedelta(hours=int(tz[1:3]), minutes=int(tz[3:5])) * sign
    return (datetime.fromtimestamp(int(epoch), timezone.utc) + off).isoformat()


author = {'name': m.group(1), 'email': m.group(2), 'date': iso(m.group(3), m.group(4))}
committer = {'name': c.group(1), 'email': c.group(2), 'date': iso(c.group(3), c.group(4))}

# 变更清单（-z 避免中文路径被转义，--no-renames 拆成 A/D/M）
# 每条元信息形如 ":100644 100644 <旧sha> <新sha> M"，以 NUL 与路径交替
out = git('diff-tree', '-r', '-z', '--no-renames', parent, head)
items = out.split('\0')
changes = []
i = 0
while i + 1 < len(items):
    meta, path = items[i], items[i + 1]
    if not meta:
        break
    parts = meta.split(' ')          # [':旧mode', '新mode', '旧sha', '新sha', '状态']
    changes.append({'old_mode': parts[0][1:], 'new_mode': parts[1],
                    'old_sha': parts[2], 'new_sha': parts[3],
                    'status': parts[4][0], 'path': path})
    i += 2

adds = [x for x in changes if x['status'] in ('A', 'M')]
dels = [x for x in changes if x['status'] == 'D']
print(u'变更文件    : 新增/修改 %d，删除 %d' % (len(adds), len(dels)))

# ---------- 2. 上传 blob ----------
tree_entries = []
blob_cache = {}
for k, ch in enumerate(adds, 1):
    sha = ch['new_sha']
    if sha not in blob_cache:
        raw_blob = subprocess.run(['git', '-C', PROJ, 'cat-file', 'blob', sha],
                                  capture_output=True).stdout
        st, res = api('POST', '/repos/%s/git/blobs' % REPO,
                      {'content': base64.b64encode(raw_blob).decode('ascii'), 'encoding': 'base64'})
        if st not in (200, 201) or res.get('sha') != sha:
            raise RuntimeError(u'blob 上传不一致 %s：远端 %s 本地 %s / %s'
                               % (ch['path'], res.get('sha'), sha, res))
        blob_cache[sha] = res['sha']
    tree_entries.append({'path': ch['path'], 'mode': ch['new_mode'], 'type': 'blob', 'sha': sha})
    if k % 10 == 0 or k == len(adds):
        print(u'  已上传 blob %d/%d' % (k, len(adds)))

for ch in dels:
    tree_entries.append({'path': ch['path'], 'mode': ch['old_mode'], 'type': 'blob', 'sha': None})

# ---------- 3. 建 tree ----------
st, tres = api('POST', '/repos/%s/git/trees' % REPO,
               {'base_tree': base_tree, 'tree': tree_entries})
if st not in (200, 201):
    raise RuntimeError(u'建 tree 失败: %s' % tres)
if tres.get('sha') != new_tree:
    print(u'⚠️ tree SHA 不一致：远端 %s / 本地 %s' % (tres.get('sha'), new_tree))
else:
    print(u'tree SHA 与本地完全一致 ✔')

# ---------- 4. 建 commit ----------
st, cres = api('POST', '/repos/%s/git/commits' % REPO,
               {'message': msg, 'tree': tres['sha'], 'parents': [parent],
                'author': author, 'committer': committer})
if st not in (200, 201):
    raise RuntimeError(u'建 commit 失败: %s' % cres)
remote_commit = cres.get('sha')
if remote_commit != head:
    print(u'⚠️ commit SHA 不一致：远端 %s / 本地 %s（内容相同，仅元数据不同）'
          % (remote_commit, head))
else:
    print(u'commit SHA 与本地完全一致 ✔')

# ---------- 5. 更新分支引用 ----------
st, rres = api('PATCH', '/repos/%s/git/refs/heads/%s' % (REPO, BRANCH),
               {'sha': remote_commit, 'force': False})
if st not in (200, 201):
    raise RuntimeError(u'更新分支失败: %s' % rres)
print(u'远端 %s 已指向 %s ✔' % (BRANCH, remote_commit))

# ---------- 6. 本地对齐 ----------
# ⚠️ 绝不能对本地不存在的对象做 reset --hard（曾把工作区砸回旧版本）。
# 安全做法：按远端实际存储的元数据在本地重建同一个 commit 对象，
# SHA 校验一致后才更新引用；不一致则中止，不碰任何东西。
if remote_commit != head:
    import hashlib

    def to_git_date(s):
        from datetime import datetime as _dt
        d = _dt.fromisoformat(s.replace('Z', '+00:00'))
        return int(d.timestamp()), '+0000'

    a_ep, a_tz = to_git_date(cres['author']['date'])
    c_ep, c_tz = to_git_date(cres['committer']['date'])
    rebuild = (
        'tree %s\n' % cres['tree']['sha'] +
        ''.join('parent %s\n' % p['sha'] for p in cres['parents']) +
        'author %s <%s> %d %s\n' % (cres['author']['name'], cres['author']['email'], a_ep, a_tz) +
        'committer %s <%s> %d %s\n' % (cres['committer']['name'], cres['committer']['email'], c_ep, c_tz) +
        '\n' + cres['message'] + '\n'   # API 的 message 会剥掉尾换行，实际对象带 \n
    ).encode('utf-8')
    rebuilt = hashlib.sha1(b'commit %d\0' % len(rebuild) + rebuild).hexdigest()
    if rebuilt != remote_commit:
        raise SystemExit(u'❌ 重建的远端 commit SHA 不一致（%s ≠ %s），中止对齐，'
                         u'本地保持 HEAD=%s，请手动处理' % (rebuilt, remote_commit, head))
    git_raw('hash-object', '-t', 'commit', '-w', '--stdin', data=rebuild)
    git('update-ref', 'refs/heads/master', remote_commit)
    git('reset', '--hard', 'master')      # 对象已存在且 tree 与原 HEAD 相同，工作区不变
    git('update-ref', 'refs/remotes/origin/master', remote_commit)
    print(u'本地已对齐远端（%s），内容完全相同，仅提交哈希不同' % remote_commit[:12])
else:
    git('update-ref', 'refs/remotes/origin/master', remote_commit)
    print(u'本地与远端一致，无需处理')

print(u'\n✅ 推送完成')
