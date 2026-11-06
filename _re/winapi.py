# -*- coding: utf-8 -*-
"""枚举窗口的子控件（类名/文本/矩形），并支持按坐标点击。"""
import ctypes
import ctypes.wintypes as wt
import sys

user32 = ctypes.windll.user32

WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def children(hwnd):
    out = []

    def cb(h, _):
        cls = ctypes.create_unicode_buffer(64)
        user32.GetClassNameW(h, cls, 64)
        n = user32.GetWindowTextLengthW(h)
        buf = ctypes.create_unicode_buffer(n + 1)
        user32.GetWindowTextW(h, buf, n + 1)
        r = wt.RECT()
        user32.GetWindowRect(h, ctypes.byref(r))
        out.append({'hwnd': h, 'cls': cls.value, 'text': buf.value,
                    'rect': (r.left, r.top, r.right, r.bottom)})
        return True

    user32.EnumChildWindows(hwnd, WNDENUMPROC(cb), 0)
    return out


def click(hwnd, x, y):
    """向窗口客户区坐标发送一次左键按下/抬起。"""
    lp = (y << 16) | (x & 0xFFFF)
    user32.PostMessageW(hwnd, 0x0200, 0, lp)   # WM_MOUSEMOVE
    user32.PostMessageW(hwnd, 0x0201, 1, lp)   # WM_LBUTTONDOWN
    user32.PostMessageW(hwnd, 0x0202, 0, lp)   # WM_LBUTTONUP


if __name__ == '__main__':
    hwnd = int(sys.argv[1])
    for c in children(hwnd):
        r = c['rect']
        print('%-22s %-40r (%d,%d)-(%d,%d)' % (c['cls'], c['text'][:38], r[0], r[1], r[2], r[3]))
