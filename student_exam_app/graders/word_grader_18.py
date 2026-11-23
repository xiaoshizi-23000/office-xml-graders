"""WPS 文档评分器 - 第18套（人间萤火）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import WordDoc, Report, run

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


class WordGrader18:
    def __init__(self, path):
        self.doc = WordDoc(path)

    def grade(self):
        report = Report('WPS 文档 第18套 · 人间萤火')
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
        if abs(w - 11906) <= 30 and abs(h - 16838) <= 30:
            got += 3
            notes.append('A4 纵向 OK')
        else:
            notes.append('纸张=%dx%d' % (w, h))
        v = {k: int(ps.get(k) or 0) for k in ('top', 'bottom', 'left', 'right')}
        if all(abs(v[k] - 720) <= 12 for k in v):
            got += 7
            notes.append('页边距1.27cm OK')
        else:
            notes.append('边距twips=%s' % v)
        return (1, '纸张与边距', got, 10, notes)

    def r2(self):
        got, notes = 0, []
        ps = self.paras()
        if not ps:
            return (2, '标题格式', 0, 18, ['无正文'])
        p0 = ps[0]
        rp = self.doc.run_props(list(p0.iter(W + 'r'))[0], p0)
        font = rp.get('eastAsia') or rp.get('font') or ''
        if font == '黑体':
            got += 3
            notes.append('黑体 OK')
        else:
            notes.append('字体=%s' % font)
        if str(rp.get('size') or '') == '44':
            got += 2
            notes.append('二号 OK')
        else:
            notes.append('字号=%s' % rp.get('size'))
        if str(rp.get('color') or '').upper().endswith('FF0000'):
            got += 2
            notes.append('红色 OK')
        else:
            notes.append('颜色=%s' % rp.get('color'))
        seg = self.pxml(p0)
        if re.search(r':b[\s/>]', seg) and 'border' not in seg:
            got += 1
            notes.append('加粗 OK')
        if 'val="distribute"' in seg:
            got += 2
            notes.append('分散对齐 OK')
        else:
            notes.append('未分散对齐')
        if 'outlineLvl' in seg:
            got += 2
            notes.append('大纲1级 OK')
        if 'before="340"' in seg and 'after="330"' in seg:
            got += 2
            notes.append('段前17磅段后16.5磅 OK')
        else:
            notes.append('段前后=%s' % re.findall(r'(?:before|after)="(\d+)"', seg)[:2])
        if re.search(r'line="576"[^/]*lineRule="auto"', seg):
            got += 2
            notes.append('2.4倍行距 OK')
        else:
            notes.append('行距=%s' % re.findall(r'line="(\d+)"', seg)[:1])
        if 'outerShdw' in seg or 'shadow' in seg:
            got += 2
            notes.append('阴影 OK')
        else:
            notes.append('无阴影')
        return (2, '标题格式', got, 18, notes)

    def r3(self):
        got, notes = 0, []
        target = None
        for p in self.paras()[1:]:
            seg = self.pxml(p)
            rp = self.doc.run_props(list(p.iter(W + 'r'))[0], p) if list(p.iter(W + 'r')) else {}
            color = str(rp.get('color') or '').upper()
            if color.endswith('0000FF') or color.endswith('0070C0') or 'distribute' in seg or 'center' in seg:
                if len(self.ptext(p)) > 2:
                    target = p
                    break
        if target is None:
            return (3, '小标题格式', 0, 14, ['找不到小标题段'])
        seg = self.pxml(target)
        rp = self.doc.run_props(list(target.iter(W + 'r'))[0], target)
        font = rp.get('eastAsia') or rp.get('font') or ''
        if font == '楷体':
            got += 3
            notes.append('楷体 OK')
        else:
            notes.append('字体=%s' % font)
        if str(rp.get('size') or '') == '28':
            got += 2
            notes.append('四号 OK')
        else:
            notes.append('字号=%s' % rp.get('size'))
        if str(rp.get('color') or '').upper().endswith('FF0000'):
            got += 2
            notes.append('红色 OK')
        if re.search(r'<[a-z0-9]+:b[\s/>]', seg):
            got += 1
            notes.append('加粗 OK')
        if 'val="center"' in seg:
            got += 1
            notes.append('居中 OK')
        if 'before="200"' in seg and 'after="200"' in seg:
            got += 2
            notes.append('段前段后10磅 OK')
        else:
            notes.append('段前后=%s' % re.findall(r'(?:before|after)="(\d+)"', seg)[:2])
        if 'numPr' in seg:
            got += 3
            notes.append('项目编号 OK')
        else:
            notes.append('无编号')
        return (3, '小标题格式', got, 14, notes)

    def r4(self):
        got, notes = 0, []
        secs = self.doc.sections
        if len(secs) < 2:
            return (4, '分节与横向', 0, 10, ['只有1节'])
        got += 4
        notes.append('分节 OK')
        last = self.doc.page_setup(secs[-1])
        if last.get('orient') == 'landscape':
            got += 4
            notes.append('第二页横向 OK')
        else:
            notes.append('方向=%s' % last.get('orient'))
        v = {k: int(last.get(k) or 0) / 567 for k in ('top', 'bottom', 'left', 'right')}
        if abs(v['top'] - 2.54) < 0.2 and abs(v['left'] - 1.9) < 0.2:
            got += 2
            notes.append('页边距"适中" OK')
        else:
            notes.append('页边距 %.1f/%.1f/%.1f/%.1f' % (v['top'], v['bottom'], v['left'], v['right']))
        return (4, '分节与横向', got, 10, notes)

    def r5(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        if '<wp:anchor' not in full:
            return (5, '图片', 0, 16, ['没有浮动图片'])
        got += 3
        notes.append('浮动图片 OK')
        if 'wrapTight' in full or 'wrapSquare' in full:
            got += 3
            notes.append('紧密型环绕 OK')
        exts = [(int(a) / 360000, int(b) / 360000) for a, b in re.findall(r'ext cx="(\d+)" cy="(\d+)"', full)]
        heights = [h for w, h in exts]
        if any(abs(h - 8) < 0.5 for h in heights):
            got += 3
            notes.append('高度8cm OK')
        elif heights:
            notes.append('高度=%s cm' % [round(h, 1) for h in heights[:3]])
        if 'glow' in full:
            got += 3
            notes.append('发光 OK')
        else:
            notes.append('无发光')
        if re.search(r'<a:softEdge[^>]*rad="\d+"', full):
            got += 2
            notes.append('柔化边缘 OK')
        if re.search(r'<wp:positionH[^>]*relativeFrom="page"', full):
            got += 2
            notes.append('相对页面位置 OK')
        return (5, '图片', got, 16, notes)

    def r6(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        if 'txbxContent' not in full:
            return (6, '文本框', 0, 12, ['没有文本框'])
        got += 3
        notes.append('文本框 OK')
        hit = False
        dims = []
        for st in re.findall(r'style="([^"]*)"', full):
            mw = re.search(r'width:([\d.]+)pt', st)
            mh = re.search(r'height:([\d.]+)pt', st)
            if mw and mh:
                w_cm = float(mw.group(1)) / 28.35
                h_cm = float(mh.group(1)) / 28.35
                dims.append((round(w_cm, 1), round(h_cm, 1)))
                if abs(w_cm - 18) < 1.2 and abs(h_cm - 3.5) < 0.8:
                    hit = True
        if hit:
            got += 3
            notes.append('18×3.5cm OK')
        elif dims:
            notes.append('尺寸=%s' % dims[:3])
        if 'noFill' in full or 'filled="f"' in full:
            got += 2
            notes.append('无边框 OK')
        if 'accent4' in full or 'E2F0D9' in full.upper() or 'tint' in full:
            got += 2
            notes.append('浅绿底纹 OK')
        box = re.search(r'<w:txbxContent>(.*?)</w:txbxContent>', full, re.S)
        if box:
            txt = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', box.group(1)))
            if len(txt) > 10:
                got += 2
                notes.append('含正文内容 OK')
        return (6, '文本框', got, 12, notes)

    def r7(self):
        got, notes = 0, []
        hx = ''
        for n in self.doc.names:
            if 'header' in n and n.endswith('.xml'):
                c = self.doc.read(n)
                if '天台山' in c:
                    hx = c
                    break
        if not hx:
            return (7, '文字水印', 0, 8, ['没有水印'])
        got += 4
        notes.append('水印文字 OK')
        if '微软雅黑' in hx and '66pt' in hx:
            got += 2
            notes.append('微软雅黑66 OK')
        else:
            notes.append('字体字号未匹配')
        if 'rotation' in hx.lower() or 'v-text-align' in hx:
            got += 2
            notes.append('倾斜版式 OK')
        else:
            notes.append('版式未识别')
        return (7, '文字水印', got, 8, notes)

    def r8(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        if 'type="pattern"' in full:
            got += 4
            notes.append('图案背景 OK')
            if '网格' in full:
                got += 1
                notes.append('网格纹样 OK')
        else:
            notes.append('无图案背景')
        bg = re.search(r'<w:background[^>]*>', full)
        if bg and ('accent3' in bg.group(0) or 'FFF2CA' in bg.group(0).upper()):
            got += 2
            notes.append('橙色着色3 OK')
        odd = even = False
        for n in self.doc.names:
            if 'header' in n and n.endswith('.xml'):
                c = self.doc.read(n)
                if '人间萤火' in c:
                    odd = True
                if '山水天台' in c:
                    even = True
        if odd and even:
            got += 5
            notes.append('奇偶页眉 OK')
        elif odd or even:
            got += 2
            notes.append('只设一个页眉')
        return (8, '背景与页眉', got, 12, notes)


if __name__ == '__main__':
    sys.exit(run(WordGrader18, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Word 2010 操作题题库', '18', '1结果.docx')))
