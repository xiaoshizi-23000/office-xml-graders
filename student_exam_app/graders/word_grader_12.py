"""WPS 文档评分器 - 第12套（生炒鳝鱼丝）"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import WordDoc, Report, run

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


class WordGrader12:
    def __init__(self, path):
        self.doc = WordDoc(path)

    def grade(self):
        report = Report('WPS 文档 第12套 · 生炒鳝鱼丝')
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
        ps = self.paras()
        if not ps:
            return (1, '标题格式', 0, 14, ['无正文'])
        p0 = ps[0]
        runs = list(p0.iter(W + 'r'))
        rp = self.doc.run_props(runs[0], p0) if runs else {}
        font = rp.get('eastAsia') or rp.get('font') or ''
        if font == '微软雅黑':
            got += 3
            notes.append('微软雅黑 OK')
        else:
            notes.append('字体=%s' % font)
        if str(rp.get('size') or '') == '96':
            got += 3
            notes.append('48号 OK')
        else:
            notes.append('字号=%s' % rp.get('size'))
        if str(rp.get('color') or '').upper().endswith('00B0F0'):
            got += 2
            notes.append('浅蓝色 OK')
        else:
            notes.append('颜色=%s' % rp.get('color'))
        seg = self.pxml(p0)
        has_b = bool(re.search(r'<[a-z0-9]+:b\s*/?>', seg)) or bool(re.search(r'<w:b/>', seg))
        has_i = bool(re.search(r'<[a-z0-9]+:i\s*/?>', seg)) or bool(re.search(r'<w:i/>', seg))
        if has_b and has_i:
            got += 2
            notes.append('加粗倾斜 OK')
        else:
            notes.append('加粗=%s 倾斜=%s' % (has_b, has_i))
        if 'outlineLvl' in seg:
            got += 2
            notes.append('大纲1级 OK')
        else:
            notes.append('无大纲级别')
        if 'algn="l"' in seg or 'val="left"' in seg:
            got += 2
            notes.append('左对齐 OK')
        else:
            notes.append('未左对齐')
        return (1, '标题格式', got, 14, notes)

    def r2(self):
        got, notes = 0, []
        ps = self.paras()
        target = None
        for p in ps:
            if self.ptext(p).startswith('鳝为我国特产'):
                target = p
                break
        if target is None:
            return (2, '正文格式', 0, 16, ['找不到正文段'])
        pr = self.doc.para_props(target)
        runs = list(target.iter(W + 'r'))
        rp = self.doc.run_props(runs[0], target) if runs else {}
        font = rp.get('eastAsia') or rp.get('font') or ''
        seg = self.pxml(target)
        if not font or font == 'zh-CN':
            m = re.search(r'rFonts[^>]*eastAsia="([^"]*)"', seg)
            font = m.group(1) if m else ''
        if font == '等线':
            got += 3
            notes.append('等线 OK')
        elif font:
            got += 2
            notes.append('字体=%s（题干要求等线）' % font)
        else:
            notes.append('字体未显式设置')
        if str(rp.get('size') or '') == '28':
            got += 3
            notes.append('四号 OK')
        else:
            notes.append('字号=%s' % rp.get('size'))
        if str(pr.get('firstLineChars') or '') == '200':
            got += 3
            notes.append('首行缩进2字符 OK')
        else:
            notes.append('缩进=%s' % (pr.get('firstLineChars') or pr.get('firstLine')))
        if str(pr.get('afterLines') or '') == '50':
            got += 3
            notes.append('段后0.5行 OK')
        else:
            notes.append('段后=%s' % pr.get('afterLines'))
        if str(pr.get('line') or '') == '320' and pr.get('lineRule') == 'atLeast':
            got += 4
            notes.append('行距最小16磅 OK')
        else:
            notes.append('行距=%s/%s' % (pr.get('line'), pr.get('lineRule')))
        return (2, '正文格式', got, 16, notes)

    def r3(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        if 'glow' in full:
            got += 6
            notes.append('发光效果 OK')
        else:
            notes.append('无发光')
        fr = re.search(r'<w:framePr[^/]*w:dropCap="drop"[^/]*/>', full)
        if fr:
            got += 3
            notes.append('首字下沉 OK')
            m = re.search(r'w:lines="(\d+)"', fr.group(0))
            if m and m.group(1) == '3':
                got += 3
                notes.append('下沉3行 OK')
            else:
                notes.append('行数=%s' % (m.group(1) if m else '?'))
        else:
            notes.append('无首字下沉')
        return (3, '发光与首字下沉', got, 12, notes)

    def r4(self):
        got, notes = 0, []
        found = ''
        for p in self.paras():
            seg = self.pxml(p)
            if 'pBdr' in seg:
                m = re.search(r'pBdr.*?</[a-z0-9]+:pBdr>', seg, re.S)
                if m:
                    found = m.group(0)
                    break
        if not found:
            return (4, '段落边框', 0, 10, ['没有段落边框'])
        if 'dotted' in found:
            got += 4
            notes.append('点线 OK')
        else:
            notes.append('线型未识别')
        if '00B0F0' in found.upper():
            got += 3
            notes.append('浅蓝色 OK')
        else:
            notes.append('颜色未匹配')
        if 'sz="24"' in found:
            got += 3
            notes.append('3磅 OK')
        else:
            notes.append('线宽=%s' % re.findall(r'sz="(\d+)"', found)[:2])
        return (4, '段落边框', got, 10, notes)

    def r5(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        n = 0
        for p in self.paras():
            if 'numPr' in self.pxml(p):
                n += 1
        if n >= 3:
            got += 5
            notes.append('编号段落 %d 个 OK' % n)
        elif n:
            got += 3
            notes.append('编号段落 %d 个' % n)
        else:
            notes.append('无编号')
        num_xml = self.doc.read('word/numbering.xml') if 'word/numbering.xml' in self.doc.names else ''
        if 'chineseCounting' in num_xml or 'chineseCountingThousand' in num_xml:
            got += 4
            notes.append('中文数字编号 OK')
        else:
            notes.append('编号格式=%s' % re.findall(r'numFmt w:val="([^"]*)"', num_xml)[:3])
        if re.search(r'<w:start w:val="2"', num_xml):
            got += 3
            notes.append('起始编号2 OK')
        else:
            notes.append('起始=%s' % re.findall(r'<w:start w:val="(\d+)"', num_xml)[:2])
        return (5, '项目编号', got, 12, notes)

    def r6(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        if '<wp:anchor' not in full:
            return (6, '图片', 0, 16, ['没有浮动图片'])
        got += 4
        notes.append('浮动图片 OK')
        if 'wrapThrough' in full or 'wrapTight' in full:
            got += 3
            notes.append('穿越型环绕 OK')
        else:
            notes.append('环绕方式未匹配')
        ext = re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"/>', full)
        if ext:
            h = int(ext.group(2)) / 360000
            if abs(h - 9) < 0.4:
                got += 3
                notes.append('高度9cm OK')
            else:
                notes.append('高度%.1fcm' % h)
        pic = re.search(r'<pic:spPr>.*?</pic:spPr>', full, re.S)
        if pic and 'FF0000' in pic.group(0).upper() and 'w="' in pic.group(0):
            got += 3
            notes.append('红色5磅边框 OK')
        else:
            notes.append('边框未匹配')
        if re.search(r'<a:softEdge[^>]*rad="\d+"', full):
            got += 3
            notes.append('柔化边缘 OK')
        else:
            notes.append('无柔化边缘')
        return (6, '图片', got, 16, notes)

    def r7(self):
        got, notes = 0, []
        header_xml = ''
        for n in self.doc.names:
            if 'header' in n and n.endswith('.xml'):
                c = self.doc.read(n)
                if '雅舍谈吃' in c:
                    header_xml = c
                    break
        if not header_xml:
            return (7, '文字水印', 0, 10, ['没有水印'])
        got += 6
        notes.append('水印文字 OK')
        if '00B0F0' in header_xml.upper():
            got += 2
            notes.append('浅蓝 OK')
        if '黑体' in header_xml and '44pt' in header_xml:
            got += 2
            notes.append('黑体44 OK')
        return (7, '文字水印', got, 10, notes)

    def r8(self):
        got, notes = 0, []
        full = self.doc.xml_all()
        bg = re.search(r'<w:background[^/]*/>', full)
        if bg:
            got += 5
            notes.append('渐变背景 OK（%s）' % bg.group(0)[:60])
        else:
            notes.append('无页面背景')
        joined = ''.join(self.doc.header_texts())
        if '梁实秋雅舍系列节选' in joined:
            got += 3
            notes.append('页眉文字 OK')
        else:
            notes.append('页眉=%s' % joined[:24])
        red_header = False
        for n in self.doc.names:
            if 'header' in n and n.endswith('.xml'):
                if 'FF0000' in self.doc.read(n).upper():
                    red_header = True
                    break
        if red_header:
            got += 2
            notes.append('页眉红色 OK')
        else:
            notes.append('页眉未设红色')
        return (8, '背景与页眉', got, 10, notes)


if __name__ == '__main__':
    sys.exit(run(WordGrader12, default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Word 2010 操作题题库', '12', '1结果.docx')))
