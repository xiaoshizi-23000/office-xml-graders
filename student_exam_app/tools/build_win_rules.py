# -*- coding: utf-8 -*-
"""把提取出的题目条目映射到各程序的清单 key，生成判分规则草稿。

用法：python tools/build_win_rules.py [网络|Windows|all]
输出：windows_kb/rules/<qid>.json，以及一份 _report.md 供人工校对。
"""
import difflib
import json
import os
import re
import sys
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB = os.path.join(BASE, 'windows_kb')
PROGS = os.path.join(KB, 'progs')
RULES = os.path.join(KB, 'rules')

# 题目 → 程序：按关键词判断，顺序即优先级
PROG_KW = [
    ('wangluoWin7', ('IPv4', 'IP地址', 'DNS', '网关', '子网掩码')),
    ('jlljWin7', ('设置连接或网络', 'PPPoE', '连接名称', '连接到 Internet', '连接到Internet', '电话号码')),
    ('bhsxWin7', ('宽带连接', '拨号', '连接的用户名', '重播')),
    ('iesxWin7', ('主页', '历史记录', 'Cookie', '安全级别', '弹出窗口', '自动完成',
                  '临时文件', '代理服务器', '选项卡', 'HTML编辑器')),
    ('tjdyjWin7', ('打印机', '打印端口', '共享名')),
    ('xianshiWin7', ('主题', '桌面背景', '分辨率', '屏幕保护', 'DPI', '文本大小')),
    ('rwlsxWin7', ('任务栏', '开始菜单', '通知区域', 'Aero')),
    ('qyszWin7', ('区域', '度量衡', '日期格式', '时间格式', '货币', '数字')),
    ('srfWin7', ('输入法', '语言栏', '键盘')),
    ('outlook', ('邮件', '收件人', '抄送', '附件')),
]

# 条目 → key 的强规则（key, 触发词, 期望值提取正则）
KEY_HINTS = [
    ('homepage', ('主页',), r'(?:www\.|https?://)[\w\.\-/]+'),
    ('temp_review_jlts', ('历史记录中的天数', '历史记录保存天数', '保存在历史记录'), r'(\d+)'),
    ('temp_review_cpkj', ('磁盘', '使用的磁盘空间'), r'(\d+)'),
    ('keepwebsite', ('退出时删除浏览', '退出时删除'), None),
    ('upblock_stoplevel', ('阻止级别',), r'(\d+)'),
    ('upblock_website', ('允许的站点', '允许的网站'), r'([\w\.\-]+\.\w+)'),
    ('aq_internetlevel', ('Internet区域的安全级别', '安全级别'), None),
    ('cx_html', ('HTML编辑器', 'HTML 编辑器'), r'[“"]([^”"]+)[”"]'),
    ('lan_vpn', ('代理服务器',), None),
    ('auto_address', ('自动完成', '地址栏'), None),
    ('auto_use', ('用户名和密码',), None),
    ('auto_pass', ('保存密码之前',), None),
    ('Ipv4_IpAddress', ('IP地址',), r'(\d{1,3}(?:\.\d{1,3}){3})'),
    ('Ipv4_Mask', ('子网掩码',), r'(\d{1,3}(?:\.\d{1,3}){3})'),
    ('Ipv4_Gateway', ('默认网关', '网关'), r'(\d{1,3}(?:\.\d{1,3}){3})'),
    ('Ipv4_MainDNS', ('首选DNS', 'DNS服务器'), r'(\d{1,3}(?:\.\d{1,3}){3})'),
    ('Ipv4_SubDNS', ('备用DNS',), r'(\d{1,3}(?:\.\d{1,3}){3})'),
    ('connect_username', ('用户名',), r'[：:]\s*([\w\.\-@]+)'),
    ('connect_password', ('密码',), r'[：:]\s*([\w\.\-@]+)'),
    ('PPPoEConnName', ('连接名称',), r'[“"]([^”"]+)[”"]'),
    ('PPPoEUserName', ('用户名',), r'[：:]\s*([\w\.\-@]+)'),
    ('PPPoEPassword', ('密码',), r'[：:]\s*([\w\.\-@]+)'),
    ('PrintNameSetup', ('打印机名称', '打印机名'), r'[：:]\s*([^\s，。]+)'),
    ('PrintShareSetup', ('共享',), r'[：:]\s*([^\s，。]+)'),
]

STEP_WORDS = ('连接到 Internet', '连接到Internet', '宽带PPPoE', '宽带 PPPoE', '下一步',
              '点击', '单击', '选择“', '打开窗口', '关闭窗口')


def is_step(text):
    return any(w in text for w in STEP_WORDS) and not re.search(r'[：:]|设置为|设为', text)


ITEM_SPLIT = re.compile(r'(?<![0-9])(?:^|[；;])\s*(?=\d{1,2}\s*[、．]\s*(?!\d))')


def load_progs():
    out = {}
    for name in os.listdir(PROGS):
        if not name.endswith('.txt'):
            continue
        prog = name[:-4]
        keys = {}
        with open(os.path.join(PROGS, name), 'rb') as f:
            raw = f.read()
        for enc in ('gbk', 'utf-8', 'utf-16'):
            try:
                text = raw.decode(enc)
                break
            except Exception:
                text = ''
        for line in text.splitlines():
            parts = line.split('□')
            if len(parts) >= 2 and parts[1].strip():
                keys[parts[1].strip()] = {'path': parts[0].strip(),
                                          'default': parts[2].strip() if len(parts) > 2 else ''}
        out[prog] = keys
    return out


def pick_prog(text, progs):
    for prog, kws in PROG_KW:
        if prog in progs and any(k in text for k in kws):
            return prog
    return ''


def split_items(q):
    """把题目的条目拆成单条要求（有的行里塞了 1、2、3）。"""
    out = []
    for raw in q['items']:
        parts = re.split(r'(?<![0-9.])(?=\d{1,2}\s*[、．]\s*(?!\d))', raw)
        for p in parts:
            p = p.strip(' ；;')
            if len(p) >= 4:
                out.append(p)
    return out




def key_keywords(prog, key, path):
    """从中文路径里抽关键词：去掉程序名前缀和"设置"等虚词。"""
    seg = path.split('>')[-1].strip()
    for pre in ('IPv4设置', 'IPv6设置', 'IPv4高级设置', 'IPv6高级设置', 'IPv4', 'IPv6'):
        if seg.startswith(pre):
            seg = seg[len(pre):]
    seg = seg.replace('是否', '').strip()
    words = [seg]
    if 'DNS' in seg:
        words.append('DNS')
    if 'WINS' in seg:
        words.append('WINS')
    return [w for w in words if len(w) >= 2]


def match_by_path(text, keys, prog):
    best, score = '', 0
    for key, info in keys.items():
        for w in key_keywords(prog, key, info['path']):
            if w and w in text and len(w) > score:
                best, score = key, len(w)
    return best

ADV = json.load(open(os.path.join(KB, 'advanced_items.json'), encoding='utf-8')) if os.path.exists(os.path.join(KB, 'advanced_items.json')) else {}


def match_advanced(text):
    """题目条目里出现某个高级页项名 → key=对应分组，期望值=项名原样（含 *）。"""
    best_g, best_name = '', ''
    for g, names in ADV.items():
        for nm in names:
            if nm.startswith('- ') or len(nm) < 6:
                continue
            nm_clean = nm.strip()
            if nm_clean in text and len(nm_clean) > len(best_name):
                best_g, best_name = g, nm_clean
    if best_g:
        return best_g, best_name
    # 兜底：条目较短时，找包含它的项名（如“启用内存保护帮助减少联机攻击”匹配带 * 的）
    for g, names in ADV.items():
        for nm in names:
            nm_clean = nm.strip()
            if len(text) >= 8 and text in nm_clean and len(nm_clean) - len(text) <= 2:
                return g, nm_clean
    return '', ''


def guess_key(text, keys, prog=""):
    """先走强规则，再按中文路径相似度兜底。"""
    for key, words, pat in KEY_HINTS:
        if key in keys and any(w in text for w in words):
            return key, 'rule'
    adv_g, adv_name = match_advanced(text)
    if adv_g and adv_g in keys:
        return adv_g, 'adv'
    hit = match_by_path(text, keys, prog)
    if hit:
        return hit, 'path'
    best, score = '', 0.0
    for key, info in keys.items():
        seg = info['path'].split('>')[-1].strip()
        for w in (seg, seg[:4] if len(seg) >= 5 else seg):
            if len(w) >= 4 and w in text and len(w) > score:
                best, score = key, len(w)
    if best:
        return best, 'short'
    for key, info in keys.items():
        s = difflib.SequenceMatcher(None, text, info['path']).ratio()
        if s > score:
            best, score = key, s
    return (best, 'fuzzy') if score >= 0.42 else ('', '')


SWITCH_ON = ('启用', '勾选', '允许', '显示', '打开', '开启')
SWITCH_OFF = ('禁用', '取消', '不允许', '隐藏', '关闭', '禁止')


def guess_expect(text, default, path=''):
    q = re.search(r'[“"]([^”"]{1,40})[”"]', text)
    if q:
        v = q.group(1).strip()
        if default in ('0', '1'):
            return '1' if v != default else '0'
        return v
    m = re.search(r'设置为[：: ]*([\w\.\-/:％%]+)', text)
    if m:
        return m.group(1).strip()
    if default in ('0', '1'):
        if any(w in text for w in SWITCH_OFF):
            return '0'
        if any(w in text for w in SWITCH_ON):
            return '1'
        # 题目直接写了这个设置项的名字（如“锁定任务栏”）→ 就是要启用它
        tail = path.split('>')[-1].strip().replace('是否', '')
        if len(tail) >= 4 and tail[:4] in text:
            return '1'
        if ('不' + tail[:2]) in text or ('取消' + tail[:2]) in text:
            return '0'
        return ''


def extract_expect(text, key, pat):
    text = re.sub(r'^\s*\d{1,2}\s*[、.．]\s*', '', text)   # 去掉条目序号，否则会被当成数值
    if pat:
        m = re.search(pat, text)
        if m:
            return m.group(1) if m.groups() else m.group(0)
    return ''


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else '网络'
    progs = load_progs()
    qs = json.load(open(os.path.join(KB, 'questions.json'), encoding='utf-8'))
    os.makedirs(RULES, exist_ok=True)

    picked = [q for q in qs.values()
              if (which == 'all' or q['section'] == which) and q['section'] != '中英文打字']
    report, stat = [], Counter()
    made = 0

    for q in sorted(picked, key=lambda x: int(x['qid'])):
        text_all = ' '.join(q['items'])
        prog = pick_prog(text_all, progs)
        if not prog:
            stat['无对应程序'] += 1
            continue
        keys = progs[prog]
        items = split_items(q)
        if not items:
            continue
        judge_items = [i for i in items if not is_step(i)]
        unit = round(q['score'] / max(len(judge_items), 1), 2)
        rule = {'id': 'w%s' % q['qid'], 'section': q['section'], 'qid': q['qid'],
                'score': q['score'], 'prog': prog, 'title': '%s 第 %s 题' % (q['section'], q['qid']),
                'items': []}
        for it in items:
            if is_step(it):
                rule['items'].append({'text': it, 'key': '', 'step': True, 'score': 0,
                                      'path': '', 'expect': '', 'how': 'step'})
                continue
            key, how = guess_key(it, keys, prog)
            pat = next((pp for kk, ww, pp in KEY_HINTS if kk == key), None)
            expect = extract_expect(it, key, pat) if key else ''
            if how == 'adv':
                _, adv_name = match_advanced(it)
                expect = adv_name
            rule['items'].append({'text': it, 'key': key, 'path': keys[key]['path'] if key in keys else
                                  ('Internet属性 > 高级' if how == 'adv' else ''),
                                  'expect': expect, 'how': how, 'score': unit})
            if q['qid'] == '69':
                print('  DBG69:', repr(it[:36]), '->', key or '(空)', '| how=', how, '| expect=', repr(expect))
            stat[how or '未匹配'] += 1
        # 同 key 去重（同题同一项只判一次）+ 期望值兜底（这一步必须在判断之前，否则能救回的题被跳过）
        seen_keys = set()
        for it in rule['items']:
            k = it.get('key')
            if not k:
                continue
            if k in seen_keys:
                it['key'] = ''
                it['how'] = 'dup'
            else:
                seen_keys.add(k)
            if it.get('key') and not it.get('expect'):
                g = guess_expect(it['text'], keys[it['key']]['default'], keys[it['key']]['path'])
                if g:
                    it['expect'] = g
                else:
                    it['key'] = ''
                    it['how'] = 'noexpect'

        # 以清单为准：兜底后一条都判不了的题才不要
        judge = [i for i in rule['items'] if i.get('key') and i.get('expect') and not i.get('step')]
        if not judge:
            print('  DEBUG 跳过 第%s题 prog=%s items=%d' % (q['qid'], prog, len(rule['items'])))
            continue

        # 分值按可判项重算，最后一条吃掉误差
        unit = round(rule['score'] / len(judge), 2)
        for i in judge:
            i['score'] = unit
        gap = round(rule['score'] - unit * len(judge), 2)
        judge[-1]['score'] = round(judge[-1]['score'] + gap, 2)
        for i in rule['items']:
            if i not in judge:
                i['score'] = 0
        matched = len(judge)
        rule['matched'] = matched
        rule['covered'] = matched == len(rule['items'])
        json.dump(rule, open(os.path.join(RULES, '%s.json' % rule['id']), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        made += 1
        report.append('### 第 %s 题（%g 分，程序 %s）%s' % (
            q['qid'], q['score'], prog, '　✅ 全覆盖' if rule['covered'] else ''))
        for i in rule['items']:
            report.append('- [%s] %s → `%s` 期望 `%s`' % (
                i['how'] or '未匹配', i['text'], i['key'] or '?', i['expect']))

    with open(os.path.join(RULES, '_report.md'), 'w', encoding='utf-8') as f:
        f.write('# %s 规则草稿校对表\n\n' % which + '\n'.join(report))

    print('生成 %d 份规则（分节 %s）' % (made, which))
    print('条目匹配情况:', dict(stat))
    covered = 0
    for q in picked:
        fp = os.path.join(RULES, 'w%s.json' % q['qid'])
        if os.path.exists(fp) and json.load(open(fp, encoding='utf-8')).get('covered'):
            covered += 1
    print('整题全覆盖:', covered, '/', made)


if __name__ == '__main__':
    main()
