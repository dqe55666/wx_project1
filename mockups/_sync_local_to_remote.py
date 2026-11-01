# -*- coding: utf-8 -*-
"""让本地 master 与 GitHub 上已存在的 commit（API 建的那个）完全一致。

GitHub 的 git/commits API 会把时区规范化成 UTC、并去掉 message 末尾换行，
所以远端 commit 的 SHA 与本地不同，但 tree 完全相同（内容一致）。
这里按远端实际存储的元数据，在本地重建同一个 commit 对象，再对齐引用。
"""
import hashlib
import io
import json
import os
import subprocess
from datetime import datetime

PROJ = r'D:\yxy\wx_project1'
REPO = 'dqe55666/wx_project1'
REMOTE_COMMIT = '14567f9b068ef5d7e1817ea8b18632ceca15ccc3'


def git(*args, data=None):
    p = subprocess.run(['git', '-C', PROJ] + list(args), input=data, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError('git %s 失败: %s' % (' '.join(args), p.stderr.decode('utf-8', 'replace')))
    return p.stdout


def token():
    p = subprocess.run(['git', '-C', PROJ, 'credential', 'fill'],
                       input=b'protocol=https\nhost=github.com\n\n', capture_output=True)
    for line in p.stdout.decode('utf-8', 'replace').splitlines():
        if line.startswith('password='):
            return line[len('password='):].strip()
    raise RuntimeError('没有凭据')


import urllib.request
req = urllib.request.Request('https://api.github.com/repos/%s/git/commits/%s' % (REPO, REMOTE_COMMIT))
req.add_header('Authorization', 'token ' + token())
d = json.load(urllib.request.urlopen(req, timeout=60))


def to_git_date(s):
    # tz-aware 的 UTC 时间，timestamp() 不受本地时区影响
    dt = datetime.fromisoformat(s.replace('Z', '+00:00'))
    return int(dt.timestamp()), '+0000'


a_ep, a_tz = to_git_date(d['author']['date'])
c_ep, c_tz = to_git_date(d['committer']['date'])

raw = (
    'tree %s\n' % d['tree']['sha'] +
    ''.join('parent %s\n' % p['sha'] for p in d['parents']) +
    'author %s <%s> %d %s\n' % (d['author']['name'], d['author']['email'], a_ep, a_tz) +
    'committer %s <%s> %d %s\n' % (d['committer']['name'], d['committer']['email'], c_ep, c_tz) +
    '\n' + d['message'] + '\n'   # API 的 message 字段会剥掉对象里的尾换行，实际对象带 \n
).encode('utf-8')

sha = hashlib.sha1(b'commit %d\0' % len(raw) + raw).hexdigest()
print(u'GitHub 实际存储的元数据：')
print(u'  author    %s <%s> %d %s' % (d['author']['name'], d['author']['email'], a_ep, a_tz))
print(u'  committer %s <%s> %d %s' % (d['committer']['name'], d['committer']['email'], c_ep, c_tz))
print(u'  message 末尾:', repr(d['message'][-12:]))
print(u'按此重建的对象 SHA: %s' % sha)
print(u'目标              : %s' % REMOTE_COMMIT)
if sha != REMOTE_COMMIT:
    raise SystemExit(u'❌ 重建结果不一致，未做任何改动')

# 写入对象并对齐引用
git('hash-object', '-t', 'commit', '-w', '--stdin', data=raw)
git('update-ref', 'refs/heads/master', REMOTE_COMMIT)
git('reset', '--hard', 'master')          # tree 与 f252d00 完全相同，工作区不变
git('update-ref', 'refs/remotes/origin/master', REMOTE_COMMIT)

print()
print(u'本地 HEAD       : %s' % git('rev-parse', 'HEAD').strip())
print(u'origin/master   : %s' % git('rev-parse', 'origin/master').strip())
print(u'最近提交        :')
print(git('log', '--oneline', '-2').rstrip())
st = git('status', '--porcelain').strip()
print(u'工作区          : %s' % (u'干净' if not st else st[:200]))
print(u'\n✅ 本地与远端已完全一致，之后可以直接用 git push / git pull')
