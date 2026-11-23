"""WPS 表格评分器 - 第18套（招聘面试信息）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import ExcelBook, Report, run, formula_has

S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'


class ExcelGrader18:
    def __init__(self, path):
        self.book = ExcelBook(path)

    def grade(self):
        report = Report('WPS 表格 第18套 · 招聘面试信息')
        for fn in (self.r1, self.r2, self.r3, self.r4,
                   self.r5, self.r6, self.r7, self.r8):
            report.add(*fn())
        return report

    def sheet(self, name):
        return self.book.sheet(name)

    def fmt(self, sheet, ref):
        return self.book.format_in(sheet.root, ref)

    def r1(self):
        got, notes = 0, []
        hidden = [s.name for s in self.book.sheets if s.state == 'hidden']
        if any('Sheet4' in h for h in hidden):
            got += 4
            notes.append('Sheet4 隐藏 OK')
        else:
            notes.append('隐藏表=%s' % hidden)
        ws = self.sheet('Sheet1')
        if ws is None:
            return (1, '新建列与行高', got, 17, notes)
        widths = [(c.get('min'), c.get('width')) for c in ws.root.iter('{%s}col' % S)]
        w1 = ''
        for mn, w in widths:
            if mn == '1':
                w1 = w or ''
        if w1 and abs(float(w1) - 2.38) < 1.2:
            got += 3
            notes.append('A列宽 %s OK' % w1)
        else:
            notes.append('A列宽=%s' % (w1 or '无'))
        h5 = [r.get('ht') for r in ws.root.iter('{%s}row' % S) if r.get('r') == '5']
        if h5 and abs(float(h5[0] or 0) - 5) < 1.0:
            got += 3
            notes.append('第5行高5磅 OK')
        else:
            notes.append('行5高=%s' % (h5[0] if h5 else '无'))
        f = self.fmt(ws, 'B7')['font']
        if f.get('name') == '仿宋' and f.get('size') == '14':
            got += 7
            notes.append('仿宋14 OK')
        else:
            notes.append('字体=%s/%s' % (f.get('name'), f.get('size')))
        return (1, '新建列与行高', got, 17, notes)

    def r2(self):
        got, notes = 0, []
        st = self.book.read('xl/styles.xml') if 'xl/styles.xml' in self.book.names else ''
        if re.search(r'<cellStyle name="表标题"', st):
            got += 6
            notes.append('自定义样式"表标题" OK')
        else:
            notes.append('未找到"表标题"样式')
        if 'shrinkToFit="1"' in st or 'shrinkToFit="true"' in st:
            got += 3
            notes.append('缩小字体填充 OK')
        else:
            notes.append('无缩小字体填充')
        if 'fillId' in st or 'Gradient' in st:
            pass
        return (2, '表标题样式', got, 9, notes)

    def r3(self):
        got, notes = 0, []
        ws = self.sheet('Sheet1')
        if ws is None:
            return (3, '边框与填充', 0, 14, ['缺 Sheet1'])
        purple = False
        for node in ws.cells().values():
            fm = self.book.styles.get(int(node.get('s', '0') or 0))
            for _k, v in (fm.get('border') or {}).items():
                c = (v.get('color') or {}).get('rgb') or ''
                if v.get('style') and c.upper().endswith(('7030A0', '8064A2', '800080')):
                    purple = True
        if purple:
            got += 8
            notes.append('紫色内外边框 OK')
        else:
            notes.append('未找到紫色边框')
        fill = (self.fmt(ws, 'B6')['fill'] or {}).get('fg') or {}
        f6 = self.fmt(ws, 'B6')['font']
        fc = f6.get('color') or {}
        white = (str(fc.get('rgb') or '').upper().endswith('FFFFFF') or str(fc.get('theme')) == '0')
        if (fill.get('rgb') or fill.get('theme') or fill.get('indexed')) and white:
            got += 6
            notes.append('浅蓝底白字 OK')
        elif fill:
            got += 3
            notes.append('有填充（%s）字色=%s' % (fill, (f6.get('color') or {}).get('rgb')))
        else:
            notes.append('B6 无填充')
        return (3, '边框与填充', got, 14, notes)

    def r4(self):
        got, notes = 0, []
        ws = self.sheet('Sheet1')
        if ws is None:
            return (4, '日期/有效性/条件格式', 0, 16, ['缺 Sheet1'])
        date_ok = 0
        serial_ok = 0
        for r in range(7, 24):
            for c in ('M', 'O'):
                nf = self.fmt(ws, '%s%d' % (c, r)).get('numfmt') or ''
                if '月' in nf and '日' in nf:
                    date_ok += 1
                v = self.book.value_in(ws.root, '%s%d' % (c, r))
                try:
                    if v is not None and 40000 < float(v) < 60000:
                        serial_ok += 1
                except (TypeError, ValueError):
                    pass
        if date_ok >= 20:
            got += 6
            notes.append('日期格式"3月7日" OK（%d格）' % date_ok)
        elif serial_ok >= 30:
            got += 6
            notes.append('日期列已存为日期序列号 OK（%d格，题干格式未套用）' % serial_ok)
        elif date_ok or serial_ok:
            got += 3
            notes.append('日期列部分就绪（格式%d/序列%d）' % (date_ok, serial_ok))
        else:
            notes.append('日期列未处理')
        dv = []
        for d in ws.root.iter('{%s}dataValidation' % S):
            dv.append(d.get('sqref', ''))
            f1 = d.find('{%s}formula1' % S)
            txt = f1.text if f1 is not None else ''
            if '录取' in str(txt):
                got += 5
                notes.append('数据有效性序列 OK（%s）' % d.get('sqref'))
                break
        if not any('录取' in (d.find('{%s}formula1' % S).text or '') if d.find('{%s}formula1' % S) is not None else False
                   for d in ws.root.iter('{%s}dataValidation' % S)):
            notes.append('有效性=%s' % dv[:3])
        rules = [(c.get('sqref'), r.get('type')) for c in ws.root.iter('{%s}conditionalFormatting' % S) for r in c]
        if rules:
            got += 5
            notes.append('条件格式 OK（%s）' % rules[0][0])
        else:
            notes.append('无条件格式')
        return (4, '日期/有效性/条件格式', got, 16, notes)

    def r5(self):
        got, notes = 0, []
        ws = self.sheet('Sheet1')
        if ws is None:
            return (5, '函数与统计', 0, 14, ['缺 Sheet1'])
        f = self.book.formula_in(ws.root, 'K7')
        if formula_has(f, 'VLOOKUP'):
            got += 5
            notes.append('K列 VLOOKUP OK')
        else:
            notes.append('K7=%r' % f)
        d4 = self.book.formula_in(ws.root, 'D4')
        if formula_has(d4, 'COUNTA', 'COUNT'):
            got += 5
            notes.append('应聘总人数 OK')
        elif self.book.value_in(ws.root, 'D4') not in (None, ''):
            got += 3
            notes.append('D4 有值（无公式）')
        else:
            notes.append('D4=%r' % d4)
        i4 = self.book.formula_in(ws.root, 'I4')
        if formula_has(i4, 'COUNTIF', 'COUNTIFS'):
            got += 4
            notes.append('录取人数 OK')
        else:
            notes.append('I4=%r' % i4)
        return (5, '函数与统计', got, 14, notes)

    def r6(self):
        got, notes = 0, []
        ws = self.sheet('Sheet1')
        if ws is None:
            return (6, '页面设置', 0, 10, ['缺 Sheet1'])
        ps = ws.root.find('{%s}pageSetup' % S)
        if ps is not None and ps.get('orientation') == 'landscape':
            got += 4
            notes.append('横向 OK')
        else:
            notes.append('方向=%s' % (ps.get('orientation') if ps is not None else '无'))
        sheet_xml = self.book.read('xl/worksheets/sheet1.xml') if 'xl/worksheets/sheet1.xml' in self.book.names else ''
        if (ps is not None and (ps.get('fitToWidth') or '') == '1') or 'fitToPage="1"' in sheet_xml:
            got += 2
            notes.append('列打印在一页 OK')
        po = ws.root.find('{%s}printOptions' % S)
        if po is not None and po.get('horizontalCentered') == '1':
            got += 2
            notes.append('水平居中 OK')
        if ps is not None and (ps.get('paperSize') or '') in ('43', '41', '1'):
            got += 2
            notes.append('信纸/Letter OK（%s）' % ps.get('paperSize'))
        else:
            notes.append('纸张=%s' % (ps.get('paperSize') if ps is not None else '无'))
        return (6, '页面设置', got, 10, notes)

    def r7(self):
        got, notes = 0, []
        ws2 = self.sheet('Sheet2')
        if ws2 is None:
            return (7, '学历统计与饼图', 0, 10, ['缺 Sheet2'])
        n = 0
        for r in range(1, 20):
            for c in 'ABCDEF':
                if formula_has(self.book.formula_in(ws2.root, '%s%d' % (c, r)), 'COUNTIF'):
                    n += 1
        if n >= 3:
            got += 4
            notes.append('学历统计 OK（%d格）' % n)
        else:
            notes.append('COUNTIF %d 格' % n)
        charts = [x for x in self.book.names if re.match(r'xl/charts/chart\d+\.xml$', x)]
        if charts:
            x = self.book.read(charts[0])
            if 'pieChart' in x:
                got += 4
                notes.append('饼图 OK')
            else:
                notes.append('类型非饼图')
            texts = re.findall(r'<a:t>([^<]*)</a:t>', x)
            if any('分布图' in t for t in texts):
                got += 2
                notes.append('标题 OK')
        else:
            notes.append('没有图表')
        return (7, '学历统计与饼图', got, 10, notes)

    def r8(self):
        got, notes = 0, []
        tables = [n for n in self.book.names if re.match(r'xl/pivotTables/pivotTable\d+\.xml$', n)]
        if not tables:
            return (8, '数据透视表', 0, 10, ['没有透视表'])
        x = self.book.read(tables[0])
        loc = re.search(r'<location[^>]*ref="([A-Z]+\d+)', x)
        if loc and loc.group(1).upper() == 'B3':
            got += 4
            notes.append('位置 B3 OK')
        else:
            notes.append('位置=%s' % (loc.group(1) if loc else '?'))
        if 'axis="axisRow"' in x:
            got += 2
            notes.append('行区域 OK')
        cols = len(re.findall(r'axis="axisCol"', x))
        if cols >= 2:
            got += 2
            notes.append('列区域2字段 OK')
        else:
            notes.append('列字段=%d' % cols)
        df = re.findall(r'<dataField name="([^"]*)"', x)
        if df and '姓名' in df[0]:
            got += 2
            notes.append('值=姓名 OK')
        else:
            notes.append('值=%s' % (df or '无'))
        return (8, '数据透视表', got, 10, notes)


if __name__ == '__main__':
    sys.exit(run(ExcelGrader18, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Excel 2010 操作题题库', '18', '1结果.xlsx')))
