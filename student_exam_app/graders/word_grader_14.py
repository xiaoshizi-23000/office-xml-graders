"""WPS 文档评分器 - 第14套（古老村落）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import WordDoc, Report, run

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


class WordGrader14:
    def __init__(self, path):
        self.doc = WordDoc(path)

    def grade(self):
        report = Report('WPS 文档 第14套 · 古老村落')
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
        ps = self.doc.page_setup()
        w, h = int(ps.get('w') or 0), int(ps.get('h') or 0)
        vals = {k: int(ps.get(k) or 0) / 567 for k in ('top', 'bottom', 'left', 'right')}
        if (abs(vals['top'] - 3) < 0.12 and abs(vals['bottom'] - 3) < 0.12
                and abs(vals['left'] - 2) < 0.12 and abs(vals['right'] - 2) < 0.12):
            got += 8
            notes.append('页边距 3/3/2/2cm OK（A4）')
        else:
            notes.append('页边距 %.1f/%.1f/%.1f/%.1f' % (vals['top'], vals['bottom'], vals['left'], vals['right']))
        return (1, '纸张与页边距', got, 8, notes)

    def r2(self):
        got, notes = 0, []
        ps = self.paras()
        if not ps:
            return (2, '标题格式', 0, 22, ['无正文'])
        p0 = ps[0]
        runs = list(p0.iter(W + 'r'))
        rp = self.doc.run_props(runs[0], p0) if runs else {}
        font = rp.get('eastAsia') or rp.get('font') or ''
        if font == '微软雅黑':
            got += 4
            notes.append('微软雅黑 OK')
        else:
            notes.append('字体=%s' % font)
        if str(rp.get('size') or '') == '144':
            got += 4
            notes.append('72号 OK')
        else:
            notes.append('字号=%s' % rp.get('size'))
        seg = self.pxml(p0)
        has_b = bool(re.search(r'<[a-z0-9]+:b[\s/>]', seg))
        has_i = bool(re.search(r'<[a-z0-9]+:i[\s/>]', seg))
        if has_b and has_i:
            got += 2
            notes.append('加粗倾斜 OK')
        else:
            notes.append('加粗=%s 倾斜=%s' % (has_b, has_i))
        if 'val="center"' in seg:
            got += 2
            notes.append('居中 OK')
        if 'outlineLvl' in seg:
            got += 2
            notes.append('大纲1级 OK')
        sp = re.findall(r'spacing[^>]*val="(\d+)"', seg)
        if sp and abs(int(sp[0]) - 57) <= 4:
            got += 2
            notes.append('字符间距0.1cm OK')
        else:
            notes.append('间距=%s' % (sp[:1] or '无'))
        if 'textOutline' in seg or re.search(r'<w14:outline', seg):
            got += 3
            notes.append('文本轮廓 OK')
        else:
            # 轮廓也可能落在 run 级 alternateContent 里，按全文精确标签再看一次
            if re.search(r'<w14:(textOutline|outline)', self.doc.xml_all()):
                got += 3
                notes.append('文本轮廓 OK')
            else:
                notes.append('无文本轮廓')
        if 'outerShdw' in seg or 'shadow' in seg:
            got += 2
            notes.append('阴影 OK')
        else:
            notes.append('无阴影')
        m = re.search(r'pBdr.*?</[a-z0-9]+:pBdr>', seg, re.S)
        if m and 'double' in m.group(0) and 'FF0000' in m.group(0).upper() and 'sz="18"' in m.group(0):
            got += 4
            notes.append('红双实线下边框2.25磅 OK')
        elif m and 'double' in m.group(0):
            got += 2
            notes.append('双线边框但颜色/宽度不符')
        else:
            notes.append('无段落边框')
        return (2, '标题格式', got, 22, notes)

    def r3(self):
        got, notes = 0, []
        target = None
        for p in self.paras():
            t = self.ptext(p)
            if t.startswith('过了神驼峰') or len(t) > 30:
                target = p
                break
        if target is None:
            return (3, '正文格式', 0, 16, ['找不到正文段'])
        pr = self.doc.para_props(target)
        runs = list(target.iter(W + 'r'))
        rp = self.doc.run_props(runs[0], target) if runs else {}
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
            got += 7
            notes.append('正文四号 OK')
        else:
            notes.append('字号=%s' % (size or rp.get('size')))
        if str(pr.get('firstLineChars') or '') == '200':
            got += 3
            notes.append('首行缩进2字符 OK')
        before = str(pr.get('before') or '')
        after = str(pr.get('after') or '')
        if before == '100' and after == '100':
            got += 3
            notes.append('段前段后5磅 OK')
        elif before or after:
            got += 1
            notes.append('段前后=%s/%s' % (before, after))
        else:
            notes.append('无段前后间距')
        if str(pr.get('lineRule') or '') in ('auto', '') and str(pr.get('line') or '') in ('240', ''):
            got += 3
            notes.append('单倍行距 OK')
        else:
            notes.append('行距=%s/%s' % (pr.get('line'), pr.get('lineRule')))
        return (3, '正文格式', got, 16, notes)

    def r4(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        fr = re.search(r'<w:framePr[^/]*w:dropCap="drop"[^/]*/>', full)
        if not fr:
            return (4, '首字下沉', 0, 8, ['无首字下沉'])
        got += 3
        notes.append('首字下沉 OK')
        m = re.search(r'w:lines="(\d+)"', fr.group(0))
        if m and m.group(1) == '1':
            got += 2
            notes.append('下沉1行 OK')
        hs = re.search(r'w:hSpace="(\d+)"', fr.group(0))
        if hs and abs(int(hs.group(1)) - 100) <= 10:
            got += 1
            notes.append('距正文5磅 OK')
        glyph = None
        for p in self.paras():
            if len(self.ptext(p)) == 1:
                glyph = p
                break
        if glyph is not None:
            runs = list(glyph.iter(W + 'r'))
            rp = self.doc.run_props(runs[0], glyph) if runs else {}
            font = rp.get('eastAsia') or rp.get('font') or ''
            color = str(rp.get('color') or '').upper()
            if font == '仿宋':
                got += 1
                notes.append('仿宋 OK')
            if color.endswith('FF0000'):
                got += 1
                notes.append('红色 OK')
        return (4, '首字下沉', got, 8, notes)

    def r5(self):
        got, notes = 0, []
        if 'word/footnotes.xml' not in self.doc.names:
            return (5, '脚注', 0, 8, ['无脚注部件'])
        fx = self.doc.read('word/footnotes.xml')
        if '河西走廊' in fx:
            got += 6
            notes.append('脚注内容 OK')
        else:
            got += 2
            notes.append('有脚注但内容不符')
        if '<w:footnoteReference' in self.doc.xml_all():
            got += 2
            notes.append('正文引用 OK')
        return (5, '脚注', got, 8, notes)

    def r6(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        if 'blipFill' not in full:
            return (6, '圆角矩形', 0, 18, ['没有图片填充形状'])
        got += 5
        notes.append('图片填充形状 OK')
        if 'roundRect' in full or 'round2SameRect' in full or 'flowChartTerminator' in full:
            got += 3
            notes.append('圆角矩形 OK')
        else:
            got += 3
            notes.append('图片填充形状（圆角类型未识别，按填充计）')
        ext = re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"/>', full)
        if ext:
            w = int(ext.group(1)) / 360000
            h = int(ext.group(2)) / 360000
            if abs(w - 7.5) < 0.5 and abs(h - 9) < 0.5:
                got += 4
                notes.append('7.5×9cm OK')
            else:
                notes.append('尺寸%.1f×%.1fcm' % (w, h))
        if 'wrapThrough' in full or 'wrapTight' in full:
            got += 2
            notes.append('穿越型环绕 OK')
        if 'rotRev' in full or 'camera' in full.lower():
            got += 2
            notes.append('三维旋转 OK')
        if 'alpha' in full.lower() and 'blipFill' in full:
            got += 2
            notes.append('透明度 OK')
        return (6, '圆角矩形', got, 18, notes)

    def r7(self):
        got, notes = 0, []
        texts = [self.ptext(p) for p in self.paras()]
        hit = sum(1 for t in texts if t.startswith('中国现代散文家') or t.startswith('代表作品'))
        if hit >= 2:
            got += 4
            notes.append('末尾两段 OK')
        elif hit:
            got += 2
            notes.append('末尾段落 %d/2' % hit)
        else:
            notes.append('末尾段落未找见')
        found = False
        for p in self.paras():
            seg = self.pxml(p)
            if ('中国现代散文家' in self.ptext(p) or '代表作品' in self.ptext(p)) and 'shd' in seg:
                if 'accent3' in seg or 'FBE5D6' in seg.upper() or 'tint' in seg:
                    found = True
        if found:
            got += 4
            notes.append('橙色底纹 OK')
        else:
            notes.append('底纹未匹配')
        return (7, '末尾段落与底纹', got, 8, notes)

    def r8(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        if 'type="pattern"' in full and ('大网格' in full or 'D2EBFA' in full.upper()):
            got += 4
            notes.append('大网格图案背景 OK')
        elif 'type="pattern"' in full:
            got += 2
            notes.append('有图案背景但非大网格')
        else:
            notes.append('无图案背景')
        odd = even = False
        for n in self.doc.names:
            if 'header' in n and n.endswith('.xml'):
                c = self.doc.read(n)
                if '古老村落' in c:
                    odd = True
                if '田园长卷' in c:
                    even = True
        if odd and even:
            got += 4
            notes.append('奇偶页眉 OK')
        elif odd or even:
            got += 2
            notes.append('只设了一个页眉')
        else:
            notes.append('页眉未设')
        if 'evenAndOddHeaders' in full or (odd and even):
            got += 1
            notes.append('奇偶页不同 OK')
        foot = ''.join(self.doc.footer_texts())
        fnum = False
        for n in self.doc.names:
            if 'footer' in n and n.endswith('.xml'):
                c = self.doc.read(n)
                if 'PAGE' in c or 'fldSimple' in c or re.search(r'<w:t[^>]*>\s*\d', c):
                    fnum = True
        if '一' in foot or '二' in foot or '&P' in foot or fnum:
            got += 3
            notes.append('页脚页码 OK')
        else:
            notes.append('页脚=%r' % foot[:20])
        return (8, '背景与页眉页脚', got, 12, notes)


if __name__ == '__main__':
    sys.exit(run(WordGrader14, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Word 2010 操作题题库', '14', '1结果.docx')))
