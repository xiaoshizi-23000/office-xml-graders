# -*- coding: utf-8 -*-
"""启动判分程序，抓它的窗口，再关掉。"""
import ctypes
import ctypes.wintypes as wt
import os
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grab import capture, window_titles

SRC = r'C:\Users\23000\Desktop\操作题评分\四川Windows操作\网络'
WORK = r'C:\Users\23000\Desktop\操作题评分\_re\run'
SHOTS = r'C:\Users\23000\Desktop\操作题评分\_re\shots'

os.makedirs(WORK, exist_ok=True)
os.makedirs(SHOTS, exist_ok=True)
for name in ('iesxWin7.exe', 'iesxWin7'):
    src = os.path.join(SRC, name)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(WORK, name))

p = subprocess.Popen([os.path.join(WORK, 'iesxWin7.exe')], cwd=WORK,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3)
wins = window_titles(p.pid)
print('pid', p.pid, '窗口数', len(wins))
for i, (hwnd, title, r) in enumerate(wins):
    print('  [%d] %r rect=(%d,%d)-(%d,%d)' % (i, title, r.left, r.top, r.right, r.bottom))
    out = os.path.join(SHOTS, 'win_%d.bmp' % i)
    print('      ->', capture(hwnd, out), out)

time.sleep(1)
p.terminate()
try:
    p.wait(timeout=5)
except Exception:
    p.kill()
print('done, files:', os.listdir(SHOTS))
