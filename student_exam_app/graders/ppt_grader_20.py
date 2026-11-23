"""WPS 演示评分器 - 第20套（父亲节）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import PptDeck, Report, run, check_show


class PptGrader20:
    def __init__(self, path):
        self.deck = PptDeck(path)

    def grade(self):
        report = Report('WPS 演示 第20套 · 父亲节')
        for fn in (self.r1, self.r2, self.r3, self.r4, self.r5, self.r_show):
            report.add(*fn())
        return report

    def sxml(self, idx):
        slides = self.deck.slides
        return self.deck.read(slides[idx].part) if idx < len(slides) else ''

    def r1(self):
        got, notes = 0, []
        total = len(self.deck.slides)
        kai = 0
        yahei = 0
        for i in range(total):
            x = self.sxml(i)
            if '楷体' in x:
                kai += 1
            if '微软雅黑' in x:
                yahei += 1
        if kai >= total and yahei == 0:
            got += 10
            notes.append('全部改为楷体 OK')
        elif kai:
            got += 5
            notes.append('楷体 %d 页（雅黑 %d 页）' % (kai, yahei))
        else:
            notes.append('未改楷体')
        withbg = 0
        for i in range(total):
            bg = re.search(r'<p:bg>.*?</p:bg>', self.sxml(i), re.S)
            if bg and 'blipFill' in bg.group(0):
                withbg += 1
        if total and withbg == total:
            got += 12
            notes.append('全部页背景图片 OK（%d页）' % withbg)
        elif withbg:
            got += 6
            notes.append('背景 %d/%d 页' % (withbg, total))
        else:
            notes.append('无背景图片')
        return (1, '字体与背景', got, 22, notes)

    def r2(self):
        got, notes = 0, []
        x = self.sxml(0)
        if not x:
            return (2, '标题与图片', 0, 18, ['没有幻灯片'])
        if 'sz="9600"' in x:
            got += 7
            notes.append('96号 OK')
        else:
            notes.append('字号=%s' % sorted(set(re.findall(r'sz="(\d+)"', x)))[:3])
        if re.search(r':b[\s/>]', x) or 'b="1"' in x:
            got += 3
            notes.append('加粗 OK')
        if 'spc="3600"' in x or 'spc="36' in x:
            got += 3
            notes.append('字符间距36磅 OK')
        else:
            notes.append('间距=%s' % re.findall(r'spc="(\d+)"', x)[:2])
        if '<p:pic>' in x:
            got += 5
            notes.append('图片 OK')
        return (2, '标题与图片', got, 18, notes)

    def r3(self):
        got, notes = 0, []
        x = self.sxml(0)
        n = x.count('prst="ellipse"')
        if n >= 1:
            got += 4
            notes.append('椭圆 OK')
        else:
            notes.append('无椭圆')
        exts = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'<a:ext cx="(\d+)" cy="(\d+)"', x)]
        if any(abs(w - 11) < 0.8 and abs(h - 7.1) < 0.8 for w, h in exts):
            got += 5
            notes.append('11×7.1cm OK')
        elif exts:
            notes.append('尺寸=%s' % [(round(w, 1), round(h, 1)) for w, h in exts[:4]])
        xs = [int(v) / 360000 for v in re.findall(r'<a:off x="(-?\d+)"', x)]
        if any(abs(px - 25.5) < 1.5 for px in xs):
            got += 4
            notes.append('水平25.5cm OK')
        else:
            notes.append('x坐标=%s' % [round(v, 1) for v in xs[:5]])
        if 'FEDC91' in x.upper():
            got += 3
            notes.append('填充 RGB(254,220,145) OK')
        if 'softEdge' in x:
            got += 2
            notes.append('柔化边缘 OK')
        return (3, '椭圆', got, 18, notes)

    def r4(self):
        got, notes = 0, []
        x = self.sxml(1)
        if not x:
            return (4, '第2页', 0, 22, ['没有第2页'])
        n = x.count('prst="ellipse"')
        if n >= 3:
            got += 5
            notes.append('三个椭圆 OK')
        elif n:
            got += 2
            notes.append('椭圆 %d 个' % n)
        exts = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'<a:ext cx="(\d+)" cy="(\d+)"', x)]
        if sum(1 for w, h in exts if abs(w - 1.93) < 0.4 and abs(h - 1.93) < 0.4) >= 3:
            got += 4
            notes.append('1.93×1.93cm OK')
        if 'buChar' in x and ('l" ' in x or '●' in x or 'u25CF' in x or 'char="l"' in x):
            got += 4
            notes.append('圆形项目符号 OK')
        elif 'buChar' in x:
            got += 2
            notes.append('项目符号=%s' % re.findall(r'buChar char="([^"]*)"', x)[:2])
        else:
            notes.append('无项目符号')
        if 'sz="1600"' in x:
            got += 3
            notes.append('16号 OK')
        if 'spcPct val="200000"' in x:
            got += 3
            notes.append('双倍行距 OK')
        if 'accent6' in x or 'C00000' in x.upper():
            got += 3
            notes.append('猩红着色6 OK')
        else:
            notes.append('颜色=%s' % (re.findall(r'schemeClr val="([^"]+)"', x)[:3]))
        return (4, '第2页', got, 22, notes)

    def r5(self):
        got, notes = 0, []
        total = len(self.deck.slides)
        fade = 0
        for i in range(total):
            m = re.search(r'<p:transition([^>]*)>(.*?)</p:transition>', self.sxml(i), re.S)
            if m and '<p:fade' in m.group(2):
                fade += 1
        if total and fade == total:
            got += 6
            notes.append('全部淡出 OK（%d页）' % fade)
        elif fade:
            got += 3
            notes.append('淡出 %d/%d 页' % (fade, total))
        else:
            notes.append('未找到淡出')
        x0 = self.sxml(0)
        if 'dur="1000"' in x0:
            got += 2
            notes.append('速度1秒 OK')
        if 'advTm="4000"' in x0:
            got += 2
            notes.append('自动换片4秒 OK')
        else:
            notes.append('advTm=%s' % re.findall(r'advTm="(\d+)"', x0)[:1])
        foot = False
        for n in self.deck.names:
            if ('slideMaster' in n or 'handoutMaster' in n or 'notesMaster' in n) and n.endswith('.xml'):
                c = self.deck.read(n)
                if '2025-6-15' in c:
                    foot = True
        if foot:
            got += 2
            notes.append('固定日期 OK')
        else:
            notes.append('未设固定日期')
        return (5, '切换与页脚', got, 12, notes)

    def r_show(self):
        ok, detail = check_show(self.deck, kind='present', st=1, en=2, manual=True)
        return (6, '放映设置', 8 if ok else 0, 8, [detail])


if __name__ == '__main__':
    sys.exit(run(PptGrader20, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'PPT 2010 操作题题库', '20', '1结果.pptx')))
