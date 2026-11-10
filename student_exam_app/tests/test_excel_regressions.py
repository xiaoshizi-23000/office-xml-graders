# -*- coding: utf-8 -*-
"""Excel 判分回归：合法变体不能误扣，真错误不能放过。"""
import os
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(APP_DIR)
GRADER_DIR = os.path.join(APP_DIR, 'graders')
S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'

sys.path.insert(0, GRADER_DIR)
from _core import ExcelBook  # noqa: E402


def standard_answer(qid):
    return os.path.join(ROOT, 'Excel 2010 操作题题库', str(qid), '1结果.xlsx')


def rewrite_zip(src, dst, changes):
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename in changes:
                data = changes[item.filename](data)
            zout.writestr(item, data)


def copy_filter_result(data):
    """把标准答案的隐藏行删掉，模拟高级筛选“复制到其他位置”。"""
    ET.register_namespace('', S)
    root = ET.fromstring(data)
    sheet_data = root.find('{%s}sheetData' % S)
    for row in list(sheet_data):
        if row.get('hidden') == '1':
            sheet_data.remove(row)
        elif row.get('hidden') is not None:
            del row.attrib['hidden']
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def use_builtin_two_decimal(data):
    """删除显式 numFmt，改用 Excel 内置 numFmtId=2（0.00）。"""
    text = data.decode('utf-8')
    text = re.sub(r'<numFmts[^>]*>.*?</numFmts>', '', text, flags=re.S)
    text = text.replace('numFmtId="176"', 'numFmtId="2"')
    text = text.replace("numFmtId='176'", "numFmtId='2'")
    return text.encode('utf-8')


class ExcelRegressionTests(unittest.TestCase):
    def run_grader(self, qid, path):
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        proc = subprocess.run(
            [sys.executable, os.path.join(GRADER_DIR, 'excel_grader_%d.py' % qid), path],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            env=env, cwd=GRADER_DIR, timeout=120,
        )
        scores = re.findall(r'总分:\s*([\d.]+)', proc.stdout or '')
        self.assertEqual(proc.returncode, 0, proc.stderr[-500:])
        self.assertTrue(scores, proc.stdout[-500:])
        return float(scores[-1])

    def test_advanced_filter_accepts_all_standard_answers(self):
        for qid in (1, 2, 3, 4, 6, 7, 8, 10):
            with self.subTest(qid=qid):
                book = ExcelBook(standard_answer(qid))
                try:
                    ok, detail = book.advanced_filter_ok('筛选')
                finally:
                    book.close()
                self.assertTrue(ok, detail)

    def test_advanced_filter_copy_result_variant_is_full_score(self):
        with tempfile.TemporaryDirectory() as td:
            variant = os.path.join(td, 'copy-result.xlsx')
            rewrite_zip(standard_answer(2), variant,
                        {'xl/worksheets/sheet2.xml': copy_filter_result})
            self.assertEqual(self.run_grader(2, variant), 100.0)

    def test_advanced_filter_unfiltered_data_is_rejected(self):
        def unhide_everything(data):
            ET.register_namespace('', S)
            root = ET.fromstring(data)
            sheet_data = root.find('{%s}sheetData' % S)
            for row in sheet_data:
                if row.get('hidden') is not None:
                    del row.attrib['hidden']
            return ET.tostring(root, encoding='utf-8', xml_declaration=True)

        with tempfile.TemporaryDirectory() as td:
            variant = os.path.join(td, 'unfiltered.xlsx')
            rewrite_zip(standard_answer(2), variant,
                        {'xl/worksheets/sheet2.xml': unhide_everything})
            book = ExcelBook(variant)
            try:
                ok, _ = book.advanced_filter_ok('筛选')
            finally:
                book.close()
            self.assertFalse(ok)

    def test_builtin_two_decimal_format_is_full_score(self):
        with tempfile.TemporaryDirectory() as td:
            variant = os.path.join(td, 'builtin-0.00.xlsx')
            rewrite_zip(standard_answer(2), variant,
                        {'xl/styles.xml': use_builtin_two_decimal})
            with zipfile.ZipFile(variant) as zf:
                styles = zf.read('xl/styles.xml')
                self.assertNotIn(b'0.00', styles)
            self.assertEqual(self.run_grader(2, variant), 100.0)


if __name__ == '__main__':
    unittest.main()
