
import unittest


class ExampleTest(unittest.TestCase):
    """ Пример теста """
    def setUp(self):
        self.maxDiff = None
        self.tearDown()

    def tearDown(self):
        pass

    def test_first(self):
        """ Пример тестового метода """
        self.assertEqual(True, True)