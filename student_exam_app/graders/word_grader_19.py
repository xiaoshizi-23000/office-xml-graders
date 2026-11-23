"""WPS 文档评分器 - 第19套（长城秋雨夕）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import WordDoc, Report, run

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


class WordGrader19:
    def __init__(self, path):
        self.doc = WordDoc(path)

    def grade(self):
        report = Report('WPS 文档 第19套 · 长城秋雨夕')
        for fn in (self.r1, self.r2, self.r3, self.r4,
                   self.r5, self.r6, self.r7, self.r8):
            report.add(*fn())
        return report

    def paras(self):
        return list(self.doc.body.iter(W + 'p')) if self.doc.body is not None else []

    def ptext(self, p):
        return ''.join(t.text or '' for t in p.iter(W + 't')).strip()

    def pxml(self, p):
        return __import__('xml.etree.ElementTree', fromlist=['x']).tostring(p, encoding='unicode')

    def r1(self):
        got, notes = 0, []
        secs = self.doc.sections
        ps = self.doc.page_setup(secs[0]) if secs else self.doc.page_setup()
        w, h = int(ps.get('w') or 0), int(ps.get('h') or 0)
        if abs(w - 11906) <= 30 and abs(h - 16838) <= 30:
            got += 3
            notes.append('A4 OK')
        else:
            notes.append('纸张=%dx%d' % (w, h))
        v = {k: int(ps.get(k) or 0) / 567 for k in ('top', 'bottom', 'left', 'right')}
        if all(abs(v[k] - 1.27) < 0.1 for k in v):
            got += 4
            notes.append('窄边距1.27cm OK')
        else:
            notes.append('边距%.2f/%.2f/%.2f/%.2f' % (v['top'], v['bottom'], v['left'], v['right']))
        grid = ''
        for m in re.finditer(r'<w:docGrid[^/]*/>', self.doc.xml_all()):
            grid = m.group(0)
            break
        pitch = int(ps.get('linePitch') or 0)
        avail = int(ps.get('h') or 0) - int(ps.get('top') or 0) - int(ps.get('bottom') or 0)
        lines = round(avail / pitch) if pitch else 0
        if 'linesAndChars' in grid and abs(lines - 48) <= 2:
            got += 3
            notes.append('48行48字符网格 OK（算得%d行）' % lines)
        else:
            notes.append('网格=%s 行数=%d' % (grid[:36] or '无', lines))
        return (1, '纸张与网格', got, 10, notes)

    def r2(self):
        got, notes = 0, []
        ps = self.paras()
        if not ps:
            return (2, '标题格式', 0, 14, ['无正文'])
        p0 = ps[0]
        rp = self.doc.run_props(list(p0.iter(W + 'r'))[0], p0)
        font = rp.get('eastAsia') or rp.get('font') or ''
        if font == '微软雅黑':
            got += 3
            notes.append('微软雅黑 OK')
        else:
            notes.append('字体=%s' % font)
        if str(rp.get('size') or '') == '48':
            got += 3
            notes.append('小一号(24pt) OK')
        else:
            notes.append('字号=%s' % rp.get('size'))
        if str(rp.get('color') or '').upper().endswith('00B0F0'):
            got += 2
            notes.append('浅蓝色 OK')
        else:
            notes.append('颜色=%s' % rp.get('color'))
        seg = self.pxml(p0)
        if re.search(r':b[\s/>]', seg):
            got += 1
            notes.append('加粗 OK')
        if 'outlineLvl' in seg:
            got += 1
            notes.append('大纲1级 OK')
        if 'before="340"' in seg and 'after="330"' in seg:
            got += 2
            notes.append('段前17磅段后16.5磅 OK')
        else:
            notes.append('段前后=%s' % re.findall(r'(?:before|after)="(\d+)"', seg)[:2])
        if re.search(r'line="576"[^/]*lineRule="auto"', seg):
            got += 2
            notes.append('2.4倍行距 OK')
        else:
            notes.append('行距=%s' % re.findall(r'line="(\d+)"', seg)[:1])
        return (2, '标题格式', got, 14, notes)

    def r3(self):
        got, notes = 0, []
        targets = []
        for p in self.paras():
            t = self.ptext(p)
            if t.startswith('雨中登长城') or t.startswith('雨是今天'):
                targets.append(p)
        if not targets:
            return (3, '正文两段格式', 0, 16, ['找不到第一二段'])
        p = targets[0]
        seg = self.pxml(p)
        runs = list(p.iter(W + 'r'))
        size = ''
        bold = False
        for r in runs:
            rpr = r.find(W + 'rPr')
            if rpr is None:
                continue
            szv = rpr.find(W + 'sz')
            if szv is not None and not size:
                size = szv.get(W + 'val') or ''
            if rpr.find(W + 'b') is not None:
                bold = True
        if size == '28':
            got += 4
            notes.append('四号 OK')
        else:
            notes.append('字号=%s' % size)
        rp = self.doc.run_props(runs[0], p) if runs else {}
        if str(rp.get('color') or '').upper().endswith('FF0000'):
            got += 3
            notes.append('红色 OK')
        else:
            notes.append('颜色=%s' % rp.get('color'))
        if bold:
            got += 2
            notes.append('加粗 OK')
        if 'val="distribute"' in seg:
            got += 2
            notes.append('分散对齐 OK')
        if 'reflection' in seg:
            got += 2
            notes.append('倒影 OK')
        else:
            notes.append('无倒影')
        bd = re.search(r'pBdr.*?</[a-z0-9]+:pBdr>', seg, re.S)
        if bd and 'dotted' in bd.group(0) and '00B0F0' in bd.group(0).upper():
            got += 3
            notes.append('点线浅蓝边框 OK')
        elif bd:
            got += 1
            notes.append('有边框但线型/颜色不符')
        else:
            notes.append('无段落边框')
        return (3, '正文两段格式', got, 16, notes)

    def r4(self):
        got, notes = 0, []
        cols = re.findall(r'<w:cols([^/]*)/>', self.doc.xml_all())
        two = [c for c in cols if 'num="2"' in c]
        if not two:
            return (4, '分栏', 0, 10, ['没有2栏设置'])
        got += 5
        notes.append('2栏 OK')
        c = two[0]
        if 'sep="1"' in c:
            got += 2
            notes.append('分割线 OK')
        else:
            notes.append('无分割线')
        if 'space="315"' in c or 'equalWidth' in c:
            got += 3
            notes.append('间距1.5字符 OK')
        else:
            notes.append('间距=%s' % re.findall(r'space="(\d+)"', c)[:1])
        return (4, '分栏', got, 10, notes)

    def r5(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        if '<wp:anchor' not in full:
            return (5, '图片', 0, 16, ['没有浮动图片'])
        got += 3
        notes.append('浮动图片 OK')
        if 'wrapSquare' in full:
            got += 3
            notes.append('四周型环绕 OK')
        if 'flipH="1"' in full or 'flipH="true"' in full:
            got += 3
            notes.append('水平翻转 OK')
        else:
            notes.append('未水平翻转')
        exts = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'ext cx="(\d+)" cy="(\d+)"', full)]
        if any(abs(w - 12) < 0.6 and abs(h - 8) < 0.6 for w, h in exts):
            got += 4
            notes.append('12×8cm OK')
        elif exts:
            notes.append('尺寸=%s' % [(round(w, 1), round(h, 1)) for w, h in exts[:2]])
        if re.search(r'<a:softEdge[^>]*rad="\d+"', full):
            got += 2
            notes.append('柔化边缘 OK')
        if re.search(r'<wp:positionH[^>]*relativeFrom="page"', full):
            got += 1
            notes.append('相对页面位置 OK')
        return (5, '图片', got, 16, notes)

    def r6(self):
        got, notes = 0, []
        hx = ''
        for n in self.doc.names:
            if 'header' in n and n.endswith('.xml'):
                c = self.doc.read(n)
                if '长城' in c and 'textpath' in c:
                    hx = c
                    break
        if not hx:
            return (6, '文字水印', 0, 8, ['没有水印'])
        got += 4
        notes.append('水印文字 OK')
        if '楷体' in hx and '66pt' in hx:
            got += 2
            notes.append('楷体66 OK')
        else:
            notes.append('字体字号未匹配')
        if 'FF0000' in hx.upper():
            got += 2
            notes.append('红色 OK')
        else:
            notes.append('颜色未匹配')
        return (6, '文字水印', got, 8, notes)

    def r7(self):
        got, notes = 0, []
        names = re.findall(r'<w:bookmarkStart[^>]*w:name="([^"]*)"', self.doc.xml_all())
        if '标题' in names:
            got += 6
            notes.append('书签"标题" OK')
        else:
            notes.append('书签=%s' % names[:3])
        return (7, '书签', got, 6, notes)

    def r8(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        if 'type="pattern"' in full and '上对角虚线' in full:
            got += 7
            notes.append('上对角虚线图案 OK')
        elif 'type="pattern"' in full:
            got += 3
            notes.append('有图案背景')
        else:
            notes.append('无图案背景')
        bg = re.search(r'<w:background[^>]*>', full)
        if bg and ('F3DC96' in bg.group(0).upper() or 'F3DC96' in full.upper()):
            got += 4
            notes.append('前景RGB(243,220,150) OK')
        else:
            notes.append('前景色未匹配')
        even = False
        right_red = False
        for n in self.doc.names:
            if 'header' in n and n.endswith('.xml'):
                c = self.doc.read(n)
                if '万里长城' in c:
                    even = True
                    if 'val="right"' in c and 'FF0000' in c.upper():
                        right_red = True
        if even:
            got += 3
            notes.append('偶数页眉 OK')
        else:
            notes.append('页眉未设')
        if right_red:
            got += 2
            notes.append('右对齐红色 OK')
        foot = ''.join(self.doc.footer_texts())
        if '共' in foot:
            got += 4
            notes.append('页脚"第一页共X页" OK')
        else:
            notes.append('页脚=%r' % foot[:20])
        return (8, '背景与页眉页脚', got, 20, notes)


if __name__ == '__main__':
    sys.exit(run(WordGrader19, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Word 2010 操作题题库', '19', '1结果.docx')))
