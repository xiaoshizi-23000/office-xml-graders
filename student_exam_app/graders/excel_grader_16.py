"""WPS 表格评分器 - 第16套（员工工资表）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import ExcelBook, Report, run, formula_has

S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'


class ExcelGrader16:
    def __init__(self, path):
        self.book = ExcelBook(path)

    def grade(self):
        report = Report('WPS 表格 第16套 · 员工工资表')
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
        ws = self.sheet('员工信息')
        if ws is None:
            return (1, '标题行', 0, 12, ['缺"员工信息"'])
        merged = [m.get('ref') for m in ws.root.iter('{%s}mergeCell' % S)]
        if 'A1:L1' in merged:
            got += 4
            notes.append('A1:L1 合并 OK')
        else:
            notes.append('合并=%s' % merged[:2])
        t = self.book.value_in(ws.root, 'A1')
        if str(t or '').startswith('12月员工工资表'):
            got += 3
            notes.append('标题文字 OK')
        else:
            notes.append('A1=%r' % t)
        f = self.fmt(ws, 'A1')['font']
        if f.get('name') == '黑体' and f.get('size') == '20' and f.get('bold'):
            got += 5
            notes.append('黑体20加粗 OK')
        else:
            notes.append('字体=%s/%s/%s' % (f.get('name'), f.get('size'), f.get('bold')))
        return (1, '标题行', got, 12, notes)

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
        hit = [t for t in tables if t[0] == '工资表']
        if hit:
            got += 6
            notes.append('表名"工资表" OK')
            if 'Preset3' in hit[0][1]:
                got += 4
                notes.append('黑色表样式3 OK（%s）' % hit[0][1])
            else:
                notes.append('样式=%s' % hit[0][1])
            if hit[0][2].replace('$', '') == 'A2:L31':
                got += 2
                notes.append('范围 A2:L31 OK')
            else:
                notes.append('范围=%s' % hit[0][2])
        else:
            notes.append('未找到"工资表"（%s）' % [t[0] for t in tables][:3])
        return (2, '表格对象', got, 12, notes)

    def r3(self):
        got, notes = 0, []
        ws = self.sheet('员工信息')
        if ws is None:
            return (3, '部门 VLOOKUP', 0, 12, ['缺"员工信息"'])
        f = self.book.formula_in(ws.root, 'F3')
        n = sum(1 for r in range(3, 32)
                if formula_has(self.book.formula_in(ws.root, 'F%d' % r), 'VLOOKUP'))
        if formula_has(f, 'VLOOKUP') and n >= 25:
            got += 12
            notes.append('VLOOKUP 部门 OK（%d行）' % n)
        elif formula_has(f, 'VLOOKUP'):
            got += 8
            notes.append('VLOOKUP 有了（%d行）' % n)
        else:
            v = self.book.value_in(ws.root, 'F3')
            if v:
                got += 4
                notes.append('部门有值 %s（无公式）' % v)
            else:
                notes.append('F3=%r' % v)
        return (3, '部门 VLOOKUP', got, 12, notes)

    def r4(self):
        got, notes = 0, []
        ws = self.sheet('员工信息')
        if ws is None:
            return (4, '等级 IF', 0, 12, ['缺"员工信息"'])
        f = self.book.formula_in(ws.root, 'I3')
        n = sum(1 for r in range(3, 32)
                if formula_has(self.book.formula_in(ws.root, 'I%d' % r), 'IF'))
        vals = [str(self.book.value_in(ws.root, 'I%d' % r) or '') for r in range(3, 32)]
        val_ok = sum(1 for v in vals if v in ('A', 'B', 'C', 'D'))
        if formula_has(f, 'IF') and val_ok >= 25:
            got += 12
            notes.append('等级 IF+%d行结果 OK' % val_ok)
        elif val_ok >= 25:
            got += 9
            notes.append('等级结果全对（公式仅%d处）' % n)
        elif formula_has(f, 'IF'):
            got += 6
            notes.append('IF 有了（结果%d行）' % val_ok)
        else:
            notes.append('I3=%r 结果%d行' % (f or '', val_ok))
        return (4, '等级 IF', got, 12, notes)

    def r5(self):
        got, notes = 0, []
        ws = self.sheet('员工信息')
        if ws is None:
            return (5, '奖金与月薪', 0, 18, ['缺"员工信息"'])
        k = self.book.formula_in(ws.root, 'K3')
        if formula_has(k, 'IF', 'IFS', 'LOOKUP'):
            got += 5
            notes.append('奖金公式 OK')
        else:
            notes.append('K3=%r' % k)
        l = self.book.formula_in(ws.root, 'L3')
        if formula_has(l, '3000') and ('320' in (l or '')):
            got += 5
            notes.append('月薪公式 OK')
        elif formula_has(l, '3000', '320') or (l and '+' in l):
            got += 3
            notes.append('月薪公式近似（%s）' % (l or '')[:40])
        else:
            notes.append('L3=%r' % l)
        lf = self.fmt(ws, 'L3').get('numfmt') or ''
        if '￥' in lf or '0.00' in lf:
            got += 3
            notes.append('月薪货币格式 OK')
        else:
            notes.append('月薪格式=%s' % lf)
        rngs = []
        for cf in ws.root.iter('{%s}conditionalFormatting' % S):
            for r in cf:
                if r.get('type') == 'dataBar':
                    rngs.append(cf.get('sqref', ''))
        if any(x.upper().startswith('K') for x in rngs):
            got += 5
            notes.append('橙色数据条 OK（%s）' % rngs[0])
        elif rngs:
            got += 3
            notes.append('数据条位置=%s' % rngs[0])
        else:
            notes.append('无数据条')
        return (5, '奖金与月薪', got, 18, notes)

    def r6(self):
        got, notes = 0, []
        if '数据表' not in self.book.sheet_names:
            return (6, '数据透视表', 0, 12, ['没有"数据表"工作表'])
        got += 3
        notes.append('"数据表" OK')
        tables = [n for n in self.book.names if re.match(r'xl/pivotTables/pivotTable\d+\.xml$', n)]
        if not tables:
            return (6, '数据透视表', got, 12, notes + ['没有透视表'])
        x = self.book.read(tables[0])
        loc = re.search(r'<location[^>]*ref="([A-Z]+\d+)', x)
        if loc and loc.group(1).upper() == 'C2':
            got += 4
            notes.append('位置 C2 OK')
        else:
            notes.append('位置=%s' % (loc.group(1) if loc else '?'))
        if 'axis="axisRow"' in x and 'axis="axisCol"' in x:
            got += 3
            notes.append('行列区域 OK')
        df = re.findall(r'<dataField name="([^"]*)"', x)
        if df and '月薪' in df[0]:
            got += 2
            notes.append('值=月薪 OK')
        else:
            notes.append('值=%s' % (df or '无'))
        return (6, '数据透视表', got, 12, notes)

    def r7(self):
        got, notes = 0, []
        charts = [n for n in self.book.names if re.match(r'xl/charts/chart\d+\.xml$', n)]
        if not charts:
            return (7, '数据透视图', 0, 12, ['没有图表'])
        x = self.book.read(charts[0])
        if 'pie3DChart' in x:
            got += 7
            notes.append('三维饼图 OK')
        elif 'pieChart' in x:
            got += 4
            notes.append('饼图但非三维')
        else:
            notes.append('类型非饼图')
        if re.search(r'<c:showPercent val="1"', x):
            got += 3
            notes.append('百分比标签 OK')
        if re.search(r'<c:showCatName val="1"', x):
            got += 2
            notes.append('类别名称 OK')
        return (7, '数据透视图', got, 12, notes)

    def r8(self):
        got, notes = 0, []
        ws = self.sheet('员工信息')
        if ws is None:
            return (8, '页面设置', 0, 10, ['缺"员工信息"'])
        ps = ws.root.find('{%s}pageSetup' % S)
        if ps is not None and ps.get('orientation') == 'landscape':
            got += 3
            notes.append('横向 OK')
        else:
            notes.append('方向=%s' % (ps.get('orientation') if ps is not None else '无'))
        po = ws.root.find('{%s}printOptions' % S)
        if po is not None and po.get('horizontalCentered') == '1' and po.get('verticalCentered') == '1':
            got += 4
            notes.append('水平垂直居中 OK')
        else:
            notes.append('未设居中打印')
        foot = ''
        for f in ws.root.iter('{%s}oddFooter' % S):
            foot = f.text or ''
            break
        if '共' in foot or ('&P' in foot and '&N' in foot):
            got += 3
            notes.append('页脚"第X页共Y页" OK')
        else:
            notes.append('页脚=%r' % foot)
        return (8, '页面设置', got, 10, notes)


if __name__ == '__main__':
    sys.exit(run(ExcelGrader16, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Excel 2010 操作题题库', '16', '1结果.xlsx')))
