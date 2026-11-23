"""WPS 表格评分器 - 第15套（亚运会金牌榜）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import ExcelBook, Report, run, formula_has

S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'


class ExcelGrader15:
    def __init__(self, path):
        self.book = ExcelBook(path)

    def grade(self):
        report = Report('WPS 表格 第15套 · 亚运会金牌榜')
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
        ws = self.sheet('奖牌表') or self.sheet('Sheet1')
        if ws is None:
            return (1, '导入与标题', 0, 18, ['缺工作表'])
        merged = [m.get('ref') for m in ws.root.iter('{%s}mergeCell' % S)]
        if 'B2:F2' in merged:
            got += 6
            notes.append('B2:F2 合并 OK')
        else:
            notes.append('合并=%s' % merged[:2])
        t = self.book.value_in(ws.root, 'B2')
        if str(t or '').startswith('2021多哈'):
            got += 4
            notes.append('标题文字 OK')
        else:
            notes.append('B2=%r' % t)
        f = self.fmt(ws, 'B2')
        font = f.get('font', {})
        if font.get('name') == '黑体' and font.get('size') == '18':
            got += 3
            notes.append('黑体18 OK')
        else:
            notes.append('字体=%s/%s' % (font.get('name'), font.get('size')))
        h = [r.get('ht') for r in ws.root.iter('{%s}row' % S) if r.get('r') == '2']
        if h and abs(float(h[0] or 0) - 22.5) < 0.9:
            got += 5
            notes.append('行高22.5 OK')
        else:
            notes.append('行高=%s' % (h[0] if h else '无'))
        return (1, '导入与标题', got, 18, notes)

    def r2(self):
        got, notes = 0, []
        if '奖牌表' in self.book.sheet_names:
            got += 5
            notes.append('"奖牌表" OK')
        else:
            notes.append('工作表=%s' % self.book.sheet_names)
        ws = self.sheet('奖牌表')
        if ws is None:
            return (2, '边框与填充', got, 14, notes)
        purple = False
        for node in ws.cells().values():
            fm = self.book.styles.get(int(node.get('s', '0') or 0))
            for _k, v in (fm.get('border') or {}).items():
                if v.get('style') and (v.get('color') or {}).get('rgb', '').upper().endswith(('7030A0', '8064A2')):
                    purple = True
        if purple:
            got += 4
            notes.append('紫色边框 OK')
        else:
            notes.append('未找到紫色边框')
        f3 = (self.fmt(ws, 'B3').get('fill') or {}).get('fg') or {}
        if (f3.get('rgb') or '').upper().endswith('FFFF00') or str(f3.get('indexed')) in ('13', '5') or 'yellow' in str(f3).lower():
            got += 3
            notes.append('表头黄色 OK')
        else:
            notes.append('B3填充=%s' % f3)
        f4 = (self.fmt(ws, 'B4').get('fill') or {}).get('fg') or {}
        if f4 and (f4.get('rgb') or '').upper() not in ('', 'FFFFFFFF'):
            got += 2
            notes.append('数据区浅蓝 OK（%s）' % (f4.get('rgb') or f4.get('theme')))
        else:
            notes.append('B4填充=%s' % f4)
        return (2, '边框与填充', got, 14, notes)

    def r3(self):
        got, notes = 0, []
        ws = self.sheet('奖牌表')
        if ws is None:
            return (3, '奖牌总数与条件格式', 0, 14, ['缺"奖牌表"'])
        f = self.book.formula_in(ws.root, 'F4')
        if formula_has(f, 'SUM') and ('C4' in (f or '') and 'E4' in (f or '')):
            got += 7
            notes.append('奖牌总数公式 OK')
        else:
            v = self.book.value_in(ws.root, 'F4')
            if v not in (None, ''):
                got += 4
                notes.append('有值 %s（公式缺失）' % v)
            else:
                notes.append('F4=%r' % v)
        rules = [(cf.get('sqref', ''), r.get('type')) for cf in ws.root.iter('{%s}conditionalFormatting' % S) for r in cf]
        if rules:
            got += 4
            notes.append('条件格式 OK（%s）' % rules[0][0])
        else:
            notes.append('无条件格式')
        styles = self.book.read('xl/styles.xml') if 'xl/styles.xml' in self.book.names else ''
        m = re.search(r'<dxfs[^>]*>(.*?)</dxfs>', styles, re.S)
        if m and ('FF0000' in m.group(1).upper() or 'red' in m.group(1).lower()):
            got += 3
            notes.append('红底白字 OK')
        else:
            notes.append('dxf 未匹配红底')
        return (3, '奖牌总数与条件格式', got, 14, notes)

    def r4(self):
        got, notes = 0, []
        charts = [n for n in self.book.names if re.match(r'xl/charts/chart\d+\.xml$', n)]
        if not charts:
            return (4, '雷达图', 0, 12, ['没有图表'])
        x = self.book.read(charts[0])
        if 'radarChart' in x:
            got += 6
            notes.append('雷达图 OK')
        else:
            typ = [k for k in ('barChart', 'pieChart', 'lineChart', 'scatterChart') if k in x]
            notes.append('类型=%s' % (typ or '未知'))
        texts = re.findall(r'<a:t>([^<]*)</a:t>', x)
        if any('奖牌榜' in t for t in texts):
            got += 3
            notes.append('标题 OK')
        else:
            notes.append('标题=%s' % texts[:2])
        if re.search(r'legendPos val="b"', x):
            got += 3
            notes.append('图例底部 OK')
        else:
            notes.append('图例=%s' % (re.findall(r'legendPos val="([^"]+)"', x) or '无'))
        return (4, '雷达图', got, 12, notes)

    def r5(self):
        got, notes = 0, []
        tables = [n for n in self.book.names if re.match(r'xl/pivotTables/pivotTable\d+\.xml$', n)]
        if not tables:
            return (5, '数据透视表', 0, 12, ['没有透视表'])
        x = self.book.read(tables[0])
        loc = re.search(r'<location[^>]*ref="([A-Z]+\d+)', x)
        if loc and loc.group(1).upper() == 'H24':
            got += 5
            notes.append('位置 H24 OK')
        else:
            notes.append('位置=%s' % (loc.group(1) if loc else '?'))
        if 'axis="axisRow"' in x:
            got += 3
            notes.append('行区域 OK')
        df = re.findall(r'<dataField name="([^"]*)"', x)
        if df and '奖牌总数' in df[0]:
            got += 4
            notes.append('值=奖牌总数 OK')
        else:
            notes.append('值=%s' % (df or '无'))
        return (5, '数据透视表', got, 12, notes)

    def r6(self):
        got, notes = 0, []
        ws = self.sheet('名次')
        if ws is None:
            return (6, '名次表', 0, 10, ['缺"名次"工作表'])
        import re
        rgb = ''
        for n in ws.root.iter('{%s}tabColor' % S):
            rgb = (n.get('rgb') or '').upper() or ('theme:' + (n.get('theme') or ''))
            break
        if rgb and (rgb.endswith('C00000') or rgb.startswith('theme')):
            got += 4
            notes.append('标签色 OK（%s）' % rgb)
        else:
            notes.append('标签=%s' % rgb)
        n = 0
        for ref in ('B3', 'C3', 'D3'):
            f = self.book.formula_in(ws.root, ref)
            if formula_has(f, 'LARGE', 'INDEX', 'MATCH', 'VLOOKUP'):
                n += 1
        if n >= 3:
            got += 6
            notes.append('名次公式 OK')
        elif n:
            got += 3
            notes.append('名次公式 %d/3' % n)
        else:
            notes.append('B3=%r' % self.book.formula_in(ws.root, 'B3'))
        return (6, '名次表', got, 10, notes)

    def r7(self):
        got, notes = 0, []
        ws = self.sheet('筛选')
        if ws is None:
            return (7, '筛选工作表', 0, 12, ['没有"筛选"工作表'])
        got += 3
        notes.append('"筛选"表 OK')
        v = self.book.value_in(ws.root, 'B3')
        if v not in (None, ''):
            got += 3
            notes.append('数据已粘贴（B3=%s）' % v)
        else:
            notes.append('B3 为空')
        conds = []
        for st in ws.root.iter('{%s}sortState' % S):
            for sc in st.iter('{%s}sortCondition' % S):
                conds.append((sc.get('ref', ''), sc.get('descending')))
        if conds and (conds[0][0].upper().startswith('B') or len(conds[0][0]) > 1) and conds[0][1] != '1':
            got += 3
            notes.append('升序排序 OK（%s）' % conds[0][0])
        else:
            notes.append('排序=%s' % (conds[:1] or '无'))
        af = ws.root.find('{%s}autoFilter' % S)
        if af is not None:
            got += 3
            notes.append('自动筛选 OK')
        else:
            notes.append('无自动筛选')
        return (7, '筛选工作表', got, 12, notes)

    def r8(self):
        got, notes = 0, []
        ws = self.sheet('奖牌表')
        if ws is None:
            return (8, '页面设置', 0, 8, ['缺"奖牌表"'])
        ps = ws.root.find('{%s}pageSetup' % S)
        if ps is not None and ps.get('orientation') == 'landscape':
            got += 3
            notes.append('横向 OK')
        else:
            notes.append('方向=%s' % (ps.get('orientation') if ps is not None else '无'))
        pm = ws.root.find('{%s}pageMargins' % S)
        if pm is not None:
            v = {k: float(pm.get(k) or 0) * 2.54 for k in ('top', 'bottom', 'left', 'right')}
            if (abs(v['top'] - 1) < 0.15 and abs(v['bottom'] - 2.5) < 0.15
                    and abs(v['left'] - 1.5) < 0.15 and abs(v['right'] - 2) < 0.15):
                got += 5
                notes.append('页边距 OK')
            else:
                notes.append('页边距 %.1f/%.1f/%.1f/%.1f' % (v['top'], v['bottom'], v['left'], v['right']))
        return (8, '页面设置', got, 8, notes)


if __name__ == '__main__':
    sys.exit(run(ExcelGrader15, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Excel 2010 操作题题库', '15', '1结果.xlsx')))
