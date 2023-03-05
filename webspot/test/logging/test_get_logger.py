import unittest
from io import StringIO
from unittest.mock import patch

from webspot.logging import get_logger


class TestGetLogger(unittest.TestCase):
    # @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_get_logger(self, stderr):
        logger = get_logger('web.utils.time')
        text = 'it works'
        logger.info(text)
        # print(stdout.getvalue())
        # a = stdout.getvalue()
        # print(stderr.getvalue())
        # b = stderr.getvalue()
        self.assertTrue(text in stderr.getvalue())
        # self.assertTrue(text in stdout.getvalue())


if __name__ == '__main__':
    unittest.main()
