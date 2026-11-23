"""WPS 表格评分器 - 第13套（期末成绩分析）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import ExcelBook, Report, run, formula_has

S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'


class ExcelGrader13:
    def __init__(self, path):
        self.book = ExcelBook(path)

    def grade(self):
        report = Report('WPS 表格 第13套 · 期末成绩分析')
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
        ws = self.sheet('成绩')
        if ws is None:
            return (1, '标题行格式', 0, 10, ['缺"成绩"工作表'])
        merged = [m.get('ref') for m in ws.root.iter('{%s}mergeCell' % S)]
        if 'A1:L1' in merged:
            got += 4
            notes.append('A1:L1 合并 OK')
        else:
            notes.append('合并=%s' % merged[:3])
        if (self.fmt(ws, 'A1').get('style_name') or '') == '标题':
            got += 3
            notes.append('样式"标题" OK')
        else:
            notes.append('样式=%s' % self.fmt(ws, 'A1').get('style_name'))
        h = [r.get('ht') for r in ws.root.iter('{%s}row' % S) if r.get('r') == '1']
        if h and abs(float(h[0] or 0) - 30) < 0.1:
            got += 3
            notes.append('行高30 OK')
        else:
            notes.append('行高=%s' % (h[0] if h else '无'))
        return (1, '标题行格式', got, 10, notes)

    def r2(self):
        got, notes = 0, []
        ws = self.sheet('成绩')
        if ws is None:
            return (2, '班级列', 0, 12, ['缺"成绩"'])
        n = 0
        for r in range(3, 20):
            f = self.book.formula_in(ws.root, 'C%d' % r)
            if formula_has(f, 'RIGHT') and ('&' in (f or '') or 'CONCAT' in (f or '').upper()):
                n += 1
        vals = [self.book.value_in(ws.root, 'C%d' % r) for r in range(3, 20)]
        val_ok = sum(1 for v in vals if str(v).startswith('八年级') and str(v).endswith('班'))
        if n >= 2 and val_ok >= 17:
            got += 12
            notes.append('班级公式+17行结果 OK')
        elif val_ok >= 17:
            got += 9
            notes.append('班级结果全对（公式仅%d处）' % n)
        elif val_ok >= 8:
            got += 5
            notes.append('班级结果 %d/17' % val_ok)
        else:
            notes.append('C3=%r 结果%d/17' % (vals[0] if vals else '', val_ok))
        return (2, '班级列', got, 12, notes)

    def r3(self):
        got, notes = 0, []
        ws = self.sheet('成绩')
        if ws is None:
            return (3, '等级与规则表', 0, 14, ['缺"成绩"'])
        n = 0
        for r in range(3, 20):
            f = self.book.formula_in(ws.root, 'L%d' % r)
            if formula_has(f, 'IF', 'VLOOKUP', 'LOOKUP'):
                n += 1
        vals = [self.book.value_in(ws.root, 'L%d' % r) for r in range(3, 20)]
        val_ok = sum(1 for v in vals if str(v).strip() in ('A', 'B', 'C', 'D'))
        if n >= 2 and val_ok >= 17:
            got += 8
            notes.append('等级公式+17行结果 OK')
        elif val_ok >= 17:
            got += 6
            notes.append('等级结果全对（公式仅%d处）' % n)
        elif val_ok >= 8:
            got += 3
            notes.append('等级结果 %d/17' % val_ok)
        else:
            notes.append('L3=%r 结果%d/17' % (self.book.formula_in(ws.root, 'L3'), val_ok))
        hidden = False
        for sh in self.book.sheets:
            if sh.name == '等级计算规则' and sh.state == 'hidden':
                hidden = True
        if hidden:
            got += 6
            notes.append('规则表已隐藏 OK')
        else:
            notes.append('规则表未隐藏')
        return (3, '等级与规则表', got, 14, notes)

    def r4(self):
        got, notes = 0, []
        ws = self.sheet('成绩')
        if ws is None:
            return (4, '条件格式', 0, 14, ['缺"成绩"'])
        ranges = []
        for cf in ws.root.iter('{%s}conditionalFormatting' % S):
            for rl in cf:
                if rl.get('type') == 'aboveAverage':
                    ranges.append(cf.get('sqref', ''))
        if len(ranges) >= 8:
            got += 8
            notes.append('8科高于平均 OK')
        elif ranges:
            got += 4
            notes.append('高于平均 %d/8' % len(ranges))
        else:
            notes.append('无条件格式')
        styles = self.book.read('xl/styles.xml') if 'xl/styles.xml' in self.book.names else ''
        m = re.search(r'<dxfs[^>]*>(.*?)</dxfs>', styles, re.S)
        dxf = m.group(1) if m else ''
        has_fill = bool(re.search(r'(B4C6E7|9DC3E6|DDEBF7|BDD7EE)', dxf, re.I)) or ('bgColor theme=' in dxf)
        has_font = bool(re.search(r'(C00000|9C0006|FF0000)', dxf, re.I))
        if has_fill and has_font:
            got += 6
            notes.append('浅蓝底+深红字 OK')
        elif has_fill or has_font:
            got += 3
            notes.append('填充或字色只中一个')
        else:
            notes.append('dxf 样式未识别')
        return (4, '条件格式', got, 14, notes)

    def r5(self):
        got, notes = 0, []
        wa = self.sheet('成绩分析')
        if wa is None:
            return (5, '成绩分析公式', 0, 18, ['缺"成绩分析"'])
        checks = [('B2', 'AVERAGE'), ('B3', 'MAX'), ('B4', 'MIN'), ('B5', 'COUNTIF'), ('B6', 'COUNTIF')]
        hit = 0
        for ref, fn in checks:
            if formula_has(self.book.formula_in(wa.root, ref), fn):
                hit += 1
        if hit >= 5:
            got += 18
            notes.append('平均/最高/最低/及格/优秀 全 OK')
        elif hit:
            got += hit * 3
            notes.append('公式 %d/5' % hit)
        else:
            notes.append('B2=%r' % self.book.formula_in(wa.root, 'B2'))
        return (5, '成绩分析公式', got, 18, notes)

    def r6(self):
        got, notes = 0, []
        tables = [n for n in self.book.names if re.match(r'xl/pivotTables/pivotTable\d+\.xml$', n)]
        if not tables:
            return (6, '数据透视表', 0, 14, ['没有透视表'])
        x = self.book.read(tables[0])
        loc = re.search(r'<location[^>]*ref="([A-Z]+\d+)', x)
        if loc and loc.group(1) == 'A3':
            got += 4
            notes.append('位置 A3 OK')
        else:
            notes.append('位置=%s' % (loc.group(1) if loc else '?'))
        rows = len(re.findall(r'axis="axisRow"', x))
        cols = len(re.findall(r'axis="axisCol"', x))
        if rows >= 1 and cols >= 1:
            got += 5
            notes.append('行1列1 OK')
        else:
            notes.append('行%d列%d' % (rows, cols))
        df = re.findall(r'<dataField name="([^"]*)"', x)
        if df and '计数' in df[0] and '学号' in df[0]:
            got += 5
            notes.append('学号计数 OK')
        elif df and '计数' in df[0]:
            got += 3
            notes.append('计数值=%s' % df[0])
        else:
            notes.append('值=%s' % (df or '无'))
        return (6, '数据透视表', got, 14, notes)

    def r7(self):
        got, notes = 0, []
        charts = [n for n in self.book.names if re.match(r'xl/charts/chart\d+\.xml$', n)]
        if not charts:
            return (7, '数据透视图', 0, 10, ['没有图表'])
        x = self.book.read(charts[0])
        if 'barChart' in x:
            got += 4
            notes.append('簇状柱形图 OK')
        else:
            notes.append('类型非柱形图')
        if 'errBars' in x:
            got += 3
            notes.append('误差线 OK')
        else:
            notes.append('无误差线')
        name_hit = False
        for dn in self.book.names:
            if 'drawings/drawing' in dn and dn.endswith('.xml'):
                if '各等级人数' in self.book.read(dn):
                    name_hit = True
                    break
        texts = re.findall(r'<a:t>([^<]*)</a:t>', x)
        if name_hit or any('各等级人数' in t for t in texts):
            got += 3
            notes.append('图表名称 OK')
        else:
            notes.append('图表名称未找见')
        return (7, '数据透视图', got, 10, notes)

    def r8(self):
        got, notes = 0, []
        ws = self.sheet('成绩')
        if ws is None:
            return (8, '页面设置', 0, 8, ['缺"成绩"'])
        ps = ws.root.find('{%s}pageSetup' % S)
        if ps is not None and ps.get('orientation') == 'landscape':
            got += 3
            notes.append('横向 OK')
        else:
            notes.append('方向=%s' % (ps.get('orientation') if ps is not None else '无'))
        if ps is not None and (ps.get('paperSize') or '') == '8':
            got += 2
            notes.append('A3 OK')
        else:
            notes.append('纸张=%s' % (ps.get('paperSize') if ps is not None else '无'))
        foot = ''
        for f in ws.root.iter('{%s}oddFooter' % S):
            foot = f.text or ''
            break
        if '第' in foot and '&P' in foot and '&N' in foot:
            got += 3
            notes.append('页脚"第X页共Y页" OK')
        else:
            notes.append('页脚=%r' % foot)
        return (8, '页面设置', got, 8, notes)


if __name__ == '__main__':
    sys.exit(run(ExcelGrader13, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Excel 2010 操作题题库', '13', '1结果.xlsx')))
