# -*- coding: utf-8 -*-
"""把题库整理成"每个程序 5 题、每题 5 条"的整齐结构。

做法：汇总现有题库里所有能判的条目 → 按 (程序, key) 去重 → 每程序切 5 题，
不足 25 条时用程序自身 key 池的备选值补齐（与专项练习同一套规则）。
"""
import json
import glob
import os
import re

import sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_manual_questions import ALT, KEY_PHRASE, polish_name as polish


def variants(key, info):
    d = info['default']
    if d in ('0', '1'):
        return ['1' if d == '0' else '0']
    return [v for v in ALT.get(key, []) if v != d][:2]
KB = os.path.join(BASE, 'windows_kb')
PROGS = os.path.join(KB, 'progs')
RULES = os.path.join(KB, 'rules')

GROUPS = {
    '网络': ['iesxWin7', 'wangluoWin7', 'bhsxWin7', 'jlljWin7'],
    'Windows': ['qyszWin7', 'rwlsxWin7', 'xianshiWin7', 'srfWin7', 'tjdyjWin7', 'outlook'],
}
TITLES = {
    'iesxWin7': 'Internet 选项', 'wangluoWin7': '网络 IPv4', 'bhsxWin7': '宽带连接',
    'jlljWin7': '连接向导', 'qyszWin7': '区域和语言', 'rwlsxWin7': '任务栏和开始菜单',
    'xianshiWin7': '显示和主题', 'srfWin7': '输入法和语言栏', 'tjdyjWin7': '打印机',
    'outlook': '邮件设置',
}
# 程序内 key 的补充取值（去重后不够 25 条时用来凑数）
EXTRA = {
    'tjdyjWin7': [('PrintNameSetup', 'Easy'), ('PrintNameSetup', 'Printer01'),
                  ('SelectPrintPort', 'USB001'), ('SelectPrintPort', 'COM1:(串行端口)'),
                  ('PrintShareSetup', '1'), ('DefaultPrint', '1'), ('TestPage', '1')],
}


def load_keys(prog):
    out = {}
    for line in open(os.path.join(PROGS, prog + '.txt'), 'rb').read().decode('gbk').splitlines():
        p = line.split('□')
        if len(p) >= 3 and p[1].strip():
            out[p[1].strip()] = {'path': p[0].strip(), 'default': p[2].strip()}
    return out


ON_WORDS = ('启用', '勾选', '允许', '显示', '打开', '开启')
OFF_WORDS = ('禁用', '取消', '不允许', '隐藏', '关闭', '禁止')


def fix_region_key(it, key):
    t = it['text']
    if key.startswith('aq_'):
        if '本地Intranet' in t or '本地 intranet' in t.lower():
            return 'aq_intranetevel'
        if '可信站点' in t:
            return 'aq_crediblelevel'
        if '受限站点' in t:
            return 'aq_boundlevel'
        if 'Internet' in t:
            return 'aq_internetlevel'
    return key


def sanitize(it, info, key):
    """按清单的取值形态修正或丢弃条目。"""
    d = info['default']
    e = (it.get('expect') or '').strip()
    seg = info['path'].split('>')[-1].strip()
    # 文本必须和 key 的中文名有交集，否则说明匹配错了
    core = seg.replace('IPv4设置', '').replace('是否', '')
    if core and not any(ch in it['text'] for ch in core[:3]):
        return None
    if key == 'keepwebsite':
        it['expect'] = '1'
        return it
    if d in ('0', '1'):
        if e in ('0', '1'):
            return it
        if any(w in it['text'] for w in ON_WORDS):
            it['expect'] = '1'
            return it
        if any(w in it['text'] for w in OFF_WORDS):
            it['expect'] = '0'
            return it
        return None
    if not e or e in ('启用', '禁用') or len(e) > 24:
        return None
    return it


def collect():
    """从现有题库收集可判条目，按 (prog, key) 去重，保留最长的表述。"""
    best = {}
    for f in glob.glob(os.path.join(RULES, 'w*.json')):
        r = json.load(open(f, encoding='utf-8'))
        prog = r.get('prog')
        if not prog:
            continue
        for it in r['items']:
            k = it.get('key')
            if not k or not it.get('expect'):
                continue
            cur = best.get((prog, k))
            if cur is None or len(it['text']) > len(cur['text']):
                best[(prog, k)] = {'text': it['text'], 'key': k,
                                   'expect': it['expect'], 'path': it.get('path', '')}
    return best


def main():
    best = collect()
    total_q = 0
    index = []
    for section, progs in GROUPS.items():
        for prog in progs:
            keys = load_keys(prog)
            cands = []
            for k, info in keys.items():
                if k.startswith('gj_') or k.startswith('security_internet_'):
                    continue
                bank = best.get((prog, k))
                if bank:
                    b = dict(bank, src='bank')
                    b['key'] = fix_region_key(b, k)
                    info2 = keys.get(b['key'], info)
                    cleaned = sanitize(b, info2, b['key'])
                    if cleaned:
                        cands.append(cleaned)
                for want in variants(k, info):
                    tpl = KEY_PHRASE.get(k)
                    if info['default'] in ('0', '1'):
                        nm = tpl if tpl and '{v}' not in tpl else polish(info['path'])
                        text = '%s设置为：%s' % (nm, '启用' if want == '1' else '禁用')
                    elif tpl:
                        text = tpl.format(v=want) if '{v}' in tpl else '%s设置为：%s' % (tpl, want)
                    else:
                        text = '%s设置为：%s' % (polish(info['path']), want)
                    cands.append({'text': text, 'key': k, 'expect': want,
                                  'path': info['path'], 'src': 'auto'})
            # 排序：真题优先，其次自动
            cands.sort(key=lambda x: (x['src'] != 'bank', x['key']))
            pool = []
            cursor = 0
            for qi in range(5):
                chunk = []
                scan = 0
                while len(chunk) < 5 and scan < len(cands) * 2:
                    c = cands[cursor % len(cands)]
                    cursor += 1
                    scan += 1
                    if any(x['key'] == c['key'] for x in chunk):
                        continue
                    chunk.append(c)
                pool.append(chunk)

            for qi in range(5):
                chunk = pool[qi] if qi < len(pool) else []
                if len(chunk) < 3:
                    continue
                qid = 'n%s%d' % (prog, qi + 1)
                items = []
                for n, it in enumerate(chunk, 1):
                    text = re.sub(r'^\s*\d+\s*[、.．]\s*', '', it['text'])
                    items.append({'text': '%d、%s' % (n, text), 'key': it['key'],
                                  'path': it.get('path', ''), 'expect': it['expect'],
                                  'score': 1, 'how': 'bank'})
                rule = {'id': qid, 'section': section, 'group': prog, 'qid': qid,
                        'score': len(items), 'prog': prog,
                        'title': '%s · 第 %d 题' % (TITLES[prog], qi + 1),
                        'items': items, 'matched': len(items), 'covered': True}
                json.dump(rule, open(os.path.join(RULES, qid + '.json'), 'w', encoding='utf-8'),
                          ensure_ascii=False, indent=1)
                index.append({'id': qid, 'section': section, 'group': prog,
                              'qid': '%s-%d' % (prog, qi + 1), 'score': len(items),
                              'prog': prog, 'title': rule['title'], 'total': len(items),
                              'texts': [i['text'] for i in items]})
                total_q += 1
            print('%-12s 池 %2d 条 → %d 题' % (prog, len(pool), sum(1 for i in index if i['group'] == prog)))

    json.dump(index, open(os.path.join(KB, 'bank_index.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('合计', total_q, '题')


if __name__ == '__main__':
    main()
