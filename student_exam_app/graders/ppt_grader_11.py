"""WPS 演示评分器 - 第11套（东岳泰山）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import PptDeck, Report, run

A = 'http://schemas.openxmlformats.org/drawingml/2006/main'


class PptGrader11:
    def __init__(self, path):
        self.deck = PptDeck(path)

    def grade(self):
        report = Report('WPS 演示 第11套 · 东岳泰山')
        for fn in (self.r1, self.r2, self.r3, self.r4, self.r5,
                   self.r6, self.r7, self.r8):
            report.add(*fn())
        return report

    def slide_xml(self, idx):
        if idx < len(self.deck.slides):
            s = self.deck.slides[idx]
            return s.xml if isinstance(s.xml, str) else self.deck.read(s.part)
        return ''

    def r1(self):
        notes, got = [], 0
        xml = self.deck.xml_all()
        kai = xml.count('楷体')
        if kai >= 20:
            got += 6
            notes.append('楷体统一 OK（%d处）' % kai)
        elif kai > 0:
            got += 3
            notes.append('部分楷体（%d处）' % kai)
        else:
            notes.append('未设楷体')
        ln = xml.count('val="200000"')
        if ln >= 4:
            got += 6.5
            notes.append('双倍行距 OK（%d处）' % ln)
        elif ln:
            got += 3
            notes.append('部分双倍行距（%d处）' % ln)
        else:
            notes.append('无双倍行距')
        return (1, '字体与段落', got, 12.5, notes)

    def r2(self):
        notes, got = [], 0
        s1 = self.slide_xml(0)
        if '东岳泰山' in s1:
            got += 4
            notes.append('标题"东岳泰山" OK')
        else:
            notes.append('第一张未见标题文字')
        if 'sz="8000"' in s1:
            got += 4
            notes.append('80号 OK')
        else:
            notes.append('字号非80')
        body = re.findall(r'<a:p>.*?</a:p>', s1, re.S)
        left_ok = any('东岳泰山' in seg and 'algn="l"' in seg for seg in body)
        if left_ok or '<a:pPr algn="l"' in s1:
            got += 2
            notes.append('左对齐 OK')
        else:
            notes.append('标题未左对齐')
        if 'outerShdw' in s1:
            got += 2.5
            notes.append('文字阴影 OK')
        else:
            notes.append('无阴影')
        return (2, '首页标题', got, 12.5, notes)

    def r3(self):
        notes, got = [], 0
        s2 = self.slide_xml(1)
        if '<p:timing>' not in s2:
            return (3, '第二页动画', 0, 12.5, ['第二页没有动画'])
        got += 4
        notes.append('有动画 OK')
        ids = re.findall(r'presetID="(\d+)"', s2)
        if 'presetClass="entr"' in s2:
            got += 4
            notes.append('进入类动画 OK（presetID=%s）' % ','.join(ids[:4]))
        elif ids:
            got += 2
            notes.append('有动画但非进入类（presetID=%s）' % ','.join(ids[:4]))
        else:
            notes.append('无动画效果')
        if 'dur="3500"' in s2:
            got += 4.5
            notes.append('持续3.5秒 OK')
        else:
            notes.append('时长=%s' % ','.join(set(re.findall(r'dur="(\d+)"', s2)))or '无')
        return (3, '第二页动画', got, 12.5, notes)

    def r4(self):
        notes, got = [], 0
        s3 = self.slide_xml(2)
        if 'prstGeom prst="rect"' not in s3:
            return (4, '第三页矩形', 0, 12.5, ['第三页没有矩形'])
        if '434343' in s3:
            got += 8
            notes.append('矩形+填充RGB(67,67,67) OK')
        else:
            notes.append('填充色=%s' % (re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', s3)[:3] or '无'))
        no_line = ('<a:ln><a:noFill/>' in s3.replace(' ', '')) or ('noFill' in s3 and '434343' in s3)
        if no_line:
            got += 4.5
            notes.append('无边框 OK')
        else:
            notes.append('边框未去除')
        return (4, '第三页矩形', got, 12.5, notes)

    def r5(self):
        notes, got = [], 0
        s3 = self.slide_xml(2)
        pics = re.findall(r'<p:pic>.*?</p:pic>', s3, re.S)
        if not pics:
            return (5, '第三页图片', 0, 12.5, ['第三页没有图片'])
        target = None
        for p in pics:
            ext = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"/>', p)
            if ext and abs(int(ext.group(2)) / 360000 - 12.6) < 0.4:
                target = p
                break
        if target is None:
            target = pics[-1]
        ext = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"/>', target)
        if ext and abs(int(ext.group(2)) / 360000 - 12.6) < 0.4:
            got += 4
            notes.append('高度12.6cm OK')
        else:
            h = int(ext.group(2)) / 360000 if ext else 0
            notes.append('高度%.1fcm' % h)
        off = re.search(r'<a:off x="(\d+)" y="(\d+)"/>', target)
        if off:
            x_cm = int(off.group(1)) / 360000
            y_cm = int(off.group(2)) / 360000
            if abs(x_cm - 23.5) < 0.6 and abs(y_cm - 3.5) < 0.6:
                got += 4
                notes.append('位置 OK')
            else:
                notes.append('位置%.1f/%.1fcm' % (x_cm, y_cm))
        else:
            notes.append('无位置')
        ln = re.search(r'<a:ln[^>]*w="(\d+)"', target)
        clr = re.search(r'<a:ln[^>]*>.*?<a:srgbClr val="([0-9A-Fa-f]{6})"', target, re.S)
        theme = re.search(r'<a:ln[^>]*>.*?<a:schemeClr val="([^"]+)"', target, re.S)
        if ln and (clr or theme):
            got += 4.5
            notes.append('3磅边框 OK（%s）' % (clr.group(1) if clr else theme.group(1)))
        else:
            notes.append('边框未设置')
        return (5, '第三页图片', got, 12.5, notes)

    def r6(self):
        notes, got = [], 0
        if len(self.deck.slides) < 4:
            return (6, '第四页', 0, 12.5, ['只有%d张幻灯片' % len(self.deck.slides)])
        got += 3
        notes.append('有第四张 OK')
        s4 = self.slide_xml(3)
        if '壮丽山川风光' in s4:
            got += 3
            notes.append('标题"壮丽山川风光" OK')
        else:
            notes.append('标题文字未找见')
        xml = self.deck.xml_all()
        if 'buChar' in s4 or 'buAutoNum' in s4:
            got += 3
            notes.append('项目符号 OK')
        else:
            notes.append('无项目符号')
        if 'dur="75"' in s4:
            got += 3.5
            notes.append('0.75秒逐字 OK')
        else:
            notes.append('动画时长未匹配')
        return (6, '第四页', got, 12.5, notes)

    def r7(self):
        notes, got = [], 0
        s2 = self.slide_xml(1)
        s3 = self.slide_xml(2)
        s4 = self.slide_xml(3)
        bg_hit = 0
        if 'schemeClr val="accent4"' in s2 or 'DCDCDC' in s2.upper() or 'BFBFBF' in s2.upper():
            bg_hit += 1
        if 'DEDEDE' in s3.upper() or 'DCDCDC' in s3.upper():
            bg_hit += 1
        if 'blipFill' in s4:
            bg_hit += 1
        if bg_hit >= 2:
            got += 4
            notes.append('背景填充 OK（%d/3）' % bg_hit)
        else:
            got += bg_hit
            notes.append('背景 %d/3' % bg_hit)
        trans = 0
        for s in (s2, s3, s4):
            if '<p:transition' in s:
                trans += 1
        if trans >= 3:
            got += 4
            notes.append('三张都有切换 OK')
        else:
            notes.append('切换 %d/3' % trans)
        adv = sum(1 for s in (s2, s3, s4) if 'advTm="3000"' in s)
        if adv >= 3:
            got += 4.5
            notes.append('自动换片3秒 OK')
        elif adv:
            got += 2
            notes.append('自动换片 %d/3' % adv)
        else:
            notes.append('未设自动换片')
        return (7, '背景与切换', got, 12.5, notes)

    def r8(self):
        notes, got = [], 0
        try:
            pres = self.deck.read('ppt/presProps.xml')
        except Exception:
            return (8, '放映设置', 0, 12.5, ['无 presProps'])
        m = re.search(r'<p:showPr.*?</p:showPr>', pres, re.S)
        block = m.group(0) if m else ''
        if '<p:present/>' in block:
            got += 4
            notes.append('演讲者放映 OK')
        else:
            notes.append('放映类型=%s' % ('展台' if 'kiosk' in block else '未设'))
        rng = re.search(r'<p:sldRg st="(\d+)" end="(\d+)"', block)
        if rng and rng.group(1) == '1' and rng.group(2) == str(len(self.deck.slides)):
            got += 4
            notes.append('放映范围 1-%s OK' % rng.group(2))
        else:
            notes.append('范围=%s' % (rng.group(0) if rng else '全部'))
        if 'loop="1"' in block and '<p:present/>' in block:
            got += 4.5
            notes.append('循环放映 OK')
        else:
            notes.append('循环放映未设置')
        return (8, '放映设置', got, 12.5, notes)


if __name__ == '__main__':
    sys.exit(run(PptGrader11, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'PPT 2010 操作题题库', '11', '1结果.pptx')))
