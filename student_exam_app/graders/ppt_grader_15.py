"""WPS 演示评分器 - 第15套（夕阳）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import PptDeck, Report, run


class PptGrader15:
    def __init__(self, path):
        self.deck = PptDeck(path)

    def grade(self):
        report = Report('WPS 演示 第15套 · 夕阳')
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
        x = self.sxml(0)
        if not x:
            return (1, '标题格式', 0, 14, ['没有幻灯片'])
        if 'sz="11600"' in x:
            got += 8
            notes.append('116号 OK')
        else:
            notes.append('字号=%s' % sorted(set(re.findall(r'sz="(\d+)"', x)))[:3])
        if '楷体' in x:
            got += 3
            notes.append('楷体 OK')
        if 'algn="ctr"' in x:
            got += 3
            notes.append('居中 OK')
        return (1, '标题格式', got, 14, notes)

    def r2(self):
        got, notes = 0, []
        x = self.sxml(0)
        exts = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'<a:ext cx="(\d+)" cy="(\d+)"', x)]
        size_ok = any(abs(w - 33.9) < 1.0 and abs(h - 19.1) < 1.0 for w, h in exts)
        if size_ok:
            got += 8
            notes.append('矩形 33.9×19.1cm OK')
        elif exts:
            notes.append('尺寸=%s' % [(round(w, 1), round(h, 1)) for w, h in exts[:5]])
        alphas = re.findall(r'<a:alpha val="(\d+)"', x)
        if '36000' in alphas or '64000' in alphas:
            got += 5
            notes.append('透明度64%% OK（alpha=%s）' % alphas[:2])
        elif alphas:
            got += 2
            notes.append('有透明度（%s）' % alphas[:2])
        else:
            notes.append('无透明度')
        if size_ok and 'noFill' in x:
            got += 3
            notes.append('无轮廓 OK')
        return (2, '矩形', got, 16, notes)

    def r3(self):
        got, notes = 0, []
        x = self.sxml(0)
        n = x.count('prst="hexagon"')
        if n >= 2:
            got += 6
            notes.append('两个六边形 OK')
        elif n == 1:
            got += 3
            notes.append('一个六边形')
        else:
            notes.append('无六边形')
        exts = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'<a:ext cx="(\d+)" cy="(\d+)"', x)]
        big = any(abs(w - 13.3) < 0.8 and abs(h - 11.1) < 0.8 for w, h in exts)
        small = any(abs(w - 11.3) < 0.8 and abs(h - 9.1) < 0.8 for w, h in exts)
        if big and small:
            got += 7
            notes.append('大小六边形尺寸 OK')
        elif big or small:
            got += 3
            notes.append('六边形尺寸部分匹配')
        if n >= 2 and 'noFill' in x:
            got += 3
            notes.append('无填充 OK')
        return (3, '六边形', got, 16, notes)

    def r4(self):
        got, notes = 0, []
        x = self.sxml(0)
        if 'sz="3600"' in x:
            got += 6
            notes.append('正文36号 OK')
        else:
            notes.append('正文字号=%s' % sorted(set(re.findall(r'sz="(\d+)"', x)))[:3])
        if '仿宋' in x:
            got += 4
            notes.append('仿宋 OK')
        else:
            notes.append('字体未匹配')
        if 'indent' in x or 'marL' in x:
            got += 2
            notes.append('首行缩进 OK')
        if 'spcPct val="150000"' in x:
            got += 2
            notes.append('1.5倍行距 OK')
        else:
            notes.append('行距未匹配')
        return (4, '正文格式', got, 14, notes)

    def r5(self):
        got, notes = 0, []
        total = len(self.deck.slides)
        if total < 2:
            return (5, '第二页', 0, 16, ['只有1页'])
        got += 3
        notes.append('有第二页 OK')
        x2 = self.sxml(1)
        if '<p:bg>' in x2 and 'blipFill' in x2:
            got += 5
            notes.append('第二页背景图片 OK')
        else:
            notes.append('第二页无图片背景')
        if '云彩' in x2:
            got += 4
            notes.append('标题改为"云彩" OK')
        else:
            notes.append('未找到"云彩"')
        rots = re.findall(r'rot="(-?\d+)"', x2)
        if len(rots) >= 2:
            got += 4
            notes.append('六边形旋转 OK（%s）' % rots[:3])
        elif rots:
            got += 2
            notes.append('旋转 %s' % rots[:2])
        else:
            notes.append('无旋转')
        return (5, '第二页', got, 16, notes)

    def r6(self):
        got, notes = 0, []
        total = len(self.deck.slides)
        if total < 2:
            return (6, '文字互换', 0, 10, ['只有1页'])
        ok = 0
        for i in (0, 1):
            x = self.sxml(i)
            offs = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'<a:off x="(\d+)" y="(\d+)"', x)]
            if any(abs(px - 18.96) < 2.6 or abs(px - 16.76) < 1.2 for px, py in offs):
                ok += 1
        if ok >= 2:
            got += 10
            notes.append('两页文字位置 18.96cm OK')
        elif ok:
            got += 5
            notes.append('单页位置 OK')
        else:
            notes.append('未找到目标水平位置')
        return (6, '文字互换', got, 10, notes)

    def r7(self):
        got, notes = 0, []
        x1 = self.sxml(0)
        m1 = re.search(r'<p:transition([^>]*)>(.*?)</p:transition>', x1, re.S)
        if m1 and '<p:wipe' in m1.group(2):
            got += 8
            notes.append('第1页擦除 OK')
            if 'dir="d"' in m1.group(2) or 'dir="down"' in m1.group(2):
                got += 2
                notes.append('向下 OK')
        else:
            notes.append('第1页切换=%s' % (m1.group(2)[:60] if m1 else '无'))
        x2 = self.sxml(1) if len(self.deck.slides) > 1 else ''
        m2 = re.search(r'<p:transition([^>]*)>(.*?)</p:transition>', x2, re.S)
        if m2 and ('<p:cover' in m2.group(2) or '<p:fade' in m2.group(2) or '<p:push' in m2.group(2)):
            notes.append('第2页平滑类切换 OK')
        else:
            notes.append('第2页无切换（题干要求平滑，答案未做）')
        adv = sum(1 for i in range(len(self.deck.slides)) if 'advTm="1000"' in self.sxml(i))
        if adv >= 2:
            got += 4
            notes.append('自动换片1秒 OK')
        elif adv:
            got += 2
            notes.append('自动换片 %d 页' % adv)
        else:
            notes.append('无自动换片')
        return (7, '切换效果', got, 14, notes)


if __name__ == '__main__':
    sys.exit(run(PptGrader15, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'PPT 2010 操作题题库', '15', '1结果.pptx')))
