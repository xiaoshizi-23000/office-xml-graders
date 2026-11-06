# -*- coding: utf-8 -*-
"""按程序补充练习题：每个程序 5 道小题，每题 5 条要求、每条 1 分。

题干按现有风格生成（"1、……设置为"xxx""），期望值取该设置项的非默认值：
开关型取反，文本型从备选值表里挑。
"""
import json
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB = os.path.join(BASE, 'windows_kb')
PROGS = os.path.join(KB, 'progs')
RULES = os.path.join(KB, 'rules')

# 文本型设置项的备选值（挑一个和默认不一样、语义合理的）
ALT = {
    'taskbarlocation': ['顶部', '左侧', '右侧'],
    'taskbarbtn': ['始终合并、隐藏标签', '任务栏被占满时合并', '从不合并'],
    'tz_yl': ['隐藏图标和通知', '仅显示通知'],
    'tz_wl': ['隐藏图标和通知', '仅显示通知'],
    'tz_cz': ['隐藏图标和通知', '仅显示通知'],
    'tz_zy': ['显示图标和通知', '隐藏图标和通知'],
    'poweruse': ['睡眠', '重新启动', '锁定', '注销'],
    'WindowsThemeIndex': ['0', '1', '2', '4', '5'],
    'resulution': ['1024 × 768', '1280 × 1024', '1440 × 900'],
    'Screen': ['三维文字', '彩带', '变幻线', '气泡'],
    'DisplayDPI': ['125%', '150%'],
    'BackgroundDisplay': ['0', '2', '3', '4', '5'],
    'gs_gs': ['英语(美国)', '中文(繁体，台湾)'],
    'gs_drq': ['yyyy-MM-dd', 'yy/M/d'],
    'gs_crq': ["yyyy'年'M'月'd'日'", "dddd, MMMM d, yyyy"],
    'gs_dsj': ['HH:mm', 'h:mm tt'],
    'gs_csj': ['HH:mm:ss', 'h:mm:ss tt'],
    'gs_dyt': ['星期一', '星期日'],
    'sz_xsd': [',', '．'],
    'sz_fzfh': ['.', ' '],
    'sz_fh': ['−', '△'],
    'sz_lbfe': ['；', '、'],
    'sz_dlh': ['美制', '公制'],
    'sz_ddsz': ['上下文', '从不'],
    'hb_hbfh': ['$', '€'],
    'sj_am': ['AM', '上午'],
    'sj_pm': ['PM', '下午'],
    'px_px': ['笔画', '拼音'],
    'wz_wz': ['美国', '中国'],
    'PrintNameSetup': ['Easy', 'Printer01'],
    'SelectPrintPort': ['LPT1:(打印机端口)', 'USB001', 'COM1:(串行端口)'],
    'InstallationPrintType': ['添加本地打印机', '添加网络、无线或 Bluetooth 打印机'],
    'connect_username': ['admin', 'user01'],
    'cg_fwq': ['10000', '172.16.1.1'],
    'PPPoEConnName': ['宽带连接a', '宽带连接b'],
    'PPPoEUserName': ['user01', 'admin'],
    'DefaultInputLanguage': ['英语(美国) - 美式键盘', '中文(简体，中国) - 中文(简体) - 美式键盘'],
    'LanguageBarPosition': ['1', '2', '3'],
    'Ipv4_IpAddress': ['192.168.1.100', '10.0.0.8'],
    'Ipv4_Mask': ['255.255.255.0', '255.255.0.0'],
    'Ipv4_Gateway': ['192.168.1.1', '10.0.0.1'],
    'Ipv4_MainDNS': ['8.8.8.8', '114.114.114.114'],
    'Ipv4_SubDNS': ['8.8.4.4', '223.5.5.5'],
    'General_Display_FontSize': ['小号', '大号'],
    'General_Display_MailList_PageSize': ['50', '100'],
    'Account_Info_DefaultName': ['小狮子', 'student'],
    'WriteMail_Topic': ['关于期中考试的通知', '作业提交提醒'],
    'WriteMail_Address': ['teacher@example.com', 'admin@school.edu.cn'],
    'WriteMail_Content': ['老师您好，附件是本次作业。', '请查收本月报表。'],
}

# 开关型 key：默认 0/1，取反即为非默认
def is_switch(default):
    return default in ('0', '1')


def key_cn(path):
    seg = path.split('>')[-1].strip()
    for pre in ('IPv4设置', 'IPv6设置', 'IPv4高级设置', 'IPv6高级设置', 'IPv4', 'IPv6'):
        if seg.startswith(pre):
            seg = seg[len(pre):]
    return seg


def phrase(key, base_cn, default, want):
    """按设置项类型生成一句要求。"""
    if is_switch(default):
        if key == 'keepwebsite':
            return '勾选「退出时删除浏览历史记录」' if want == '1' else '取消勾选「退出时删除浏览历史记录」'
        verb = '启用' if want == '1' else '关闭'
        return '%s「%s」' % (verb, base_cn)
    return '将「%s」设置为“%s”' % (base_cn, want)


def load_prog(prog):
    path = os.path.join(PROGS, prog + '.txt')
    rows = []
    for line in open(path, 'rb').read().decode('gbk').splitlines():
        p = line.split('□')
        if len(p) >= 3 and p[1].strip():
            rows.append({'key': p[1].strip(), 'path': p[0].strip(), 'default': p[2].strip()})
    return rows


TITLES = {
    'bhsxWin7': '宽带连接', 'iesxWin7': 'Internet 选项', 'jlljWin7': '连接向导',
    'outlook': '邮件设置', 'qyszWin7': '区域和语言', 'rwlsxWin7': '任务栏和开始菜单',
    'srfWin7': '输入法和语言栏', 'tjdyjWin7': '打印机', 'wangluoWin7': '网络 IPv4',
    'xianshiWin7': '显示和主题',
}


def main():
    made = 0
    index = []
    for prog in TITLES:
        rows = load_prog(prog)
        usable = []
        for r in rows:
            if is_switch(r['default']):
                r['want'] = '0' if r['default'] == '1' else '1'
                usable.append(dict(r))
            elif r['key'] in ALT:
                for v in ALT[r['key']]:
                    if v != r['default']:
                        x = dict(r); x['want'] = v
                        usable.append(x)
        # 文本型变体少时，用开关型再补一轮（换相反值，题干措辞也随之变化）
        if len(usable) < 25:
            for r in rows:
                if not is_switch(r['default']):
                    continue
                x = dict(r); x['want'] = r['default']
                usable.append(x)
        # 每个程序 5 道题，每题 5 条要求，每条 1 分（共 5 分）
        need = 25
        pool = usable[:need]
        if len(pool) < need:
            # 不够就循环填满，题面允许重复考同一项的不同取值
            while len(pool) < need:
                pool.append(pool[len(pool) % max(len(usable), 1)])
        for qi in range(5):
            chunk = pool[qi * 5:(qi + 1) * 5]
            qid = 'm%s%d' % (prog, qi + 1)
            items = []
            for n, r in enumerate(chunk, 1):
                cn = key_cn(r['path'])
                text = '%d、%s' % (n, phrase(r['key'], cn, r['default'], r['want']))
                items.append({'text': text, 'key': r['key'], 'path': r['path'],
                              'expect': r['want'], 'score': 1, 'how': 'manual'})
            rule = {'id': qid, 'section': '专项练习', 'qid': qid, 'group': prog,
                    'score': len(items), 'prog': prog,
                    'title': '%s · 第 %d 题' % (TITLES[prog], qi + 1), 'items': items,
                    'matched': len(items), 'covered': True}
            json.dump(rule, open(os.path.join(RULES, qid + '.json'), 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
            index.append({'id': qid, 'section': '专项练习', 'group': prog,
                          'qid': '%s-%d' % (prog, qi + 1),
                          'score': len(items), 'prog': prog, 'title': rule['title'],
                          'total': len(items), 'texts': [i['text'] for i in items]})
            made += 1
    print('生成专项练习 %d 题，覆盖 %d 个程序' % (made, len(TITLES)))
    json.dump(index, open(os.path.join(KB, 'practice_index.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
