"""WPS 演示评分器 - 第13套（科技启航未来）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import PptDeck, Report, run, check_show


class PptGrader13:
    def __init__(self, path):
        self.deck = PptDeck(path)

    def grade(self):
        report = Report('WPS 演示 第13套 · 科技启航未来')
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
            return (1, '标题格式', 0, 20, ['没有幻灯片'])
        if 'sz="11000"' in x:
            got += 8
            notes.append('110号 OK')
        else:
            notes.append('字号=%s' % re.findall(r'sz="(\d+)"', x)[:3])
        if '宋体' in x or 'SimSun' in x:
            got += 3
            notes.append('宋体 OK')
        else:
            notes.append('字体未匹配')
        if 'blipFill' in x and x.count('blipFill') >= 2 and 'sz="11000"' in x:
            got += 4
            notes.append('文本图片填充 OK')
        elif 'blipFill' in x:
            notes.append('有图片填充但字号不符')
        else:
            notes.append('无图片填充')
        if 'glow' in x:
            got += 3
            notes.append('发光 OK')
        else:
            notes.append('无发光')
        if 'algn="l"' in x:
            got += 2
            notes.append('左对齐 OK')
        if 'Technology sets sail' in x:
            got += 2
            notes.append('副标题英文 OK')
        return (1, '标题格式', got, 20, notes)

    def r2(self):
        got, notes = 0, []
        total = len(self.deck.slides)
        withbg = 0
        for i in range(1, total):
            x = self.sxml(i)
            if '<p:bg>' in x and 'blipFill' in x:
                withbg += 1
        if total > 1 and withbg == total - 1:
            got += 12
            notes.append('除标题页外背景图片 OK（%d页）' % withbg)
        elif withbg:
            got += 6
            notes.append('背景图片 %d/%d 页' % (withbg, total - 1))
        else:
            notes.append('无背景图片')
        return (2, '背景图片', got, 12, notes)

    def r3(self):
        got, notes = 0, []
        x = self.sxml(1)
        if not x:
            return (3, '图片与正文', 0, 20, ['没有第2页'])
        exts = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'<a:ext cx="(\d+)" cy="(\d+)"', x)]
        if any(abs(w - 15.5) < 1.0 and abs(h - 14) < 1.0 for w, h in exts):
            got += 6
            notes.append('15.5×14cm OK')
        elif exts:
            notes.append('尺寸=%s' % [(round(w, 1), round(h, 1)) for w, h in exts[:3]])
        if 'rotRev' in x or 'camera' in x:
            got += 4
            notes.append('三维旋转 OK')
        else:
            notes.append('无三维旋转')
        pos = re.search(r'<a:off x="(\d+)" y="(\d+)"', x)
        if pos:
            px, py = int(pos.group(1)) / 360000, int(pos.group(2)) / 360000
            if abs(px - 2) < 1.0 and abs(py - 3.8) < 1.0:
                got += 4
                notes.append('位置 2/3.8cm OK')
            else:
                notes.append('位置 %.1f/%.1f' % (px, py))
        if '仿宋' in x:
            got += 3
            notes.append('正文仿宋 OK')
        if 'sz="2500"' in x:
            got += 3
            notes.append('25号 OK')
        else:
            notes.append('正文号=%s' % re.findall(r'sz="(\d+)"', x)[:4])
        return (3, '图片与正文', got, 20, notes)

    def r4(self):
        got, notes = 0, []
        if len(self.deck.slides) < 3:
            return (4, '艺术字', 0, 16, ['没有第3页'])
        x = self.sxml(2)
        if '科技' in x and '引领未来' in x:
            got += 6
            notes.append('艺术字内容 OK（科技/引领未来）')
        else:
            notes.append('未找到艺术字')
        if 'gradFill' in x:
            got += 4
            notes.append('渐变填充 OK')
        else:
            notes.append('非渐变填充')
        if 'vert="vert"' in x or 'vert="eaVert"' in x or 'vert="mongolianVert"' in x:
            got += 4
            notes.append('竖排 OK')
        else:
            notes.append('文字方向未竖排')
        exts = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'<a:ext cx="(\d+)" cy="(\d+)"', x)]
        if any(abs(w - 33.8) < 1.5 and abs(h - 19) < 1.5 for w, h in exts):
            got += 2
            notes.append('33.8×19cm OK')
        return (4, '艺术字', got, 16, notes)

    def r5(self):
        got, notes = 0, []
        x = self.sxml(2)
        if not x:
            return (5, '形状与折线图', 0, 18, ['没有第3页'])
        exts = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'<a:ext cx="(\d+)" cy="(\d+)"', x)]
        if any(abs(w - 22.6) < 1.5 and abs(h - 11) < 1.0 for w, h in exts):
            got += 5
            notes.append('双括号 22.6×11cm OK')
        elif exts:
            notes.append('尺寸=%s' % [(round(w, 1), round(h, 1)) for w, h in exts[:3]])
        if re.search(r'<a:ln w="38100"', x):
            got += 3
            notes.append('3磅轮廓 OK')
        else:
            notes.append('轮廓=%s' % re.findall(r'<a:ln w="(\d+)"', x)[:2])
        charts = [n for n in self.deck.names if re.match(r'ppt/charts/chart\d+\.xml$', n)]
        cx = self.deck.read(charts[0]) if charts else ''
        if 'lineChart' in cx:
            got += 5
            notes.append('折线图 OK')
        else:
            notes.append('图表类型=%s' % ([k for k in ('barChart', 'pieChart') if k in cx] or '无'))
        if 'layout' in cx.lower() or 'dLbls' in cx:
            got += 2
            notes.append('快速布局 OK')
        anims = self.slide(2).animations() if self.slide(2) else []
        if anims:
            got += 3
            notes.append('动画 OK（%d处）' % len(anims))
            if 'dur="1300"' in x:
                notes.append('持续1.3秒 OK')
        else:
            notes.append('无动画')
        return (5, '形状与折线图', got, 18, notes)

    def r6(self):
        got, notes = 0, []
        total = len(self.deck.slides)
        kinds = []
        durs = []
        for i in range(total):
            x = self.sxml(i)
            m = re.search(r'<p:transition([^>]*)>(.*?)</p:transition>', x, re.S)
            if m:
                tag = re.findall(r'<p:([a-zA-Z]+)', m.group(2))
                kinds.append(tag[0] if tag else '')
                d = re.search(r'dur="(\d+)"', m.group(1))
                durs.append(d.group(1) if d else '')
            else:
                kinds.append('')
                durs.append('')
        if any(k in ('randomBar', 'wipe', 'shape', 'cover') for k in kinds):
            got += 6
            notes.append('切换效果 OK（%s）' % kinds[:3])
        else:
            notes.append('切换=%s' % kinds[:3])
        if any(d in ('1500', '8000', '800') for d in durs):
            got += 4
            notes.append('速度已设（%s）' % durs[:3])
        else:
            notes.append('时长=%s' % durs[:3])
        if 'sndAc' in self.sxml(0) or 'audio' in self.sxml(0):
            got += 4
            notes.append('切换声音 OK')
        else:
            notes.append('无切换声音')
        return (6, '切换效果', got, 6, notes)


    def r_show(self):
        ok, detail = check_show(self.deck, kind='present', loop=1, manual=True)
        return (99, '放映设置', 8 if ok else 0, 8, [detail])


if __name__ == '__main__':
    sys.exit(run(PptGrader13, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'PPT 2010 操作题题库', '13', '1结果.pptx')))
