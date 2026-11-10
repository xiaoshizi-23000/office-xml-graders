# -*- coding: utf-8 -*-
"""Flask 上传、安全入口和 Windows 复合值回归。"""
import io
import os
import sys
import tempfile
import unittest
import zipfile
from unittest import mock

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP_DIR)
os.environ['EXAM_JANITOR'] = '0'

import app as exam  # noqa: E402


class WebSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        exam.app.config['TESTING'] = True
        cls.client = exam.app.test_client()

    def test_health_is_ok(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'ok')
        self.assertGreater(data['graders'], 0)
        self.assertGreater(data['questions'], 0)

    def test_baidu_verify_rejects_html(self):
        response = self.client.get(
            '/baidu_verify_%3Cimg%20src%3Dx%20onerror%3Dalert(1)%3E.html')
        self.assertEqual(response.status_code, 404)

    def test_windows_qid_traversal_is_rejected(self):
        snapshot = 'A\u25a1homepage\u25a1x\n'.encode('utf-8')
        response = self.client.post(
            '/api/windows/check',
            data={'qid': '../w1', 'file': (io.BytesIO(snapshot), 'snapshot.txt')},
            content_type='multipart/form-data',
        )
        self.assertEqual(response.status_code, 400)

    def test_windows_composite_value_matching(self):
        self.assertTrue(exam._windows_value_ok('中\u25a0启用保护模式', '中'))
        self.assertTrue(exam._windows_value_ok(
            '历史记录\u25a0表单数据', '表单数据\u25a0历史记录'))
        self.assertFalse(exam._windows_value_ok(
            '历史记录\u25a0表单数据', '历史记录\u25a0密码'))
        self.assertTrue(exam._windows_value_ok(
            'LPT3:(打印机端口)', 'LPT3', mode='contains'))

    def test_archive_traversal_and_entry_limit(self):
        with tempfile.TemporaryDirectory() as td:
            bad_path = os.path.join(td, 'bad.zip')
            with zipfile.ZipFile(bad_path, 'w') as zf:
                zf.writestr('../escape.txt', 'x')
            with self.assertRaises(exam.ArchiveError):
                exam.validate_archive(bad_path)

            many = os.path.join(td, 'many.zip')
            with zipfile.ZipFile(many, 'w') as zf:
                zf.writestr('a.txt', '1')
                zf.writestr('b.txt', '2')
            with mock.patch.object(exam, 'ZIP_MAX_FILES', 1):
                with self.assertRaises(exam.ArchiveTooLarge):
                    exam.validate_archive(many)

    def test_tempdir_failure_releases_slot(self):
        before = exam.SLOTS._value
        with mock.patch.object(exam.tempfile, 'mkdtemp', side_effect=OSError('disk full')), \
                mock.patch.object(exam.app.logger, 'exception'):
            response = self.client.post(
                '/api/grade/word/1',
                data={'file': (io.BytesIO(b'x'), 'a.docx')},
                content_type='multipart/form-data',
            )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(exam.SLOTS._value, before)

    def test_grader_failure_is_not_counted_as_score(self):
        docx = os.path.join(APP_DIR, 'materials', 'word', '1', '3题干.docx')
        with open(docx, 'rb') as f:
            payload = f.read()
        exam.TODAY = {'date': '', 'count': 0}
        with mock.patch.object(exam, 'run_grader',
                               return_value=(None, ['[info] 评分器运行失败'], 'grader_failed')):
            response = self.client.post(
                '/api/grade/word/1',
                data={'file': (io.BytesIO(payload), 'a.docx')},
                content_type='multipart/form-data',
            )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(exam.today_count(), 0)

    def test_unparseable_score_is_not_returned_as_success(self):
        docx = os.path.join(APP_DIR, 'materials', 'word', '1', '3题干.docx')
        with open(docx, 'rb') as f:
            payload = f.read()
        exam.TODAY = {'date': '', 'count': 0}
        with mock.patch.object(exam, 'run_grader',
                               return_value=('评分: broken', None, None)):
            response = self.client.post(
                '/api/grade/word/1',
                data={'file': (io.BytesIO(payload), 'a.docx')},
                content_type='multipart/form-data',
            )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(exam.today_count(), 0)


if __name__ == '__main__':
    unittest.main()
