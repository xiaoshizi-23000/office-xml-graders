"""WPS 演示评分器 - 第19套（小暑）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import PptDeck, Report, run, check_show


class PptGrader19:
    def __init__(self, path):
        self.deck = PptDeck(path)

    def grade(self):
        report = Report('WPS 演示 第19套 · 小暑')
        for fn in (self.r1, self.r2, self.r3, self.r4, self.r5):
            report.add(*fn())
        return report

    def sxml(self, idx):
        slides = self.deck.slides
        return self.deck.read(slides[idx].part) if idx < len(slides) else ''

    def r1(self):
        got, notes = 0, []
        x = self.sxml(0)
        if not x:
            return (1, '标题与副标题', 0, 20, ['没有幻灯片'])
        sizes = sorted(set(re.findall(r'sz="(\d+)"', x)))
        if '12000' in sizes:
            got += 9
            notes.append('主标题120号 OK')
        else:
            notes.append('标题字号=%s' % sizes[:4])
        if '楷体' in x:
            got += 3
            notes.append('楷体 OK')
        if '1900' in sizes:
            got += 4
            notes.append('副标题19号 OK')
        if '仿宋' in x:
            got += 2
            notes.append('副标题仿宋 OK')
        if ('effectLst' in x or 'prstTxWarp' in x or 'lnRef' in x) and '12000' in x:
            got += 2
            notes.append('艺术字样式 OK')
        return (1, '标题与副标题', got, 20, notes)

    def r2(self):
        got, notes = 0, []
        total = len(self.deck.slides)
        withbg = 0
        for i in range(1, total):
            x = self.sxml(i)
            bg = re.search(r'<p:bg>.*?</p:bg>', x, re.S)
            if bg and 'blipFill' in bg.group(0):
                withbg += 1
        if total > 1 and withbg == total - 1:
            got += 16
            notes.append('其余页图片背景 OK（%d页）' % withbg)
        elif withbg:
            got += 6
            notes.append('背景 %d 页' % withbg)
        else:
            notes.append('无图片背景')
        if withbg and 'alpha' in self.sxml(1):
            got += 8
            notes.append('透明度 OK')
        else:
            notes.append('无透明度')
        return (2, '背景', got, 24, notes)

    def r3(self):
        got, notes = 0, []
        x = self.sxml(1)
        if not x:
            return (3, '第2页', 0, 24, ['没有第2页'])
        verts = [v for v in re.findall(r'vert="([^"]*)"', x) if v != 'horz']
        if len(set(verts)) >= 2:
            got += 8
            notes.append('左右竖排方向 OK（%s）' % list(set(verts)))
        elif verts:
            got += 4
            notes.append('竖排=%s' % list(set(verts)))
        else:
            notes.append('无竖排')
        if '楷体' in x and 'sz="1700"' in x:
            got += 5
            notes.append('楷体17 OK')
        else:
            notes.append('字号/字体=%s' % sorted(set(re.findall(r'sz="(\d+)"', x)))[:3])
        if 'w="12700"' in x:
            got += 4
            notes.append('文本框1磅线条 OK')
        else:
            notes.append('线宽=%s' % re.findall(r'<a:ln w="(\d+)"', x)[:2])
        exts = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'<a:ext cx="(\d+)" cy="(\d+)"', x)]
        if any(abs(w - 25) < 2 and abs(h - 2.6) < 0.6 for w, h in exts):
            got += 7
            notes.append('双波形 25×2.6cm OK')
        elif exts:
            notes.append('尺寸=%s' % [(round(w, 1), round(h, 1)) for w, h in exts[:3]])
        return (3, '第2页', got, 24, notes)

    def r4(self):
        got, notes = 0, []
        x = self.sxml(2)
        if not x:
            return (4, '第3页', 0, 24, ['没有第3页'])
        if '传统习俗' in x:
            got += 6
            notes.append('艺术字内容 OK')
        else:
            notes.append('未找到艺术字')
        if 'prstGeom prst="ellipse"' in x or 'srcRect' in x:
            got += 4
            notes.append('椭圆裁剪 OK')
        if 'p:timing' in x and ('传统习俗' in x):
            got += 5
            notes.append('有动画 OK')
            if 'dur="1500"' in x:
                got += 2
                notes.append('持续1.5秒 OK')
        else:
            notes.append('无动画')
        if 'indent' in x or 'marL' in x:
            got += 4
            notes.append('首行缩进 OK')
        if 'spcBef' in x or 'spcAft' in x:
            got += 3
            notes.append('段前段后 OK')
        return (4, '第3页', got, 24, notes)

    def r5(self):
        got, notes = 0, []
        x2 = self.sxml(1)
        m2 = re.search(r'<p:transition([^>]*)>(.*?)</p:transition>', x2, re.S)
        if m2 and '<p:newsflash' in m2.group(2):
            got += 6
            notes.append('第2页新闻快报 OK')
            if 'dur="1000"' in m2.group(1):
                got += 2
                notes.append('速度1秒 OK')
        else:
            notes.append('第2页切换=%s' % (m2.group(2)[:50] if m2 else '无'))
        x3 = self.sxml(2)
        m3 = re.search(r'<p:transition([^>]*)>(.*?)</p:transition>', x3, re.S)
        if m3 and '<p:split' in m3.group(2):
            got += 5
            notes.append('第3页分割 OK')
            if 'dur="1250"' in m3.group(1):
                got += 3
                notes.append('速度1.25秒 OK')
        else:
            notes.append('第3页切换=%s' % (m3.group(2)[:50] if m3 else '无'))
        return (5, '切换效果', got, 8, notes)


    def r_show(self):
        ok, detail = check_show(self.deck, kind='kiosk', loop=1, st=1, en=2, anim=0)
        return (99, '放映设置', 8 if ok else 0, 8, [detail])


if __name__ == '__main__':
    sys.exit(run(PptGrader19, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'PPT 2010 操作题题库', '19', '1结果.pptx')))
