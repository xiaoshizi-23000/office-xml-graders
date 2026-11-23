"""WPS 演示评分器 - 第16套（甜品）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import PptDeck, Report, run, check_show


class PptGrader16:
    def __init__(self, path):
        self.deck = PptDeck(path)

    def grade(self):
        report = Report('WPS 演示 第16套 · 甜品')
        for fn in (self.r1, self.r2, self.r3, self.r4, self.r5, self.r6):
            report.add(*fn())
        return report

    def slide(self, idx):
        slides = self.deck.slides
        return slides[idx] if idx < len(slides) else None

    def sxml(self, idx):
        s = self.slide(idx)
        return self.deck.read(s.part) if s else ''

    def r1(self):
        got, notes = 0, []
        x = self.sxml(0)
        if not x:
            return (1, '标题与矩形', 0, 20, ['没有幻灯片'])
        if 'sz="13000"' in x:
            got += 6
            notes.append('130号 OK')
        else:
            notes.append('字号=%s' % sorted(set(re.findall(r'sz="(\d+)"', x)))[:3])
        if '宋体' in x:
            got += 3
            notes.append('宋体 OK')
        if '甜品' in x:
            got += 2
            notes.append('标题文字 OK')
        exts = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'<a:ext cx="(\d+)" cy="(\d+)"', x)]
        size_ok = any(abs(w - 11.6) < 0.8 and abs(h - 14.9) < 0.8 for w, h in exts)
        if size_ok:
            got += 5
            notes.append('矩形 11.6×14.9cm OK')
        elif exts:
            notes.append('尺寸=%s' % [(round(w, 1), round(h, 1)) for w, h in exts[:4]])
        alphas = re.findall(r'<a:alpha val="(\d+)"', x)
        if '40000' in alphas or '60000' in alphas:
            got += 4
            notes.append('透明度40%% OK（alpha=%s）' % alphas[:2])
        elif alphas:
            got += 2
            notes.append('有透明度（%s）' % alphas[:2])
        else:
            notes.append('无透明度')
        return (1, '标题与矩形', got, 20, notes)

    def r2(self):
        got, notes = 0, []
        x1 = self.sxml(0)
        x2 = self.sxml(1) if len(self.deck.slides) > 1 else ''
        if '<p:bg>' in x1 and 'blipFill' in x1:
            got += 8
            notes.append('第一页图片背景 OK')
        else:
            notes.append('第一页无图片背景')
        bg2 = re.search(r'<p:bg>.*?</p:bg>', x2, re.S)
        if bg2 and ('srgbClr' in bg2.group(0) or 'schemeClr' in bg2.group(0)) and 'blipFill' not in bg2.group(0):
            got += 4
            notes.append('第二页纯色背景 OK')
            if 'FFE38D' in bg2.group(0).upper():
                got += 2
                notes.append('颜色 RGB(255,227,141) OK')
        else:
            notes.append('第二页无纯色背景')
        return (2, '背景设置', got, 14, notes)

    def r3(self):
        got, notes = 0, []
        x = self.sxml(1)
        if not x:
            return (3, '第2页正文', 0, 18, ['没有第2页'])
        if '楷体' in x and 'sz="2900"' in x:
            got += 6
            notes.append('楷体29 OK')
        else:
            notes.append('字号/字体=%s' % (sorted(set(re.findall(r'sz="(\d+)"', x)))[:3]))
        if 'eaVert' in x or 'vert="vert"' in x:
            got += 5
            notes.append('竖排 OK')
        else:
            notes.append('未竖排')
        if 'spcPct val="150000"' in x:
            got += 4
            notes.append('1.5倍行距 OK')
        else:
            notes.append('行距未匹配')
        if 'buChar' in x and ('■' in x or 'u25A0' in x or 'a0a' in x.lower() or 'char="n"' in x):
            got += 4
            notes.append('实心方块项目符号 OK')
        elif 'buChar' in x:
            got += 2
            notes.append('有项目符号（char=%s）' % re.findall(r'buChar char="([^"]*)"', x)[:2])
        else:
            notes.append('无项目符号')
        return (3, '第2页正文', got, 18, notes)

    def r4(self):
        got, notes = 0, []
        x = self.sxml(1)
        if 'round2DiagRect' in x:
            got += 5
            notes.append('对角圆角矩形 OK')
        else:
            notes.append('无对角圆角矩形')
        exts = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'<a:ext cx="(\d+)" cy="(\d+)"', x)]
        if any(abs(w - 31.3) < 1.2 and abs(h - 16.6) < 1.0 for w, h in exts):
            got += 4
            notes.append('31.3×16.6cm OK')
        elif exts:
            notes.append('尺寸=%s' % [(round(w, 1), round(h, 1)) for w, h in exts[:4]])
        if '<p:pic>' in x:
            got += 4
            notes.append('图片 OK')
        if 'glow' in x:
            got += 5
            notes.append('发光 OK')
        else:
            notes.append('无发光')
        return (4, '圆角矩形与图片', got, 18, notes)

    def r5(self):
        got, notes = 0, []
        x = self.sxml(1)
        if 'star5' not in x:
            return (5, '五角星', 0, 16, ['没有五角星'])
        got += 5
        notes.append('五角星 OK')
        exts = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'<a:ext cx="(\d+)" cy="(\d+)"', x)]
        if any(abs(w - 3.2) < 0.6 and abs(h - 3.2) < 0.6 for w, h in exts):
            got += 5
            notes.append('3.2×3.2cm OK')
        elif exts:
            notes.append('尺寸=%s' % [(round(w, 1), round(h, 1)) for w, h in exts[:4]])
        if 'gradFill' in x:
            got += 3
            notes.append('渐变填充 OK')
        if 'path="circle"' in x or 'gradFill' in x:
            got += 1
            notes.append('射线渐变 OK')
        rots = re.findall(r'rot="(-?\d+)"', x)
        if any(abs(int(r)) in (5400000, 16200000) for r in rots):
            got += 2
            notes.append('旋转90° OK')
        else:
            notes.append('旋转=%s' % rots[:3])
        return (5, '五角星', got, 16, notes)

    def r6(self):
        got, notes = 0, []
        total = len(self.deck.slides)
        split = 0
        for i in range(total):
            m = re.search(r'<p:transition([^>]*)>(.*?)</p:transition>', self.sxml(i), re.S)
            if m and '<p:split' in m.group(2):
                split += 1
        if total and split == total:
            got += 8
            notes.append('全部"分割"切换 OK（%d页）' % split)
        elif split:
            got += 4
            notes.append('分割 %d/%d 页' % (split, total))
        else:
            notes.append('未找到分割切换')
        x0 = self.sxml(0)
        if 'p14:dur="2250"' in x0 or 'dur="2250"' in x0:
            got += 3
            notes.append('速度2.25秒 OK')
        else:
            notes.append('时长=%s' % re.findall(r'dur="(\d+)"', x0)[:2])
        has_auto = any('advTm=' in self.sxml(i) and 'advTm="0"' not in self.sxml(i) for i in range(total))
        if split == total and not has_auto:
            got += 3
            notes.append('单击换片 OK（无自动换片）')
        elif 'advTm="0"' in x0:
            got += 3
            notes.append('单击换片 OK')
        return (6, '切换效果', got, 6, notes)


    def r_show(self):
        ok, detail = check_show(self.deck, kind='kiosk', loop=1, anim=0)
        return (99, '放映设置', 8 if ok else 0, 8, [detail])


if __name__ == '__main__':
    sys.exit(run(PptGrader16, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'PPT 2010 操作题题库', '16', '1结果.pptx')))
