from http.client import HTTPConnection
import unittest


class HttpServer(unittest.TestCase):
    host = '127.0.0.1'
    port = 8080

    def setUp(self):
        self.conn = HTTPConnection(self.host, self.port, timeout=10)

    def tearDown(self):
        self.conn.close()

    def test_ok(self):
        """Correct IP"""
        self.conn.request('GET', '/ip2w/178.219.186.12')
        r = self.conn.getresponse()
        self.assertEqual(int(r.status), 200)

    def test_no_ip(self):
        """No IP"""
        self.conn.request('GET', '/ip2w/')
        r = self.conn.getresponse()
        self.assertIn(int(r.status), [200, 500])

    def test_invalid_ip(self):
        """Invalid IP"""
        self.conn.request('GET', '/ip2w/400.219.1860.12')
        r = self.conn.getresponse()
        self.assertEqual(int(r.status), 400)

    def test_internal_ip(self):
        """Internal IP"""
        self.conn.request('GET', '/ip2w/127.0.0.1')
        r = self.conn.getresponse()
        self.assertEqual(int(r.status), 500)

    def test_subdir_after_ip(self):
        """Subdir after IP"""
        self.conn.request('GET', '/ip2w/178.219.186.12/subdir1/')
        r = self.conn.getresponse()
        self.assertEqual(int(r.status), 400)


loader = unittest.TestLoader()
suite = unittest.TestSuite()
a = loader.loadTestsFromTestCase(HttpServer)
suite.addTest(a)


class NewResult(unittest.TextTestResult):
    def getDescription(self, test):
        doc_first_line = test.shortDescription()
        return doc_first_line or ''


class NewRunner(unittest.TextTestRunner):
    resultclass = NewResult


runner = NewRunner(verbosity=2)
runner.run(suite)
