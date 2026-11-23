"""WPS 演示评分器 - 第18套（夏至）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import PptDeck, Report, run, check_show


class PptGrader18:
    def __init__(self, path):
        self.deck = PptDeck(path)

    def grade(self):
        report = Report('WPS 演示 第18套 · 夏至')
        for fn in (self.r1, self.r2, self.r3, self.r4, self.r5, self.r6):
            report.add(*fn())
        return report

    def sxml(self, idx):
        slides = self.deck.slides
        return self.deck.read(slides[idx].part) if idx < len(slides) else ''

    def r1(self):
        got, notes = 0, []
        x = self.sxml(0)
        if not x:
            return (1, '标题格式', 0, 16, ['没有幻灯片'])
        if '夏至' in x:
            got += 3
            notes.append('标题"夏至" OK')
        if 'sz="13000"' in x:
            got += 5
            notes.append('130号 OK')
        else:
            notes.append('字号=%s' % sorted(set(re.findall(r'sz="(\d+)"', x)))[:3])
        if '楷体' in x:
            got += 4
            notes.append('楷体 OK')
        if '298681' in x.upper():
            got += 2
            notes.append('颜色 RGB(41,134,129) OK')
        else:
            notes.append('颜色未匹配')
        if 'outerShdw' in x or 'shadow' in x:
            got += 2
            notes.append('文字阴影 OK')
        else:
            notes.append('无阴影')
        return (1, '标题格式', got, 16, notes)

    def r2(self):
        got, notes = 0, []
        withbg = []
        for n in self.deck.names:
            if re.match(r'ppt/slideLayouts/slideLayout\d+\.xml$', n):
                x = self.deck.read(n)
                if '<p:bg>' in x and 'blipFill' in x:
                    withbg.append(n)
        if len(withbg) >= 2:
            got += 12
            notes.append('两个版式背景图片 OK（%d个）' % len(withbg))
        elif withbg:
            got += 6
            notes.append('版式背景 %d 个' % len(withbg))
        else:
            notes.append('版式无背景图片')
        titles = 0
        for n in self.deck.names:
            if re.match(r'ppt/(slideMasters|slideLayouts)/slide(Master|Layout)\d+\.xml$', n):
                x = self.deck.read(n)
                if '楷体' in x or '宋体' in x:
                    titles += 1
        if titles:
            got += 6
            notes.append('母版标题字体 OK')
        else:
            notes.append('母版标题字体未改')
        lay = 0
        for n in withbg:
            x = self.deck.read(n)
            if 'sz="3400"' in x or 'sz="3200"' in x:
                lay += 1
        if lay:
            got += 4
            notes.append('版式标题字号 OK')
        return (2, '母版与版式', got, 22, notes)

    def r3(self):
        got, notes = 0, []
        total = len(self.deck.slides)
        body = 0
        for i in range(1, total):
            x = self.sxml(i)
            if '仿宋' in x and 'sz="2000"' in x:
                body += 1
        if body >= total - 2:
            got += 8
            notes.append('正文仿宋20 OK（%d页）' % body)
        elif body >= (total - 1) * 0.6:
            got += 6
            notes.append('正文仿宋20 覆盖 %d/%d 页' % (body, total - 1))
        elif body:
            got += 3
            notes.append('正文格式 %d 页' % body)
        else:
            notes.append('正文未设仿宋20')
        indent = sum(1 for i in range(1, total) if 'indent' in self.sxml(i) or 'marL' in self.sxml(i))
        if indent >= 2:
            got += 4
            notes.append('首行缩进 OK')
        spacing = sum(1 for i in range(1, total) if 'spcPct val="200000"' in self.sxml(i))
        if spacing >= 2:
            got += 4
            notes.append('2倍行距 OK')
        else:
            notes.append('行距匹配 %d 页' % spacing)
        foot = False
        for n in self.deck.names:
            if 'slideMaster' in n and n.endswith('.xml'):
                c = self.deck.read(n)
                if '夏至时节' in c or '2025-06-21' in c:
                    foot = True
        if foot:
            got += 6
            notes.append('日期/页脚 OK')
        else:
            notes.append('未设页脚')
        return (3, '正文与页脚', got, 20, notes)

    def r4(self):
        got, notes = 0, []
        if len(self.deck.slides) < 6:
            return (4, '第6页图片', 0, 16, ['页数不足6页'])
        x = self.sxml(5)
        has_pic = '<p:pic>' in x
        if has_pic:
            got += 5
            notes.append('图片 OK')
        exts = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'<a:ext cx="(\d+)" cy="(\d+)"', x)]
        if has_pic and any(abs(h - 10) < 0.8 and abs(w - 9) < 0.8 for w, h in exts):
            got += 5
            notes.append('10×9cm OK')
        elif exts:
            notes.append('尺寸=%s' % [(round(w, 1), round(h, 1)) for w, h in exts[:3]])
        if 'p:timing' in x:
            got += 4
            notes.append('有动画 OK')
            if 'dur="3000"' in x:
                got += 2
                notes.append('持续3秒 OK')
        else:
            notes.append('无动画')
        return (4, '第6页图片', got, 16, notes)

    def r5(self):
        got, notes = 0, []
        if len(self.deck.slides) < 9:
            return (5, '第9页格式', 0, 12, ['页数不足9页'])
        x = self.sxml(8)
        if 'w="50800"' in x:
            got += 5
            notes.append('4磅边框 OK')
        else:
            notes.append('线宽=%s' % re.findall(r'<a:ln w="(\d+)"', x)[:2])
        if 'sysDashDot' in x or 'dashDot' in x:
            got += 3
            notes.append('划线-点线 OK')
        else:
            notes.append('线型未匹配')
        if 'softEdge' in x or 'softEdge' in self.sxml(8):
            got += 4
            notes.append('柔化边缘 OK')
        else:
            notes.append('无柔化')
        alphas = re.findall(r'<a:alpha val="(\d+)"', x)
        if alphas:
            notes.append('透明度已设（alpha=%s）' % alphas[:2])
        else:
            notes.append('无透明度（答案未做）')
        return (5, '第9页格式', got, 12, notes)

    def r6(self):
        got, notes = 0, []
        total = len(self.deck.slides)
        blind = 0
        for i in range(total):
            m = re.search(r'<p:transition([^>]*)>(.*?)</p:transition>', self.sxml(i), re.S)
            if m and '<p:blinds' in m.group(2):
                blind += 1
        if total and blind == total:
            got += 8
            notes.append('全部百叶窗 OK（%d页）' % blind)
        elif blind:
            got += 3
            notes.append('百叶窗 %d/%d 页' % (blind, total))
        else:
            notes.append('未找到百叶窗')
        x0 = self.sxml(0)
        m = re.search(r'<p:transition([^>]*)>(.*?)</p:transition>', x0, re.S)
        if m and 'dir="vert"' in m.group(2):
            got += 3
            notes.append('垂直方向 OK')
        if m and ('dur="2000"' in m.group(1) or 'p14:dur="2000"' in m.group(1)):
            got += 3
            notes.append('速度2秒 OK')
        else:
            notes.append('时长=%s' % (re.findall(r'dur="(\d+)"', m.group(1))[:2] if m else '无'))
        return (6, '切换效果', got, 6, notes)


    def r_show(self):
        ok, detail = check_show(self.deck, kind='present', loop=1, st=2, en=12)
        return (99, '放映设置', 8 if ok else 0, 8, [detail])


if __name__ == '__main__':
    sys.exit(run(PptGrader18, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'PPT 2010 操作题题库', '18', '1结果.pptx')))
