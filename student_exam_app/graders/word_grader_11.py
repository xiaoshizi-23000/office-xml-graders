"""WPS 文档评分器 - 第11套（梁实秋雅舍系列节选）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import WordDoc, Report, run

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
NS_W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'


class WordGrader11:
    def __init__(self, path):
        self.doc = WordDoc(path)

    def grade(self):
        report = Report('WPS 文档 第11套 · 雅舍系列节选')
        for fn in (self.r1, self.r2, self.r3, self.r4, self.r5,
                   self.r6, self.r7, self.r8):
            report.add(*fn())
        return report

    def body_paras(self):
        if self.doc.body is None:
            return []
        return [p for p in self.doc.body.iter(W + 'p')]

    def para_text(self, p):
        return ''.join(t.text or '' for t in p.iter(W + 't')).strip()

    def r1(self):
        notes, got = [], 0
        ps = self.doc.page_setup()
        if ps.get('orient') == 'landscape':
            got += 4
            notes.append('横向 OK')
        else:
            notes.append('方向=%s' % ps.get('orient'))
        if abs(int(ps.get('w') or 0) - 16838) <= 20 and abs(int(ps.get('h') or 0) - 11906) <= 20:
            got += 2
            notes.append('A4 OK')
        else:
            notes.append('纸张=%sx%s' % (ps.get('w'), ps.get('h')))
        grid = ''
        for m in re.finditer(r'<w:docGrid[^/]*/>', self.doc.xml_all()):
            grid = m.group(0)
            break
        if 'linesAndChars' in grid:
            got += 4
            notes.append('行和字符网格 OK')
        else:
            notes.append('网格=%s' % (grid[:50] or '无'))
        pitch = int(ps.get('linePitch') or 0)
        avail = int(ps.get('h') or 0) - int(ps.get('top') or 0) - int(ps.get('bottom') or 0)
        lines = round(avail / pitch) if pitch else 0
        if abs(lines - 28) <= 1:
            got += 2
            notes.append('每页28行 OK（算得%d）' % lines)
        else:
            notes.append('每页约%d行' % lines)
        return (1, '页面设置与网格', got, 12, notes)

    def r2(self):
        notes, got = [], 0
        xml = self.doc.xml_all()
        m = re.search(r'<w:style [^>]*w:styleId="([^"]*)"[^>]*>(?:(?!</w:style>).)*?heading 1.*?</w:style>', xml, re.S)
        if not m:
            return (2, '标题1样式', 0, 14, ['没有修改标题1样式'])
        body = m.group(0)
        fonts = re.search(r'<w:rFonts([^/]*)/>', body)
        east = re.search(r'w:eastAsia="([^"]*)"', fonts.group(1)) if fonts else None
        if east and east.group(1) == '黑体':
            got += 3
            notes.append('黑体 OK')
        else:
            notes.append('中文字体=%s' % (east.group(1) if east else '无'))
        sz = re.search(r'<w:sz w:val="(\d+)"/>', body)
        if sz and sz.group(1) == '52':
            got += 2
            notes.append('一号(26pt) OK')
        else:
            notes.append('字号=%s' % (sz.group(1) if sz else '无'))
        if '<w:b/>' in body and '<w:i/>' in body:
            got += 2
            notes.append('加粗倾斜 OK')
        else:
            notes.append('加粗=%s 倾斜=%s' % ('<w:b/>' in body, '<w:i/>' in body))
        if re.search(r'<w:jc w:val="center"', body):
            got += 2
            notes.append('居中 OK')
        else:
            notes.append('未居中')
        before = re.search(r'w:before="(\d+)"', body)
        after = re.search(r'w:after="(\d+)"', body)
        if before and after and abs(int(before.group(1)) - 100) <= 10 and abs(int(after.group(1)) - 400) <= 20:
            got += 2
            notes.append('段前5磅段后20磅 OK')
        else:
            notes.append('段前=%s 段后=%s' % (before.group(1) if before else '?', after.group(1) if after else '?'))
        wave = re.findall(r'<w:(?:top|left|bottom|right) w:val="wave"', body)
        red_border = 'FF0000' in body and 'w:sz="6"' in body
        if len(wave) >= 3 and red_border:
            got += 2
            notes.append('单波浪红0.75磅边框 OK')
        else:
            notes.append('波浪边=%d 红/0.75=%s' % (len(wave), red_border))
        shd = re.search(r'<w:shd[^/]*w:fill="([0-9A-Fa-f]{6})"', body)
        if shd and shd.group(1).upper() in ('E6FAD2', 'D2FAF0'):
            got += 1
            notes.append('底纹 OK')
        else:
            notes.append('底纹=%s' % (shd.group(1) if shd else '无'))
        return (2, '标题1样式', got, 14, notes)

    def r3(self):
        notes, got = [], 0
        paras = self.body_paras()
        target = None
        for p in paras:
            if self.para_text(p).startswith('夏天喝酸梅汤'):
                target = p
                break
        if target is None:
            return (3, '正文格式', 0, 14, ['找不到正文第一段'])
        pr = self.doc.para_props(target)
        runs = [r for r in target.iter(W + 'r')]
        rp = self.doc.run_props(runs[0], target) if runs else {}
        font = rp.get('eastAsia') or rp.get('font') or ''
        if not font:
            seg = __import__('xml.etree.ElementTree', fromlist=['x']).tostring(target, encoding='unicode')
            m = re.search(r'eastAsia="([^"]*)"', seg)
            font = m.group(1) if m else ''
        size = str(rp.get('size') or '')
        if font and size == '28':
            got += 6
            notes.append('正文中文字体+四号 OK（%s/14pt）' % font)
        elif size == '28':
            got += 3
            notes.append('字号四号 OK，字体未显式设置')
        else:
            notes.append('字体=%s 字号=%s' % (font, size))
        if str(pr.get('firstLineChars') or '') == '200':
            got += 3
            notes.append('首行缩进2字符 OK')
        elif str(pr.get('firstLine') or '') == '540':
            got += 2
            notes.append('首行缩进540缇 OK')
        else:
            notes.append('缩进=%s' % (pr.get('firstLineChars') or pr.get('firstLine')))
        if str(pr.get('afterLines') or '') == '50' or abs(int(pr.get('after') or 0) - 157) <= 20:
            got += 2
            notes.append('段后0.5行 OK')
        else:
            notes.append('段后=%s' % (pr.get('afterLines') or pr.get('after')))
        if str(pr.get('line') or '') == '300' and pr.get('lineRule') == 'atLeast':
            got += 3
            notes.append('行距最小值15磅 OK')
        else:
            notes.append('行距=%s/%s' % (pr.get('line'), pr.get('lineRule')))
        return (3, '正文格式', got, 14, notes)

    def r4(self):
        notes, got = [], 0
        xml = self.doc.xml_all()
        fr = re.search(r'<w:framePr[^/]*w:dropCap="([^"]*)"[^/]*/>', xml)
        if not fr:
            return (4, '首字下沉', 0, 12, ['没有首字下沉'])
        got += 4
        notes.append('首字下沉 OK')
        lines = re.search(r'w:lines="(\d+)"', fr.group(0))
        if lines and lines.group(1) == '2':
            got += 2
            notes.append('下沉2行 OK')
        else:
            notes.append('行数=%s' % (lines.group(1) if lines else '?'))
        hs = re.search(r'w:hSpace="(\d+)"', fr.group(0))
        if hs and abs(int(hs.group(1)) - 100) <= 10:
            got += 2
            notes.append('距正文5磅 OK')
        else:
            notes.append('hSpace=%s' % (hs.group(1) if hs else '?'))
        target = None
        for p in self.body_paras():
            if self.para_text(p) == '暑':
                target = p
                break
        if target is not None:
            runs = [r for r in target.iter(W + 'r')]
            rp = self.doc.run_props(runs[0], target) if runs else {}
            color = str(rp.get('color') or '').upper()
            font = rp.get('eastAsia') or rp.get('font') or ''
            if color.endswith('FF0000') or color == 'FF0000':
                got += 2
                notes.append('红色 OK')
            else:
                notes.append('颜色=%s' % color)
            if font == '微软雅黑':
                got += 2
                notes.append('微软雅黑 OK')
            else:
                notes.append('字体=%s' % font)
        return (4, '首字下沉', got, 12, notes)

    def r5(self):
        notes, got = [], 0
        xml = self.doc.xml_all()
        if '<wp:anchor' not in xml:
            return (5, '图片与环绕', 0, 14, ['没有浮动图片'])
        got += 3
        notes.append('浮动图片 OK')
        ext = re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"/>', xml)
        if ext:
            w_cm = int(ext.group(1)) / 360000
            h_cm = int(ext.group(2)) / 360000
            if abs(w_cm - 9) < 0.35 and abs(h_cm - 14) < 0.35:
                got += 3
                notes.append('9×14cm OK')
            else:
                got += 1
                notes.append('尺寸%.1f×%.1fcm' % (w_cm, h_cm))
        else:
            notes.append('无 extent')
        if 'wrapSquare' in xml:
            got += 2
            notes.append('四周型环绕 OK')
        else:
            notes.append('无四周型环绕')
        pic = re.search(r'<pic:spPr>.*?</pic:spPr>', xml, re.S)
        edge = False
        if pic:
            ln = re.search(r'<a:ln[^>]*w="(\d+)"', pic.group(0))
            clr = re.search(r'<a:srgbClr val="([0-9A-Fa-f]{6})"', pic.group(0))
            edge = bool(ln and clr and clr.group(1).upper() == 'FF0000')
        if edge:
            got += 2
            notes.append('红色边框 OK')
        else:
            notes.append('边框未识别')
        effects = 0
        if re.search(r'<a:softEdge[^>]*rad="\d+"', xml):
            effects += 1
        if 'rotBack' in xml or 'camera' in xml.lower() or 'rotRev' in xml:
            effects += 1
        if effects >= 2:
            got += 2
            notes.append('柔化+三维旋转 OK')
        elif effects == 1:
            got += 1
            notes.append('柔化/三维只中一个')
        else:
            notes.append('无柔化与三维旋转')
        pos = re.search(r'<wp:positionH[^>]*relativeFrom="page".*?<wp:posOffset>(-?\d+)</wp:posOffset>', xml, re.S)
        posv = re.search(r'<wp:positionV[^>]*relativeFrom="page".*?<wp:posOffset>(-?\d+)</wp:posOffset>', xml, re.S)
        if pos and posv:
            h_cm = int(pos.group(1)) / 360000
            v_cm = int(posv.group(1)) / 360000
            if abs(h_cm - 18.5) < 0.6 and abs(v_cm - 3.25) < 0.6:
                got += 2
                notes.append('绝对位置 OK')
            else:
                got += 1
                notes.append('位置%.1f/%.1fcm' % (h_cm, v_cm))
        else:
            notes.append('相对页面位置未设置')
        return (5, '图片与环绕', got, 14, notes)

    def r6(self):
        notes, got = [], 0
        header_xml = ''
        for n in self.doc.names:
            if 'header' in n and n.endswith('.xml'):
                c = self.doc.read(n)
                if '雅舍谈吃' in c:
                    header_xml = c
                    break
        if not header_xml:
            return (6, '文字水印', 0, 12, ['没有"雅舍谈吃"水印'])
        got += 4
        notes.append('水印文字 OK')
        if re.search(r'font-family:\s*黑体', header_xml) and re.search(r'font-size:\s*44pt', header_xml):
            got += 3
            notes.append('黑体44 OK')
        else:
            notes.append('字体字号未匹配')
        if '00B0F0' in header_xml.upper():
            got += 2
            notes.append('浅蓝 OK')
        else:
            notes.append('颜色未匹配')
        h_left = 'mso-position-horizontal:left' in header_xml
        v_bottom = 'mso-position-vertical:bottom' in header_xml
        if h_left and v_bottom:
            got += 2
            notes.append('左对齐底端 OK')
        else:
            notes.append('水平=%s 垂直=%s' % (h_left, v_bottom))
        op = re.search(r'opacity="([0-9.]+)f?"', header_xml)
        if op:
            pct = float(op.group(1)) / 65536 * 100
            if 50 <= pct <= 60:
                got += 1
                notes.append('透明度45%% OK（不透明%.0f%%）' % pct)
            else:
                notes.append('不透明%.0f%%' % pct)
        else:
            notes.append('未读到透明度')
        return (6, '文字水印', got, 12, notes)

    def r7(self):
        notes, got = [], 0
        if self.doc.body is None:
            return (7, '末尾表格', 0, 12, ['无正文'])
        tables = list(self.doc.body.iter(W + 'tbl'))
        if not tables:
            return (7, '末尾表格', 0, 12, ['没有表格'])
        tbl = tables[-1]
        rows = list(tbl.iter(W + 'tr'))
        cols = 0
        if rows:
            cols = len(list(rows[0].iter(W + 'tc')))
        if len(rows) == 3 and cols == 2:
            got += 4
            notes.append('3行2列 OK')
        else:
            notes.append('表格 %d行%d列' % (len(rows), cols))
        texts = [''.join(t.text or '' for t in tc.iter(W + 't')).strip()
                 for tc in rows[0].iter(W + 'tc')] if rows else []
        if texts[:2] == ['现代散文作家', '代表作品']:
            got += 3
            notes.append('首行文字 OK')
        else:
            notes.append('首行=%s' % texts)
        centered = 0
        total = 0
        for tc in tbl.iter(W + 'tc'):
            tcpr = tc.find(W + 'tcPr')
            total += 1
            if tcpr is None:
                continue
            va = tcpr.find(W + 'vAlign')
            if va is None or va.get(W + 'val') != 'center':
                continue
            for p in tc.iter(W + 'p'):
                ppr = p.find(W + 'pPr')
                if ppr is not None:
                    jc = ppr.find(W + 'jc')
                    if jc is not None and jc.get(W + 'val') == 'center':
                        centered += 1
                        break
        if total and centered >= total - 1:
            got += 2
            notes.append('水平垂直居中 OK')
        else:
            notes.append('居中 %d/%d' % (centered, total))
        txml = __import__('xml.etree.ElementTree', fromlist=['x']).tostring(tbl, encoding='unicode')
        style = re.search(r'tblStyle[^>]*val="([^"]*)"', txml)
        sname = style.group(1) if style else ''
        if sname:
            got += 3
            notes.append('表格样式 OK（%s）' % sname)
        else:
            notes.append('未套用表格样式')
        return (7, '末尾表格', got, 12, notes)

    def r8(self):
        notes, got = [], 0
        xml = self.doc.xml_all()
        bg = re.search(r'<w:background([^/]*)/>', xml)
        if bg and ('themeTint' in bg.group(1) or 'w:color' in bg.group(1)):
            got += 4
            notes.append('图案背景 OK')
        else:
            notes.append('无页面背景')
        ht = self.doc.header_texts()
        joined = ''.join(ht)
        if '梁实秋雅舍系列节选' in joined:
            got += 3
            notes.append('页眉文字 OK')
        else:
            notes.append('页眉=%s' % joined[:30])
        right_red = False
        for n in self.doc.names:
            if 'header' in n and n.endswith('.xml'):
                c = self.doc.read(n)
                if '梁实秋' in c and re.search(r'<w:jc w:val="right"', c) and 'FF0000' in c:
                    right_red = True
                    break
        if right_red:
            got += 3
            notes.append('右对齐红色 OK')
        else:
            notes.append('页眉对齐/颜色未匹配')
        return (8, '页面背景与页眉', got, 10, notes)


if __name__ == '__main__':
    sys.exit(run(WordGrader11, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Word 2010 操作题题库', '11', '1结果.docx')))
