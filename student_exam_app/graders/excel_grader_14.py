"""WPS 表格评分器 - 第14套（客户购买登记）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import ExcelBook, Report, run, formula_has

S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'


class ExcelGrader14:
    def __init__(self, path):
        self.book = ExcelBook(path)

    def grade(self):
        report = Report('WPS 表格 第14套 · 客户购买登记')
        for fn in (self.r1, self.r2, self.r3, self.r4, self.r5,
                   self.r6, self.r7, self.r8, self.r9, self.r10):
            report.add(*fn())
        return report

    def sheet(self, name):
        return self.book.sheet(name)

    def fmt(self, sheet, ref):
        return self.book.format_in(sheet.root, ref)

    def r1(self):
        got, notes = 0, []
        if '登记表' in self.book.sheet_names:
            got += 4
            notes.append('"登记表" OK')
        else:
            notes.append('工作表=%s' % self.book.sheet_names)
        ws = self.sheet('登记表')
        if ws is not None:
            rgb = ''
            for n in ws.root.iter('{%s}tabColor' % S):
                rgb = (n.get('rgb') or '').upper()
                break
            if rgb.endswith('0070C0') or rgb.endswith('0000FF'):
                got += 4
                notes.append('标签蓝色 OK')
            else:
                notes.append('标签=%s' % rgb)
        return (1, '工作表与标签', got, 8, notes)

    def r2(self):
        got, notes = 0, []
        ws = self.sheet('登记表')
        if ws is None:
            return (2, '隐藏首行与标题', 0, 10, ['缺"登记表"'])
        first = None
        for r in ws.root.iter('{%s}row' % S):
            if r.get('r') == '1':
                first = r
                break
        if first is not None and first.get('hidden') == '1':
            got += 4
            notes.append('首行隐藏 OK')
        else:
            notes.append('首行 hidden=%s' % (first.get('hidden') if first is not None else '无'))
        f = self.fmt(ws, 'C3')
        font = f.get('font', {})
        fill = (f.get('fill') or {}).get('fg') or {}
        if font.get('name') == '微软雅黑' and font.get('size') == '22':
            got += 2
            notes.append('微软雅黑22 OK')
        else:
            notes.append('字体=%s/%s' % (font.get('name'), font.get('size')))
        if (fill.get('rgb') or '').upper().endswith('4DC3BC'):
            got += 2
            notes.append('填充4DC3BC OK')
        else:
            notes.append('填充=%s' % (fill.get('rgb') or fill.get('theme')))
        if str(self.book.value_in(ws.root, 'C3') or '').startswith('客户购买登记表'):
            got += 2
            notes.append('标题文字 OK')
        else:
            notes.append('C3=%r' % self.book.value_in(ws.root, 'C3'))
        return (2, '隐藏首行与标题', got, 10, notes)

    def r3(self):
        got, notes = 0, []
        ws = self.sheet('登记表')
        if ws is None:
            return (3, '日期标注星期', 0, 8, ['缺"登记表"'])
        n = 0
        for r in range(6, 35):
            f = self.book.formula_in(ws.root, 'L%d' % r)
            if formula_has(f, 'TEXT', 'WEEKDAY'):
                n += 1
        if n >= 25:
            got += 8
            notes.append('TEXT/WEEKDAY OK（%d行）' % n)
        elif n:
            got += 5
            notes.append('公式 %d/29' % n)
        else:
            nf = self.book.format_in(ws.root, 'L6').get('numfmt') or ''
            cnt = 0
            for r in range(6, 35):
                f2 = self.book.format_in(ws.root, 'L%d' % r).get('numfmt') or ''
                if 'aaaa' in f2 or 'ddd' in f2 or '星期' in str(self.book.value_in(ws.root, 'L%d' % r) or ''):
                    cnt += 1
            if 'aaaa' in nf or 'ddd' in nf or cnt >= 20:
                got += 8
                notes.append('星期格式 OK（numfmt=%s，%d行）' % (nf, cnt))
            else:
                notes.append('L6 numfmt=%s' % nf)
        return (3, '日期标注星期', got, 8, notes)

    def r4(self):
        got, notes = 0, []
        ws = self.sheet('登记表')
        if ws is None:
            return (4, '图标集', 0, 10, ['缺"登记表"'])
        x = self.book.read(ws.part) if hasattr(ws, 'part') else ''
        if not x:
            for n in self.book.names:
                if 'worksheets' in n and n.endswith('.xml'):
                    c = self.book.read(n)
                    if 'iconSet' in c and ('3Stars' in c or '3Traffic' in c):
                        x = c
                        break
        if '3Stars' in x:
            got += 8
            notes.append('3个星形图标集 OK')
        elif 'iconSet' in x:
            got += 4
            notes.append('有图标集但非3星形')
        else:
            notes.append('无图标集')
        if 'showValue="0"' in x or 'showValue="false"' in x:
            got += 2
            notes.append('仅显示图标 OK')
        else:
            notes.append('未设仅显示图标')
        return (4, '图标集', got, 10, notes)

    def r5(self):
        got, notes = 0, []
        comments = [n for n in self.book.names if 'comment' in n.lower() and n.endswith('.xml')]
        if comments:
            c = self.book.read(comments[0])
            if '优惠金额' in c:
                got += 5
                notes.append('U5 批注 OK')
            else:
                got += 3
                notes.append('有批注但内容不符')
        else:
            notes.append('无批注')
        ws = self.sheet('登记表')
        if ws is not None:
            n = sum(1 for r in range(6, 35) if formula_has(self.book.formula_in(ws.root, 'U%d' % r), 'IF', 'IFS'))
            vals = [str(self.book.value_in(ws.root, 'U%d' % r) or '') for r in range(6, 35)]
            val_ok = sum(1 for v in vals if v in ('普通', 'VIP', 'SVIP'))
            if (n >= 2 and val_ok >= 20) or n >= 20:
                got += 5
                notes.append('备注列 OK（公式%d行/结果%d行）' % (n, val_ok))
            elif val_ok >= 10:
                got += 3
                notes.append('备注结果 %d/29' % val_ok)
            else:
                notes.append('备注列无公式（结果%d）' % val_ok)
        return (5, '批注与备注', got, 10, notes)

    def r6(self):
        got, notes = 0, []
        ws = self.sheet('登记表')
        if ws is None:
            return (6, '购买次数与图表', 0, 12, ['缺"登记表"'])
        n = 0
        for col in ('I', 'H'):
            n = sum(1 for r in range(7, 10) if formula_has(self.book.formula_in(ws.root, '%s%d' % (col, r)), 'COUNTIF'))
            if n:
                break
        if n >= 3:
            got += 4
            notes.append('购买次数 COUNTIF OK')
        elif n:
            got += 2
            notes.append('COUNTIF %d/3' % n)
        else:
            notes.append('I7=%r' % self.book.formula_in(ws.root, 'I7'))
        charts = [x for x in self.book.names if re.match(r'xl/charts/chart\d+\.xml$', x)]
        if not charts:
            return (6, '购买次数与图表', got, 12, notes + ['无图表'])
        c = self.book.read(charts[0])
        if 'barChart' in c:
            got += 4
            notes.append('簇状柱形图 OK')
        else:
            notes.append('类型非柱形图')
        if 'legend' not in c or 'delete' in c:
            got += 2
            notes.append('无图例 OK')
        else:
            notes.append('仍有图例')
        if '<c:autoTitleDeleted val="1"' in c or 'autoTitleDeleted val="1"' in c:
            got += 2
            notes.append('无标题 OK')
        else:
            notes.append('标题未删')
        return (6, '购买次数与图表', got, 12, notes)

    def r7(self):
        got, notes = 0, []
        charts = [x for x in self.book.names if re.match(r'xl/charts/chart\d+\.xml$', x)]
        if not charts:
            return (7, '图表大小位置', 0, 8, ['无图表'])
        for n in self.book.names:
            if 'drawings/drawing' in n and n.endswith('.xml'):
                d = self.book.read(n)
                m = re.search(r'<[a-z0-9]+:ext cx="(\d+)" cy="(\d+)"', d)
                if m:
                    w = int(m.group(1)) / 360000
                    h = int(m.group(2)) / 360000
                    if abs(w - 9.92) < 1.0 and abs(h - 6.68) < 1.0:
                        got += 5
                        notes.append('大小 9.92×6.68cm OK')
                    else:
                        notes.append('大小 %.2f×%.2fcm' % (w, h))
                two = re.search(r'<xdr:from>.*?<xdr:col>(\d+)</xdr:col>.*?<xdr:row>(\d+)</xdr:row>', d, re.S)
                if two:
                    col, row = int(two.group(1)), int(two.group(2))
                    if col == 2 and row == 9:
                        got += 3
                        notes.append('位置 C10 OK')
                    else:
                        notes.append('位置 列%d行%d' % (col + 1, row + 1))
                break
        return (7, '图表大小位置', got, 8, notes)

    def r8(self):
        got, notes = 0, []
        ws = self.sheet('登记表')
        if ws is None:
            return (8, '金额计算', 0, 12, ['缺"登记表"'])
        f25 = self.book.formula_in(ws.root, 'F25')
        f27 = self.book.formula_in(ws.root, 'F27')
        f33 = self.book.formula_in(ws.root, 'F33')
        if formula_has(f25, 'SUM', 'SUMPRODUCT'):
            got += 4
            notes.append('总销售金额 OK')
        else:
            notes.append('F25=%r' % f25)
        if formula_has(f27, 'SUM', 'SUMPRODUCT'):
            got += 4
            notes.append('总优惠金额 OK')
        else:
            notes.append('F27=%r' % f27)
        if formula_has(f33, 'SUMIFS', 'SUMPRODUCT'):
            got += 4
            notes.append('时段销售金额 OK')
        else:
            notes.append('F33=%r' % f33)
        return (8, '金额计算', got, 12, notes)

    def r9(self):
        got, notes = 0, []
        tables = [n for n in self.book.names if re.match(r'xl/pivotTables/pivotTable\d+\.xml$', n)]
        if not tables:
            return (9, '数据透视表', 0, 14, ['无透视表'])
        x = self.book.read(tables[0])
        loc = re.search(r'<location[^>]*ref="([A-Z]+\d+)', x)
        if loc and loc.group(1) == 'A3':
            got += 4
            notes.append('位置 A3 OK')
        else:
            notes.append('位置=%s' % (loc.group(1) if loc else '?'))
        if 'axis="axisRow"' in x and 'axis="axisCol"' in x:
            got += 4
            notes.append('行列区域 OK')
        else:
            notes.append('行列未设')
        df = re.findall(r'<dataField name="([^"]*)"', x)
        if df and '客户名称' in df[0]:
            got += 3
            notes.append('值=客户名称 OK')
        else:
            notes.append('值=%s' % (df or '无'))
        cache = [n for n in self.book.names if 'pivotCacheDefinition' in n]
        grouped = False
        for n in cache:
            if 'group' in self.book.read(n).lower():
                grouped = True
        if grouped:
            got += 3
            notes.append('日期按月组合 OK')
        else:
            notes.append('无日期组合')
        return (9, '数据透视表', got, 14, notes)

    def r10(self):
        got, notes = 0, []
        wb = self.book.read('xl/workbook.xml')
        area = re.search(r'name="_xlnm\.Print_Area"[^>]*>([^<]*)<', wb)
        if area and 'C$2:$U$34' in area.group(1).replace(' ', ''):
            got += 4
            notes.append('打印区域 C2:U34 OK')
        elif area:
            got += 2
            notes.append('打印区域=%s' % area.group(1))
        else:
            notes.append('无打印区域')
        ws = self.sheet('登记表')
        if ws is not None:
            ps = ws.root.find('{%s}pageSetup' % S)
            if ps is not None and ps.get('orientation') == 'landscape' and (ps.get('paperSize') or '') == '8':
                got += 2
                notes.append('横向A3 OK')
            else:
                notes.append('页面=%s' % (dict(ps.attrib) if ps is not None else '无'))
            pm = ws.root.find('{%s}pageMargins' % S)
            if pm is not None:
                try:
                    v = {k: float(pm.get(k) or 0) * 2.54 for k in ('top', 'bottom', 'left', 'right')}
                    if (abs(v['top'] - 2) < 0.15 and abs(v['bottom'] - 3) < 0.15
                            and abs(v['left'] - 1.5) < 0.15 and abs(v['right'] - 2.5) < 0.15):
                        got += 2
                        notes.append('页边距 2/3/1.5/2.5 OK')
                    else:
                        notes.append('页边距 %.1f/%.1f/%.1f/%.1f' % (v['top'], v['bottom'], v['left'], v['right']))
                except ValueError:
                    notes.append('页边距读取失败')
        return (10, '打印与页面', got, 8, notes)


if __name__ == '__main__':
    sys.exit(run(ExcelGrader14, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Excel 2010 操作题题库', '14', '1结果.xlsx')))
