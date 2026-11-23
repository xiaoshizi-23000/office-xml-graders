"""WPS 文档评分器 - 第15套（前尘隔海）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import WordDoc, Report, run

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


class WordGrader15:
    def __init__(self, path):
        self.doc = WordDoc(path)

    def grade(self):
        report = Report('WPS 文档 第15套 · 前尘隔海')
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
        if abs(w - 12472) <= 40 and abs(h - 14173) <= 40:
            got += 5
            notes.append('22×25cm 纸张 OK')
        else:
            notes.append('纸张=%dx%d twips' % (w, h))
        l = int(ps.get('left') or 0) / 567
        r = int(ps.get('right') or 0) / 567
        if abs(l - 3) < 0.12 and abs(r - 3) < 0.12:
            got += 5
            notes.append('左右边距3cm OK')
        else:
            notes.append('左右边距%.1f/%.1f' % (l, r))
        return (1, '纸张与边距', got, 10, notes)

    def r2(self):
        got, notes = 0, []
        ps = self.paras()
        if not ps:
            return (2, '标题格式', 0, 16, ['无正文'])
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
        if str(rp.get('color') or '').upper().endswith('FF0000'):
            got += 2
            notes.append('红色 OK')
        else:
            notes.append('颜色=%s' % rp.get('color'))
        seg = self.pxml(p0)
        u = re.search(r'<[a-z0-9]+:u ([^/]*)/>', seg)
        if u and 'double' in u.group(1) and '00B0F0' in u.group(1).upper():
            got += 3
            notes.append('双横线浅蓝下划线 OK')
        elif u and 'double' in u.group(1):
            got += 2
            notes.append('双线但颜色不符')
        else:
            notes.append('下划线未匹配')
        if 'val="center"' in seg:
            got += 1
            notes.append('居中 OK')
        sp = re.findall(r'spacing[^>]*val="(\d+)"', seg)
        if sp and abs(int(sp[0]) - 113) <= 8:
            got += 2
            notes.append('字符间距0.2cm OK')
        else:
            notes.append('间距=%s' % (sp[:1] or '无'))
        has_b = bool(re.search(r'<[a-z0-9]+:b[\s/>]', seg))
        has_i = bool(re.search(r'<[a-z0-9]+:i[\s/>]', seg))
        if has_b and has_i:
            got += 2
            notes.append('加粗倾斜 OK')
        return (2, '标题格式', got, 16, notes)

    def r3(self):
        got, notes = 0, []
        target = None
        for p in self.paras()[1:]:
            if len(self.ptext(p)) > 20:
                target = p
                break
        if target is None:
            return (3, '正文格式', 0, 16, ['找不到正文段'])
        pr = self.doc.para_props(target)
        runs = list(target.iter(W + 'r'))
        rp = self.doc.run_props(runs[0], target) if runs else {}
        font = rp.get('eastAsia') or rp.get('font') or ''
        if font == '仿宋':
            got += 3
            notes.append('仿宋 OK')
        else:
            notes.append('字体=%s' % font)
        size = ''
        caps = False
        for r in runs:
            rpr = r.find(W + 'rPr')
            if rpr is None:
                continue
            szv = rpr.find(W + 'sz')
            if szv is not None and not size:
                size = szv.get(W + 'val') or ''
            if rpr.find(W + 'caps') is not None:
                caps = True
        if size == '28':
            got += 4
            notes.append('四号 OK')
        else:
            notes.append('字号=%s' % (size or rp.get('size')))
        if caps:
            got += 3
            notes.append('全部大写 OK')
        else:
            notes.append('未设全部大写')
        if str(pr.get('firstLineChars') or '') == '200':
            got += 2
            notes.append('首行缩进2字符 OK')
        if str(pr.get('beforeLines') or '') == '50' and str(pr.get('afterLines') or '') == '50':
            got += 2
            notes.append('段前段后0.5行 OK')
        elif str(pr.get('before') or '') == '100' and str(pr.get('after') or '') == '100':
            got += 2
            notes.append('段前段后5磅 OK')
        if str(pr.get('line') or '') == '360' and pr.get('lineRule') == 'exact':
            got += 2
            notes.append('固定值18磅 OK')
        else:
            notes.append('行距=%s/%s' % (pr.get('line'), pr.get('lineRule')))
        return (3, '正文格式', got, 16, notes)

    def r4(self):
        got, notes = 0, []
        if 'word/endnotes.xml' not in self.doc.names:
            return (4, '尾注', 0, 8, ['无尾注部件'])
        ex = self.doc.read('word/endnotes.xml')
        if '标志春雷' in ex or '春雷始鸣' in ex:
            got += 6
            notes.append('尾注内容 OK')
        else:
            got += 2
            notes.append('有尾注但内容不符')
        if '<w:endnoteReference' in self.doc.xml_all():
            got += 2
            notes.append('正文引用 OK')
        return (4, '尾注', got, 8, notes)

    def r5(self):
        got, notes = 0, []
        cols = re.findall(r'<w:cols([^/]*)/>', self.doc.xml_all())
        three = [c for c in cols if 'num="3"' in c]
        if three:
            got += 6
            notes.append('3栏 OK')
            c = three[0]
            if 'sep="1"' in c:
                got += 2
                notes.append('分割线 OK')
            else:
                notes.append('无分割线')
            if 'equalWidth' in c or 'w:space="210"' in c or 'space="210"' in c:
                got += 2
                notes.append('栏间距1字符 OK')
        else:
            notes.append('分栏未设置（cols=%s）' % cols[:2])
        return (5, '分栏', got, 10, notes)

    def r6(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        if 'blipFill' not in full:
            return (6, '同侧圆角矩形', 0, 16, ['没有图片填充形状'])
        if 'round2SameRect' in full or 'roundRect' in full:
            got += 4
            notes.append('同侧圆角矩形 OK')
        else:
            got += 2
            notes.append('形状类型未识别')
        ext = re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"/>', full)
        if ext:
            w = int(ext.group(1)) / 360000
            h = int(ext.group(2)) / 360000
            if abs(w - 6) < 0.5 and abs(h - 8) < 0.5:
                got += 4
                notes.append('6×8cm OK')
            else:
                notes.append('尺寸%.1f×%.1fcm' % (w, h))
        if 'wrapTight' in full or 'wrapSquare' in full:
            got += 2
            notes.append('紧密型环绕 OK')
        if re.search(r'<a:softEdge[^>]*rad="\d+"', full):
            got += 2
            notes.append('柔化边缘 OK')
        if 'rotRev' in full or 'camera' in full.lower():
            got += 2
            notes.append('左透视 OK')
        if 'alpha' in full.lower():
            got += 2
            notes.append('透明度 OK')
        return (6, '同侧圆角矩形', got, 16, notes)

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
            if not (self.ptext(p).startswith('中国现代散文家') or self.ptext(p).startswith('代表作品')):
                continue
            seg = self.pxml(p)
            if 'shd' in seg and ('00B0F0' in seg.upper() or 'DDEBF7' in seg.upper() or 'themeFill' in seg):
                found = True
        if found:
            got += 4
            notes.append('浅蓝底纹 OK')
        else:
            notes.append('底纹未匹配')
        return (7, '末尾段落与底纹', got, 8, notes)

    def r8(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        if 'type="gradient"' in full:
            got += 8
            notes.append('渐变背景 OK')
            if 'FADBDF' in full.upper() or 'accent6' in full:
                got += 2
                notes.append('颜色1/2 OK')
        else:
            notes.append('无渐变背景')
        joined = ''.join(self.doc.header_texts())
        if '前尘隔海' in joined:
            got += 3
            notes.append('页眉文字 OK')
        else:
            notes.append('页眉=%s' % joined[:20])
        left_red = False
        for n in self.doc.names:
            if 'header' in n and n.endswith('.xml'):
                c = self.doc.read(n)
                if '前尘隔海' in c and 'FF0000' in c.upper() and ('left' in c or 'jc' in c):
                    left_red = True
        if left_red:
            got += 2
            notes.append('页眉左对齐红色 OK')
        foot = ''.join(self.doc.footer_texts())
        fnum = any('PAGE' in self.doc.read(n) or 'NUMPAGES' in self.doc.read(n)
                   for n in self.doc.names if 'footer' in n and n.endswith('.xml'))
        if '共' in foot or fnum:
            got += 3
            notes.append('页脚页码 OK')
        else:
            notes.append('页脚=%r' % foot[:20])
        return (8, '背景与页眉页脚', got, 16, notes)


if __name__ == '__main__':
    sys.exit(run(WordGrader15, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Word 2010 操作题题库', '15', '1结果.docx')))
