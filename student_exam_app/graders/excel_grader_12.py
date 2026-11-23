"""WPS 表格评分器 - 第12套（员工信息表）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import ExcelBook, Report, run, formula_has

S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'


class ExcelGrader12:
    def __init__(self, path):
        self.book = ExcelBook(path)

    def grade(self):
        report = Report('WPS 表格 第12套 · 员工信息表')
        for fn in (self.r1, self.r2, self.r3, self.r4,
                   self.r5, self.r6, self.r7, self.r8):
            report.add(*fn())
        return report

    def sheet(self, name):
        return self.book.sheet(name)

    def fmt(self, sheet, ref):
        return self.book.format_in(sheet.root, ref)

    def r1(self):
        names = self.book.sheet_names
        got, notes = 0, []
        if '基本信息' in names:
            got += 4
            notes.append('"基本信息" OK')
        else:
            notes.append('工作表=%s' % names)
        if '筛选' in names:
            got += 4
            notes.append('"筛选" OK')
        return (1, '工作表重命名', got, 8, notes)

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
        hit = [t for t in tables if t[0] == '员工信息表']
        if hit:
            got += 6
            notes.append('表名"员工信息表" OK')
            if 'Preset3' in hit[0][1] or 'Accent1' in hit[0][1]:
                got += 3
                notes.append('表样式 OK（%s）' % hit[0][1])
            else:
                notes.append('样式=%s' % hit[0][1])
            if hit[0][2].replace('$', '') == 'A1:M23':
                got += 3
                notes.append('范围 A1:M23 OK')
            else:
                notes.append('范围=%s' % hit[0][2])
        else:
            notes.append('未找到"员工信息表"（%s）' % [t[0] for t in tables][:3])
        return (2, '表格对象', got, 12, notes)

    def r3(self):
        got, notes = 0, []
        ws = self.sheet('基本信息')
        if ws is None:
            return (3, '平均/总计与样式', 0, 14, ['缺"基本信息"'])
        h = self.book.formula_in(ws.root, 'H23')
        if formula_has(h, 'AVERAGE'):
            got += 4
            notes.append('H23 AVERAGE OK')
        else:
            notes.append('H23=%r' % h)
        m = self.book.formula_in(ws.root, 'M23')
        if formula_has(m, 'SUM'):
            got += 3
            notes.append('M23 SUM OK')
        else:
            notes.append('M23=%r' % m)
        s1 = (self.fmt(ws, 'H23').get('style_name') or '')
        s2 = (self.fmt(ws, 'M23').get('style_name') or '')
        if s1 == '计算' and s2 == '计算':
            got += 3
            notes.append('单元格样式"计算" OK')
        else:
            notes.append('样式=%s/%s' % (s1, s2))
        mf = self.fmt(ws, 'M23').get('numfmt') or ''
        if '￥' in mf:
            got += 2
            notes.append('会计专用格式 OK')
        else:
            notes.append('营收格式=%s' % mf)
        hf = self.fmt(ws, 'H23').get('numfmt') or ''
        if hf.strip() in ('0_ ', '0', '0_') or hf.startswith('0'):
            got += 2
            notes.append('平均年龄保留0位 OK')
        else:
            notes.append('平均年龄格式=%s' % hf)
        return (3, '平均/总计与样式', got, 14, notes)

    def r4(self):
        got, notes = 0, []
        ws = self.sheet('基本信息')
        if ws is None:
            return (4, 'COUNTIFS 统计', 0, 12, ['缺"基本信息"'])
        refs = ['B28', 'C28', 'B29', 'C29', 'B30', 'C30', 'B31', 'C31']
        n = sum(1 for r in refs if formula_has(self.book.formula_in(ws.root, r), 'COUNTIF'))
        if n >= 8:
            got += 12
            notes.append('COUNTIFS 8格 OK')
        elif n >= 4:
            got += 8
            notes.append('COUNTIFS %d/8' % n)
        elif n:
            got += 4
            notes.append('COUNTIFS %d/8' % n)
        else:
            notes.append('B28=%r' % self.book.formula_in(ws.root, 'B28'))
        return (4, 'COUNTIFS 统计', got, 12, notes)

    def r5(self):
        got, notes = 0, []
        charts = [n for n in self.book.names if re.match(r'xl/charts/chart\d+\.xml$', n)]
        if not charts:
            return (5, '各部门人数图表', 0, 12, ['没有图表'])
        x = self.book.read(charts[0])
        if 'barChart' in x:
            got += 6
            notes.append('簇状柱形图 OK')
        else:
            typ = [k for k in ('pieChart', 'lineChart', 'radarChart', 'areaChart') if k in x]
            notes.append('图表类型=%s' % (typ or '未知'))
        texts = re.findall(r'<a:t>([^<]*)</a:t>', x)
        name_hit = any('各部门人数' in t for t in texts)
        if not name_hit:
            for dn in self.book.names:
                if 'drawings/drawing' in dn and dn.endswith('.xml'):
                    if '各部门人数' in self.book.read(dn):
                        name_hit = True
                        break
        if name_hit:
            got += 4
            notes.append('图表名称 OK')
        else:
            notes.append('标题/名称未找见')
        if re.search(r'<c:style val="\d+"', x):
            got += 2
            notes.append('图表样式已设')
        else:
            notes.append('未套图表样式')
        return (5, '各部门人数图表', got, 12, notes)

    def r6(self):
        got, notes = 0, []
        ws = self.sheet('基本信息')
        if ws is None:
            return (6, '营收前三名', 0, 12, ['缺"基本信息"'])
        p2 = self.book.formula_in(ws.root, 'P2')
        q2 = self.book.formula_in(ws.root, 'Q2')
        large_n = sum(1 for r in range(2, 5) if formula_has(self.book.formula_in(ws.root, 'P%d' % r), 'LARGE'))
        if large_n >= 3:
            got += 6
            notes.append('LARGE 前三名 OK')
        elif large_n:
            got += 3
            notes.append('LARGE %d/3' % large_n)
        else:
            notes.append('P2=%r' % p2)
        if formula_has(q2, 'INDEX') and formula_has(q2, 'MATCH'):
            got += 6
            notes.append('INDEX+MATCH 取名 OK')
        elif formula_has(q2, 'VLOOKUP', 'INDEX', 'LOOKUP'):
            got += 4
            notes.append('用查找函数取值')
        else:
            notes.append('Q2=%r' % q2)
        return (6, '营收前三名', got, 12, notes)

    def r7(self):
        got, notes = 0, []
        ws = self.sheet('筛选')
        if ws is None:
            return (7, '高级筛选', 0, 14, ['缺"筛选"工作表'])
        a2 = self.book.value_in(ws.root, 'A2')
        b2 = self.book.value_in(ws.root, 'B2')
        a3 = self.book.value_in(ws.root, 'A3')
        b3 = self.book.value_in(ws.root, 'B3')
        if a2 == '部门' and b2 == '婚否' and a3 == '销售部' and b3 == '未婚':
            got += 6
            notes.append('条件区域 A2:B3 OK')
        else:
            notes.append('条件=%s' % [a2, b2, a3, b3])
        ok, detail = self.book.advanced_filter_ok('筛选')
        if ok:
            got += 4
            notes.append('高级筛选(%s) OK' % detail)
        else:
            notes.append(detail)
        rgb = ''
        for n in ws.root.iter('{%s}tabColor' % S):
            rgb = (n.get('rgb') or '').upper()
            break
        if rgb.endswith('FF0000'):
            got += 4
            notes.append('标签红色 OK')
        else:
            notes.append('标签=%s' % rgb)
        return (7, '高级筛选', got, 14, notes)

    def r8(self):
        got, notes = 0, []
        tables = [n for n in self.book.names if re.match(r'xl/pivotTables/pivotTable\d+\.xml$', n)]
        if not tables:
            return (8, '数据透视表', 0, 16, ['没有透视表'])
        x = self.book.read(tables[0])
        loc = re.search(r'<location[^>]*ref="([A-Z]+\d+)', x)
        if loc and loc.group(1) == 'D3':
            got += 5
            notes.append('起始 D3 OK')
        else:
            notes.append('位置=%s' % (loc.group(1) if loc else '?'))
        rows = len(re.findall(r'axis="axisRow"', x))
        cols = len(re.findall(r'axis="axisCol"', x))
        if rows >= 2:
            got += 4
            notes.append('行区域2字段 OK')
        else:
            notes.append('行字段=%d' % rows)
        if cols >= 1:
            got += 4
            notes.append('列区域 OK')
        else:
            notes.append('列字段=%d' % cols)
        df = re.findall(r'<dataField name="([^"]*)"', x)
        if df and '计数' in df[0]:
            got += 3
            notes.append('计数汇总 OK（%s）' % df[0])
        elif df:
            notes.append('值=%s' % df[0])
        else:
            notes.append('无值字段')
        return (8, '数据透视表', got, 16, notes)


if __name__ == '__main__':
    sys.exit(run(ExcelGrader12, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Excel 2010 操作题题库', '12', '1结果.xlsx')))
