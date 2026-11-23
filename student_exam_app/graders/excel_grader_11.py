"""WPS 表格评分器 - 第11套（6月份销售记录表）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import ExcelBook, Report, run, formula_has

S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'


class ExcelGrader11:
    def __init__(self, path):
        self.book = ExcelBook(path)

    def grade(self):
        report = Report('WPS 表格 第11套 · 6月份销售记录表')
        for fn in (self.r1, self.r2, self.r3, self.r4, self.r5,
                   self.r6, self.r7, self.r8):
            report.add(*fn())
        return report

    def sheet(self, name):
        return self.book.sheet(name)

    def fmt(self, sheet, ref):
        return self.book.format_in(sheet.root, ref)

    def r1(self):
        notes, got = [], 0
        sheet = self.sheet('销售记录表')
        if sheet is None:
            return (1, '标题行与格式', 0, 12, ['未找到"销售记录表"'])
        title = self.book.value_in(sheet.root, 'A1')
        if str(title).strip() == '6月份销售记录表':
            got += 4
            notes.append('A1 标题 OK')
        else:
            notes.append('A1=%r' % title)
        fmt = self.fmt(sheet, 'A1')
        font = fmt.get('font', {})
        color = (font.get('color') or {}).get('rgb') or ''
        if font.get('name') == '微软雅黑' and font.get('size') == '22':
            got += 2
            notes.append('微软雅黑22 OK')
        else:
            notes.append('字体=%s/%s' % (font.get('name'), font.get('size')))
        if color.upper().endswith('7030A0'):
            got += 2
            notes.append('紫色 OK')
        else:
            notes.append('颜色=%s' % color)
        if (fmt.get('alignment') or {}).get('horizontal') == 'centerContinuous':
            got += 2
            notes.append('跨列居中 OK')
        else:
            notes.append('对齐=%s' % (fmt.get('alignment') or {}).get('horizontal'))
        row1 = None
        for r in sheet.root.iter('{%s}row' % S):
            if r.get('r') == '1':
                row1 = r
                break
        if row1 is not None and abs(float(row1.get('ht') or 0) - 28.5) < 0.1:
            got += 2
            notes.append('行高28.5 OK')
        else:
            notes.append('行高=%s' % (row1.get('ht') if row1 is not None else '无'))
        return (1, '标题行与格式', got, 12, notes)

    def r2(self):
        notes, got = [], 0
        sheet = self.sheet('销售记录表')
        if sheet is None:
            return (2, '冻结窗格+排序+补空值', 0, 13, ['缺工作表'])
        pane = None
        for p in sheet.root.iter('{%s}pane' % S):
            pane = p
            break
        if pane is not None and (pane.get('ySplit') or '') == '2' and (pane.get('topLeftCell') or '').upper() == 'A3':
            got += 4
            notes.append('冻结前两行 OK')
        else:
            notes.append('冻结=%s' % (pane.attrib if pane is not None else '无'))
        conds = []
        for st in sheet.root.iter('{%s}sortState' % S):
            for sc in st.iter('{%s}sortCondition' % S):
                conds.append((sc.get('ref', ''), sc.get('descending')))
        if conds and conds[0][0].upper().startswith('A') and conds[0][1] != '1':
            got += 3
            notes.append('日期升序 OK')
        else:
            notes.append('主排序=%s' % (conds[:1] or '无'))
        if len(conds) > 1 and conds[1][0].upper().startswith('B') and conds[1][1] != '1':
            got += 3
            notes.append('编码升序 OK')
        else:
            notes.append('次排序=%s' % (conds[1:2] or '无'))
        blank = 0
        filled = 0
        for r in range(3, 53):
            v = self.book.value_in(sheet.root, 'E%d' % r)
            if v in (None, ''):
                blank += 1
            elif str(v).strip() == '无':
                filled += 1
        if blank == 0 and filled > 0:
            got += 3
            notes.append('尺寸空值已填"无" OK')
        else:
            notes.append('尺寸列空值%d个、"无"%d个' % (blank, filled))
        return (2, '冻结窗格+排序+补空值', got, 13, notes)

    def r3(self):
        notes, got = [], 0
        sheet = self.sheet('销售记录表')
        if sheet is None:
            return (3, '销售金额与货币格式', 0, 13, ['缺工作表'])
        f = self.book.formula_in(sheet.root, 'I3')
        have_formula = formula_has(f, 'G3', 'H3') and ('*' in (f or ''))
        value_ok = 0
        for r in range(3, 53):
            g = self.book.value_in(sheet.root, 'G%d' % r)
            h = self.book.value_in(sheet.root, 'H%d' % r)
            i = self.book.value_in(sheet.root, 'I%d' % r)
            try:
                if g not in (None, '') and h not in (None, '') and i not in (None, ''):
                    if abs(float(i) - float(g) * float(h)) < 0.5:
                        value_ok += 1
            except (TypeError, ValueError):
                continue
        if have_formula and value_ok >= 45:
            got += 7
            notes.append('销售金额=单价*数量 OK（公式+%d行数值）' % value_ok)
        elif have_formula:
            got += 5
            notes.append('I3 公式 OK，数值对上 %d 行' % value_ok)
        elif value_ok >= 45:
            got += 6
            notes.append('金额为计算值（无公式）%d 行 OK' % value_ok)
        else:
            notes.append('I3=%r，数值对上 %d 行' % (f or '', value_ok))
        gfmt = (self.fmt(sheet, 'G3').get('numfmt') or '')
        if '￥' in gfmt and '0.00' in gfmt:
            got += 3
            notes.append('单价货币2位 OK')
        else:
            notes.append('单价格式=%s' % gfmt)
        ifmt = (self.fmt(sheet, 'I3').get('numfmt') or '')
        if '￥' in ifmt and '0.00' in ifmt:
            got += 3
            notes.append('金额货币2位 OK')
        else:
            notes.append('金额格式=%s' % ifmt)
        return (3, '销售金额与货币格式', got, 13, notes)

    def r4(self):
        notes, got = [], 0
        sheet = self.sheet('销售记录表')
        if sheet is None:
            return (4, '条件格式', 0, 12, ['缺工作表'])
        rule = None
        rng = ''
        for cf in sheet.root.iter('{%s}conditionalFormatting' % S):
            for rl in cf:
                if rl.tag.endswith('cfRule'):
                    rule, rng = rl, cf.get('sqref', '')
                    break
            if rule is not None:
                break
        if rule is None:
            return (4, '条件格式', 0, 12, ['没有条件格式'])
        if rng.upper().startswith('I'):
            got += 4
            notes.append('作用于金额列 OK')
        else:
            notes.append('范围=%s' % rng)
        if rule.get('type') == 'aboveAverage' and rule.get('aboveAverage') == '0':
            got += 4
            notes.append('低于平均值 OK')
        elif rule.get('type') in ('cellIs', 'expression') and 'AVERAGE' in (rule.findtext('{%s}formula' % S) or ''):
            got += 3
            notes.append('公式式低于平均 OK')
        else:
            notes.append('规则=%s/%s' % (rule.get('type'), rule.get('operator')))
        styles = self.book.read('xl/styles.xml') if 'xl/styles.xml' in self.book.names else ''
        dxf = ''
        m = re.search(r'<dxfs[^>]*>(.*?)</dxfs>', styles, re.S)
        if m:
            dxf = m.group(1)
        idx = int(rule.get('dxfId') or 0)
        chunks = re.findall(r'<dxf>(.*?)</dxf>', dxf, re.S)
        target = chunks[idx] if idx < len(chunks) else ''
        has_fill = '00B0F0' in target.upper() or 'DDEBF7' in target.upper()
        has_font = '002060' in target.upper() or '1F497D' in target.upper()
        if has_fill and has_font:
            got += 4
            notes.append('浅蓝底+深蓝字 OK')
        elif has_fill or has_font:
            got += 2
            notes.append('填色或字色只中一个')
        else:
            notes.append('dxf=%s' % target[:60])
        return (4, '条件格式', got, 12, notes)

    def r5(self):
        notes, got = [], 0
        sheet = self.sheet('按产品统计销售收入')
        if sheet is None:
            return (5, '按产品汇总', 0, 13, ['未找到"按产品统计销售收入"'])
        brands = [self.book.value_in(sheet.root, 'B%d' % r) for r in range(5, 10)]
        brands = [b for b in brands if b]
        qty = sum(1 for r in range(5, 10) if formula_has(self.book.formula_in(sheet.root, 'C%d' % r), 'SUMIF'))
        amt = sum(1 for r in range(5, 10) if formula_has(self.book.formula_in(sheet.root, 'D%d' % r), 'SUMIF'))
        if qty >= 5:
            got += 5
            notes.append('数量 SUMIF OK')
        else:
            got += qty
            notes.append('数量 SUMIF %d/5' % qty)
        if amt >= 5:
            got += 5
            notes.append('收入 SUMIF OK')
        else:
            got += amt
            notes.append('收入 SUMIF %d/5' % amt)
        total_c = self.book.formula_in(sheet.root, 'C10')
        total_d = self.book.formula_in(sheet.root, 'D10')
        if formula_has(total_c, 'SUM') and formula_has(total_d, 'SUM'):
            got += 3
            notes.append('合计行 OK')
        else:
            notes.append('合计 C10=%r D10=%r' % (total_c, total_d))
        return (5, '按产品汇总', got, 13, notes)

    def r6(self):
        notes, got = [], 0
        charts = [n for n in self.book.names if re.match(r'xl/charts/chart\d+\.xml$', n)]
        if not charts:
            return (6, '三维饼图', 0, 13, ['没有图表'])
        xml = self.book.read(charts[0])
        if 'pie3DChart' in xml:
            got += 4
            notes.append('三维饼图 OK')
        elif 'pieChart' in xml:
            got += 2
            notes.append('是饼图但非三维')
        else:
            notes.append('图表类型不是饼图')
        texts = re.findall(r'<a:t>([^<]*)</a:t>', xml)
        if any('品牌销售收入结构图表' in t for t in texts):
            got += 3
            notes.append('图表标题 OK')
        else:
            notes.append('标题=%s' % texts[:2])
        if re.search(r'<c:legendPos val="r"', xml):
            got += 3
            notes.append('图例靠右 OK')
        else:
            notes.append('图例位置=%s' % (re.findall(r'legendPos val="([^"]+)"', xml) or '无'))
        has_percent = re.search(r'<c:showPercent val="1"', xml)
        center = re.search(r'<c:dLblPos val="ctr"', xml)
        if has_percent and center:
            got += 3
            notes.append('居中百分比标签 OK')
        elif has_percent:
            got += 2
            notes.append('有百分比但未居中')
        else:
            notes.append('未设百分比数据标签')
        return (6, '三维饼图', got, 13, notes)

    def r7(self):
        notes, got = [], 0
        if '品牌销售' not in self.book.sheet_names:
            return (7, '数据透视表', 0, 12, ['没有"品牌销售"工作表'])
        got += 4
        notes.append('"品牌销售"工作表 OK')
        tables = [n for n in self.book.names if re.match(r'xl/pivotTables/pivotTable\d+\.xml$', n)]
        if not tables:
            return (7, '数据透视表', got, 12, notes + ['没有数据透视表'])
        xml = self.book.read(tables[0])
        loc = re.search(r'<location ref="([A-Z]+\d+)', xml)
        if loc and loc.group(1).upper() == 'A3':
            got += 4
            notes.append('起始 A3 OK')
        else:
            notes.append('位置=%s' % (loc.group(1) if loc else '?'))
        has_row = 'axis="axisRow"' in xml
        has_col = 'axis="axisCol"' in xml
        data_field = re.search(r'<dataField name="([^"]*)"', xml)
        value_ok = data_field and '销售数量' in data_field.group(1)
        if has_row and has_col and value_ok:
            got += 4
            notes.append('行列值与销售数量 OK')
        elif has_row and has_col:
            got += 2
            notes.append('行列 OK，值=%s' % (data_field.group(1) if data_field else '?'))
        else:
            notes.append('行=%s 列=%s' % (has_row, has_col))
        return (7, '数据透视表', got, 12, notes)

    def r8(self):
        notes, got = [], 0
        sheet = self.sheet('销售记录表')
        if sheet is None:
            return (8, '页面设置与标签色', 0, 12, ['缺工作表'])
        ps = sheet.root.find('{%s}pageSetup' % S)
        orient_ok = ps is not None and ps.get('orientation') == 'landscape'
        paper_ok = ps is not None and (ps.get('paperSize') or '') == '13'
        if orient_ok:
            got += 2
            notes.append('横向 OK')
        else:
            notes.append('方向=%s' % (ps.get('orientation') if ps is not None else '无'))
        if paper_ok:
            got += 2
            notes.append('B5(JIS) OK')
        else:
            notes.append('纸张=%s' % (ps.get('paperSize') if ps is not None else '无'))
        pm = sheet.root.find('{%s}pageMargins' % S)
        if pm is not None:
            try:
                vals = {k: float(pm.get(k) or 0) * 2.54 for k in ('top', 'bottom', 'left', 'right')}
                good = (abs(vals['top'] - 1.2) < 0.12 and abs(vals['bottom'] - 1.3) < 0.12
                        and abs(vals['left'] - 1.0) < 0.12 and abs(vals['right'] - 0.9) < 0.12)
                if good:
                    got += 4
                    notes.append('页边距 OK')
                else:
                    notes.append('页边距偏差 上%.1f下%.1f左%.1f右%.1f' % (vals['top'], vals['bottom'], vals['left'], vals['right']))
            except ValueError:
                notes.append('页边距读取失败')
        else:
            notes.append('无页边距设置')
        want = {'销售记录表': 'FFFF0000', '品牌销售': 'FF0070C0', '按产品统计销售收入': 'FFFFFF00'}
        hit = 0
        for name, rgb in want.items():
            s2 = self.sheet(name)
            if s2 is None:
                continue
            got_rgb = ''
            for n in s2.root.iter('{%s}tabColor' % S):
                got_rgb = (n.get('rgb') or '').upper()
                break
            if got_rgb == rgb.upper():
                hit += 1
        if hit == 3:
            got += 4
            notes.append('标签红蓝黄 OK')
        else:
            got += hit
            notes.append('标签色 %d/3' % hit)
        return (8, '页面设置与标签色', got, 12, notes)


if __name__ == '__main__':
    sys.exit(run(ExcelGrader11, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Excel 2010 操作题题库', '11', '1结果.xlsx')))