"""WPS 演示评分器 - 第17套（芒种）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import PptDeck, Report, run, check_show


class PptGrader17:
    def __init__(self, path):
        self.deck = PptDeck(path)

    def grade(self):
        report = Report('WPS 演示 第17套 · 芒种')
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
            return (1, '标题与副标题', 0, 16, ['没有幻灯片'])
        if 'sz="12000"' in x:
            got += 6
            notes.append('主标题120号 OK')
        else:
            notes.append('字号=%s' % sorted(set(re.findall(r'sz="(\d+)"', x)))[:3])
        if '等线' in x:
            got += 4
            notes.append('等线 OK')
        if 'sz="1800"' in x:
            got += 3
            notes.append('副标题18号 OK')
        if '仿宋' in x:
            got += 3
            notes.append('副标题仿宋 OK')
        return (1, '标题与副标题', got, 16, notes)

    def r2(self):
        got, notes = 0, []
        x = self.sxml(0)
        bg = re.search(r'<p:bg>.*?</p:bg>', x, re.S)
        if bg and 'blipFill' in bg.group(0):
            got += 12
            notes.append('首页图片背景 OK')
        else:
            notes.append('首页无图片背景')
        return (2, '背景', got, 12, notes)

    def r3(self):
        got, notes = 0, []
        x = self.sxml(1)
        if not x:
            return (3, '第2页正文', 0, 22, ['没有第2页'])
        if '楷体' in x and 'sz="2400"' in x:
            got += 8
            notes.append('楷体24 OK')
        else:
            notes.append('字体/字号=%s' % (sorted(set(re.findall(r'sz="(\d+)"', x)))[:3]))
        if 'indent' in x or 'marL' in x:
            got += 4
            notes.append('首行缩进 OK')
        if 'spcPct val="150000"' in x:
            got += 5
            notes.append('1.5倍行距 OK')
        else:
            notes.append('行距未匹配')
        if 'reflection' in x:
            got += 5
            notes.append('倒影 OK')
        else:
            notes.append('无倒影')
        return (3, '第2页正文', got, 22, notes)

    def r4(self):
        got, notes = 0, []
        x = self.sxml(2)
        if not x:
            return (4, '第3页图片', 0, 26, ['没有第3页'])
        has_pic = '<p:pic>' in x
        if has_pic:
            got += 6
            notes.append('图片 OK')
        exts = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'<a:ext cx="(\d+)" cy="(\d+)"', x)]
        if has_pic and any(abs(h - 13.6) < 0.8 for w, h in exts):
            got += 6
            notes.append('高13.6cm OK')
        elif exts:
            notes.append('尺寸=%s' % [(round(w, 1), round(h, 1)) for w, h in exts[:3]])
        offs = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'<a:off x="(\d+)" y="(\d+)"', x)]
        if any(abs(px - 2.3) < 0.8 and abs(py - 3.8) < 0.8 for px, py in offs):
            got += 5
            notes.append('位置 2.3/3.8cm OK')
        else:
            notes.append('位置=%s' % [(round(p, 1), round(q, 1)) for p, q in offs[:3]])
        if 'hlinkClick' in x:
            got += 5
            notes.append('超链接 OK')
        else:
            notes.append('无超链接')
        if '宋体' in x and 'sz="2000"' in x:
            got += 4
            notes.append('正文宋体20 OK')
        else:
            notes.append('正文格式=%s' % (sorted(set(re.findall(r'sz="(\d+)"', x)))[:3]))
        return (4, '第3页图片', got, 26, notes)

    def r5(self):
        got, notes = 0, []
        x = self.sxml(0)
        m = re.search(r'<p:transition([^>]*)>(.*?)</p:transition>', x, re.S)
        if m and '<p:dissolve' in m.group(2):
            got += 8
            notes.append('溶解切换 OK')
        else:
            notes.append('切换=%s' % (m.group(2)[:50] if m else '无'))
        if m and ('p14:dur="2500"' in m.group(1) or 'dur="2500"' in m.group(1)):
            got += 5
            notes.append('速度2.5秒 OK')
        if m and 'wav' in m.group(2):
            got += 4
            notes.append('声音 OK')
        else:
            notes.append('无声音')
        if m and 'advTm="5000"' in m.group(1):
            got += 4
            notes.append('5秒自动换片 OK')
        else:
            notes.append('advTm=%s' % (re.findall(r'advTm="(\d+)"', m.group(1))[:1] if m else '无'))
        foot = False
        for n in self.deck.names:
            if 'slideMaster' in n and n.endswith('.xml'):
                c = self.deck.read(n)
                if '二十四节气' in c or '2025-6-5' in c:
                    foot = True
        pr = self.deck.read('ppt/presentation.xml')
        if foot or 'hf' in pr:
            got += 3
            notes.append('日期/页脚 OK')
        else:
            notes.append('未设页脚')
        return (5, '切换与页脚', got, 16, notes)


    def r_show(self):
        ok, detail = check_show(self.deck, kind='present', loop=1)
        return (99, '放映设置', 8 if ok else 0, 8, [detail])


if __name__ == '__main__':
    sys.exit(run(PptGrader17, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'PPT 2010 操作题题库', '17', '1结果.pptx')))
