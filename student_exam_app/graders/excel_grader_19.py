"""WPS 表格评分器 - 第19套（2018餐饮数据）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import ExcelBook, Report, run, formula_has

S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'


class ExcelGrader19:
    def __init__(self, path):
        self.book = ExcelBook(path)

    def grade(self):
        report = Report('WPS 表格 第19套 · 2018餐饮数据')
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
        if '餐饮数据' in self.book.sheet_names:
            got += 6
            notes.append('"餐饮数据"工作表 OK')
        else:
            notes.append('工作表=%s' % self.book.sheet_names)
        ws = self.sheet('餐饮数据')
        if ws is None:
            return (1, '建表与导入', got, 12, notes)
        vals = [self.book.value_in(ws.root, '%s1' % c) for c in ('A', 'B', 'C')]
        if all(v not in (None, '') for v in vals):
            got += 6
            notes.append('数据已导入 A1 起 OK（%s/%s/%s）' % tuple(vals))
        else:
            notes.append('A1:C1=%s' % vals)
        return (1, '建表与导入', got, 12, notes)

    def r2(self):
        got, notes = 0, []
        tables = []
        for n in self.book.names:
            if n.startswith('xl/tables/') and n.endswith('.xml'):
                x = self.book.read(n)
                nm = re.search(r'<table[^>]*name="([^"]*)"', x)
                st = re.search(r'tableStyleInfo[^>]*name="([^"]*)"', x)
                rf = re.search(r'<table[^>]*ref="([^"]*)"', x)
                tables.append((nm.group(1) if nm else '', st.group(1) if st else '', rf.group(1) if rf else ''))
        hit = [t for t in tables if t[0] == '数据源']
        if hit:
            got += 6
            notes.append('表名"数据源" OK')
            if 'Preset3' in hit[0][1]:
                got += 4
                notes.append('黄色表样式3 OK（%s）' % hit[0][1])
            else:
                notes.append('样式=%s' % hit[0][1])
            if hit[0][2].replace('$', '').startswith('A1:I1152'):
                got += 2
                notes.append('范围 OK')
            else:
                notes.append('范围=%s' % hit[0][2])
        else:
            notes.append('未找到"数据源"（%s）' % [t[0] for t in tables][:3])
        return (2, '表格对象', got, 12, notes)

    def r3(self):
        got, notes = 0, []
        ws = self.sheet('餐饮数据')
        if ws is None:
            return (3, '地区 VLOOKUP', 0, 12, ['缺"餐饮数据"'])
        if self.book.value_in(ws.root, 'B1') == '地区':
            got += 3
            notes.append('B1"地区" OK')
        f = self.book.formula_in(ws.root, 'B2')
        if formula_has(f, 'VLOOKUP'):
            got += 9
            notes.append('VLOOKUP 地区 OK')
        else:
            v = self.book.value_in(ws.root, 'B2')
            if v:
                got += 4
                notes.append('有值 %s（无公式）' % v)
            else:
                notes.append('B2=%r' % v)
        return (3, '地区 VLOOKUP', got, 12, notes)

    def r4(self):
        got, notes = 0, []
        ws = self.sheet('餐饮数据')
        if ws is None:
            return (4, '三项达标门店数', 0, 12, ['缺"餐饮数据"'])
        f = self.book.formula_in(ws.root, 'L2')
        if formula_has(f, 'COUNTIFS', 'SUMPRODUCT'):
            got += 12
            notes.append('COUNTIFS 三项达标 OK')
        else:
            v = self.book.value_in(ws.root, 'L2')
            if v not in (None, ''):
                got += 5
                notes.append('L2 有值 %s（无公式）' % v)
            else:
                notes.append('L2=%r' % v)
        return (4, '三项达标门店数', got, 12, notes)

    def r5(self):
        got, notes = 0, []
        ws = self.sheet('餐饮数据')
        if ws is None:
            return (5, '页面设置', 0, 14, ['缺"餐饮数据"'])
        wb = self.book.read('xl/workbook.xml')
        area = re.search(r'name="_xlnm\.Print_Area"[^>]*>([^<]*)<', wb)
        if area and 'A$1:$I$1152' in area.group(1).replace(' ', ''):
            got += 4
            notes.append('打印区域 A1:I1152 OK')
        elif area:
            got += 2
            notes.append('打印区域=%s' % area.group(1))
        else:
            notes.append('无打印区域')
        ps = ws.root.find('{%s}pageSetup' % S)
        if ps is not None and ps.get('orientation') == 'portrait':
            got += 2
            notes.append('纵向 OK')
        if ps is not None and (ps.get('paperSize') or '') == '8':
            got += 2
            notes.append('A3 OK')
        po = ws.root.find('{%s}printOptions' % S)
        if po is not None and po.get('horizontalCentered') == '1':
            got += 2
            notes.append('水平居中 OK')
        head = ''
        for h in ws.root.iter('{%s}oddHeader' % S):
            head = h.text or ''
            break
        if '2018年餐饮数据表' in head:
            got += 4
            notes.append('页眉 OK')
        else:
            notes.append('页眉=%r' % head)
        return (5, '页面设置', got, 14, notes)

    def r6(self):
        got, notes = 0, []
        ws = self.sheet('详情')
        if ws is None:
            return (6, '统计与迷你图', 0, 14, ['缺"详情"工作表'])
        fns = set()
        for r in range(1, 30):
            for c in 'ABCDEFG':
                f = self.book.formula_in(ws.root, '%s%d' % (c, r))
                for fn in ('AVERAGE', 'MAX', 'MIN', 'SUM', 'MEDIAN', 'MODE'):
                    if formula_has(f, fn):
                        fns.add(fn)
        if len(fns) >= 5:
            got += 8
            notes.append('六类统计 OK（%s）' % '/'.join(sorted(fns)))
        elif fns:
            got += 4
            notes.append('统计函数 %d 类' % len(fns))
        else:
            notes.append('未找到统计函数')
        spark = False
        for n in self.book.names:
            if 'worksheets' in n and n.endswith('.xml'):
                if 'sparkline' in self.book.read(n):
                    spark = True
        if spark:
            got += 6
            notes.append('迷你图 OK')
        else:
            notes.append('无迷你图')
        return (6, '统计与迷你图', got, 14, notes)

    def r7(self):
        got, notes = 0, []
        if '数据可视' in self.book.sheet_names:
            got += 3
            notes.append('"数据可视"表 OK')
        else:
            notes.append('工作表=%s' % self.book.sheet_names)
        tables = [n for n in self.book.names if re.match(r'xl/pivotTables/pivotTable\d+\.xml$', n)]
        if not tables:
            return (7, '数据透视表', got, 12, notes + ['没有透视表'])
        x = self.book.read(tables[0])
        loc = re.search(r'<location[^>]*ref="([A-Z]+\d+)', x)
        if loc and loc.group(1).upper() == 'B3':
            got += 3
            notes.append('位置 B3 OK')
        else:
            notes.append('位置=%s' % (loc.group(1) if loc else '?'))
        if 'axis="axisRow"' in x:
            got += 2
            notes.append('行区域 OK')
        if 'axis="axisPage"' in x or '<pageField' in x:
            got += 2
            notes.append('筛选器 OK')
        df = re.findall(r'<dataField name="([^"]*)"', x)
        if len(df) >= 3:
            got += 2
            notes.append('三个值字段 OK')
        else:
            notes.append('值字段=%d 个' % len(df))
        return (7, '数据透视表', got, 12, notes)

    def r8(self):
        got, notes = 0, []
        charts = [n for n in self.book.names if re.match(r'xl/charts/chart\d+\.xml$', n)]
        if not charts:
            return (8, '数据透视图', 0, 12, ['没有图表'])
        x = self.book.read(charts[0])
        if 'radarChart' in x:
            got += 6
            notes.append('雷达图 OK')
        else:
            typ = [k for k in ('barChart', 'pieChart', 'lineChart') if k in x]
            notes.append('类型=%s' % (typ or '未知'))
        if re.search(r'legendPos val="b"', x):
            got += 3
            notes.append('图例底部 OK')
        else:
            notes.append('图例=%s' % (re.findall(r'legendPos val="([^"]+)"', x) or '无'))
        if '图表分析' in self.book.sheet_names:
            got += 3
            notes.append('"图表分析"表 OK')
        else:
            notes.append('无"图表分析"表')
        return (8, '数据透视图', got, 12, notes)


if __name__ == '__main__':
    sys.exit(run(ExcelGrader19, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Excel 2010 操作题题库', '19', '1结果.xlsx')))
