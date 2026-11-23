"""WPS 表格评分器 - 第20套（员工信息表）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import ExcelBook, Report, run, formula_has

S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'


class ExcelGrader20:
    def __init__(self, path):
        self.book = ExcelBook(path)

    def grade(self):
        report = Report('WPS 表格 第20套 · 员工信息表')
        for fn in (self.r1, self.r2, self.r3, self.r4, self.r5,
                   self.r6, self.r7, self.r8, self.r9):
            report.add(*fn())
        return report

    def sheet(self, name):
        return self.book.sheet(name)

    def fmt(self, sheet, ref):
        return self.book.format_in(sheet.root, ref)

    def r1(self):
        got, notes = 0, []
        ws = self.sheet('员工信息')
        if ws is None:
            return (1, '表标题', 0, 13, ['缺"员工信息"'])
        t = self.book.value_in(ws.root, 'A1')
        if str(t or '').startswith('XXX员工信息表'):
            got += 6
            notes.append('标题文字 OK')
        else:
            notes.append('A1=%r' % t)
        f = self.fmt(ws, 'A1')
        font = f.get('font') or {}
        if 'Light' in (font.get('name') or '') and font.get('size') == '26':
            got += 5
            notes.append('微软雅黑Light 26 OK')
        else:
            notes.append('字体=%s/%s' % (font.get('name'), font.get('size')))
        if (f.get('alignment') or {}).get('horizontal') == 'centerContinuous':
            got += 2
            notes.append('跨列居中 OK')
        else:
            notes.append('对齐=%s' % (f.get('alignment') or {}).get('horizontal'))
        return (1, '表标题', got, 13, notes)

    def r2(self):
        got, notes = 0, []
        ws = self.sheet('员工信息')
        if ws is None:
            return (2, '边框底纹', 0, 14, ['缺"员工信息"'])
        colors = set()
        for node in ws.cells().values():
            fm = self.book.styles.get(int(node.get('s', '0') or 0))
            for _k, v in (fm.get('border') or {}).items():
                col = v.get('color') or {}
                if v.get('style'):
                    colors.add((col.get('rgb') or '', col.get('theme') or '', col.get('tint') or ''))
        if len(colors) >= 2:
            got += 7
            notes.append('内外边框区分 OK（%d 种）' % len(colors))
        elif colors:
            got += 3
            notes.append('只有一种边框')
        else:
            notes.append('无边框')
        f2 = self.fmt(ws, 'A2')
        fill = (f2.get('fill') or {}).get('fg') or {}
        if fill.get('theme') or fill.get('rgb'):
            got += 4
            notes.append('表头底纹 OK')
        else:
            notes.append('表头无底纹')
        if (f2.get('font') or {}).get('bold'):
            got += 3
            notes.append('表头加粗 OK')
        return (2, '边框底纹', got, 14, notes)

    def r3(self):
        got, notes = 0, []
        ws = self.sheet('员工信息')
        if ws is None:
            return (3, '提取市', 0, 10, ['缺"员工信息"'])
        f = self.book.formula_in(ws.root, 'I3')
        if formula_has(f, 'MID', 'RIGHT', 'FIND'):
            got += 10
            notes.append('提取市公式 OK（%s）' % (f or '')[:40])
        else:
            v = self.book.value_in(ws.root, 'I3')
            if v:
                got += 5
                notes.append('有值 %s（无公式）' % v)
            else:
                notes.append('I3=%r' % v)
        return (3, '提取市', got, 10, notes)

    def r4(self):
        got, notes = 0, []
        ws = self.sheet('员工信息')
        if ws is None:
            return (4, '等级', 0, 12, ['缺"员工信息"'])
        f = self.book.formula_in(ws.root, 'K3')
        vals = [str(self.book.value_in(ws.root, 'K%d' % r) or '') for r in range(3, 41)]
        val_ok = sum(1 for v in vals if v in ('A', 'B', 'C', 'D'))
        if formula_has(f, 'IF') and val_ok >= 20:
            got += 12
            notes.append('等级 IF+%d行结果 OK' % val_ok)
        elif val_ok >= 20:
            got += 9
            notes.append('等级结果全对（公式仅少数）')
        elif formula_has(f, 'IF'):
            got += 6
            notes.append('IF 有了（结果%d行）' % val_ok)
        else:
            notes.append('K3=%r 结果%d行' % (f or '', val_ok))
        return (4, '等级', got, 12, notes)

    def r5(self):
        got, notes = 0, []
        ws = self.sheet('员工信息')
        if ws is None:
            return (5, '奖金薪资', 0, 14, ['缺"员工信息"'])
        m = self.book.formula_in(ws.root, 'M3')
        if formula_has(m, 'IF'):
            got += 5
            notes.append('奖金 IF OK')
        else:
            notes.append('M3=%r' % m)
        n = self.book.formula_in(ws.root, 'N3')
        if formula_has(n, '400') or (n and '*' in n):
            got += 5
            notes.append('薪资公式 OK（%s）' % (n or '')[:32])
        else:
            notes.append('N3=%r' % n)
        o = self.book.formula_in(ws.root, 'O3')
        ov = str(self.book.value_in(ws.root, 'O3') or '')
        if formula_has(o, 'IF') or ov.upper() in ('TRUE', 'FALSE'):
            got += 4
            notes.append('薪资高于8000 判断 OK')
        else:
            notes.append('O3=%r' % (o or ov))
        return (5, '奖金薪资', got, 14, notes)

    def r6(self):
        got, notes = 0, []
        ws = self.sheet('员工信息')
        if ws is None:
            return (6, '条件格式', 0, 10, ['缺"员工信息"'])
        rules = [(c.get('sqref'), r.get('type')) for c in ws.root.iter('{%s}conditionalFormatting' % S) for r in c]
        if rules:
            got += 6
            notes.append('条件格式 OK（%s）' % rules[0][0])
        else:
            notes.append('无条件格式')
        st = self.book.read('xl/styles.xml') if 'xl/styles.xml' in self.book.names else ''
        m = re.search(r'<dxfs[^>]*>(.*?)</dxfs>', st, re.S)
        if m and ('FADBDF' in m.group(1).upper() or 'accent6' in m.group(1) or 'theme' in m.group(1)):
            got += 4
            notes.append('猩红浅色底纹 OK')
        else:
            notes.append('dxf 样式未匹配')
        return (6, '条件格式', got, 10, notes)

    def r7(self):
        got, notes = 0, []
        ws = self.sheet('员工信息')
        if ws is None:
            return (7, '页面设置', 0, 8, ['缺"员工信息"'])
        ps = ws.root.find('{%s}pageSetup' % S)
        sheet_xml = ''
        for n in self.book.names:
            if 'worksheets/sheet' in n and n.endswith('.xml'):
                sheet_xml += self.book.read(n)
        if ps is not None and ps.get('orientation') == 'landscape' and 'fitToPage="1"' in sheet_xml:
            got += 8
            notes.append('横向+缩放到一页 OK')
        elif ps is not None and ps.get('orientation') == 'landscape':
            got += 5
            notes.append('横向 OK（未缩放到一页）')
        else:
            notes.append('方向=%s' % (ps.get('orientation') if ps is not None else '无'))
        return (7, '页面设置', got, 8, notes)

    def r8(self):
        got, notes = 0, []
        ws = self.sheet('人数占比')
        if ws is None:
            return (8, '人数占比与饼图', 0, 12, ['缺"人数占比"'])
        n = 0
        pct = False
        for r in range(1, 15):
            for c in 'ABCDEF':
                f = self.book.formula_in(ws.root, '%s%d' % (c, r))
                if formula_has(f, 'COUNTIF'):
                    n += 1
                nf = self.fmt(ws, '%s%d' % (c, r)).get('numfmt') or ''
                if '%' in nf:
                    pct = True
        if n >= 2:
            got += 5
            notes.append('男女统计 OK（%d格）' % n)
        else:
            notes.append('COUNTIF %d 格' % n)
        if pct:
            got += 3
            notes.append('百分比格式 OK')
        else:
            notes.append('未设百分比')
        charts = [x for x in self.book.names if re.match(r'xl/charts/chart\d+\.xml$', x)]
        if charts:
            x = self.book.read(charts[0])
            if 'pieChart' in x:
                got += 4
                notes.append('饼图 OK')
            else:
                notes.append('类型非饼图')
        return (8, '人数占比与饼图', got, 12, notes)

    def r9(self):
        got, notes = 0, []
        tables = [n for n in self.book.names if re.match(r'xl/pivotTables/pivotTable\d+\.xml$', n)]
        if not tables:
            return (9, '数据透视表', got, 7, notes + ['没有透视表'])
        x = self.book.read(tables[0])
        loc = re.search(r'<location[^>]*ref="([A-Z]+\d+)', x)
        if loc and loc.group(1).upper() == 'C3':
            got += 2
            notes.append('位置 C3 OK')
        else:
            notes.append('位置=%s' % (loc.group(1) if loc else '?'))
        rows = len(re.findall(r'axis="axisRow"', x))
        if rows >= 2:
            got += 2
            notes.append('行区域2字段 OK')
        if 'axis="axisCol"' in x:
            got += 1
            notes.append('列区域 OK')
        df = re.findall(r'<dataField name="([^"]*)"', x)
        if df and '计数' in df[0] and '工号' in df[0]:
            got += 2
            notes.append('工号计数 OK')
        else:
            notes.append('值=%s' % (df or '无'))
        return (9, '数据透视表', got, 7, notes)


if __name__ == '__main__':
    sys.exit(run(ExcelGrader20, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Excel 2010 操作题题库', '20', '1结果.xlsx')))
