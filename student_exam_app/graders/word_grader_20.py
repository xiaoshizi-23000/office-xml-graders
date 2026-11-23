"""WPS 文档评分器 - 第20套（故宫的文化创新）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import WordDoc, Report, run

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


class WordGrader20:
    def __init__(self, path):
        self.doc = WordDoc(path)

    def grade(self):
        report = Report('WPS 文档 第20套 · 故宫的文化创新')
        for fn in (self.r1, self.r2, self.r3, self.r4,
                   self.r6, self.r7, self.r8):
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
        if ps.get('orient') == 'landscape':
            got += 3
            notes.append('横向 OK')
        else:
            notes.append('方向=%s' % ps.get('orient'))
        v = {k: int(ps.get(k) or 0) / 567 for k in ('top', 'bottom', 'left', 'right')}
        if abs(v['top'] - 2.54) < 0.15 and abs(v['left'] - 1.9) < 0.15:
            got += 5
            notes.append('页边距"适中" OK')
        else:
            notes.append('边距 %.2f/%.2f/%.2f/%.2f' % (v['top'], v['bottom'], v['left'], v['right']))
        return (1, '纸张与边距', got, 8, notes)

    def r2(self):
        got, notes = 0, []
        ps = self.paras()
        if not ps:
            return (2, '标题格式', 0, 16, ['无正文'])
        p0 = ps[0]
        rp = self.doc.run_props(list(p0.iter(W + 'r'))[0], p0)
        font = rp.get('eastAsia') or rp.get('font') or ''
        if font == '黑体':
            got += 3
            notes.append('黑体 OK')
        else:
            notes.append('字体=%s' % font)
        if str(rp.get('size') or '') == '52':
            got += 3
            notes.append('一号(26pt) OK')
        else:
            notes.append('字号=%s' % rp.get('size'))
        if str(rp.get('color') or '').upper().endswith('FF0000'):
            got += 2
            notes.append('红色 OK')
        else:
            notes.append('颜色=%s' % rp.get('color'))
        seg = self.pxml(p0)
        if 'val="distribute"' in seg:
            got += 3
            notes.append('分散对齐 OK')
        else:
            notes.append('未分散对齐')
        if 'after="157"' in seg or 'afterLines="50"' in seg:
            got += 2
            notes.append('段后0.5行 OK')
        if 'outlineLvl' in seg:
            got += 1
            notes.append('大纲1级 OK')
        if 'glow' in seg or 'glow' in self.doc.xml_all():
            got += 2
            notes.append('发光 OK')
        return (2, '标题格式', got, 16, notes)

    def r3(self):
        got, notes = 0, []
        target = None
        for p in self.paras()[1:]:
            rp = self.doc.run_props(list(p.iter(W + 'r'))[0], p) if list(p.iter(W + 'r')) else {}
            font = rp.get('eastAsia') or rp.get('font') or ''
            if font == '微软雅黑' and len(self.ptext(p)) > 2:
                target = p
                break
        if target is None:
            return (3, '小标题格式', 0, 14, ['找不到小标题段'])
        seg = self.pxml(target)
        rp = self.doc.run_props(list(target.iter(W + 'r'))[0], target)
        if str(rp.get('size') or '') == '36':
            got += 4
            notes.append('小二(18pt) OK')
        else:
            notes.append('字号=%s' % rp.get('size'))
        if re.search(r':b[\s/>]', seg):
            got += 2
            notes.append('加粗 OK')
        if 'val="center"' in seg:
            got += 2
            notes.append('居中 OK')
        if 'beforeLines="50"' in seg and 'afterLines="50"' in seg:
            got += 3
            notes.append('段前后0.5行 OK')
        else:
            notes.append('段前后=%s' % re.findall(r'beforeLines="(\d+)"', seg)[:1])
        if 'outlineLvl w:val="1"' in seg or 'outlineLvl ns0:val="1"' in seg or 'val="1"' in seg:
            got += 2
            notes.append('大纲2级 OK')
        else:
            notes.append('大纲级别未匹配')
        if re.search(r'ascii="仿宋"', seg) or re.search(r'asciiTheme', seg):
            got += 1
            notes.append('西文字体已设 OK')
        return (3, '小标题格式', got, 14, notes)

    def r4(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        n = sum(1 for p in self.paras() if 'numPr' in self.pxml(p))
        if n >= 4:
            got += 6
            notes.append('编号段落 %d 个 OK' % n)
        elif n:
            got += 3
            notes.append('编号段落 %d 个' % n)
        else:
            notes.append('无编号')
        nx = self.doc.read('word/numbering.xml') if 'word/numbering.xml' in self.doc.names else ''
        if 'chineseCounting' in nx:
            got += 3
            notes.append('中文数字编号 OK')
        if re.search(r'<w:start w:val="2"', nx):
            got += 3
            notes.append('起始2 OK')
        bdr = re.search(r'<[a-z0-9]+:bdr ([^/]*)/>', full)
        if bdr and 'FF0000' in bdr.group(1).upper():
            got += 2
            notes.append('红色文字边框 OK')
        else:
            notes.append('文字边框未匹配')
        if re.search(r'<[a-z0-9]+:shd[^/]*w:fill="([0-9A-Fa-f]{6})"', full):
            fills = re.findall(r'<[a-z0-9]+:shd[^/]*fill="([0-9A-Fa-f]{6})"', full)
            green = [f for f in fills if f.upper() in ('00FF00', '00B050', '92D050', 'A9D08E', 'C6E0B4', 'E2F0D9', '70AD47')]
            if green:
                got += 2
                notes.append('绿色文字底纹 OK')
            else:
                notes.append('底纹色=%s' % fills[:2])
        else:
            notes.append('无文字底纹')
        return (4, '编号与边框底纹', got, 16, notes)

    def r6(self):
        got, notes = 0, []
        tables = list(self.doc.body.iter(W + 'tbl')) if self.doc.body is not None else []
        if not tables:
            return (6, '表格', 0, 18, ['没有表格'])
        tbl = tables[0]
        tx = __import__('xml.etree.ElementTree', fromlist=['x']).tostring(tbl, encoding='unicode')
        widths = [int(x) / 567 for x in re.findall(r'gridCol[^>]*w="(\d+)"', tx)]
        if len(widths) >= 3 and abs(widths[0] - 5) < 0.6 and abs(widths[1] - 6) < 0.6 and abs(widths[2] - 6) < 0.6:
            got += 5
            notes.append('列宽 5/6/6cm OK')
        elif widths:
            notes.append('列宽=%s' % [round(w, 1) for w in widths])
        if re.search(r'tblBorders.*?color="FF0000"', tx, re.S):
            got += 4
            notes.append('红边框 OK')
            if re.search(r'sz="12"', tx):
                got += 2
                notes.append('1.5磅 OK')
        else:
            notes.append('表格边框未匹配')
        if 'val="center"' in tx:
            got += 3
            notes.append('居中 OK')
        rows = list(tbl.iter(W + 'tr'))
        if rows:
            first = __import__('xml.etree.ElementTree', fromlist=['x']).tostring(rows[0], encoding='unicode')
            if 'shd' in first:
                got += 2
                notes.append('首行填充 OK')
        heights = re.findall(r'<[a-z0-9]+:trHeight w:val="(\d+)"', tx) or re.findall(r'trHeight[^>]*val="(\d+)"', tx)
        if heights and abs(int(heights[0]) / 567 - 1.2) < 0.15:
            got += 2
            notes.append('行高1.2cm OK')
        return (6, '表格', got, 18, notes)

    def r7(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        if '<wp:anchor' not in full:
            return (7, '图片', 0, 14, ['没有浮动图片'])
        got += 3
        notes.append('浮动图片 OK')
        if 'wrapSquare' in full:
            got += 3
            notes.append('四周型环绕 OK')
        exts = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'ext cx="(\d+)" cy="(\d+)"', full)]
        if any(abs(h - 8) < 0.5 for w, h in exts):
            got += 3
            notes.append('高度8cm OK')
        elif exts:
            notes.append('尺寸=%s' % [(round(w, 1), round(h, 1)) for w, h in exts[:2]])
        if re.search(r'<pic:spPr>.*?FF0000', full, re.S):
            got += 3
            notes.append('红色2磅边框 OK')
        else:
            notes.append('图片边框未匹配')
        if 'rotRev' in full or 'camera' in full.lower():
            got += 2
            notes.append('左透视 OK')
        elif re.search(r'<wp:positionH[^>]*relativeFrom="column"', full):
            got += 2
            notes.append('相对栏定位 OK')
        return (7, '图片', got, 14, notes)

    def r8(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        if 'type="gradient"' in full:
            got += 6
            notes.append('渐变背景 OK')
            if 'A8EDEA' in full.upper() and 'FED6E3' in full.upper():
                got += 3
                notes.append('两种颜色 OK')
            else:
                notes.append('颜色未完全匹配')
        else:
            notes.append('无渐变背景')
        joined = ''.join(self.doc.header_texts())
        if '故宫瑰宝' in joined:
            got += 3
            notes.append('页眉文字 OK')
        else:
            notes.append('页眉=%s' % joined[:20])
        fnum = any('PAGE' in self.doc.read(n) for n in self.doc.names
                   if 'footer' in n and n.endswith('.xml'))
        if fnum or '1' in ''.join(self.doc.footer_texts()):
            got += 2
            notes.append('页脚页码 OK')
        else:
            notes.append('页脚未设')
        return (8, '背景与页眉页脚', got, 14, notes)


if __name__ == '__main__':
    sys.exit(run(WordGrader20, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Word 2010 操作题题库', '20', '1结果.docx')))
