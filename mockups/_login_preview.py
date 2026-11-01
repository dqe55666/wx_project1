# -*- coding: utf-8 -*-
"""生成登录屏的 HTML 预览（375x812 手机框，图片 base64 内联，可重复执行）"""
import base64
import io
import os

PROJ = r'D:\yxy\wx_project1'
OUT = os.path.join(PROJ, 'mockups', 'login-preview.html')


def uri(rel):
    p = os.path.join(PROJ, 'assets', 'images', rel)
    with open(p, 'rb') as f:
        return 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode('ascii')


TPL = u"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>登录屏 · 预览</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #e9e6ee; display: flex; flex-direction: column; align-items: center;
         gap: 14px; padding: 24px 16px 36px;
         font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
         -webkit-font-smoothing: antialiased; }
  .hud { display: flex; align-items: center; gap: 12px; font-size: 13px; color: #6b6478; }
  .hud b { color: #ff4d8d; font-weight: 700; }
  .hud button { border: 0; border-radius: 16px; padding: 8px 16px; font-size: 13px; font-family: inherit;
    color: #fff; background: linear-gradient(135deg, #ff5f9e, #ff74ab); cursor: pointer;
    box-shadow: 0 4px 12px rgba(255,77,141,.3); }
  .hud button:active { transform: scale(.96); }
  .phone { width: 375px; height: 812px; border-radius: 40px; overflow: hidden; background: #f7f7fa;
           box-shadow: 0 24px 60px rgba(50, 30, 70, .22); position: relative; display: flex; flex-direction: column; }

  @keyframes slideUp { from { transform: translateY(105%); } to { transform: translateY(0); } }
  .panel.play { animation: slideUp .36s cubic-bezier(.22, .61, .36, 1); }

  /* 上半屏：整页背景 */
  .stage { position: relative; flex: 1 1 auto; min-height: 170px; overflow: hidden; }
  .stage-bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
  .stage-scrim { position: absolute; inset: 0;
    background: linear-gradient(180deg, rgba(247,247,250,0) 46%, rgba(247,247,250,.55) 72%,
                rgba(247,247,250,.92) 90%, #f7f7fa 100%); }
  .statusbar { position: absolute; top: 0; left: 0; right: 0; height: 44px; z-index: 3;
    display: flex; align-items: center; justify-content: space-between; padding: 0 20px;
    font-size: 12px; font-weight: 600; color: #23202a; }
  .nav { position: absolute; top: 44px; left: 0; z-index: 3; padding-left: 12px; }
  .nav-back { width: 44px; height: 44px; border-radius: 50%; background: rgba(255,255,255,.82);
    display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 7px rgba(60,30,80,.1);
    cursor: pointer; transition: transform .12s ease, filter .12s ease; }
  .nav-back:active { transform: scale(.94); filter: brightness(.94); }
  .nav-back-ic { width: 10px; height: 10px; border-left: 2px solid #23202a; border-bottom: 2px solid #23202a;
    transform: rotate(45deg); margin-left: 3px; }

  /* 下半屏：登录面板 */
  .panel { position: relative; z-index: 2; flex: 0 0 auto; background: #fff; border-radius: 22px 22px 0 0;
    padding: 15px 20px 20px; box-shadow: 0 -5px 18px rgba(60,30,80,.07); }
  .panel-art { display: block; width: 100%; border-radius: 16px; margin-bottom: 13px; }
  .panel-title { font-size: 22px; font-weight: 800; color: #23202a; text-align: center; letter-spacing: 1px; }
  .panel-sub { margin-top: 6px; font-size: 15px; color: #7e7689; text-align: center; }

  .login-btn { width: 100%; margin-top: 20px; height: 50px; line-height: 50px; border: 0;
    border-radius: 25px; background: linear-gradient(135deg, #ff5f9e, #ff74ab); color: #fff;
    font-size: 17px; font-weight: 700; letter-spacing: .5px; text-align: center; cursor: pointer;
    box-shadow: 0 6px 14px rgba(255,77,141,.28); font-family: inherit;
    transition: transform .12s ease, filter .12s ease; }
  .login-btn:active { transform: scale(.97); filter: brightness(.95); }

  .agree { display: flex; align-items: center; justify-content: center; flex-wrap: wrap;
    margin-top: 11px; min-height: 36px; font-size: 14px; }
  .agree-toggle { display: flex; align-items: center; padding: 6px 3px 6px 0; cursor: pointer; }
  .agree-check { width: 18px; height: 18px; border-radius: 50%; border: 1px solid #d9d2e2; background: #fff;
    display: flex; align-items: center; justify-content: center; margin-right: 5px; flex: 0 0 auto;
    font-size: 11px; color: #fff; font-weight: 700; line-height: 1; }
  .agree-check.on { background: #ff4d8d; border-color: #ff4d8d; }
  .agree-txt { font-size: 14px; color: #7e7689; }
  .agree-link { font-size: 14px; color: #ff4d8d; padding: 6px 0; cursor: pointer; }
  .guest { margin-top: 3px; padding: 11px 0 4px; text-align: center; font-size: 15px; color: #7e7689;
    cursor: pointer; }
</style>
</head>
<body>
<div class="hud">
  <span>启动流程：首页 → 未登录则自动滑入本页 → 登录或「先随便看看」回首页</span>
  <button onclick="var p=document.querySelector('.panel');p.classList.remove('play');void p.offsetWidth;p.classList.add('play');">播放启动动画</button>
</div>
<div class="phone">
  <div class="stage">
    <img class="stage-bg" src="__HOSPITAL__" alt="">
    <div class="stage-scrim"></div>
    <div class="statusbar"><span>9:41</span><span>&#9679;&#9679;&#9679; &#128267;</span></div>
    <div class="nav"><div class="nav-back"><div class="nav-back-ic"></div></div></div>
  </div>

  <div class="panel">
    <img class="panel-art" src="__CARE__" alt="">
    <div class="panel-title">医伴心途</div>
    <div class="panel-sub">陪您和家人，安心看每一次病</div>
    <button class="login-btn">微信授权登录</button>
    <div class="agree">
      <div class="agree-toggle" onclick="document.querySelector('.agree-check').classList.toggle('on');
        this.querySelector('.agree-check').textContent =
        this.querySelector('.agree-check').classList.contains('on') ? '\u2713' : '';">
        <div class="agree-check"></div><span class="agree-txt">我已阅读并同意</span>
      </div>
      <span class="agree-link">《用户协议》</span>
      <span class="agree-txt">与</span>
      <span class="agree-link">《隐私政策》</span>
    </div>
    <div class="guest">先随便看看</div>
  </div>
</div>
</body>
</html>
"""

html = TPL.replace('__HOSPITAL__', uri('bg/hospital.jpg')).replace('__CARE__', uri('login/care.jpg'))
io.open(OUT, 'w', encoding='utf-8', newline='').write(html)
print(u'saved %s  %dKB' % (OUT, os.path.getsize(OUT) // 1024))
