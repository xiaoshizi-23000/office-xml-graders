# -*- coding: utf-8 -*-
"""把 Windows 操作题的判分程序打成一个 zip，方便发班级群。

用法：
    python tools/pack_win_tools.py

生成 四川Windows操作.zip（含 网络/、操作系统/ 两个文件夹和一份说明）。
站点上不提供下载，这个包由老师自己通过群文件或教师机共享给学生。
"""
import os
import zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(os.path.dirname(BASE), '四川Windows操作')
OUT = os.path.join(os.path.dirname(BASE), '四川Windows操作.zip')

README = """Windows 操作题判分程序 · 使用说明

一、怎么用
1. 解压到任意文件夹（路径不要带空格和特殊字符）。
2. 按题目要求修改 Windows / IE 设置。
3. 双击对应科目文件夹里的程序（例如 网络\\iesxWin7.exe）。
4. 程序会在同目录生成一个和它同名的文件（没有扩展名），这就是你的设置清单。
5. 把这个文件上传到 https://web.xiaoshizi.asia/windows ，系统自动判分。

二、程序对应关系
网络\\iesxWin7.exe        Internet 选项（主页、历史记录、安全级别等）
网络\\wangluoWin7.exe     网络连接与共享设置
网络\\bhsxWin7.exe        网络保护相关设置
网络\\jlljWin7.exe        连接相关设置
操作系统\\xianshiWin7.exe 显示设置（分辨率、主题、桌面等）
操作系统\\qyszWin7.exe    区域和语言选项
操作系统\\rwlsxWin7.exe   日期和时间设置
操作系统\\srfWin7.exe     输入法设置
操作系统\\tjdyjWin7.exe   打印机设置
outlook.exe              Outlook 账户设置

三、注意
1. 这些是 Windows 本机程序，只能在 Windows 上运行，Win7/Win10 均可，Win11 部分项目可能不生效。
2. 杀毒软件可能误报，属于常见现象（程序读取注册表并写一个文本文件）。不放心可以先在虚拟机里跑。
3. 只有本课程教学使用，不要外传或上传到公开网盘。
"""


def main():
    if not os.path.isdir(SRC):
        print('找不到源目录：%s' % SRC)
        return 1
    n = 0
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('使用说明.txt', README.encode('utf-8'))
        for root, _, files in os.walk(SRC):
            for name in files:
                if name.endswith('.zip'):
                    continue
                full = os.path.join(root, name)
                rel = os.path.relpath(full, SRC)
                z.write(full, rel)
                n += 1
    print('已生成 %s，共 %d 个文件，%.1f KB' % (OUT, n, os.path.getsize(OUT) / 1024))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
