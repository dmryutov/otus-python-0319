from datetime import date
import pathlib
import sys
import unittest

import log_analyzer as la


class GetConfigPathTestCase(unittest.TestCase):
    def test_default_path(self):
        path = la.get_config_path()
        self.assertEqual(path, './config.json')

    def test_path_from_args(self):
        sys.argv.append('--config=1.json')

        path = la.get_config_path()
        self.assertEqual(path, '1.json')
        sys.argv.pop()


class LoadConfigTestCase(unittest.TestCase):
    def test_ok(self):
        config = la.load_config()
        self.assertEqual(config, {
            'REPORT_SIZE': 500,
            'REPORT_DIR': './reports',
            'LOG_DIR': './log',
            'LOG_FILE': None,
            'ERROR_PERCENT': 10,
        })

    def test_no_file(self):
        path = '1.json'
        sys.argv.append('--config={}'.format(path))
        self.assertRaises(FileNotFoundError, la.load_config)
        sys.argv.pop()

    def test_not_dict(self):
        path = '1.json'
        sys.argv.append('--config={}'.format(path))
        with open(path, 'w', encoding='utf-8') as f:
            f.write('[]')

        self.assertRaises(TypeError, la.load_config)
        pathlib.Path(path).unlink()
        sys.argv.pop()


class GetLatestLogFileTestCase(unittest.TestCase):
    def test_ok(self):
        log_dir = pathlib.Path('log')
        log_file = la.get_latest_log_file(log_dir)
        self.assertEqual(log_file, la.LogFile(pathlib.Path('log/nginx-access-ui.log-20170630.gz'),
                                              date(2017, 6, 30), '.gz'))

    def test_no_log_file(self):
        log_dir = pathlib.Path('log2')
        log_dir.mkdir()

        log_file = la.get_latest_log_file(log_dir)
        self.assertIsNone(log_file)
        log_dir.rmdir()

    def test_no_log_dir(self):
        log_dir = pathlib.Path('no_dir')
        self.assertRaises(FileNotFoundError, la.get_latest_log_file, log_dir)


class GetReportPathTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.log_file = la.LogFile(pathlib.Path('log/nginx-access-ui.log-20170630.gz'),
                                  date(2017, 6, 30), '.gz')

    def test_ok(self):
        report_dir = pathlib.Path('reports')
        log_file = la.get_report_path(self.log_file, report_dir)
        self.assertEqual(log_file, pathlib.Path('reports/report-2017.06.30.html'))

    def test_no_dir(self):
        report_dir = pathlib.Path('no_dir')
        self.assertRaises(FileNotFoundError, la.get_report_path, self.log_file, report_dir)


class ParseLineTestCase(unittest.TestCase):
    def test_ok(self):
        line = '1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] ' \
               '"GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" ' \
               '"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" ' \
               '"1498697422-2190034393-4708-9752759" "dc7161be3" 0.390'
        request = la.parse_line(line)
        self.assertEqual(request, la.LogLine('GET /api/v2/banner/25019354 HTTP/1.1', 0.390))

    def test_bad_line(self):
        line = '1.194.135.240 -  - [29/Jun/2017:10:15:45 +0300] ' \
               '"HEAD /slots/3938/ HTTP/1.1" 302 0 "-" ' \
               '"Microsoft Office Excel 2013" "-" ' \
               '"1498720545-244168387-4707-10016820" "-" 0.ABC0'
        request = la.parse_line(line)
        self.assertIsNone(request)


class ExtractInfoFromFileTestCase(unittest.TestCase):
    def test_plain(self):
        log_file = la.LogFile(pathlib.Path('log/test_log'), date(2019, 1, 1), ext='')
        error_percent = 10
        requests = la.extract_info_from_file(log_file, error_percent)
        self.assertEqual(requests, {
            'GET /api/v2/banner/25019354 HTTP/1.1': [0.39],
            'GET /api/1/photogenic_banners/list/?server_name=WIN7RB4 HTTP/1.1': [0.133],
            'GET /api/v2/banner/16852664 HTTP/1.1': [0.199],
            'GET /api/v2/slot/4705/groups HTTP/1.1': [0.704],
            'GET /api/v2/internal/banner/24294027/info HTTP/1.1': [0.146]
        })

    def test_zip(self):
        log_file = la.LogFile(pathlib.Path('log/test_log.gz'), date(2019, 1, 1), ext='.gz')
        error_percent = 10
        requests = la.extract_info_from_file(log_file, error_percent)
        self.assertEqual(requests, {
            'GET /api/v2/banner/25019354 HTTP/1.1': [0.39],
            'GET /api/1/photogenic_banners/list/?server_name=WIN7RB4 HTTP/1.1': [0.133],
            'GET /api/v2/banner/16852664 HTTP/1.1': [0.199],
            'GET /api/v2/slot/4705/groups HTTP/1.1': [0.704],
            'GET /api/v2/internal/banner/24294027/info HTTP/1.1': [0.146]
        })

    def test_error_limit(self):
        log_file = la.LogFile(pathlib.Path('log/test_log_error'), date(2019, 1, 1), ext='')
        error_percent = 10
        self.assertRaises(ValueError, la.extract_info_from_file, log_file, error_percent)


class PrepareReportDataTestCase(unittest.TestCase):
    def test_ok(self):
        requests = {
            'url1': [0.39, 0.24, 0.51],
            'url2': [0.45, 0.11],
            'url3': [0.4],
        }
        report_size = 2
        report_data = la.prepare_report_data(requests, report_size)
        self.assertEqual(report_data, [
            {
                'url': 'url1',
                'count': 3,
                'count_perc': 50.0,
                'time_sum': 1.14,
                'time_perc': 54.286,
                'time_avg': 0.38,
                'time_max': 0.51,
                'time_med': 0.39
            },
            {
                'url': 'url2',
                'count': 2,
                'count_perc': 33.333,
                'time_sum': 0.56,
                'time_perc': 26.667,
                'time_avg': 0.28,
                'time_max': 0.45,
                'time_med': 0.28
            }
        ])


class CreateReportTestCase(unittest.TestCase):
    def test_ok(self):
        report_data = [
            {
                'url': 'url1',
                'count': 3,
                'count_perc': 50.0,
                'time_sum': 1.14,
                'time_perc': 54.286,
                'time_avg': 0.38,
                'time_max': 0.51,
                'time_med': 0.39
            },
            {
                'url': 'url2',
                'count': 2,
                'count_perc': 33.333,
                'time_sum': 0.56,
                'time_perc': 26.667,
                'time_avg': 0.28,
                'time_max': 0.45,
                'time_med': 0.28
            }
        ]
        report_dir = pathlib.Path('reports')
        log_date = date(2019, 1, 1)
        report_path = pathlib.Path('reports/report-2019.01.01.html')

        path = la.create_report(report_data, report_dir, log_date)
        self.assertEqual(path, report_path)

        path.unlink()


if __name__ == '__main__':
    unittest.main()
