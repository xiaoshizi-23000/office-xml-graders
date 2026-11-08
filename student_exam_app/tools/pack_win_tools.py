# -*- coding: utf-8 -*-
"""打包 Windows 操作题判分程序。

用法：
    python tools/pack_win_tools.py

生成三处：
    四川Windows操作.zip              全家桶，发班级群用
    static/win_tools.zip             全家桶，站点下载用
    static/progs/<程序>.zip          单程序包，页面每个类型一个下载按钮

说明文件统一叫 README.txt（ASCII 文件名 + UTF-8 BOM），
避免中文名或编码在部分解压软件/记事本里打不开。
"""
import json
import os
import zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(BASE)
SRC = os.path.join(ROOT, '四川Windows操作')
STATIC = os.path.join(BASE, 'static')
PROGS = os.path.join(STATIC, 'progs')

NAMES = {
    'iesxWin7': 'Internet选项', 'wangluoWin7': 'IP地址设置', 'bhsxWin7': '宽带连接',
    'jlljWin7': '新建连接', 'qyszWin7': '区域和语言', 'rwlsxWin7': '任务栏设置',
    'xianshiWin7': '显示设置', 'srfWin7': '输入法设置', 'tjdyjWin7': '打印机设置',
    'outlook': '电子邮件',
}

ALL_README = """Windows 操作题判分程序 · 使用说明
（本文件用记事本打开即可）

一、怎么用
1. 解压到任意文件夹，路径不要带空格。
2. 每个程序旁边都有一个和它同名、没有扩展名的文件，两个必须放在一起，名字都不能改。
3. 按题目要求改设置，双击对应的 exe，在它打开的控制面板里做完，然后关掉程序。
4. 同目录那个没有扩展名的文件就是你的设置记录，上传到
   https://web.xiaoshizi.asia/windows
   系统会自动判分。
5. 要重做：删掉那个没有扩展名的文件，再运行一次程序，会重新生成。

二、程序对应关系
网络\\Internet选项.exe     主页、历史记录、安全级别等
网络\\IP地址设置.exe       IPv4 地址、DNS、网关
网络\\宽带连接.exe         宽带连接属性与选项
网络\\新建连接.exe         新建连接向导、PPPoE
操作系统\\区域和语言.exe   区域格式、日期时间格式
操作系统\\任务栏设置.exe   任务栏、开始菜单、通知区域
操作系统\\显示设置.exe     主题、桌面、分辨率、屏保
操作系统\\输入法设置.exe   输入法、语言栏
操作系统\\打印机设置.exe   添加打印机、端口、共享
电子邮件.exe               邮件设置

三、注意
1. 只能在 Windows 上运行，Win7 / Win10 正常，Win11 部分项可能不生效。
2. 杀毒软件可能误报（程序要读注册表、写一个文本文件），加信任即可。
3. 同一类型只下载一份，几道题可以共用，不用每题重复下载。
4. 仅限本课程教学使用，请勿外传或上传到公开网盘。
"""

ONE_README = """{cn} · 使用说明
（本文件用记事本打开即可）

1. 解压到一个文件夹。{cn}.exe 和同目录下那个没有扩展名的 {cn} 文件必须放在一起，
   两个名字都不能改，程序靠文件名找自己的记录文件。
2. 按题目要求改设置，双击 {cn}.exe，在它打开的控制面板里做完，然后关掉程序。
3. 同目录的 {cn} 文件就是设置记录，上传到
   https://web.xiaoshizi.asia/windows
   系统会自动判分。
4. 要重做：删掉 {cn} 文件，再运行一次程序，会重新生成。

同一个类型的题只下载这一份就够了，不用每题重复下载。
"""

BOM = b'\xef\xbb\xbf'


def all_files():
    out = []
    for root, _, files in os.walk(SRC):
        for name in files:
            if name.endswith('.zip'):
                continue
            full = os.path.join(root, name)
            out.append((full, os.path.relpath(full, SRC)))
    return out


def write_all(path):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('README.txt', BOM + ALL_README.encode('utf-8'))
        for full, rel in all_files():
            z.write(full, rel.replace('\\', '/'))
    return os.path.getsize(path)


def write_one(prog, cn):
    os.makedirs(PROGS, exist_ok=True)
    path = os.path.join(PROGS, prog + '.zip')
    exe = None
    cfg = None
    for root, _, files in os.walk(SRC):
        if cn + '.exe' in files:
            exe = os.path.join(root, cn + '.exe')
            cfg = os.path.join(root, cn)
            break
    if not exe:
        return 0
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(exe, cn + '.exe')
        if os.path.exists(cfg):
            z.write(cfg, cn)
        z.writestr('README.txt', BOM + ONE_README.format(cn=cn).encode('utf-8'))
    return os.path.getsize(path)


def main():
    if not os.path.isdir(SRC):
        print('找不到源目录：%s' % SRC)
        return 1
    json.dump(NAMES, open(os.path.join(BASE, 'windows_kb', 'exe_names.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('全家桶 四川Windows操作.zip：%.0f KB' % (write_all(os.path.join(ROOT, '四川Windows操作.zip')) / 1024))
    print('全家桶 static/win_tools.zip：%.0f KB' % (write_all(os.path.join(STATIC, 'win_tools.zip')) / 1024))
    for prog, cn in NAMES.items():
        size = write_one(prog, cn)
        print('  %-14s %-12s %s' % (prog, cn, ('%.0f KB' % (size / 1024)) if size else '未找到'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
