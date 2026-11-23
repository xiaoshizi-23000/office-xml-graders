"""WPS 文档评分器 - 第17套（青城不语）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import WordDoc, Report, run

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


class WordGrader17:
    def __init__(self, path):
        self.doc = WordDoc(path)

    def grade(self):
        report = Report('WPS 文档 第17套 · 青城不语')
        for fn in (self.r1, self.r2, self.r3, self.r4,
                   self.r5, self.r6, self.r7, self.r8):
            report.add(*fn())
        return report

    def paras(self):
        return list(self.doc.body.iter(W + 'p')) if self.doc.body is not None else []

    def ptext(self, p):
        return ''.join(t.text or '' for t in p.iter(W + 't')).strip()

    def pxml(self, p):
        return __import__('xml.etree.ElementTree', fromlist=['x']).tostring(p, encoding='unicode')

    def r1(self):
        got, notes = 0, []
        secs = self.doc.sections
        ps = self.doc.page_setup(secs[0]) if secs else self.doc.page_setup()
        w, h = int(ps.get('w') or 0), int(ps.get('h') or 0)
        if abs(w - 12472) <= 40 and abs(h - 18142) <= 40:
            got += 5
            notes.append('22×32cm 纸张 OK')
        else:
            notes.append('纸张=%dx%d' % (w, h))
        v = {k: int(ps.get(k) or 0) / 567 for k in ('top', 'bottom', 'left', 'right')}
        if (abs(v['top'] - 2) < 0.12 and abs(v['bottom'] - 2) < 0.12
                and abs(v['left'] - 1) < 0.12 and abs(v['right'] - 1) < 0.12):
            got += 5
            notes.append('页边距 2/2/1/1cm OK')
        else:
            notes.append('边距 %.1f/%.1f/%.1f/%.1f' % (v['top'], v['bottom'], v['left'], v['right']))
        return (1, '纸张与边距', got, 10, notes)

    def r2(self):
        got, notes = 0, []
        ps = self.paras()
        if not ps:
            return (2, '标题格式', 0, 16, ['无正文'])
        p0 = ps[0]
        rp = self.doc.run_props(list(p0.iter(W + 'r'))[0], p0)
        font = rp.get('eastAsia') or rp.get('font') or ''
        if font == '黑体':
            got += 3
            notes.append('黑体 OK')
        else:
            notes.append('字体=%s' % font)
        if str(rp.get('size') or '') == '72':
            got += 3
            notes.append('小初 OK')
        else:
            notes.append('字号=%s' % rp.get('size'))
        if str(rp.get('color') or '').upper().endswith('00B050'):
            got += 2
            notes.append('绿色 OK')
        else:
            notes.append('颜色=%s' % rp.get('color'))
        seg = self.pxml(p0)
        has_b = bool(re.search(r'<[a-z0-9]+:b[\s/>]', seg))
        has_i = bool(re.search(r'<[a-z0-9]+:i[\s/>]', seg))
        if has_b and has_i:
            got += 2
            notes.append('加粗倾斜 OK')
        if 'val="center"' in seg:
            got += 2
            notes.append('居中 OK')
        if 'outlineLvl' in seg:
            got += 2
            notes.append('大纲1级 OK')
        else:
            notes.append('无大纲')
        if re.search(r'after="120"', seg):
            got += 1
            notes.append('段后6磅 OK')
        sp = re.findall(r'spacing[^>]*val="(\d+)"', seg)
        if sp:
            got += 1
            notes.append('字符间距已设（%s）' % sp[0])
        else:
            notes.append('未设字符间距')
        return (2, '标题格式', got, 16, notes)

    def r3(self):
        got, notes = 0, []
        target = None
        for p in self.paras():
            if self.ptext(p).startswith('晨光初破'):
                target = p
                break
        if target is None:
            return (3, '正文格式', 0, 12, ['找不到正文段'])
        pr = self.doc.para_props(target)
        runs = list(target.iter(W + 'r'))
        size = ''
        for r in runs:
            rpr = r.find(W + 'rPr')
            if rpr is not None:
                szv = rpr.find(W + 'sz')
                if szv is not None:
                    size = szv.get(W + 'val') or ''
                    if size:
                        break
        if size == '28':
            got += 6
            notes.append('四号 OK')
        else:
            notes.append('字号=%s' % size)
        if str(pr.get('firstLineChars') or '') == '200':
            got += 3
            notes.append('首行缩进2字符 OK')
        if str(pr.get('afterLines') or '') == '50':
            got += 3
            notes.append('段后0.5行 OK')
        return (3, '正文格式', got, 12, notes)

    def r4(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        fr = re.search(r'<w:framePr[^/]*w:dropCap="drop"[^/]*/>', full)
        if not fr:
            return (4, '首字下沉', 0, 10, ['无首字下沉'])
        got += 4
        notes.append('首字下沉 OK')
        m = re.search(r'w:lines="(\d+)"', fr.group(0))
        if m and m.group(1) == '2':
            got += 2
            notes.append('下沉2行 OK')
        hs = re.search(r'w:hSpace="(\d+)"', fr.group(0))
        if hs and abs(int(hs.group(1)) - 113) <= 12:
            got += 2
            notes.append('距正文0.2cm OK')
        glyph = None
        for p in self.paras():
            if len(self.ptext(p)) == 1:
                glyph = p
                break
        if glyph is not None:
            rp = self.doc.run_props(list(glyph.iter(W + 'r'))[0], glyph)
            if (rp.get('eastAsia') or rp.get('font')) == '楷体':
                got += 1
                notes.append('楷体 OK')
            if str(rp.get('color') or '').upper().endswith('00B0F0'):
                got += 1
                notes.append('浅蓝 OK')
        return (4, '首字下沉', got, 10, notes)

    def r5(self):
        got, notes = 0, []
        bd = None
        shd = None
        for p in self.paras():
            seg = self.pxml(p)
            m = re.search(r'<[a-z0-9]+:bdr ([^/]*)/>', seg)
            if m and ('dotted' in m.group(1)):
                bd = m.group(1)
                sm = re.search(r'<[a-z0-9]+:shd ([^/]*)/>', seg)
                if sm:
                    shd = sm.group(1)
                break
        if bd:
            got += 4
            notes.append('点线文字边框 OK')
        else:
            notes.append('无点线文字边框')
        if bd and ('FFC000' in bd.upper() or 'ED7D31' in bd.upper()):
            got += 3
            notes.append('橙色 OK')
        else:
            notes.append('边框颜色未匹配')
        if shd and ('accent4' in shd or 'E3F2D9' in shd.upper() or 'tint' in shd):
            got += 3
            notes.append('浅绿底纹 OK')
        else:
            notes.append('底纹未匹配')
        return (5, '文字边框底纹', got, 10, notes)

    def r6(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        if 'ellipse' not in full:
            return (6, '椭圆形状', 0, 16, ['没有椭圆形状'])
        got += 4
        notes.append('椭圆 OK')
        if 'blipFill' in full:
            got += 3
            notes.append('图片填充 OK')
        else:
            notes.append('非图片填充')
        ext = re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"/>', full)
        if ext:
            w = int(ext.group(1)) / 360000
            h = int(ext.group(2)) / 360000
            if abs(w - 5) < 0.6 and abs(h - 5) < 0.6:
                got += 3
                notes.append('5×5cm OK')
            else:
                notes.append('尺寸%.1f×%.1fcm' % (w, h))
        if 'wrapTight' in full or 'wrapSquare' in full:
            got += 2
            notes.append('紧密型环绕 OK')
        if re.search(r'<a:softEdge[^>]*rad="\d+"', full):
            got += 2
            notes.append('柔化边缘 OK')
        if 'glow' in full:
            got += 2
            notes.append('发光 OK')
        return (6, '椭圆形状', got, 16, notes)

    def r7(self):
        got, notes = 0, []
        tables = list(self.doc.body.iter(W + 'tbl')) if self.doc.body is not None else []
        if not tables:
            return (7, '末尾表格', 0, 14, ['没有表格'])
        tbl = tables[-1]
        rows = list(tbl.iter(W + 'tr'))
        cols = len(list(rows[0].iter(W + 'tc'))) if rows else 0
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
        tx = __import__('xml.etree.ElementTree', fromlist=['x']).tostring(tbl, encoding='unicode')
        widths = [int(x) for x in re.findall(r'gridCol[^>]*w="(\d+)"', tx)]
        wide = [x for x in widths if abs(x / 567 - 8) < 0.8]
        if len(wide) >= 2:
            got += 3
            notes.append('列宽8cm OK')
        elif widths:
            notes.append('列宽=%s cm' % [round(x / 567, 1) for x in widths])
        if re.search(r'tblStyle[^>]*val="[^"]+"', tx):
            got += 2
            notes.append('表格样式 OK')
        if 'val="center"' in tx:
            got += 2
            notes.append('表格居中/文字居中 OK')
        return (7, '末尾表格', got, 14, notes)

    def r8(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        if 'type="pattern"' in full and '竖虚线' in full:
            got += 5
            notes.append('竖虚线图案背景 OK')
        elif 'type="pattern"' in full:
            got += 3
            notes.append('有图案背景但非竖虚线')
        else:
            notes.append('无图案背景')
        bg = re.search(r'<w:background[^>]*>', full)
        if bg and ('accent2' in bg.group(0) or 'FCE6D5' in bg.group(0).upper()):
            got += 2
            notes.append('巧克力黄着色2 OK')
        foot = ''.join(self.doc.footer_texts())
        if '第' in foot and '共' in foot:
            got += 3
            notes.append('页脚"第X页共Y页" OK')
        else:
            notes.append('页脚=%r' % foot[:20])
        red_foot = False
        for n in self.doc.names:
            if 'footer' in n and n.endswith('.xml'):
                c = self.doc.read(n)
                if 'FF0000' in c.upper():
                    red_foot = True
        if red_foot:
            got += 2
            notes.append('页码红色 OK')
        else:
            notes.append('页码未设红色')
        return (8, '背景与页脚', got, 12, notes)


if __name__ == '__main__':
    sys.exit(run(WordGrader17, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Word 2010 操作题题库', '17', '1结果.docx')))
