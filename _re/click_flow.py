# -*- coding: utf-8 -*-
"""启动判分程序，按坐标点击进入子页面，逐级截图。"""
import ctypes
import ctypes.wintypes as wt
import os
import shutil
import subprocess
import time

from grab import capture, window_titles
from winapi import children, click

SRC = r'C:\Users\23000\Desktop\操作题评分\四川Windows操作\网络'
WORK = r'C:\Users\23000\Desktop\操作题评分\_re\run'
SHOTS = r'C:\Users\23000\Desktop\操作题评分\_re\shots'
os.makedirs(WORK, exist_ok=True)
os.makedirs(SHOTS, exist_ok=True)
for n in ('iesxWin7.exe', 'iesxWin7'):
    s = os.path.join(SRC, n)
    if os.path.exists(s):
        shutil.copy2(s, os.path.join(WORK, n))

p = subprocess.Popen([os.path.join(WORK, 'iesxWin7.exe')], cwd=WORK,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3)

wins = window_titles(p.pid)
main = None
for hwnd, title, r in wins:
    if title.strip():
        print('window %r %sx%s' % (title, r.right - r.left, r.bottom - r.top))
        if '控制面板' in title:
            main = hwnd

if not main:
    print('没找到控制面板窗口')
    p.terminate()
    raise SystemExit(1)

print('子控件:')
for c in children(main):
    r = c['rect']
    print('  %-20s %-30r (%d,%d)-(%d,%d)' % (c['cls'], c['text'][:28], r[0], r[1], r[2], r[3]))

# 控制面板里“网络和 Internet”大概在客户区 (150, 175) 附近
click(main, 150, 172)
time.sleep(2)
capture(main, os.path.join(SHOTS, 'step1_network.bmp'))
print('step1 截图完成')

p.terminate()
try:
    p.wait(timeout=5)
except Exception:
    p.kill()
print('files:', sorted(os.listdir(SHOTS)))
