# -*- coding: utf-8 -*-
"""每天跑一次的 SEO 体检：页面健康 + 蜘蛛来访 + 收录查询入口。

用法：
    python tools/seo_check.py

说明：各引擎的 site: 结果对机房 IP 不稳定（会弹验证码、返回降级页面），
所以收录判断不做自动抓取，只输出查询链接，人工点开看更准。
本脚本负责能稳定拿到的部分：页面元素是否齐全、蜘蛛来没来、页面是否 200。

输出：终端 + tools/seo_report.txt
"""
import datetime
import os
import re
import subprocess
import urllib.error
import urllib.request

SITE = 'https://web.xiaoshizi.asia'
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'tools', 'seo_report.txt')
SSH_KEY = os.path.expanduser('~/.workbuddy/secrets/xiaoshizi.pem')
SSH_HOST = 'root@8.137.181.130'
SSH_PORT = '31318'

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0 Safari/537.36')

PAGES = ['/', '/windows', '/exam', '/knowledge', '/typing', '/faq', '/q/excel/1', '/sitemap.xml', '/robots.txt',
         '/llms.txt', '/a7f3c9e14b8d4f62a1c05e7d3b9f8a26.txt']

QUERIES = [
    ('百度', 'https://www.baidu.com/s?wd=site%3Aweb.xiaoshizi.asia'),
    ('360', 'https://www.so.com/s?q=site%3Aweb.xiaoshizi.asia'),
    ('搜狗', 'https://www.sogou.com/web?query=site%3Aweb.xiaoshizi.asia'),
    ('必应', 'https://cn.bing.com/search?q=site%3Aweb.xiaoshizi.asia'),
]


def get(path):
    req = urllib.request.Request(SITE + path, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b''
    except Exception:
        return 'ERR', b''


def page_health():
    rows = []
    for path in PAGES:
        code, body = get(path)
        text = body.decode('utf-8', 'replace')
        flags = []
        if path == '/' or path.startswith('/q/'):
            if re.search(r'<title>[^<]{8,}', text):
                flags.append('title')
            if 'name="description"' in text:
                flags.append('desc')
        if path == '/windows' or path.startswith('/q/'):
            if 'rel="canonical"' in text:
                flags.append('canonical')
        if 'application/ld+json' in text:
            flags.append('结构化数据')
        rows.append((path, code, len(body), '/'.join(flags) or '-'))
    return rows


def spider_stats():
    remote = ("for k in Baiduspider 360Spider bingbot Sogou Bytespider; do "
              "printf '%s ' $k; grep -hi $k /www/wwwlogs/*.log 2>/dev/null "
              "| grep -v 127.0.0.1 | wc -l; done")
    cmd = ['ssh', '-i', SSH_KEY, '-p', SSH_PORT,
           '-o', 'StrictHostKeyChecking=accept-new', '-o', 'ConnectTimeout=12',
           SSH_HOST, remote]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        out = r.stdout
    except Exception as e:
        return {}, 'SSH 失败：%s' % str(e)[:60]
    counts = {}
    for line in out.splitlines():
        m = re.match(r'^(\w+)\s+(\d+)\s*$', line.strip())
        if m:
            counts[m.group(1)] = int(m.group(2))
    return counts, ''


def main():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = ['SEO 体检 %s' % now, '=' * 46, '', '一、页面健康']
    for path, code, size, flags in page_health():
        lines.append('  %-44s %-4s %6d 字节  %s' % (path, code, size, flags))

    counts, err = spider_stats()
    lines += ['', '二、蜘蛛累计来访（已排除本机测试）']
    if err:
        lines.append('  ' + err)
    else:
        for k in ('Baiduspider', '360Spider', 'bingbot', 'Sogou', 'Bytespider'):
            lines.append('  %-16s %d 次' % (k, counts.get(k, 0)))

    lines += ['', '三、收录查询（点开人工确认）']
    for name, url in QUERIES:
        lines.append('  %-4s %s' % (name, url))

    report = '\n'.join(lines)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(report + '\n')
    print(report)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
