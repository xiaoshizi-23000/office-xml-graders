"""WPS 表格评分器 - 第17套（商品信息）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import ExcelBook, Report, run, formula_has

S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'


class ExcelGrader17:
    def __init__(self, path):
        self.book = ExcelBook(path)

    def grade(self):
        report = Report('WPS 表格 第17套 · 商品信息')
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
        if '商品信息' in self.book.sheet_names:
            got += 4
            notes.append('"商品信息" OK')
        else:
            notes.append('工作表=%s' % self.book.sheet_names)
        ws = self.sheet('商品信息')
        if ws is None:
            return (1, '改名与边框', got, 12, notes)
        rgbs, themes, tints = set(), set(), set()
        for node in ws.cells().values():
            fm = self.book.styles.get(int(node.get('s', '0') or 0))
            for _k, v in (fm.get('border') or {}).items():
                col = v.get('color') or {}
                if not v.get('style'):
                    continue
                if col.get('rgb'):
                    rgbs.add(col['rgb'].upper())
                if col.get('theme'):
                    themes.add(str(col['theme']))
                if col.get('tint'):
                    tints.add(str(col['tint']))
        has_dark = any(c.endswith(('1F4E79', '2E75B6', '1F3864')) for c in rgbs) or len(themes) >= 1
        has_light = (any(c.endswith(('9DC3E6', 'BDD7EE', 'DEEBF7')) for c in rgbs)
                     or len(themes) >= 2 or len(tints) >= 2)
        if has_dark:
            got += 4
            notes.append('外边框已设 OK（theme%s rgb%s）' % (sorted(themes), sorted(rgbs)[:2]))
        else:
            notes.append('边框色：rgb=%s theme=%s' % (list(rgbs)[:3], list(themes)[:3]))
        if has_light:
            got += 4
            notes.append('内边框已设 OK')
        elif has_dark:
            got += 2
            notes.append('内外边框区分不明（同色系）')
        return (1, '改名与边框', got, 12, notes)

    def r2(self):
        got, notes = 0, []
        ws = self.sheet('商品信息')
        if ws is None:
            return (2, '正文字体与标题填充', 0, 12, ['缺"商品信息"'])
        f = self.fmt(ws, 'A1')['font']
        size_ok = f.get('size') == '10'
        align_ok = (self.fmt(ws, 'A1')['alignment'] or {}).get('horizontal') == 'center'
        if size_ok:
            got += 5
            notes.append('10号 OK（字体%s）' % f.get('name'))
        else:
            notes.append('字号=%s 字体=%s' % (f.get('size'), f.get('name')))
        if align_ok:
            got += 4
            notes.append('水平居中 OK')
        else:
            notes.append('对齐=%s' % (self.fmt(ws, 'A1')['alignment'] or {}).get('horizontal'))
        fill = (self.fmt(ws, 'A1')['fill'] or {}).get('fg') or {}
        bold = self.fmt(ws, 'A1')['font'].get('bold')
        if (fill.get('rgb') or fill.get('theme')) and bold:
            got += 3
            notes.append('标题行填充+加粗 OK')
        else:
            notes.append('填充=%s 加粗=%s' % (fill, bold))
        return (2, '正文字体与标题填充', got, 12, notes)

    def r3(self):
        got, notes = 0, []
        ws = self.sheet('商品信息')
        if ws is None:
            return (3, '日期格式', 0, 8, ['缺"商品信息"'])
        n = 0
        sample = ''
        for r in range(2, 101):
            nf = self.fmt(ws, 'B%d' % r).get('numfmt') or ''
            if '年' in nf and '月' in nf and '日' in nf:
                n += 1
                if not sample:
                    sample = nf
        if n >= 50:
            got += 8
            notes.append('年月日格式 OK（%s，%d行）' % (sample, n))
        elif n:
            got += 4
            notes.append('日期格式 %d 行' % n)
        else:
            notes.append('日期格式=%s' % (self.fmt(ws, 'B2').get('numfmt') or 'General'))
        return (3, '日期格式', got, 8, notes)

    def r4(self):
        got, notes = 0, []
        ws = self.sheet('商品信息')
        if ws is None:
            return (4, '商品名称 VLOOKUP', 0, 12, ['缺"商品信息"'])
        f = self.book.formula_in(ws.root, 'G3')
        n = sum(1 for r in range(2, 101)
                if formula_has(self.book.formula_in(ws.root, 'G%d' % r), 'VLOOKUP'))
        if formula_has(f, 'VLOOKUP') and n >= 5:
            got += 12
            notes.append('VLOOKUP 商品名称 OK（%d行）' % n)
        elif formula_has(f, 'VLOOKUP'):
            got += 8
            notes.append('VLOOKUP 有了（%d行）' % n)
        else:
            v = self.book.value_in(ws.root, 'G3')
            if v:
                got += 5
                notes.append('有值 %s（无公式）' % v)
            else:
                notes.append('G3=%r' % v)
        return (4, '商品名称 VLOOKUP', got, 12, notes)

    def r5(self):
        got, notes = 0, []
        ws = self.sheet('商品信息')
        if ws is None:
            return (5, '数据条与货币', 0, 12, ['缺"商品信息"'])
        bars = []
        for cf in ws.root.iter('{%s}conditionalFormatting' % S):
            for r in cf:
                if r.get('type') == 'dataBar':
                    bars.append(cf.get('sqref', ''))
        if bars:
            got += 7
            notes.append('蓝色数据条 OK（%s）' % bars[0])
        else:
            notes.append('无数据条')
        nf = self.fmt(ws, 'L2').get('numfmt') or ''
        if '￥' in nf and '0.00' in nf:
            got += 5
            notes.append('货币2位 OK')
        else:
            notes.append('金额格式=%s' % nf)
        return (5, '数据条与货币', got, 12, notes)

    def r6(self):
        got, notes = 0, []
        ws = self.sheet('商品信息')
        if ws is None:
            return (6, '页面设置', 0, 10, ['缺"商品信息"'])
        pm = ws.root.find('{%s}pageMargins' % S)
        if pm is not None:
            v = {k: float(pm.get(k) or 0) * 2.54 for k in ('top', 'bottom', 'left', 'right')}
            if (abs(v['top'] - 2) < 0.15 and abs(v['bottom'] - 3) < 0.15
                    and abs(v['left'] - 1.5) < 0.15 and abs(v['right'] - 1) < 0.15):
                got += 6
                notes.append('页边距 2/3/1.5/1 OK')
            else:
                notes.append('页边距 %.1f/%.1f/%.1f/%.1f' % (v['top'], v['bottom'], v['left'], v['right']))
        foot = ''
        for f in ws.root.iter('{%s}oddFooter' % S):
            foot = f.text or ''
            break
        if '共' in foot and '&P' in foot:
            got += 4
            notes.append('页脚 OK')
        else:
            notes.append('页脚=%r' % foot)
        return (6, '页面设置', got, 10, notes)

    def r7(self):
        got, notes = 0, []
        ws = self.sheet('Sheet3')
        if ws is None:
            return (7, '数量与占比', 0, 12, ['缺 Sheet3'])
        f = None
        for r in range(1, 20):
            for c in 'ABCDEF':
                v = self.book.formula_in(ws.root, '%s%d' % (c, r))
                if formula_has(v, 'COUNTIF', 'SUMIF'):
                    f = v
                    break
            if f:
                break
        if f:
            got += 7
            notes.append('统计公式 OK（%s）' % f[:44])
        else:
            notes.append('未找到 COUNTIF/SUMIF')
        pct = False
        for r in range(1, 20):
            for c in 'ABCDEF':
                nf = self.fmt(ws, '%s%d' % (c, r)).get('numfmt') or ''
                if '%' in nf:
                    pct = True
        if pct:
            got += 5
            notes.append('百分比格式 OK')
        else:
            notes.append('未设百分比')
        return (7, '数量与占比', got, 12, notes)

    def r8(self):
        got, notes = 0, []
        charts = [n for n in self.book.names if re.match(r'xl/charts/chart\d+\.xml$', n)]
        if not charts:
            return (8, '三维饼图', 0, 12, ['没有图表'])
        x = self.book.read(charts[0])
        if 'pie3DChart' in x:
            got += 5
            notes.append('三维饼图 OK')
        elif 'pieChart' in x:
            got += 3
            notes.append('饼图但非三维')
        else:
            notes.append('类型非饼图')
        texts = re.findall(r'<a:t>([^<]*)</a:t>', x)
        if any('各品牌总占比' in t for t in texts):
            got += 3
            notes.append('标题 OK')
        else:
            notes.append('标题=%s' % texts[:2])
        if re.search(r'<c:dLbls>', x):
            got += 2
            notes.append('数据标签 OK')
        if re.search(r'legendPos val="b"', x):
            got += 2
            notes.append('图例底部 OK')
        return (8, '三维饼图', got, 12, notes)

    def r9(self):
        got, notes = 0, []
        tables = [n for n in self.book.names if re.match(r'xl/pivotTables/pivotTable\d+\.xml$', n)]
        if not tables:
            return (9, '数据透视表', 0, 10, ['没有透视表'])
        x = self.book.read(tables[0])
        loc = re.search(r'<location[^>]*ref="([A-Z]+\d+)', x)
        if loc and loc.group(1).upper() == 'I10':
            got += 4
            notes.append('位置 I10 OK')
        else:
            notes.append('位置=%s' % (loc.group(1) if loc else '?'))
        if 'axis="axisRow"' in x and 'axis="axisCol"' in x:
            got += 4
            notes.append('行列区域 OK')
        df = re.findall(r'<dataField name="([^"]*)"', x)
        if df and ('金额合计' in df[0] or '求和' in df[0]):
            got += 2
            notes.append('值=金额合计求和 OK')
        else:
            notes.append('值=%s' % (df or '无'))
        return (9, '数据透视表', got, 10, notes)


if __name__ == '__main__':
    sys.exit(run(ExcelGrader17, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Excel 2010 操作题题库', '17', '1结果.xlsx')))
