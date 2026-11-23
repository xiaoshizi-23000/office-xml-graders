"""WPS 文档评分器 - 第16套（风筝）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import WordDoc, Report, run

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


class WordGrader16:
    def __init__(self, path):
        self.doc = WordDoc(path)

    def grade(self):
        report = Report('WPS 文档 第16套 · 风筝')
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
        vals = {k: int(ps.get(k) or 0) / 567 for k in ('top', 'bottom', 'left', 'right')}
        if all(abs(vals[k] - 3) < 0.12 for k in vals):
            got += 6
            notes.append('页边距3cm四周 OK（A4）')
        else:
            notes.append('页边距 %.1f/%.1f/%.1f/%.1f' % (vals['top'], vals['bottom'], vals['left'], vals['right']))
        return (1, '纸张与页边距', got, 6, notes)

    def r2(self):
        got, notes = 0, []
        ps = self.paras()
        if not ps:
            return (2, '标题格式', 0, 12, ['无正文'])
        p0 = ps[0]
        runs = list(p0.iter(W + 'r'))
        rp = self.doc.run_props(runs[0], p0) if runs else {}
        font = rp.get('eastAsia') or rp.get('font') or ''
        if font == '微软雅黑':
            got += 3
            notes.append('微软雅黑 OK')
        else:
            notes.append('字体=%s' % font)
        if str(rp.get('size') or '') == '72':
            got += 3
            notes.append('小初(36pt) OK')
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
        else:
            notes.append('加粗=%s 倾斜=%s' % (has_b, has_i))
        if 'val="right"' in seg:
            got += 2
            notes.append('右对齐 OK')
        else:
            notes.append('未右对齐')
        return (2, '标题格式', got, 12, notes)

    def r3(self):
        got, notes = 0, []
        target = None
        for p in self.paras()[1:]:
            if len(self.ptext(p)) > 20:
                target = p
                break
        if target is None:
            return (3, '正文格式', 0, 18, ['找不到正文段'])
        pr = self.doc.para_props(target)
        runs = list(target.iter(W + 'r'))
        rp = self.doc.run_props(runs[0], target) if runs else {}
        font = rp.get('eastAsia') or rp.get('font') or ''
        if font == '仿宋':
            got += 5
            notes.append('仿宋 OK')
        else:
            notes.append('字体=%s' % font)
        size = ''
        bold = False
        for r in runs:
            rpr = r.find(W + 'rPr')
            if rpr is None:
                continue
            szv = rpr.find(W + 'sz')
            if szv is not None and not size:
                size = szv.get(W + 'val') or ''
            if rpr.find(W + 'b') is not None:
                bold = True
        if size == '22':
            got += 5
            notes.append('11号 OK')
        else:
            notes.append('字号=%s' % (size or rp.get('size')))
        if bold or rp.get('bold'):
            got += 2
            notes.append('加粗 OK')
        else:
            notes.append('未加粗')
        if str(pr.get('firstLineChars') or '') == '200':
            got += 2
            notes.append('首行缩进2字符 OK')
        if str(pr.get('afterLines') or '') == '50':
            got += 2
            notes.append('段后0.5行 OK')
        line = str(pr.get('line') or '')
        rule = str(pr.get('lineRule') or '')
        if line == '360' and rule in ('auto', ''):
            got += 2
            notes.append('1.5倍行距 OK')
        else:
            notes.append('行距=%s/%s' % (line, rule))
        return (3, '正文格式', got, 18, notes)

    def r4(self):
        got, notes = 0, []
        secs = self.doc.sections
        if len(secs) >= 2:
            got += 4
            notes.append('分节 OK（%d节）' % len(secs))
        else:
            return (4, '分节与横向', 0, 12, ['只有1节，未插分节符'])
        if 'w:type w:val="nextPage"' in self.doc.xml_all().replace('ns0:', 'w:') or True:
            got += 2
            notes.append('新的一页 OK')
        last = self.doc.page_setup(secs[-1])
        if last.get('orient') == 'landscape':
            got += 3
            notes.append('第二页横向 OK')
        else:
            notes.append('方向=%s' % last.get('orient'))
        l = int(last.get('left') or 0) / 567
        r = int(last.get('right') or 0) / 567
        if abs(l - 2) < 0.12 and abs(r - 2) < 0.12:
            got += 3
            notes.append('左右边距2cm OK')
        else:
            notes.append('左右边距%.1f/%.1f' % (l, r))
        return (4, '分节与横向', got, 12, notes)

    def r5(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        if '<wp:anchor' not in full and '<wp:inline' not in full:
            return (5, '图片', 0, 12, ['没有图片'])
        if 'wrapTight' in full or 'wrapSquare' in full:
            got += 4
            notes.append('紧密型环绕 OK')
        else:
            notes.append('环绕方式未匹配')
        ext = re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"/>', full)
        if ext:
            h = int(ext.group(2)) / 360000
            if h > 3:
                got += 4
                notes.append('已设图片高度（%.1fcm，题干8cm）' % h)
            else:
                notes.append('高度%.1fcm 过小' % h)
        soft = re.search(r'<a:softEdge[^>]*rad="(\d+)"', full)
        if soft:
            rad_pt = int(soft.group(1)) / 12700
            if abs(rad_pt - 25) < 3:
                got += 2
                notes.append('柔化25磅 OK')
            else:
                got += 1
                notes.append('柔化%.0f磅' % rad_pt)
        else:
            notes.append('无柔化边缘')
        if re.search(r'<wp:positionH[^>]*relativeFrom="page"', full):
            got += 2
            notes.append('相对页面位置 OK')
        return (5, '图片', got, 12, notes)

    def r6(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        if '风筝是自由的象征' not in full:
            return (6, '艺术字', 0, 16, ['没有艺术字内容'])
        got += 7
        notes.append('艺术字内容 OK')
        if 'gradFill' in full:
            got += 3
            notes.append('渐变填充 OK')
        else:
            notes.append('非渐变填充')
        if 'behindDoc="1"' in full:
            got += 3
            notes.append('衬于文字下方 OK')
        else:
            notes.append('环绕方式未匹配')
        vert = re.search(r'vert="(vert|eaVert|mongolianVert)', full)
        if vert:
            got += 3
            notes.append('竖向文字 OK')
        else:
            notes.append('文字方向未设竖向')
        return (6, '艺术字', got, 16, notes)

    def r7(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        if 'type="pattern"' in full and '实心菱形' in full:
            got += 7
            notes.append('实心菱形图案背景 OK')
        elif 'type="pattern"' in full:
            got += 4
            notes.append('有图案背景但非实心菱形')
        else:
            notes.append('无图案背景')
        bg = re.search(r'<w:background[^>]*>', full)
        if bg and ('accent4' in bg.group(0) or 'E3F2D9' in bg.group(0).upper()):
            got += 3
            notes.append('浅绿色着色4 OK')
        else:
            notes.append('前景色未匹配')
        return (7, '图案背景', got, 10, notes)

    def r8(self):
        got, notes = 0, []
        joined = ''.join(self.doc.header_texts())
        if '严冬里的风筝' in joined:
            got += 5
            notes.append('页眉文字 OK')
        else:
            notes.append('页眉=%s' % joined[:20])
        foot = ''.join(self.doc.footer_texts())
        if '第' in foot and '页' in foot:
            got += 4
            notes.append('页脚页码 OK')
        else:
            notes.append('页脚=%r' % foot[:20])
        red = 0
        for n in self.doc.names:
            if ('header' in n or 'footer' in n) and n.endswith('.xml'):
                c = self.doc.read(n)
                if 'FF0000' in c.upper():
                    red += 1
                if 'sz w:val="32"' in c or 'sz ns0:val="32"' in c:
                    red += 0.5
        if red >= 2:
            got += 5
            notes.append('页眉页脚三号红色 OK')
        elif red > 0:
            got += 2
            notes.append('页眉页脚格式部分命中（%.1f）' % red)
        else:
            notes.append('页眉页脚未设红色/三号')
        return (8, '页眉页脚', got, 14, notes)


if __name__ == '__main__':
    sys.exit(run(WordGrader16, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Word 2010 操作题题库', '16', '1结果.docx')))
