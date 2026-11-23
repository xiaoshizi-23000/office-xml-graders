"""WPS 演示评分器 - 第14套（茶叶）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import PptDeck, Report, run


class PptGrader14:
    def __init__(self, path):
        self.deck = PptDeck(path)

    def grade(self):
        report = Report('WPS 演示 第14套 · 茶叶')
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
        total = len(self.deck.slides)
        body_ok = 0
        title_ok = 0
        for i in range(total):
            x = self.sxml(i)
            if i != 1 and '楷体' in x and 'sz="2000"' in x:
                body_ok += 1
            if i != 0 and 'sz="3000"' in x and '楷体' in x:
                title_ok += 1
        if body_ok >= total - 2:
            got += 8
            notes.append('正文楷体20 OK（%d页）' % body_ok)
        elif body_ok:
            got += 4
            notes.append('正文格式 %d/%d 页' % (body_ok, total - 1))
        else:
            notes.append('正文未设楷体20')
        if title_ok >= total - 2:
            got += 8
            notes.append('标题楷体30 OK（%d页）' % title_ok)
        elif title_ok:
            got += 4
            notes.append('标题格式 %d 页' % title_ok)
        else:
            notes.append('标题未设楷体30')
        return (1, '正文与标题格式', got, 16, notes)

    def r2(self):
        got, notes = 0, []
        x = self.sxml(0)
        if not x:
            return (2, '主副标题', 0, 14, ['没有第1页'])
        if '茶叶' in x:
            got += 3
            notes.append('主标题"茶叶" OK')
        if 'sz="8000"' in x:
            got += 4
            notes.append('80号 OK')
        else:
            notes.append('字号=%s' % sorted(set(re.findall(r'sz="(\d+)"', x)))[:3])
        if '仿宋' in x:
            got += 2
            notes.append('仿宋 OK')
        if 'eaVert' in x or 'vert="vert"' in x:
            got += 4
            notes.append('副标题竖排 OK')
        else:
            notes.append('未竖排')
        if 'sz="1600"' in x:
            got += 1
            notes.append('副标题16号 OK')
        return (2, '主副标题', got, 14, notes)

    def r3(self):
        got, notes = 0, []
        x = self.sxml(0)
        if 'roundRect' not in x:
            return (3, '圆角矩形与直线', 0, 14, ['没有圆角矩形'])
        got += 5
        notes.append('圆角矩形 OK')
        exts = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'<a:ext cx="(\d+)" cy="(\d+)"', x)]
        if any(abs(w - 11) < 0.8 and abs(h - 13.6) < 0.8 for w, h in exts):
            got += 5
            notes.append('11×13.6cm OK')
        elif exts:
            notes.append('尺寸=%s' % [(round(w, 1), round(h, 1)) for w, h in exts[:4]])
        if re.search(r'srgbClr val="32501C"', x) or '32501C' in x.upper():
            got += 2
            notes.append('填充色 32501C OK')
        if x.count('prst="line"') or 'prstGeom prst="line"' in x:
            got += 2
            notes.append('直线形状 OK')
        else:
            notes.append('无直线形状')
        return (3, '圆角矩形与直线', got, 14, notes)

    def r4(self):
        got, notes = 0, []
        x = self.sxml(1)
        if not x:
            return (4, '第2页形状与链接', 0, 16, ['没有第2页'])
        alphas = re.findall(r'<a:alpha val="(\d+)"', x)
        if 'alpha' in x and ('5000' in alphas or '50000' in alphas):
            got += 4
            notes.append('矩形透明度95%% OK（alpha=%s）' % alphas[:2])
        elif 'alpha' in x:
            got += 2
            notes.append('有透明度（%s）' % alphas[:2])
        else:
            notes.append('无透明度')
        if 'buChar' in x and ('diamond' in x or '◆' in x):
            got += 4
            notes.append('菱形项目符号 OK')
        elif 'buChar' in x:
            got += 4
            notes.append('有项目符号（字符 %s）' % re.findall(r'buChar char="([^"]*)"', x)[:2])
        else:
            notes.append('无项目符号')
        if 'sz="3200"' in x and '宋体' in x:
            got += 4
            notes.append('宋体32 OK')
        else:
            notes.append('字号/字体=%s' % (re.findall(r'sz="(\d+)"', x)[:3]))
        if '<a:hlinkClick' in x:
            got += 4
            notes.append('超链接 OK（%d处）' % x.count('hlinkClick'))
        else:
            notes.append('无超链接')
        return (4, '第2页形状与链接', got, 16, notes)

    def r5(self):
        got, notes = 0, []
        x = self.sxml(3)
        if not x:
            return (5, '第4页矩形与文本框', 0, 12, ['没有第4页'])
        exts = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'<a:ext cx="(\d+)" cy="(\d+)"', x)]
        if any(abs(w - 16.77) < 1.0 and abs(h - 19.05) < 1.0 for w, h in exts):
            got += 5
            notes.append('16.77×19.05cm OK')
        elif exts:
            notes.append('尺寸=%s' % [(round(w, 1), round(h, 1)) for w, h in exts[:4]])
        if '36791E' in x.upper():
            got += 3
            notes.append('填充 36791E OK')
        if ('txbx' in x or '<p:sp>' in x) and '楷体' in x and 'sz="2000"' in x:
            got += 4
            notes.append('文本框楷体20 OK')
        return (5, '第4页矩形与文本框', got, 12, notes)

    def r6(self):
        got, notes = 0, []
        x = self.sxml(4)
        if not x:
            return (6, '图片与批注', 0, 14, ['没有第5页'])
        if '<p:pic>' in x:
            got += 4
            notes.append('图片 OK')
        if 'reflection' in x:
            got += 4
            notes.append('倒影 OK')
        else:
            notes.append('无倒影')
        comments = [n for n in self.deck.names if re.match(r'ppt/comments/comment\d+\.xml$', n)]
        if comments:
            cx = self.deck.read(comments[0])
            if '茶香四溢' in cx:
                got += 6
                notes.append('批注"茶香四溢" OK')
            else:
                got += 3
                notes.append('有批注但内容不符')
        else:
            notes.append('无批注')
        return (6, '图片与批注', got, 14, notes)

    def r7(self):
        got, notes = 0, []
        total = len(self.deck.slides)
        comb = 0
        for i in range(total):
            m = re.search(r'<p:transition([^>]*)>(.*?)</p:transition>', self.sxml(i), re.S)
            if m and '<p:comb' in m.group(2):
                comb += 1
        if total and comb == total:
            got += 8
            notes.append('全部梳理切换 OK（%d页）' % comb)
        elif comb:
            got += 4
            notes.append('梳理 %d/%d 页' % (comb, total))
        else:
            notes.append('未找到梳理切换')
        x0 = self.sxml(0)
        if 'sndAc' in x0 and 'wav' in x0:
            got += 3
            notes.append('切换声音 OK')
        else:
            notes.append('无切换声音')
        if 'advTm="3000"' in x0:
            got += 3
            notes.append('3秒自动换片 OK')
        elif 'advTm' in x0:
            got += 1
            notes.append('advTm=%s' % re.findall(r'advTm="(\d+)"', x0)[:1])
        else:
            notes.append('无自动换片')
        return (7, '切换效果', got, 14, notes)


if __name__ == '__main__':
    sys.exit(run(PptGrader14, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'PPT 2010 操作题题库', '14', '1结果.pptx')))
