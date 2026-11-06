# -*- coding: utf-8 -*-
"""从成绩单导出文档里抽 Windows / 网络 操作题，去重、清洗，存成 json 和 md。

用法：python tools/extract_win_questions.py <docx路径>
"""
import json
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE, 'windows_kb')

SEC_RE = re.compile(r'^[一二三四五六七八]、\s*([^\s（(]+)')
Q_RE = re.compile(r'^第(\d+)题\s*（([\d.]+)分）\s*题号[:：]\s*(\d+)')
ALT_Q_RE = re.compile(r'^【([^】]+)】\s*第(\d+)题\s*题号[:：]\s*(\d+)')
SEP_RE = re.compile(r'^[━\-=_]{6,}$')
NOISE = ('请在打开的窗口', '完成所有操作后', '注意：题干没有要求', '难度:', '考生得分',
         '本题标准分数', '标准答案:', '回答正确', '得分率')


def paragraphs(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read('word/document.xml'))
    out = []
    for p in root.iter(W + 'p'):
        t = ''.join(x.text or '' for x in p.iter(W + 't')).strip()
        if t:
            out.append(t)
    return out


def extract(path):
    qs = {}
    section = ''
    cur = None
    for t in paragraphs(path):
        m = SEC_RE.match(t)
        if m:
            section = m.group(1)
            cur = None
            continue
        mq = Q_RE.match(t)
        if mq:
            qid = mq.group(3)
            if qid not in qs:
                qs[qid] = {'qid': qid, 'section': section, 'no': int(mq.group(1)),
                           'score': float(mq.group(2)), 'items': []}
                cur = qid
            else:
                cur = None
            continue
        if not cur or SEP_RE.match(t) or any(n in t for n in NOISE):
            continue
        line = t.strip()
        if not line:
            continue
        ma = ALT_Q_RE.match(line)
        if ma:
            sec, no, qid = ma.group(1), ma.group(2), ma.group(3)
            if qid not in qs:
                qs[qid] = {'qid': qid, 'section': sec, 'no': int(no),
                           'score': 10.0, 'items': []}
            cur = qid
            continue
        if re.search(r'题号\s*[:：]', line):
            cur = None
            continue
        if line.startswith('【') or line.startswith('━'):
            cur = None
            continue
        items = qs[cur]['items']
        cont = (re.match(r'^\s*[)）]', line) or re.match(r'^\s*\d+\.\d', line)
                or re.match(r'^\s*[（(]', line))
        starts_num = re.match(r'^\s*\d{1,2}\s*[、.．]', line)
        if items and cont:
            items[-1] += line
        elif items and not starts_num and len(line) <= 40 and items[-1][-1] in '（(“"':
            items[-1] += line
        elif starts_num and line not in items:
            items.append(line)
        elif len(line) <= 40 and line not in items:
            items.append(line)
    return qs


def main():
    if len(sys.argv) < 2:
        print('用法: python tools/extract_win_questions.py <docx>')
        return 1
    qs = extract(sys.argv[1])
    os.makedirs(OUT_DIR, exist_ok=True)

    keep = {k: v for k, v in qs.items()
            if v['section'] in ('中英文打字', 'Windows', '网络') and v['items']}
    with open(os.path.join(OUT_DIR, 'questions.json'), 'w', encoding='utf-8') as f:
        json.dump(keep, f, ensure_ascii=False, indent=1)

    lines = ['# 中英文打字 / Windows / 网络 操作题（从成绩单文档抽取）', '']
    for sec in ('中英文打字', 'Windows', '网络'):
        group = [q for q in keep.values() if q['section'] == sec]
        group.sort(key=lambda x: (x['score'], int(x['qid'])))
        lines.append('## %s（%d 题）' % (sec, len(group)))
        lines.append('')
        for q in group:
            lines.append('### 题号 %s（%g 分）' % (q['qid'], q['score']))
            for it in q['items']:
                lines.append('- ' + it)
            lines.append('')
    with open(os.path.join(OUT_DIR, 'questions.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    from collections import Counter
    c = Counter(q['section'] for q in keep.values())
    print('保存 %d 题 → windows_kb/questions.json / questions.md' % len(keep))
    print('分布:', dict(c))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
