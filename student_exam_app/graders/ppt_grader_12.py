"""WPS 演示评分器 - 第12套（墨）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import PptDeck, Report, run

A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
P = '{http://schemas.openxmlformats.org/presentationml/2006/main}'


class PptGrader12:
    def __init__(self, path):
        self.deck = PptDeck(path)

    def grade(self):
        report = Report('WPS 演示 第12套 · 墨')
        for fn in (self.r1, self.r2, self.r3, self.r4,
                   self.r5, self.r6, self.r7):
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
        pr = self.deck.read('ppt/presentation.xml')
        m = re.search(r'<p:sldSz cx="(\d+)" cy="(\d+)"', pr)
        if m:
            w, h = int(m.group(1)), int(m.group(2))
            if abs(w / h - 16 / 9) < 0.02:
                got += 12
                notes.append('16:9 宽屏 OK')
            else:
                notes.append('比例 %.2f' % (w / h))
        else:
            notes.append('读不到 sldSz')
        first = self.sxml(0)
        if '<p:bg>' in first and 'blipFill' in first:
            got += 6
            notes.append('首页图片背景 OK')
            if 'alphaModFix' in first or 'alpha' in first:
                got += 2
                notes.append('透明度 OK')
        else:
            notes.append('首页无图片背景')
        solid = 0
        for i in range(1, len(self.deck.slides)):
            x = self.sxml(i)
            if '<p:bg>' in x and ('srgbClr' in x or 'schemeClr' in x) and 'blipFill' not in x:
                solid += 1
        if solid:
            notes.append('其余页纯色背景 %d 页' % solid)
        return (1, '页面与背景', got, 20, notes)

    def r2(self):
        got, notes = 0, []
        s = self.slide(0)
        if s is None:
            return (2, '标题与副标题动画', 0, 14, ['没有幻灯片'])
        x = self.sxml(0)
        runs = re.findall(r'<a:rPr[^>]*sz="(\d+)"', x)
        if any(v == '15000' for v in runs):
            got += 6
            notes.append('主标题150号 OK')
        else:
            notes.append('字号=%s' % runs[:3])
        if '<a:u ' in x or 'u="sng"' in x:
            got += 2
            notes.append('下划线 OK')
        if 'algn="ctr"' in x:
            got += 2
            notes.append('居中 OK')
        anims = s.animations()
        if anims:
            got += 2
            notes.append('动画存在 OK')
            if re.search(r'dur="1500"', x):
                got += 2
                notes.append('持续1.5秒 OK')
            else:
                notes.append('时长=%s' % re.findall(r'dur="(\d+)"', x)[:3])
        else:
            notes.append('无动画')
        return (2, '标题与副标题动画', got, 14, notes)

    def r3(self):
        got, notes = 0, []
        x = self.sxml(1)
        if not x:
            return (3, '资料带形状', 0, 12, ['没有第2页'])
        hit = False
        for m in re.finditer(r'prst="(rect|flowChartDelay|flowChartMagneticTape|roundRect)"', x):
            hit = True
        exts = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'<a:ext cx="(\d+)" cy="(\d+)"', x)]
        size_ok = any(abs(w - 32.2) < 1.2 and abs(h - 2.5) < 0.5 for w, h in exts)
        if size_ok:
            got += 8
            notes.append('资料带 32.2×2.5cm OK')
        elif hit:
            notes.append('有形状但尺寸不符：%s' % [(round(w, 1), round(h, 1)) for w, h in exts[:3]])
        else:
            notes.append('未找到形状')
        if size_ok and '<a:noFill/>' in x:
            got += 4
            notes.append('无轮廓 OK')
        return (3, '资料带形状', got, 12, notes)

    def r4(self):
        got, notes = 0, []
        s = self.slide(1)
        if s is None:
            return (4, '备注与柔化', 0, 10, ['没有第2页'])
        note = ''
        for rid, pair in self.deck.rels(s.part).items():
            rtype, target = pair
            if 'notesSlide' in str(rtype):
                note = self.deck.read(target)
        if note and len(re.findall(r'<a:t>([^<]*)</a:t>', note)) >= 1:
            got += 6
            notes.append('备注内容 OK')
        else:
            notes.append('无备注')
        if 'softEdge' in self.sxml(1):
            got += 4
            notes.append('柔化边缘 OK')
        else:
            notes.append('无柔化边缘')
        return (4, '备注与柔化', got, 10, notes)

    def r5(self):
        got, notes = 0, []
        x = self.sxml(2)
        if not x:
            return (5, '矩形与段落', 0, 12, ['没有第3页'])
        exts = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'<a:ext cx="(\d+)" cy="(\d+)"', x)]
        size_ok = any(abs(w - 30.4) < 1.2 and abs(h - 14.08) < 1.0 for w, h in exts)
        if size_ok:
            got += 7
            notes.append('30.4×14.08cm OK')
        elif exts:
            notes.append('尺寸=%s' % [(round(w, 1), round(h, 1)) for w, h in exts[:3]])
        if size_ok and '<a:noFill/>' in x:
            got += 2
            notes.append('无填充 OK')
        if re.search(r'<a:ln w="76200"', x) or 'w="76200"' in x:
            got += 3
            notes.append('6磅轮廓 OK')
        else:
            notes.append('轮廓宽=%s' % re.findall(r'<a:ln w="(\d+)"', x)[:2])
        if 'indent="-28575"' in x or 'marL="28575"' in x or 'indent' in x:
            got += 1
            notes.append('首行缩进 OK')
        if 'lnSpc' in x and 'spcPct val="200000"' in x:
            got += 1
            notes.append('双倍行距 OK')
        return (5, '矩形与段落', got, 12, notes)

    def r6(self):
        got, notes = 0, []
        x = self.sxml(3)
        if not x:
            return (6, '三维旋转与动画', 0, 18, ['没有第4页'])
        if 'rotRev' in x or 'camera' in x:
            got += 8
            notes.append('三维透视 OK（%d处）' % max(x.count('rotRev'), x.count('camera')))
        else:
            notes.append('无三维旋转')
        s = self.slide(3)
        anims = s.animations() if s else []
        if len(anims) >= 2:
            got += 6
            notes.append('多处动画 OK（%d处）' % len(anims))
        elif anims:
            got += 3
            notes.append('动画 %d 处' % len(anims))
        else:
            notes.append('无动画')
        if re.search(r'dur="1000"', x):
            got += 2
            notes.append('持续1秒 OK')
        if 'presetClass="entr"' in x:
            got += 2
            notes.append('进入类动画 OK')
        return (6, '三维旋转与动画', got, 18, notes)

    def r7(self):
        got, notes = 0, []
        total = len(self.deck.slides)
        fade = 0
        for i in range(total):
            x = self.sxml(i)
            m = re.search(r'<p:transition[^>]*>(.*?)</p:transition>', x, re.S)
            if m and 'p:fade' in m.group(1):
                fade += 1
        if total and fade == total:
            got += 8
            notes.append('全部%dd页淡出 OK' % total)
        elif fade:
            got += 4
            notes.append('淡出 %d/%d 页' % (fade, total))
        else:
            names = []
            for i in range(total):
                m = re.search(r'<p:transition[^>]*>(.*?)</p:transition>', self.sxml(i), re.S)
                names.append(re.findall(r'<p:([a-zA-Z]+)', m.group(1))[:1] if m else [])
            notes.append('切换=%s' % names[:3])
        if re.search(r'dur="1000"', self.sxml(0)):
            got += 3
            notes.append('速度1秒 OK')
        if fade == total and ('advTm="0"' in self.sxml(0) or 'advClick' in self.sxml(0)):
            got += 3
            notes.append('单击换片 OK')
        return (7, '切换效果', got, 14, notes)


if __name__ == '__main__':
    sys.exit(run(PptGrader12, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'PPT 2010 操作题题库', '12', '1结果.pptx')))
