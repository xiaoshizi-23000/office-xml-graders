"""WPS 文档评分器 - 第13套（瓦块鱼）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import WordDoc, Report, run

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


class WordGrader13:
    def __init__(self, path):
        self.doc = WordDoc(path)

    def grade(self):
        report = Report('WPS 文档 第13套 · 瓦块鱼')
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
        ps = self.doc.page_setup()
        if abs(int(ps.get('w') or 0) - 14740) <= 30 and abs(int(ps.get('h') or 0) - 20409) <= 40:
            got += 6
            notes.append('26×36cm 纸张 OK')
        else:
            notes.append('纸张=%sx%s twips' % (ps.get('w'), ps.get('h')))
        grid = ''
        for m in re.finditer(r'<w:docGrid[^/]*/>', self.doc.xml_all()):
            grid = m.group(0)
            break
        if 'linesAndChars' in grid:
            got += 4
            notes.append('行和字符网格 OK')
        else:
            notes.append('网格=%s' % (grid[:44] or '无'))
        pitch = int(ps.get('linePitch') or 0)
        avail = int(ps.get('h') or 0) - int(ps.get('top') or 0) - int(ps.get('bottom') or 0)
        lines = round(avail / pitch) if pitch else 0
        if abs(lines - 60) <= 2:
            got += 2
            notes.append('每页约60行 OK（算得%d）' % lines)
        else:
            notes.append('每页约%d行' % lines)
        return (1, '纸张与网格', got, 12, notes)

    def r2(self):
        got, notes = 0, []
        ps = self.paras()
        if not ps:
            return (2, '标题格式', 0, 14, ['无正文'])
        p0 = ps[0]
        runs = list(p0.iter(W + 'r'))
        rp = self.doc.run_props(runs[0], p0) if runs else {}
        font = rp.get('eastAsia') or rp.get('font') or ''
        if font == '黑体':
            got += 3
            notes.append('黑体 OK')
        else:
            notes.append('字体=%s' % font)
        if str(rp.get('size') or '') == '72':
            got += 3
            notes.append('小初(36pt) OK')
        else:
            notes.append('字号=%s' % rp.get('size'))
        if str(rp.get('color') or '').upper().endswith('00B0F0'):
            got += 3
            notes.append('浅蓝色 OK')
        else:
            notes.append('颜色=%s' % rp.get('color'))
        seg = self.pxml(p0)
        has_b = bool(re.search(r'<[a-z0-9]+:b[\s/>]', seg))
        has_i = bool(re.search(r'<[a-z0-9]+:i[\s/>]', seg))
        if has_b and has_i:
            got += 2
            notes.append('加粗倾斜 OK')
        else:
            notes.append('加粗=%s 倾斜=%s' % (has_b, has_i))
        if 'val="right"' in seg:
            got += 3
            notes.append('右对齐 OK')
        else:
            notes.append('未右对齐')
        return (2, '标题格式', got, 14, notes)

    def r3(self):
        got, notes = 0, []
        poem = None
        for p in self.paras():
            if self.ptext(p).startswith('忆京都'):
                poem = p
                break
        if poem is None:
            return (3, '诗句格式', 0, 18, ['找不到诗句段'])
        runs = list(poem.iter(W + 'r'))
        rp = self.doc.run_props(runs[0], poem) if runs else {}
        font = rp.get('eastAsia') or rp.get('font') or ''
        if font == '仿宋' and str(rp.get('size') or '') == '32':
            got += 3
            notes.append('仿宋三号 OK')
        else:
            notes.append('字体=%s/%s' % (font, rp.get('size')))
        if str(rp.get('color') or '').upper() in ('FFFFFF', 'FFFFFFFF'):
            got += 2
            notes.append('白色 OK')
        else:
            notes.append('颜色=%s' % rp.get('color'))
        seg = self.pxml(poem)
        if 'val="center"' in seg:
            got += 2
            notes.append('居中 OK')
        else:
            notes.append('未居中')
        sp = re.findall(r'spacing[^>]*val="(\d+)"', seg)
        if sp and abs(int(sp[0]) - 57) <= 4:
            got += 2
            notes.append('字符间距0.1cm OK')
        else:
            notes.append('间距=%s' % (sp[:1] or '无'))
        if 'glow' in self.doc.xml_all():
            got += 3
            notes.append('发光 OK')
        else:
            notes.append('无发光')
        m = re.search(r'pBdr.*?</[a-z0-9]+:pBdr>', seg, re.S)
        if m and 'wave' in m.group(0) and 'FF0000' in m.group(0).upper() and 'sz="12"' in m.group(0):
            got += 4
            notes.append('红单波浪1.5磅边框 OK')
        elif m and 'wave' in m.group(0):
            got += 2
            notes.append('波形边框但颜色/宽度不符')
        else:
            notes.append('无段落边框')
        s = re.search(r'shd[^/]*/>', seg)
        if s and ('accent5' in s.group(0) or 'D4F4F1' in s.group(0).upper()):
            got += 2
            notes.append('底纹 OK')
        else:
            notes.append('底纹未匹配')
        return (3, '诗句格式', got, 18, notes)

    def r4(self):
        got, notes = 0, []
        target = None
        for p in self.paras():
            if self.ptext(p).startswith('严辰'):
                target = p
                break
        if target is None:
            return (4, '正文格式', 0, 14, ['找不到正文段'])
        pr = self.doc.para_props(target)
        runs = list(target.iter(W + 'r'))
        rp = self.doc.run_props(runs[0], target) if runs else {}
        size = ''
        for r in runs:
            rpr = r.find(W + 'rPr')
            if rpr is None:
                continue
            szv = rpr.find(W + 'sz')
            if szv is not None:
                size = szv.get(W + 'val') or ''
                if size:
                    break
        if size == '28':
            got += 6
            notes.append('正文四号(14pt) OK')
        else:
            notes.append('正文字号=%s' % (size or rp.get('size')))
        if str(pr.get('firstLineChars') or '') == '200':
            got += 3
            notes.append('首行缩进2字符 OK')
        if str(pr.get('afterLines') or '') == '50':
            got += 2
            notes.append('段后0.5行 OK')
        if str(pr.get('line') or '') == '360' and pr.get('lineRule') == 'exact':
            got += 3
            notes.append('行距固定18磅 OK')
        else:
            notes.append('行距=%s/%s' % (pr.get('line'), pr.get('lineRule')))
        return (4, '正文格式', got, 14, notes)

    def r5(self):
        got, notes = 0, []
        hx = ''
        for n in self.doc.names:
            if 'header' in n and n.endswith('.xml'):
                c = self.doc.read(n)
                if '雅舍谈吃' in c:
                    hx = c
                    break
        if not hx:
            return (5, '文字水印', 0, 8, ['没有水印'])
        got += 4
        notes.append('水印文字 OK')
        if '仿宋' in hx and '72pt' in hx:
            got += 2
            notes.append('仿宋72 OK')
        else:
            notes.append('字体字号未匹配')
        if 'rotation' in hx or 'rotationangle' in hx.lower() or '45' in (re.findall(r'style="([^"]*)"', hx)[0] if re.findall(r'style="([^"]*)"', hx) else ''):
            got += 2
            notes.append('倾斜版式 OK')
        else:
            notes.append('版式未识别')
        return (5, '文字水印', got, 8, notes)

    def r6(self):
        got, notes = 0, []
        tables = list(self.doc.body.iter(W + 'tbl')) if self.doc.body is not None else []
        if not tables:
            return (6, '末尾表格', 0, 14, ['没有表格'])
        tbl = tables[-1]
        rows = list(tbl.iter(W + 'tr'))
        cols = len(list(rows[0].iter(W + 'tc'))) if rows else 0
        if len(rows) == 2 and cols == 2:
            got += 5
            notes.append('2行2列 OK')
        else:
            notes.append('表格 %d行%d列' % (len(rows), cols))
        texts = [''.join(t.text or '' for t in tc.iter(W + 't')).strip()
                 for tc in rows[0].iter(W + 'tc')] if rows else []
        if texts[:2] == ['现代散文作家', '代表作品']:
            got += 3
            notes.append('首行文字 OK')
        else:
            notes.append('首行=%s' % texts)
        centered = 0
        total = 0
        for tc in tbl.iter(W + 'tc'):
            tcpr = tc.find(W + 'tcPr')
            total += 1
            if tcpr is None:
                continue
            va = tcpr.find(W + 'vAlign')
            if va is None or va.get(W + 'val') != 'center':
                continue
            for p in tc.iter(W + 'p'):
                ppr = p.find(W + 'pPr')
                if ppr is not None:
                    jc = ppr.find(W + 'jc')
                    if jc is not None and jc.get(W + 'val') == 'center':
                        centered += 1
                        break
        if total and centered >= total - 1:
            got += 3
            notes.append('水平垂直居中 OK')
        else:
            notes.append('居中 %d/%d' % (centered, total))
        tx = __import__('xml.etree.ElementTree', fromlist=['x']).tostring(tbl, encoding='unicode')
        if re.search(r'tblStyle[^>]*val="[^"]+"', tx):
            got += 3
            notes.append('表格样式 OK')
        else:
            notes.append('未套表格样式')
        return (6, '末尾表格', got, 14, notes)

    def r7(self):
        got, notes = 0, []
        if 'word/footnotes.xml' not in self.doc.names:
            return (7, '脚注', 0, 10, ['没有脚注部件'])
        fx = self.doc.read('word/footnotes.xml')
        if '樊增祥' in fx:
            got += 8
            notes.append('脚注内容 OK')
        else:
            got += 3
            notes.append('有脚注但内容不符')
        ref = '<w:footnoteReference' in self.doc.xml_all()
        if ref:
            got += 2
            notes.append('正文有脚注引用 OK')
        return (7, '脚注', got, 10, notes)

    def r8(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        if 'paper2' in full or 'type="tile"' in full:
            got += 5
            notes.append('纸纹2纹理背景 OK')
        elif '<w:background' in full:
            got += 2
            notes.append('有背景但非纸纹2')
        else:
            notes.append('无页面背景')
        joined = ''.join(self.doc.header_texts())
        if '梁实秋雅舍系列节选' in joined:
            got += 2
            notes.append('页眉文字 OK')
        left_red = False
        for n in self.doc.names:
            if 'header' in n and n.endswith('.xml'):
                c = self.doc.read(n)
                if '梁实秋' in c and 'val="left"' in c and 'FF0000' in c.upper():
                    left_red = True
        if left_red:
            got += 2
            notes.append('页眉左对齐红色 OK')
        else:
            notes.append('页眉对齐/颜色未匹配')
        foot = ''.join(self.doc.footer_texts())
        if '第' in foot and '页' in foot:
            got += 1
            notes.append('页脚页码 OK')
        else:
            notes.append('页脚=%r' % foot[:24])
        return (8, '背景与页眉页脚', got, 10, notes)


if __name__ == '__main__':
    sys.exit(run(WordGrader13, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Word 2010 操作题题库', '13', '1结果.docx')))
