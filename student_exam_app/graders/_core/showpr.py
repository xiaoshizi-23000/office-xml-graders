"""放映设置检查：p:showPr 解析"""
import re


def show_props(deck):
    """返回 dict: kind/loop/anim/st/en/manual/pen"""
    try:
        x = deck.read('ppt/presentation.xml')
    except Exception:
        return {}
    m = re.search(r'<p:showPr([^>]*)>(.*?)</p:showPr>', x, re.S)
    if not m:
        return {}
    attrs, body = m.group(1), m.group(2)
    kinds = re.findall(r'<p:(present|kiosk|browse)/>', body)
    rng = re.search(r'<p:sldRg[^>]*st="(\d+)"[^>]*end="(\d+)"', body)
    pen = re.search(r'<p:penClr>\s*<a:srgbClr val="([0-9A-Fa-f]{6})"', body)
    return {
        'kind': kinds[0] if kinds else '',
        'loop': re.search(r'loop="(\d)"', attrs).group(1) if re.search(r'loop="(\d)"', attrs) else '',
        'anim': re.search(r'showAnimation="(\d)"', attrs).group(1) if re.search(r'showAnimation="(\d)"', attrs) else '1',
        'manual': re.search(r'useTimings="(\d)"', attrs).group(1) if re.search(r'useTimings="(\d)"', attrs) else '',
        'st': int(rng.group(1)) if rng else None,
        'en': int(rng.group(2)) if rng else None,
        'pen': pen.group(1).upper() if pen else '',
        'raw': m.group(0),
    }


def check_show(deck, kind='present', loop=None, st=None, en=None, anim=None, manual=None, pen=None):
    """按题干要求核对放映设置，返回 (是否通过, 明细文字)"""
    p = show_props(deck)
    if not p:
        return (False, '未找到放映设置')
    notes, ok = [], True
    if kind:
        if p['kind'] == kind:
            notes.append('类型正确')
        else:
            ok = False
            notes.append('类型=%s（要 %s）' % (p['kind'] or '无', kind))
    if loop is not None:
        if p['loop'] == str(loop):
            notes.append('循环' if loop else '不循环')
        else:
            ok = False
            notes.append('loop=%s' % (p['loop'] or '未设'))
    if st is not None and en is not None:
        if p['st'] == st and p['en'] == en:
            notes.append('范围 %d-%d' % (st, en))
        else:
            ok = False
            notes.append('范围=%s-%s（要 %d-%d）' % (p['st'], p['en'], st, en))
    if anim is not None:
        if p['anim'] == str(anim):
            notes.append('动画显示' if anim else '不放动画')
        else:
            ok = False
            notes.append('showAnimation=%s' % p['anim'])
    if manual is not None:
        if p['manual'] == str(0 if manual else 1):
            notes.append('手动换片' if manual else '按计时换片')
        else:
            ok = False
            notes.append('useTimings=%s' % (p['manual'] or '未设'))
    if pen:
        if p['pen'] == pen.upper():
            notes.append('画笔颜色 OK')
        else:
            ok = False
            notes.append('画笔=%s' % (p['pen'] or '未设'))
    return (ok, '；'.join(notes))
